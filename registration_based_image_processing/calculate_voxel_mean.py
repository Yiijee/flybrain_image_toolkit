#!/usr/bin/env python3
"""
Calculate voxel-wise mean across all files in a folder and save the result as an NRRD file.
Supports both .nrrd and .npy files.
"""
import os
import sys
import argparse
import numpy as np
import nrrd
from tqdm import tqdm

def read_file(file_path):
    """Read file and return data and header based on file extension."""
    try:
        if file_path.lower().endswith('.npy'):
            data = np.load(file_path)
            header = None  # NPY files don't have headers
            return data, header
        else:  # Assume it's an NRRD file
            data, header = nrrd.read(file_path)
            return data, header
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None, None

def find_files_with_suffix(folder_path, suffix):
    """Find all files in folder with the specified suffix."""
    if not os.path.exists(folder_path):
        raise ValueError(f"Folder not found: {folder_path}")
        
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) 
             if f.endswith(suffix)]
    
    if not files:
        raise ValueError(f"No files with suffix '{suffix}' found in {folder_path}")
        
    return files

def calculate_voxel_mean(file_paths):
    """
    Calculate voxel-wise mean across all files.
    
    Args:
        file_paths (list): List of file paths to process
        
    Returns:
        tuple: (mean_data, header) - The voxel-wise mean data and the header from the first file
    """
    if not file_paths:
        raise ValueError("No files provided for processing")
    
    # Initialize with the first file
    print(f"Reading first file: {file_paths[0]}")
    first_data, header = read_file(file_paths[0])
    
    if first_data is None:
        raise ValueError(f"Failed to read first file: {file_paths[0]}")
    
    # Initialize sum array
    sum_data = first_data.astype(np.float64)  # Use float64 for better precision in accumulation
    file_count = 1
    
    # Process remaining files
    print(f"Calculating voxel-wise mean across {len(file_paths)} files...")
    for file_path in tqdm(file_paths[1:], desc="Processing files", unit="file"):
        data, _ = read_file(file_path)
        if data is not None:
            # Add to running sum
            sum_data += data
            file_count += 1
    
    # Calculate mean
    mean_data = sum_data / file_count
    
    # Convert to float32 for storage efficiency
    mean_data = mean_data.astype(np.float32)
    
    return mean_data, header

def main():
    parser = argparse.ArgumentParser(description="Calculate voxel-wise mean across files in a folder.")
    parser.add_argument("folder", help="Path to the folder containing input files")
    parser.add_argument("--suffix", default="_binary.nrrd", help="Suffix of files to process (e.g., _binary.nrrd or _binary.npy)")
    parser.add_argument("--output", help="Output file path. Default is voxel_mean_<suffix>.nrrd in the input folder")
    parser.add_argument("--output-format", choices=["nrrd", "npy"], default="nrrd", 
                        help="Output file format: nrrd or npy (default: nrrd)")
    
    args = parser.parse_args()
    
    try:
        # Find all matching files
        file_paths = find_files_with_suffix(args.folder, args.suffix)
        print(f"Found {len(file_paths)} files in {args.folder} with suffix '{args.suffix}'")
        
        # Calculate voxel-wise mean
        mean_data, header = calculate_voxel_mean(file_paths)
        
        # Determine output path
        if args.output:
            output_path = args.output
        else:
            # Extract suffix without the dot if present
            clean_suffix = args.suffix
            if clean_suffix.startswith('.'):
                clean_suffix = clean_suffix[1:]
            
            # Set output format extension
            output_ext = f".{args.output_format}"
            output_prefix = args.folder.split(os.sep)[-1]  # Get the last part of the folder path
            output_path = os.path.join(args.folder, f"{output_prefix}_voxel_mean_{clean_suffix}{output_ext}")
        
        # Save result in appropriate format
        if args.output_format == "npy" or output_path.lower().endswith('.npy'):
            print(f"Saving voxel-wise mean to NPY file: {output_path}")
            np.save(output_path, mean_data)
        else:
            print(f"Saving voxel-wise mean to NRRD file: {output_path}")
            if header is None:
                # Create a minimal header if one doesn't exist (for NPY inputs)
                header = {'type': 'float', 'dimension': mean_data.ndim}
            nrrd.write(output_path, mean_data, header)
        
        print("Done!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
