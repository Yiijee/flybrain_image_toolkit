# HAT FAFB 

In this project, I will follow the [connectome annotation paper](https://www.nature.com/articles/s41586-024-07686-5#Sec14) to create a Hemilineage-Associate-Tract (HAT) & Soma map in the JRC template. 

[Supplementary Data 3](https://static-content.springer.com/esm/art%3A10.1038%2Fs41586-024-07686-5/MediaObjects/41586_2024_7686_MOESM7_ESM.csv) in this paper contains all hemileange information. The table has been downloaded as "hemileanageMeta.csv". 

## Project Overview

- Download neuron meshes
- Transfer meshes into brain template
- *optional* keep only Soma and main neurite to highlight the tracts
    Currently using a configurable downsampling factor for all lineages. Default value of 10 provides balanced resolution and processing speed.
- Voxelize meshes

## HAT_FAFB Module Documentation

The `HAT_FAFB.py` module contains the main `hat_fafb` class for processing hemilineage data from the FAFB (Full Adult Fly Brain) dataset.

### Class: hat_fafb

A comprehensive class for downloading, processing, and registering neuronal hemilineage data from the FlyWire FAFB dataset.

#### Constructor

```python
hat_fafb(hemileage: str, root_path: str = None)
```

**Parameters:**
- `hemileage` (str): Name of the hemilineage to process (e.g., "FLAa2", "LHp3")
- `root_path` (str, optional): Root directory path. Defaults to current working directory

**Functionality:**
- Creates a dedicated folder structure for the hemilineage
- Downloads metadata from the FlyWire database
- Manages file organization and caching

#### Key Methods

##### `register_meshes(CBF=False, downsampling_factor=10, update=False, template="JRC2018U", source="FLYWIRE")`

Registers neuron meshes to a specified brain template.

**Parameters:**
- `CBF` (bool): Whether to use Cell Body Fiber processing
- `downsampling_factor` (int): Downsampling factor for mesh processing (default: 10)
- `update` (bool): Force update of existing files
- `template` (str): Target brain template (default: "JRC2018U")
- `source` (str): Source coordinate system (default: "FLYWIRE")

**Returns:**
- Tuple of (file_path, registered_meshes)

##### `get_registered_meshes(file_path, downsampling_factor=10, update=False, template="JRC2018U", source="FLYWIRE")`

Lower-level method for mesh registration with custom file paths.

#### File Organization

The class creates the following directory structure:

```
root_path/hemileage/
├── hemileage_meta.csv                    # Metadata from FlyWire
├── hemileage_meshes.pkl                  # Raw neuron meshes
├── hemileage_CBF_meshes.pkl             # Cell Body Fiber processed meshes
├── hemileage_registered_meshes.pkl       # Registered meshes
├── hemileage_CBF_registered_meshes.pkl   # CBF + registered meshes
├── hemileage_registered_meshes.nrrd      # Voxelized meshes
├── hemileage_CBF_registered_meshes.nrrd  # Voxelized CBF meshes
├── hemileage_registered_meshes.png       # Z-projection visualization
├── hemileage_CBF_registered_meshes.png   # CBF Z-projection visualization
└── hemileage_attributes.json             # Class attributes and metadata
```

#### Processing Parameters

##### Downsampling Factor
The `downsampling_factor` parameter controls mesh resolution and processing speed:
  
- **Default**: 10 (balanced resolution and processing speed)

#### Dependencies

- `flybrains`: Brain template handling
- `navis`: Neuroanatomy visualization and analysis
- `fafbseg.flywire`: FlyWire dataset access
- `pandas`: Data manipulation
- `numpy`: Numerical operations
- `matplotlib`: Visualization

#### Usage Example

```python
from HAT_FAFB import hat_fafb

# Initialize for FLAa2 hemilineage
hemi = hat_fafb("FLAa2")

# Register meshes with CBF processing and custom downsampling
file_path, meshes = hemi.register_meshes(CBF=True, downsampling_factor=5)

# Register to different template with higher downsampling
file_path, meshes = hemi.register_meshes(template="FCWB", CBF=False, downsampling_factor=20)
```

#### Notes

- Requires FlyWire authentication token in `~/.cloudvolume/secrets/cave-secret.json`
- Files are cached locally to avoid redundant downloads
- Supports multiple brain templates through the navis-flybrains package, need to download templates following their guidance first
- Generates both 3D mesh data and 2D visualization outputs
- The downsampling factor affects both processing time and output quality - adjust based on your needs

