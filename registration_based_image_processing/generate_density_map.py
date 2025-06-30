# load libaries

import os
import sys
import numpy as np
import nrrd
import matplotlib.pyplot as plt
from skimage import filters
from scipy import ndimage


# IO
def read_nrrd(file_path):
    data, header = nrrd.read(file_path)
    return data, header

# Thresholding
def hysteresis_3d_threshold(image_3d, low_threshold=None, high_threshold=None, low_ratio=0.3, high_ratio=0.8):
    """
    Apply Hysteresis thresholding to a 3D image.
    
    Parameters:
    -----------
    image_3d : numpy.ndarray
        3D image array to be thresholded
    low_threshold : float, optional
        Low threshold value. If None, it will be calculated as low_ratio * otsu_threshold
    high_threshold : float, optional
        High threshold value. If None, it will be calculated as high_ratio * otsu_threshold
    low_ratio : float, optional
        Ratio to calculate low threshold if not provided (multiplied by Otsu's threshold)
    high_ratio : float, optional
        Ratio to calculate high threshold if not provided (multiplied by Otsu's threshold)
    
    Returns:
    --------
    binary_image : numpy.ndarray
        Binary image after applying Hysteresis threshold
    thresholds : tuple
        (low_threshold, high_threshold) values used for thresholding
    """
    # Calculate Otsu's threshold as a reference if thresholds are not provided
    otsu_threshold = filters.threshold_otsu(image_3d)
    
    # Set default thresholds if not provided
    if low_threshold is None:
        low_threshold = low_ratio * otsu_threshold
    
    if high_threshold is None:
        high_threshold = high_ratio * otsu_threshold
    
    # Apply hysteresis thresholding
    binary_image = filters.apply_hysteresis_threshold(image_3d, low_threshold, high_threshold)
    
    return binary_image, (low_threshold, high_threshold)

# filtering
def Gaussian_filter_3d(image_3d, sigma=2.5, voxel_size=(1.0, 1.0, 1.0)):
    """
    Apply Gaussian filter to a 3D image.
    
    Parameters:
    -----------
    image_3d : numpy.ndarray
        3D image array to be filtered
    sigma (in unit of microns) : float or sequence of floats
        Standard deviation for Gaussian kernel. If a single float is provided,
        it will be used for all axes. If a sequence is provided, it should have
        the same length as the number of dimensions in image_3d.
    voxel_size (in units of microns per voxel): sequence of floats, optional
        Voxel size in each dimension (x, y, z). Used to scale the sigma values.
    
    Returns:
    --------
    filtered_image : numpy.ndarray
        Filtered 3D image (floating point values between 0 and 1)
    """
    # Convert input to float if it's boolean
    if image_3d.dtype == bool:
        image_3d = image_3d.astype(float)
    
    # Convert sigma to voxel units by dividing by voxel size
    if isinstance(sigma, (int, float)):
        # Single sigma value for all dimensions
        voxel_sigma = sigma / np.array(voxel_size)
        print(f"Using single sigma value: {voxel_sigma}")
    else:
        # Sequence of sigma values for each dimension
        voxel_sigma = np.array(sigma) / np.array(voxel_size)
        print(f"Using voxel sigma values: {voxel_sigma}")
    
    # Apply Gaussian filter with different sigma for each dimension
    return ndimage.gaussian_filter(image_3d, sigma=voxel_sigma)

# visualization

def visualize_segmentation_z_slice(original_image, thresholded_image, z_slice, figsize=(12, 6), fontsize=6):
    """
    Visualize segmentation results by plotting a z-slice from both the original image and thresholded image.
    If z_slice is None, show max projection on x, y, z axes separately.
    
    Parameters:
    -----------
    original_image : numpy.ndarray
        Original 3D image
    thresholded_image : numpy.ndarray
        Binary thresholded 3D image
    z_slice : int or None
        Z-slice number to display, or None for max projections
    figsize : tuple, optional
        Figure size (width, height) in inches
    fontsize : int, optional
        Font size for titles
        
    Returns:
    --------
    fig : matplotlib.figure.Figure
        The figure object containing the visualization
    """
    import matplotlib.pyplot as plt

    if z_slice is None:
        # Show max projections along each axis
        projections = [
            ('Max Projection (X)', 0),
            ('Max Projection (Y)', 1),
            ('Max Projection (Z)', 2)
        ]
        fig, axes = plt.subplots(2, 3, figsize=(figsize[0], figsize[1]*1.2))
        for i, (title, axis) in enumerate(projections):
            # Original max projection
            orig_proj = np.max(original_image, axis=axis)
            axes[0, i].imshow(orig_proj, cmap='gray')
            axes[0, i].set_title(f'Original {title}', fontsize=fontsize)
            axes[0, i].axis('off')
            # Thresholded max projection
            thresh_proj = np.max(thresholded_image, axis=axis)
            axes[1, i].imshow(thresh_proj, cmap='hot')
            axes[1, i].set_title(f'Thresholded {title}', fontsize=fontsize)
            axes[1, i].axis('off')
        plt.tight_layout()
        return fig

    # Check if z_slice is valid
    if z_slice < 0 or z_slice >= original_image.shape[-1]:
        raise ValueError(f"Z-slice {z_slice} is out of range (0-{original_image.shape[-1]-1})")
    
    # Extract the specified z-slice
    original_slice = original_image[:,:,z_slice] # Assuming the last dimension is z
    thresholded_slice = thresholded_image[:,:,z_slice]
    
    # Create figure
    fig, axes = plt.subplots(1, 3, figsize=figsize)
    
    # Plot original image
    axes[0].imshow(original_slice, cmap='gray')
    axes[0].set_title(f'Original Image (Z={z_slice})', fontsize=fontsize)
    axes[0].axis('off')
    
    # Plot thresholded image
    axes[1].imshow(thresholded_slice, cmap='hot')
    axes[1].set_title(f'Thresholded Image (Z={z_slice})', fontsize=fontsize)
    axes[1].axis('off')
    
    # Plot overlay
    overlay = np.zeros((*original_slice.shape, 3))
    original_normalized = original_slice / (original_slice.max() + 1e-8)
    overlay[..., 0] = original_normalized
    overlay[..., 1] = original_normalized
    overlay[..., 2] = original_normalized
    overlay[thresholded_slice > 0, 0] = 1.0  # Red channel
    overlay[thresholded_slice > 0, 1] = 0.0  # Green channel
    overlay[thresholded_slice > 0, 2] = 0.0  # Blue channel
    
    axes[2].imshow(overlay)
    axes[2].set_title(f'Overlay (Z={z_slice})', fontsize=fontsize)
    axes[2].axis('off')
    
    plt.tight_layout()
    return fig

def visualize_density_map(original_image, density_map, z_slice=None, figsize=(12, 6), fontsize=6):
    """
    Visualize density map results by plotting slices or projections.
    If z_slice is None, show max projection on x, y, z axes separately.
    
    Parameters:
    -----------
    original_image : numpy.ndarray
        Original 3D image
    density_map : numpy.ndarray
        Floating-point density map (Gaussian filtered binary image)
    z_slice : int or None
        Z-slice number to display, or None for max projections
    figsize : tuple, optional
        Figure size (width, height) in inches
    fontsize : int, optional
        Font size for titles
        
    Returns:
    --------
    fig : matplotlib.figure.Figure
        The figure object containing the visualization
    """
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap

    # Create a custom colormap for density (white to red)
    density_cmap = LinearSegmentedColormap.from_list('density', ['white', 'red'])
    
    if z_slice is None:
        # Show max projections along each axis
        projections = [
            ('Max Projection (X)', 0),
            ('Max Projection (Y)', 1),
            ('Max Projection (Z)', 2)
        ]
        fig, axes = plt.subplots(2, 3, figsize=(figsize[0], figsize[1]*1.2))
        for i, (title, axis) in enumerate(projections):
            # Original max projection
            orig_proj = np.max(original_image, axis=axis)
            axes[0, i].imshow(orig_proj, cmap='gray')
            axes[0, i].set_title(f'Original {title}', fontsize=fontsize)
            axes[0, i].axis('off')
            
            # Density map max projection
            density_proj = np.max(density_map, axis=axis)
            axes[1, i].imshow(density_proj, cmap=density_cmap)
            axes[1, i].set_title(f'Density {title}', fontsize=fontsize)
            axes[1, i].axis('off')
        plt.tight_layout()
        return fig

    # For single slice visualization
    # Check if z_slice is valid
    if z_slice < 0 or z_slice >= original_image.shape[-1]:
        raise ValueError(f"Z-slice {z_slice} is out of range (0-{original_image.shape[-1]-1})")
    
    # Extract the specified z-slice
    original_slice = original_image[:,:,z_slice]
    density_slice = density_map[:,:,z_slice]
    
    # Create figure
    fig, axes = plt.subplots(1, 3, figsize=figsize)
    
    # Plot original image
    axes[0].imshow(original_slice, cmap='gray')
    axes[0].set_title(f'Original Image (Z={z_slice})', fontsize=fontsize)
    axes[0].axis('off')
    
    # Plot density map
    im = axes[1].imshow(density_slice, cmap=density_cmap)
    axes[1].set_title(f'Density Map (Z={z_slice})', fontsize=fontsize)
    axes[1].axis('off')
    plt.colorbar(im, ax=axes[1], shrink=0.8)
    
    # Plot overlay
    overlay = np.zeros((*original_slice.shape, 3))
    original_normalized = original_slice / (original_slice.max() + 1e-8)
    overlay[..., 0] = original_normalized
    overlay[..., 1] = original_normalized
    overlay[..., 2] = original_normalized
    
    # Add red color based on density (more transparent for lower values)
    for i in range(density_slice.shape[0]):
        for j in range(density_slice.shape[1]):
            if density_slice[i, j] > 0:
                intensity = density_slice[i, j] / density_map.max()
                overlay[i, j, 0] = max(original_normalized[i, j], intensity)  # Red
                overlay[i, j, 1] = original_normalized[i, j] * (1-intensity)  # Green
                overlay[i, j, 2] = original_normalized[i, j] * (1-intensity)  # Blue
    
    axes[2].imshow(overlay)
    axes[2].set_title(f'Overlay (Z={z_slice})', fontsize=fontsize)
    axes[2].axis('off')
    
    plt.tight_layout()
    return fig

# script takes two arguments: folder_path and suffix
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_density_map.py <folder_path> <suffix>")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    suffix = sys.argv[2] if len(sys.argv) > 2 else '.nrrd'
    
    # Import tqdm for progress bars
    from tqdm import tqdm
    
    # Get all nrrd files in the folder
    nrrd_files = [f for f in os.listdir(folder_path) if f.endswith('.nrrd')]
    print(f"Found {len(nrrd_files)} nrrd files in the folder.")
    if not nrrd_files:
        print("No nrrd files found in the folder.")
        sys.exit(1)
    
    file_paths = [os.path.join(folder_path, nrrd_file) for nrrd_file in nrrd_files]
    # threshold images
    for file_path in tqdm(file_paths, desc="Processing files", unit="file"):
        print(f"\nProcessing file: {file_path}")
        data, header = read_nrrd(file_path)
        
        # Apply hysteresis thresholding
        binary_image, thresholds = hysteresis_3d_threshold(data)
        print(f"Applied hysteresis thresholding with thresholds: {thresholds}")
        # visualize segmentation
        z_slice = None  # Set to None to visualize max projections
        fig = visualize_segmentation_z_slice(data, binary_image, z_slice)
        plt.suptitle(f"Segmentation Visualization for {os.path.basename(file_path)}", 
                     x=0.5, y=1.05, fontsize=12)
        # save the figure
        output_fig_path = file_path.replace(suffix, '_segmentation.png')
        fig.savefig(output_fig_path, dpi=300)
        plt.close(fig)  
        print(f"Saved segmentation visualization to: {output_fig_path}")
        # save the binary image as npy file
        binary_output_path = file_path.replace(suffix, '_binary.npy')
        np.save(binary_output_path, binary_image.astype(np.float32))
        print(f"Saved binary image to: {binary_output_path}")
        
        # Apply Gaussian filter
        with tqdm(total=1, desc="Applying Gaussian filter", leave=False) as pbar:
            filtered_image = Gaussian_filter_3d(binary_image, sigma=2.5, voxel_size=(0.2, 0.2, 0.5))
            pbar.update(1)
        print("Applied Gaussian filter.")
        # visualize density map
        fig_density = visualize_density_map(data, filtered_image, z_slice)
        plt.suptitle(f"Density Map Visualization for {os.path.basename(file_path)}", 
                     x=0.5, y=1.05, fontsize=12)
        # save the figure
        output_density_fig_path = file_path.replace(suffix, '_density_map.png')
        fig_density.savefig(output_density_fig_path, dpi=300)
        plt.close(fig_density)
        print(f"Saved density map visualization to: {output_density_fig_path}")
        
        # Save the filtered image
        output_path = file_path.replace(suffix, '_density_map.nrrd')
        nrrd.write(output_path, filtered_image.astype(np.float32), header, compression_level=1)
        print(f"Saved density map to: {output_path}")
