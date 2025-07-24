#!/bin/bash

#SBATCH --job-name=CMTK-template-ChAT  ## Name of the job for the scheduler
#SBATCH --account=jclowney0           ## Your PI's uniqname plus 0,99, or other number
#SBATCH --partition=standard          ## Name of the queue to submit the job to
#SBATCH --nodes=1                     ## Number of nodes you are requesting
#SBATCH --ntasks=1                    ## How many task spaces you want to reserve
#SBATCH --cpus-per-task=16            ## How many cores you want to use per task
#SBATCH --time=18:00:00               ## Maximum length of time you are reserving the resources for
#SBATCH --mem=128g                     ## Memory requested per core
#SBATCH --mail-user=yijiep@umich.edu  ## Send email notifications to the listed email
#SBATCH --mail-type=END               ## When to send email (e.g., END, FAIL)
#SBATCH --output=./%x-%j              ## Send output and error info to the file listed


# Load the necessary modules
module load cmtk/3.3.1
module load fiji

# Define paths
path_to_tifs='./Emma/VPM-MB2_OPN-silencing' #the folder for tif images need to be registered 
input_folder='./Emma/ChAT'  # Folder containing registered images
output_folder='./Emma/template_generation'  # Folder to store intermediate and final results
path_to_macro='./macro' #path to macro folder
reference_channel=3 # reference channel for registration

mkdir -p $output_folder
mkdir -p $input_folder

# get all channel nrrds 


# # find all the tif files in the folder
# find "$path_to_tifs" -maxdepth 1 -type f -name "*.tif" | while read -r file; do
#     # ----------------Preprocess the tif files----------------
#     echo "----------------Preprocessing $file----------------"
#     # create a temp folder to each tif file
#     temp_folder=$(basename "$file" .tif)
#     mkdir -p "$path_to_tifs/$temp_folder"
#     # convert the tif file to nrrd file
#     if [ ! -f "$path_to_tifs/$temp_folder/${temp_folder}_ch1.nrrd" ]; then
#         fiji --headless --console -macro "$path_to_macro/splitChannel.ijm" "$file $path_to_tifs/$temp_folder/"
#     fi
#     # find the nrrd files in the temp folder
#     nrrd_list=$(find "$path_to_tifs/$temp_folder" -maxdepth 1 -type f -name "*.nrrd" ! -name "rigid_*.nrrd")
#     echo $nrrd_list
#     # copy reference channel nrrd to input folder
#     cp "$path_to_tifs/$temp_folder/${temp_folder}_ch3.nrrd" "$input_folder/${temp_folder}_ch3.nrrd"
# done 

# Modify the image list collection section of your script
echo "Looking for NRRD files in: $input_folder"
image_files=()
while IFS= read -r file; do
    if [ -f "$file" ]; then
        image_files+=("$file")
        echo "Found: $file"
    fi
done < <(find "$input_folder" -type f -name "*.nrrd")

echo "Found ${#image_files[@]} image files"

# Verify you have files before proceeding
if [ ${#image_files[@]} -eq 0 ]; then
    echo "Error: No image files found in $input_folder"
    exit 1
fi

# Generate the template using CMTK

# Call groupwise_init with array expansion
cmtk groupwise_init -O "$input_folder/groupwise/initial" --align-centers-of-mass "${image_files[@]}"

echo "Initializing groupwise registration..."
image_list=$(find "$input_folder" -type f -name "*.nrrd")
groupwise_init_dir="$input_folder/groupwise"
mkdir -p "$groupwise_init_dir"

# # cmtk groupwise_init -O "$input_folder/groupwise/initial" --align-centers-of-mass --no-output-average $image_list
# if [ $? -ne 0 ]; then
#     echo "Error: Groupwise initialization failed"
#     exit 1
# fi
echo "Performing initial affine registration..."
cmtk groupwise_affine --rmi -O "$input_folder/groupwise/affine" --match-histograms \
    --dofs 6 --dofs 9 --zero-sum \
    --downsample-from 4 --downsample-to 2 --exploration 4 -a 0.4 \
    --sampling-density 0.2 --force-background 0 \
    "$input_folder/groupwise/initial"/groupwise.xforms


echo "Performing groupwise warp..."
# cmtk groupwise_warp --congeal -O "$input_folder/groupwise/warp" --match-histograms \
#     --zero-sum-no-affine --downsample-from 8 --downsample-to 1 --exploration 6.4 --accuracy 0.8 --sampling-density 0.5 \
#     --output-average warp_template.nrrd --force-background 0 "$input_folder/groupwise/affine"/groupwise.xforms
cmtk groupwise_warp --congeal -O "$input_folder/groupwise/warp" -v --match-histograms --grid-spacing 80 --grid-spacing-fit --refine-grid 2 --zero-sum-no-affine --downsample-from 6 --downsample-to 1 --exploration 6 --accuracy 0.3 -z "$input_folder/groupwise/affine"/groupwise.xforms

if [ $? -ne 0 ]; then
    echo "Error: Groupwise warp failed"
    exit 1
fi

echo "Template successfully generated at $input_folder/groupwise/warp/average.nii.gz"



