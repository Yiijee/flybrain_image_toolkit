# Hemilineage Processing Scripts V2 - Separate Status Tracking

This directory contains Python scripts for batch processing of hemilineages from the FAFB dataset using the HAT_FAFB module, with separate status tracking for whole neuron and CBF processing.

## Status System

The new system tracks processing status separately for two types:
- **Whole Neuron** (`status_whole_neuron`): Processing with CBF=False
- **CBF** (`status_cbf`): Processing with CBF=True (Cell Body Fiber)

### Status Codes
- **0**: Not started
- **1**: Completed  
- **-1**: Error

## Scripts Overview

### 1. `process_batch_v2.py` - Batch Processing with Separate Status
Process all hemilineages in a specific batch with separate tracking for whole neuron and CBF processing.

**Usage:**
```bash
python process_batch_v2.py <batch_number> [--whole_neuron] [--cbf] [options]
```

**Examples:**
```bash
# Process batch 0 - whole neuron only
python process_batch_v2.py 0 --whole_neuron

# Process batch 0 - CBF only
python process_batch_v2.py 0 --cbf 

# Process batch 0 - both whole neuron and CBF
python process_batch_v2.py 0 --whole_neuron --cbf

# Process batch 0 - both whole neuron and CBF without downsampling
python process_batch_v2.py 0 --whole_neuron --cbf --downsampling_factor 0

# Process batch 1 with different template
python process_batch_v2.py 1 --whole_neuron --cbf --template FCWB
```

**Required Options:**
- `--whole_neuron`: Process whole neuron (CBF=False)
- `--cbf`: Process CBF version (CBF=True)
- Must specify at least one of the above

**Other Options:**
- `--csv`: Path to hemileage summary CSV file (default: hemileage_summary.csv)
- `--downsampling_factor`: Downsampling factor for mesh processing (default: 10)
- `--template`: Target brain template (default: JRC2018U)
- `--source`: Source coordinate system (default: FLYWIRE)
- `--update`: Force update of existing files
- `--no_skip_completed`: Process even completed hemilineages

### 2. `process_single_v2.py` - Single Hemilineage Processing
Process a single hemilineage by name with separate status tracking.

**Usage:**
```bash
python process_single_v2.py <hemilineage_name> [--whole_neuron] [--cbf] [options]
```

**Examples:**
```bash
# Process FLAa2 - whole neuron only
python process_single_v2.py FLAa2 --whole_neuron

# Process LHp3 - both whole neuron and CBF
python process_single_v2.py LHp3 --whole_neuron --cbf

# Process batch 0 - both whole neuron and CBF without downsampling
python process_single_v2.py LHp3 --whole_neuron --cbf --downsampling_factor 0

```

### 3. `check_status_v2.py` - Status Monitoring with Separate Tracking
Check the processing status of hemilineages with detailed breakdown by processing type.

**Usage:**
```bash
python check_status_v2.py [options]
```

**Examples:**
```bash
# Show overall summary and all details
python check_status_v2.py

# Show only overall summary
python check_status_v2.py --summary

# Show details for batch 0
python check_status_v2.py --batch 0

# Show only processing errors
python check_status_v2.py --errors

# Show progress comparison between whole neuron and CBF
python check_status_v2.py --comparison
```

### 4. `reset_status_v2.py` - Status Reset Utility with Separate Tracking
Reset the status of hemilineages in the summary file for each processing type separately.

**Usage:**
```bash
python reset_status_v2.py [options]
```

**Examples:**
```bash
# Reset all whole neuron statuses to "not started"
python reset_status_v2.py --all_wn_to 0

# Reset all CBF statuses to "not started"
python reset_status_v2.py --all_cbf_to 0

# Reset batch 0 - both types to "not started"
python reset_status_v2.py --batch 0 --wn_to 0 --cbf_to 0

# Reset specific hemilineage - whole neuron only
python reset_status_v2.py --hemilineage FLAa2 --wn_to 0

# Reset all errors to "not started"
python reset_status_v2.py --errors_to 0

# Dry run (show what would be changed)
python reset_status_v2.py --all_wn_to 0 --dry_run
```

## CSV File Structure

The `hemileage_summary.csv` file should contain these columns:
```csv
ito_lee_hemilineage,ito_lee_lineage,batches,status_whole_neuron,status_cbf
FLAa2,FLAa2,1,0,0
LHp3,LHp3,1,1,-1
...
```

## File Organization

When processing hemilineages, the scripts create files with this naming convention:
- Whole neuron processing: `hemileage_registered_meshes.*`
- CBF processing: `hemileage_CBF_registered_meshes.*`

Directory structure per hemilineage:
```
root_path/hemileage/
├── hemileage_meta.csv                      # Metadata from FlyWire
├── hemileage_meshes.pkl                    # Raw neuron meshes
├── hemileage_CBF_meshes.pkl               # Cell Body Fiber processed meshes
├── hemileage_registered_meshes.pkl         # Whole neuron registered meshes
├── hemileage_CBF_registered_meshes.pkl     # CBF registered meshes
├── hemileage_registered_meshes.nrrd        # Whole neuron voxelized
├── hemileage_CBF_registered_meshes.nrrd    # CBF voxelized
├── hemileage_registered_meshes.png         # Whole neuron Z-projection
├── hemileage_CBF_registered_meshes.png     # CBF Z-projection
└── hemileage_attributes.json               # Class attributes and metadata
```

## Processing Parameters

### Downsampling Factor
The `--downsampling_factor` parameter controls mesh resolution:
- **Higher values** (e.g., 20): More aggressive downsampling, smaller file sizes, faster processing
- **Lower values** (e.g., 5): Less downsampling, higher resolution, larger file sizes
- **Default**: 10 (balanced resolution and processing speed)

Examples:
```bash
# High resolution (slower, larger files)
python process_batch_v2.py 0 --whole_neuron --downsampling_factor 5

# Low resolution (faster, smaller files)
python process_batch_v2.py 0 --whole_neuron --downsampling_factor 20
```

## Logging

All scripts create log files:
- `hemilineage_processing.log`: Processing logs with timestamps
- Logs include separate tracking for whole neuron vs CBF processing success/failure

## Error Handling

- If whole neuron processing fails: `status_whole_neuron` = -1
- If CBF processing fails: `status_cbf` = -1
- Each processing type is independent - one can succeed while the other fails
- Processing can be resumed for specific types only

## Workflow Examples

### 1. Process whole neurons first, then CBF

```bash
# Step 1: Process all whole neurons in batch 0
python process_batch_v2.py 0 --whole_neuron --downsampling_factor 10

# Step 2: Check progress
python check_status_v2.py --batch 0

# Step 3: Process CBF for completed whole neurons
python process_batch_v2.py 0 --cbf --downsampling_factor 10

# Step 4: Check final status
python check_status_v2.py --comparison
```

### 2. Process both types simultaneously

```bash
# Process both whole neuron and CBF for batch 1
python process_batch_v2.py 1 --whole_neuron --cbf --downsampling_factor 15

# Monitor progress
python check_status_v2.py --batch 1
```

### 3. Handle errors and retry

```bash
# Check for errors
python check_status_v2.py --errors

# Reset errors to not started
python reset_status_v2.py --errors_to 0

# Retry failed processing
python process_batch_v2.py 0 --whole_neuron --cbf --downsampling_factor 10
```

### 4. Parallel processing by batch and type

```bash
# Terminal 1: Batch 0 whole neurons
python process_batch_v2.py 0 --whole_neuron --downsampling_factor 10

# Terminal 2: Batch 1 whole neurons  
python process_batch_v2.py 1 --whole_neuron --downsampling_factor 10

# Terminal 3: Batch 0 CBF (after whole neurons complete)
python process_batch_v2.py 0 --cbf --downsampling_factor 10

# Terminal 4: Batch 1 CBF (after whole neurons complete)
python process_batch_v2.py 1 --cbf --downsampling_factor 10
```

## Migration from V1 Scripts

If you have an existing CSV with a single `status` column, you'll need to:

1. Rename `status` to `status_whole_neuron`
2. Add `status_cbf` column with initial value 0
3. Update your workflow to use the v2 scripts
4. Replace `--cbf_threshold` with `--downsampling_factor` in your commands

## Dependencies

Same as V1 scripts:
```bash
pip install pandas numpy matplotlib flybrains navis fafbseg
```

Plus ensure FlyWire authentication is configured.
