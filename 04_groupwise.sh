#!/bin/bash

# Paths
path_to_images=$1
affine_output_dir="$path_to_images/groupwise_affine_output"
warp_output_dir="$path_to_images/groupwise_warp_output"
template_output="$warp_output_dir/template.nrrd"
output_root="$path_to_images/groupwise"

# Resolution and exploration parameters
exploration="16"  # Example exploration range

mkdir -p $output_root

# Create output directories if they don't exist
if [ ! -d "$affine_output_dir" ]; then
    mkdir "$affine_output_dir"
fi

if [ ! -d "$warp_output_dir" ]; then
    mkdir "$warp_output_dir"
fi

# run initial
cmtk groupwise_init -O "$output_root/initial" -v --align-centers-of-mass "$path_to_images"/*01_rigid.nrrd

# Run groupwise affine registration
cmtk groupwise_affine --rmi -O "$output_root/affine" -v --dofs 9 --downsample-from 4 --downsample-to 1 --exploration 16 --sampling-density 0.1 -a 0.4 "$output_root/initial"/groupwise.xforms
# cmtk groupwise_affine --threads 40 --dofs 6 --dofs 9 --exploration "$exploration" --accuracy 0.8 --output-root "$affine_output_dir" --output "gruopwise.xform" --output-average "average.nrrd" "$path_to_images"/*01_rigid.nrrd

# # Run groupwise warp registration
# $cmtk_path/groupwise_warp --threads 20 --exploration "$exploration" --output-root "$warp_output_dir" --output "gruopwise.xform" --output-average "average.nrrd" "$path_to_images"/*01_rigid.nrrd
cmtk groupwise_warp --congeal -O "$output_root/warp" -v --match-histograms --grid-spacing 80 --grid-spacing-fit --refine-grid 4 --zero-sum-no-affine --downsample-from 8 --downsample-to 2 --exploration 16 --accuracy 0.4 -z "$output_root/affine"/groupwise.xforms
# # Generate average template
# $cmtk_path/average_images -o "$template_output" "$warp_output_dir.gz"
