#!/usr/bin/env python3
""" Take a thresholded image as input, count the overlapping 
voxels with each HAT images.
Options:
    --whole_neuron
    --cbf
"""

import os
import nrrd
import numpy as np
import pandas as pd
import argparse

def process_single_hemilineage(TF_image_binary, HAT_file_path):
    
    # try to load HAT nrrd file
    if not os.path.exists(HAT_file_path):
        raise FileNotFoundError(f"HAT file not found: {HAT_file_path}")

    HAT_data, HAT_header = nrrd.read(HAT_file_path)
    
    # count total number of positive voxels in HAT
    total_positive_voxels = HAT_data.sum()
    if total_positive_voxels == 0:
        raise ValueError("No positive voxels found in HAT data")

    # count the intersection between TF image and HAT
    overlapping_voxels = (TF_image_binary * HAT_data).sum()

    return overlapping_voxels/total_positive_voxels

def process_cbf(TF_image_binary, HAT_list, HAT_root_path):
    """
    Process CBF images and calculate overlap with HAT images.
    
    Args:
        TF_image_binary (numpy array): Binary thresholded image
        HAT_list (list): List of HAT hemilineages
        HAT_root_path (str): Root path to HAT files
        
    Returns:
        dict: Dictionary with hemilineage names and their overlap ratios
    """
    results = []
    
    for hemilineage in HAT_list:
        HAT_file_path = os.path.join(HAT_root_path, f"{hemilineage}/{hemilineage}_CBF_registered_meshes.nrrd")
        print(f"Processing hemilineage: {hemilineage} with file: {HAT_file_path}")
        try:
            overlap_ratio = process_single_hemilineage(TF_image_binary, HAT_file_path)
            results.append(overlap_ratio)
        except Exception as e:
            print(f"Error processing {hemilineage}: {e}")
    
    return results

def process_whole_neuron(TF_image_binary, HAT_list, HAT_root_path):
    """
    Process whole neuron images and calculate overlap with HAT images.

    Args:
        TF_image_binary (numpy array): Binary thresholded image
        HAT_list (list): List of HAT hemilineages
        HAT_root_path (str): Root path to HAT files

    Returns:
        dict: Dictionary with hemilineage names and their overlap ratios
    """
    results = []

    for hemilineage in HAT_list:
        HAT_file_path = os.path.join(HAT_root_path, f"{hemilineage}/{hemilineage}_registered_meshes.nrrd")
        print(f"Processing hemilineage: {hemilineage} with file: {HAT_file_path}")
        try:
            overlap_ratio = process_single_hemilineage(TF_image_binary, HAT_file_path)
            results.append(overlap_ratio)
            print(f"Overlap ratio for {hemilineage}: {overlap_ratio}")
        except Exception as e:
            print(f"Error processing {hemilineage}: {e}")

    return results

def main():
    """Main function to process hemilineages."""
    parser = argparse.ArgumentParser(description='Process hemilineages with separate status tracking')
    
    parser.add_argument('TF_image', type=str, help='Path to the binary thresholded TF image')
    parser.add_argument('--HAT_root_path', type=str, required=True, 
                        help='Root path to HAT files')
    parser.add_argument('--whole_neuron', action='store_true', 
                        help='Process whole neuron (CBF=False)')
    parser.add_argument('--cbf', action='store_true', 
                        help='Process CBF version (CBF=True)')
    
    args = parser.parse_args()
    
    # Load TF image
    if not os.path.exists(args.TF_image):
        raise FileNotFoundError(f"TF image not found: {args.TF_image}")
    print(f"Loading TF image: {args.TF_image}")
    TF_image_basename = os.path.basename(args.TF_image)
    TF_image_binary, _ = nrrd.read(args.TF_image)
    # make sure TF_image_binary is boolean
    TF_image_binary = TF_image_binary > 0
    
    # load HAT hemilineages names
    HAT_table = pd.read_csv(os.path.join(args.HAT_root_path, 'hemilineage_summary.csv'))
    # List of HAT hemilineages
    HAT_list = HAT_table['ito_lee_hemilineage'].tolist()

    if args.whole_neuron:
        results = process_whole_neuron(TF_image_binary, HAT_list, args.HAT_root_path)
        results_column_name = f"{TF_image_basename}_whole_neuron"
        HAT_table[results_column_name] = results
    if args.cbf:
        results = process_cbf(TF_image_binary, HAT_list, args.HAT_root_path)
        results_column_name = f"{TF_image_basename}_cbf"
        HAT_table[results_column_name] = results

    # Save results to CSV in the same path as the TF image
    output_csv_path = os.path.join(os.path.dirname(args.TF_image), f'hemilineage_mapping_{TF_image_basename}.csv')
    HAT_table.to_csv(output_csv_path, index=False)
    
if __name__ == '__main__':
    main()