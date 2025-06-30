# Fly Brain Registration and Analysis

This repository contains scripts for registering fly brain images to a common template and performing statistical analysis on the registered images.

## CMTK Registration

The registration process uses the Computational Morphometry Toolkit (CMTK) to align individual brain images to a standard template. The scripts are designed to be run on a high-performance computing cluster and handle both rigid and non-rigid (warp) transformations.

### Scripts

*   `GL_rigid_batch.sh`: Performs rigid registration of a batch of images. This script aligns the images to the template using a 6-parameter (rigid) transformation.
*   `GL_warp_batch.sh`: Performs non-rigid (warp) registration of a batch of images. This script uses a more flexible transformation to account for local deformations.
*   `04_groupwise.sh`: A script for groupwise registration, which creates an average template from a group of images.

### Usage

The registration scripts are typically run as batch jobs on a cluster. The scripts are configured with parameters such as the path to the images, the template, and the output directory.

## Voxel-wise T-Tests

The `voxel_t-stats.py` script is used to perform voxel-wise t-tests between two groups of registered images. This is useful for identifying brain regions that show statistically significant differences between experimental groups.

### Features

*   **Memory-efficient:** Uses Welford's online algorithm to calculate mean and variance, which avoids loading all images into memory at once.
*   **Multiple comparison correction:**  Performs False Discovery Rate (FDR) correction to account for the large number of statistical tests.
*   **Visualization:** Generates maximum intensity projections of the t-statistics and significant voxels.

### Usage

```bash
python voxel_t-stats.py <folder1> <folder2> --suffix <file_suffix>
```

*   `<folder1>`: Path to the directory containing the images for the first group.
*   `<folder2>`: Path to the directory containing the images for the second group.
*   `<file_suffix>`: The suffix of the image files to be analyzed (e.g., `_density_map.nrrd`).
