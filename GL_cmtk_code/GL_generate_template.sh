#!/bin/bash

#SBATCH --job-name=CMTK-template-gen  ## Name of the job for the scheduler
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
input_folder='./Yijie/KC_manipulation/rigid_attp2_ch3'  # Folder containing registered images
output_folder='./Yijie/template_generation'  # Folder to store intermediate and final results
template_output_path='./Yijie/MB_template/MB_template.nii.gz'  # Path to save the generated template
path_to_macro='./macro' #path to macro folder

# mkdir -p "$output_folder"
# mkdir -p "$(dirname "$template_output_path")"

# find "$input_folder" -maxdepth 1 -type f -name "rigid*.nrrd" | while read -r file; do
#     # ----------------Preprocess the tif files----------------
#     # create a temp folder to each tif file
#     # temp_folder=$(basename "$file" .tif)
#     # mkdir -p "$path_to_tifs/$temp_folder"
#     # convert the tif file to nrrd file
#     if [ ! -f "$input_folder/flipped_$file" ]; then
#         echo "----------------Flipping $file----------------"
#         fiji --headless --console -macro "$path_to_macro/flipImage.ijm" "$file $input_folder/"
#     fi
# done

# # # Find files matching the pattern
# # find "$input_folder" -type f -name "rigid_*_ch3.nrrd" | while read -r file; do
# #     echo "Processing $file"

# #     # Create a symmetrical copy by flipping along the x-axis
# #     flipped_file="$output_folder/$(basename "$file" .nrrd)_flipped.nrrd"
# #     if [ ! -f "$flipped_file" ]; then
# #         echo "Creating flipped copy for $file"
# #         cmtk imagemath --in "$file" --out "$flipped_file" --flip-x
# #         if [ $? -ne 0 ]; then
# #             echo "Error: Failed to create flipped copy for $file"
# #             exit 1
# #         fi
# #     fi
# # done

# # Generate the template using CMTK

# # Modify the image list collection section of your script
# echo "Looking for NRRD files in: $input_folder"
# image_files=()
# while IFS= read -r file; do
#     if [ -f "$file" ]; then
#         image_files+=("$file")
#         echo "Found: $file"
#     fi
# done < <(find "$input_folder" -type f -name "*.nrrd")

# echo "Found ${#image_files[@]} image files"

# # Verify you have files before proceeding
# if [ ${#image_files[@]} -eq 0 ]; then
#     echo "Error: No image files found in $input_folder"
#     exit 1
# fi

# # Call groupwise_init with array expansion
# cmtk groupwise_init -O "$input_folder/groupwise/initial" --align-centers-of-mass "${image_files[@]}"

# echo "Initializing groupwise registration..."
# image_list=$(find "$input_folder" -type f -name "*.nrrd")
# groupwise_init_dir="$input_folder/groupwise"
# mkdir -p "$groupwise_init_dir"

# # cmtk groupwise_init -O "$input_folder/groupwise/initial" --align-centers-of-mass --no-output-average $image_list
# if [ $? -ne 0 ]; then
#     echo "Error: Groupwise initialization failed"
#     exit 1
# fi
# echo "Performing initial affine registration..."
# cmtk groupwise_affine --rmi -O "$input_folder/groupwise/affine" --match-histograms \
#     --dofs 6 --dofs 9 --zero-sum \
#     --downsample-from 4 --downsample-to 2 --exploration 4 -a 0.8 \
#     --sampling-density 0.1 --force-background 0 \
#     "$input_folder/groupwise/initial"/groupwise.xforms


echo "Performing groupwise warp..."
# cmtk groupwise_warp --congeal -O "$input_folder/groupwise/warp" --match-histograms \
#     --zero-sum-no-affine --downsample-from 8 --downsample-to 1 --exploration 6.4 --accuracy 0.8 --sampling-density 0.5 \
#     --output-average warp_template.nrrd --force-background 0 "$input_folder/groupwise/affine"/groupwise.xforms
cmtk groupwise_warp --congeal -O "$input_folder/groupwise/warp" -v --match-histograms --grid-spacing 80 --grid-spacing-fit --refine-grid 2 --zero-sum-no-affine --downsample-from 6 --downsample-to 2 --exploration 6 --accuracy 0.4 -z "$input_folder/groupwise/affine"/groupwise.xforms

if [ $? -ne 0 ]; then
    echo "Error: Groupwise warp failed"
    exit 1
fi

# copy the generated template to the specified output path if exists
# if [ -f "$input_folder/groupwise/warp/average.nii.gz"]; then
#     cp "$input_folder/groupwise/warp/average.nii.gz" "$template_output_path"
# else
#     echo "Error: Template file not found"
#     exit 1
# fi

echo "Template successfully generated at $input_folder/groupwise/warp/average.nii.gz"
