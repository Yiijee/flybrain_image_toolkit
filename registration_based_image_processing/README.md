# Registration-Based Image Processing

This directory contains Python scripts for processing and analyzing 3D image data, typically after image registration. The scripts are designed to be run from the command line and perform tasks such as calculating voxel-wise statistics, generating density maps, and performing statistical comparisons between groups of images.

## Dependencies

The following Python packages are required to run these scripts:

*   `numpy`
*   `pynrrd`
*   `tqdm`
*   `matplotlib`
*   `scikit-image`
*   `scipy`
*   `statsmodels`

You can install these dependencies using pip:

```bash
pip install numpy pynrrd tqdm matplotlib scikit-image scipy statsmodels
```

## Scripts

### `generate_density_map.py`

This script generates a density map from a 3D image. It applies hysteresis thresholding to create a binary image and then applies a Gaussian filter to create the density map.

**Usage:**

```bash
python generate_density_map.py <folder_path> <suffix>
```

*   `<folder_path>`: Path to the folder containing the input image files.
*   `<suffix>`: Suffix of the image files to process (e.g., `.nrrd`).

### `calculate_voxel_max.py`

This script calculates the voxel-wise maximum across a series of 3D images. It can process both `.nrrd` and `.npy` files.

**Usage:**

```bash
python calculate_voxel_max.py <folder> [--suffix <suffix>] [--output <output_file>] [--output-format <format>]
```

*   `<folder>`: Path to the folder containing the input files.
*   `--suffix`: Suffix of the files to process (default: `_binary.nrrd`).
*   `--output`: Path to the output file.
*   `--output-format`: Output file format (`nrrd` or `npy`, default: `nrrd`).

### `voxel_t-stats.py`

This script performs a voxel-wise independent t-test between two groups of 3D images. It calculates the mean and variance for each group, performs the t-test, and corrects for multiple comparisons using FDR.

**Usage:**

```bash
python voxel_t-stats.py <folder1> <folder2> [--suffix <suffix>] [--alpha <alpha>] [--output <output_prefix>]
```

*   `<folder1>`: Path to the folder containing the images for group 1.
*   `<folder2>`: Path to the folder containing the images for group 2.
*   `--suffix`: Suffix of the files to analyze (default: `_density_map.nrrd`).
*   `--alpha`: Significance level for FDR correction (default: `0.05`).
*   `--output`: Prefix for the output files (default: `voxel_ttest_results`).
