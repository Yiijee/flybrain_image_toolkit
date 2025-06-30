# input arguments: folder 1, folder 2, suffixs (_density_map.nrrd)
# check if the folders exist
# check if the suffixs are valid in both folders
# calculate online statistics for image
# compare between two groups
# save the results

import numpy as np
import nrrd
from scipy.stats import ttest_ind_from_stats
from statsmodels.stats.multitest import fdrcorrection
import os
import sys
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import argparse
from tqdm import tqdm

def calculate_online_stats_3d(array_paths):
    """
    Calculates the element-wise mean and variance for a group of large 3D arrays
    using Welford's online algorithm to conserve memory.

    Args:
        array_paths (list): A list of file paths to the .npy or .nrrd files.

    Returns:
        tuple: (mean_array, variance_array, count)
    """
    if not array_paths:
        return None, None, 0

    n = 0
    
    # Initialize based on the first array's shape
    first_path = array_paths[0]
    if first_path.endswith('.npy'):
        first_array = np.load(first_path)
    else:  # Assume it's an nrrd file
        first_array, _ = nrrd.read(first_path)
        
    mean_arr = np.zeros(first_array.shape, dtype=np.float64)
    S_arr = np.zeros(first_array.shape, dtype=np.float64) # Sum of squared differences
    del first_array

    print(f"Calculating online stats for {len(array_paths)} arrays...")
    for path in tqdm(array_paths, desc="Processing arrays", unit="file"):
        # This is the only point a large array is loaded into memory
        if path.endswith('.npy'):
            current_array = np.load(path).astype(np.float64)
        else:  # Assume it's an nrrd file
            current_array, _ = nrrd.read(path)
            current_array = current_array.astype(np.float64)
        
        n += 1
        delta = current_array - mean_arr
        mean_arr += delta / n
        delta2 = current_array - mean_arr
        S_arr += delta * delta2
    
    if n < 2:
        # Variance is undefined for a single sample
        variance_arr = np.zeros(mean_arr.shape, dtype=np.float64)
    else:
        variance_arr = S_arr / (n - 1)
        
    print("...calculation complete.")
    return mean_arr, variance_arr, n

def compare_groups_voxelwise(group_a_paths, group_b_paths, alpha=0.05):
    """
    Performs a voxel-wise independent t-test between two groups of arrays
    and corrects for multiple comparisons.

    Args:
        group_a_paths (list): File paths for arrays in group A.
        group_b_paths (list): File paths for arrays in group B.
        alpha (float): The significance level for FDR correction.

    Returns:
        dict: A dictionary containing the t-stats, p-values, and a 
              boolean mask of significant voxels after correction.
    """
    # 1. & 2. Calculate statistics for each group
    mean_A, var_A, n_A = calculate_online_stats_3d(group_a_paths)
    mean_B, var_B, n_B = calculate_online_stats_3d(group_b_paths)

    if n_A < 2 or n_B < 2:
        raise ValueError("Each group must contain at least two arrays to perform a t-test.")

    # 3. Perform the t-test using the calculated statistics
    print("Performing element-wise t-test...")
    # Suppress warnings for divisions by zero in variance, they will result in NaN
    with np.errstate(divide='ignore', invalid='ignore'):
        t_stats, p_values = ttest_ind_from_stats(
            mean1=mean_A, std1=np.sqrt(var_A), nobs1=n_A,
            mean2=mean_B, std2=np.sqrt(var_B), nobs2=n_B,
            equal_var=False  # Welch's t-test is generally safer
        )

    # Handle cases where variance was zero for both groups (NaN result)
    t_stats[np.isnan(t_stats)] = 0
    p_values[np.isnan(p_values)] = 1.0

    # 4. Correct for multiple comparisons using FDR
    print(f"Correcting for multiple comparisons using FDR (alpha={alpha})...")
    
    # The correction function needs a 1D array of p-values
    original_shape = p_values.shape
    p_values_flat = p_values.flatten()
    
    # Use tqdm to show progress for this potentially long operation
    with tqdm(total=1, desc="FDR correction", unit="operation") as pbar:
        rejected, p_values_corrected = fdrcorrection(p_values_flat, alpha=alpha)
        pbar.update(1)
    
    # Reshape the results back to the original 3D shape
    significant_mask = rejected.reshape(original_shape)

    return {
        "t_statistics": t_stats,
        "p_values_uncorrected": p_values,
        "p_values_corrected_fdr": p_values_corrected.reshape(original_shape),
        "significant_mask_fdr": significant_mask,
        "mean_diff": mean_B - mean_A  # Difference in means (B-A)
    }

def visualize_t_stats(t_stats, significant_mask, mean_diff, output_prefix):
    """
    Visualizes t-statistics and significant voxels as max projections.
    
    Args:
        t_stats (ndarray): 3D array of t-statistics
        significant_mask (ndarray): Boolean mask of significant voxels
        mean_diff (ndarray): Mean difference between groups
        output_prefix (str): Prefix for output filenames
    """
    # Create a custom colormap for t-statistics (blue-white-red)
    t_cmap = LinearSegmentedColormap.from_list('t_stats', ['blue', 'white', 'red'])
    
    # Create figures for each projection axis
    axes = ['X', 'Y', 'Z']
    
    for axis_idx, axis_name in enumerate(axes):
        fig, axs = plt.subplots(1, 3, figsize=(18, 6))
        
        # Max projection of t-statistics
        t_proj = np.max(np.abs(t_stats), axis=axis_idx)
        im0 = axs[0].imshow(t_proj, cmap=t_cmap, vmin=-5, vmax=5)
        axs[0].set_title(f'Max |t-statistic| Projection ({axis_name})', fontsize=12)
        axs[0].axis('off')
        plt.colorbar(im0, ax=axs[0], shrink=0.8)
        
        # Max projection of significant voxels
        sig_proj = np.any(significant_mask, axis=axis_idx)
        axs[1].imshow(sig_proj, cmap='hot')
        axs[1].set_title(f'Significant Voxels Projection ({axis_name})', fontsize=12)
        axs[1].axis('off')
        
        # Directional difference between groups where significant
        diff_mask = np.zeros_like(mean_diff)
        diff_mask[significant_mask] = mean_diff[significant_mask]
        diff_proj = np.max(np.abs(diff_mask), axis=axis_idx) * np.sign(np.take(diff_mask, 
                                                                     np.argmax(np.abs(diff_mask), 
                                                                              axis=axis_idx), 
                                                                    axis=axis_idx))
        im2 = axs[2].imshow(diff_proj, cmap=t_cmap)
        axs[2].set_title(f'Mean Difference (Significant Only) ({axis_name})', fontsize=12)
        axs[2].axis('off')
        plt.colorbar(im2, ax=axs[2], shrink=0.8)
        
        plt.tight_layout()
        
        # Save figure
        output_path = f"{output_prefix}_t_stats_projection_{axis_name}.png"
        fig.savefig(output_path, dpi=300)
        plt.close(fig)
        print(f"Saved {axis_name}-projection visualization to: {output_path}")

def visualize_single_projection(t_stats, significant_mask, mean_diff, output_prefix, axis_idx, axis_name):
    """
    Visualizes t-statistics for a single projection axis to reduce memory usage.
    
    Args:
        t_stats (ndarray): 3D array of t-statistics
        significant_mask (ndarray): Boolean mask of significant voxels
        mean_diff (ndarray): Mean difference between groups
        output_prefix (str): Prefix for output filenames
        axis_idx (int): Index of axis to project (0=X, 1=Y, 2=Z)
        axis_name (str): Name of axis ('X', 'Y', or 'Z')
    """
    # Create a custom colormap for t-statistics
    t_cmap = LinearSegmentedColormap.from_list('t_stats', ['blue', 'white', 'red'])
    
    fig, axs = plt.subplots(1, 3, figsize=(18, 6))
    
    # Max projection of t-statistics
    t_proj = np.max(np.abs(t_stats), axis=axis_idx)
    im0 = axs[0].imshow(t_proj, cmap=t_cmap, vmin=-5, vmax=5)
    axs[0].set_title(f'Max |t-statistic| Projection ({axis_name})', fontsize=12)
    axs[0].axis('off')
    plt.colorbar(im0, ax=axs[0], shrink=0.8)
    
    # Max projection of significant voxels
    sig_proj = np.any(significant_mask, axis=axis_idx)
    axs[1].imshow(sig_proj, cmap='hot')
    axs[1].set_title(f'Significant Voxels Projection ({axis_name})', fontsize=12)
    axs[1].axis('off')
    
    # Directional difference between groups where significant
    diff_mask = np.zeros_like(mean_diff)
    diff_mask[significant_mask] = mean_diff[significant_mask]
    
    # Calculate max projection with sign preserved
    # This is a memory-efficient version
    max_indices = np.argmax(np.abs(diff_mask), axis=axis_idx)
    diff_proj = np.zeros_like(np.take(diff_mask, 0, axis=axis_idx))
    
    # Use a loop to handle potentially large arrays
    for i in range(diff_proj.shape[0]):
        for j in range(diff_proj.shape[1]):
            if axis_idx == 0:
                idx = max_indices[i, j]
                diff_proj[i, j] = diff_mask[idx, i, j] if idx > 0 else 0
            elif axis_idx == 1:
                idx = max_indices[i, j]
                diff_proj[i, j] = diff_mask[i, idx, j] if idx > 0 else 0
            else:
                idx = max_indices[i, j]
                diff_proj[i, j] = diff_mask[i, j, idx] if idx > 0 else 0
    
    im2 = axs[2].imshow(diff_proj, cmap=t_cmap)
    axs[2].set_title(f'Mean Difference (Significant Only) ({axis_name})', fontsize=12)
    axs[2].axis('off')
    plt.colorbar(im2, ax=axs[2], shrink=0.8)
    
    plt.tight_layout()
    
    # Save figure
    output_path = f"{output_prefix}_t_stats_projection_{axis_name}.png"
    fig.savefig(output_path, dpi=300)
    plt.close(fig)
    print(f"Saved {axis_name}-projection visualization to: {output_path}")

def save_results(results, output_prefix, header=None):
    """
    Saves the results of the voxel-wise t-test.
    
    Args:
        results (dict): The results from compare_groups_voxelwise
        output_prefix (str): Prefix for output filenames
        header (dict, optional): Header information for nrrd files
    """
    # Save t-statistics
    nrrd.write(f"{output_prefix}_t_statistics.nrrd", 
               results["t_statistics"].astype(np.float32), 
               header=header)
    
    # Save p-values (uncorrected)
    nrrd.write(f"{output_prefix}_p_values_uncorrected.nrrd", 
               results["p_values_uncorrected"].astype(np.float32), 
               header=header)
    
    # Save p-values (FDR-corrected)
    nrrd.write(f"{output_prefix}_p_values_corrected_fdr.nrrd", 
               results["p_values_corrected_fdr"].astype(np.float32), 
               header=header)
    
    # Save significant mask
    nrrd.write(f"{output_prefix}_significant_mask_fdr.nrrd", 
               results["significant_mask_fdr"].astype(np.uint8), 
               header=header)
    
    # Save mean difference
    nrrd.write(f"{output_prefix}_mean_difference.nrrd", 
               results["mean_diff"].astype(np.float32), 
               header=header)
    
    print(f"Saved all result files with prefix: {output_prefix}")

def get_files_with_suffix(folder_path, suffix):
    """
    Gets all files in a folder with the specified suffix.
    
    Args:
        folder_path (str): Path to the folder
        suffix (str): File suffix to match
        
    Returns:
        list: List of file paths
    """
    if not os.path.exists(folder_path):
        raise ValueError(f"Folder not found: {folder_path}")
        
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) 
             if f.endswith(suffix)]
    
    if not files:
        raise ValueError(f"No files with suffix '{suffix}' found in {folder_path}")
        
    return files

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Perform voxel-wise t-tests between two groups of 3D images.")
    parser.add_argument("folder1", help="Path to folder containing group 1 images")
    parser.add_argument("folder2", help="Path to folder containing group 2 images")
    parser.add_argument("--suffix", default="_density_map.nrrd", help="Suffix of files to analyze")
    parser.add_argument("--alpha", type=float, default=0.05, help="Significance level for FDR correction")
    parser.add_argument("--output", default="voxel_ttest_results", help="Output filename prefix")
    
    args = parser.parse_args()
    
    try:
        # Get files for each group
        group1_files = get_files_with_suffix(args.folder1, args.suffix)
        group2_files = get_files_with_suffix(args.folder2, args.suffix)
        
        print(f"Group 1: Found {len(group1_files)} files in {args.folder1}")
        print(f"Group 2: Found {len(group2_files)} files in {args.folder2}")
        
        # Read one file to get the header
        _, header = nrrd.read(group1_files[0])
        
        # Compare groups
        results = compare_groups_voxelwise(group1_files, group2_files, alpha=args.alpha)
        
        # Save results
        try:
            print("Saving results...")
            save_results(results, args.output, header=header)
            
            print("Generating visualizations...")
            # Process one projection at a time to reduce memory usage
            for axis_idx, axis_name in enumerate(['X', 'Y', 'Z']):
                visualize_single_projection(
                    results["t_statistics"], 
                    results["significant_mask_fdr"],
                    results["mean_diff"],
                    args.output,
                    axis_idx,
                    axis_name
                )
                # Force garbage collection between projections
                import gc
                gc.collect()
            
            # Print summary
            significant_count = np.sum(results["significant_mask_fdr"])
            total_voxels = results["significant_mask_fdr"].size
            print(f"Analysis complete. {significant_count} out of {total_voxels} voxels "
                  f"({significant_count/total_voxels*100:.2f}%) were significant at alpha={args.alpha}.")
                  
        except MemoryError:
            print("ERROR: The system ran out of memory while processing the results.")
            print("Consider using a machine with more RAM or reducing the image resolution.")
            sys.exit(1)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        # Clean up any potentially leaked resources
        import multiprocessing
        if hasattr(multiprocessing, 'resource_tracker'):
            try:
                multiprocessing.resource_tracker._resource_tracker.clear()
            except:
                pass

