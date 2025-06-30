#!/bin/bash
                                       ## REQUIRED: #!/bin/bash must be on the 1st line
                                       ## and it must be the only string on the line
#SBATCH --job-name=Image_process_emma_mean       ## Name of the job for the scheduler
#SBATCH --account=jclowney0            ## Your PI's uniqname plus 0,99, or other number
#SBATCH --partition=standard                ## name of the queue to submit the job to.
                                       ## Choose: standard, largemem, gpu, spgpu, debug
##SBATCH --gpus=1                                   ## if partition=gpu, number of GPUS needed
                                       ## make the directive = #SBATCH, not ##SBATCH 
#SBATCH --nodes=1                      ## number of nodes you are requesting
#SBATCH --ntasks=1                     ## how many task spaces do you want to reserve
#SBATCH --cpus-per-task=32              ## how many cores do you want to use per task
#SBATCH --time=00:30:00                ## Maximum length of time you are reserving the 
                                       ## resources for (bill is based on time used)
#SBATCH --mem=24g                      ## Memory requested per core
#SBATCH --mail-user=yijiep@umich.edu   ## send email notifications to umich email listed
#SBATCH --mail-type=END                ## when to send email (standard values are:
                                       ## NONE,BEGIN,END,FAIL,REQUEUE,ALL.
                                       ## (See documentation for others)
#SBATCH --output=./%x-%j               ## send output and error info to the file listed
                                       ##(optional: different name format than default) 

source activate registration

folder_path_1="../Emma/VPN_control"
folder_path_2="../Emma/VPN_OPN_silent"

# python generate_density_map.py $folder_path_1 ".nrrd"
# python generate_density_map.py $folder_path_2 ".nrrd"
python calculate_voxel_mean.py $folder_path_1 --suffix "_density_map.nrrd" --output "../Emma/results/Emma_control_mean_density_map.nrrd"
python calculate_voxel_mean.py $folder_path_2 --suffix "_density_map.nrrd" --output "../Emma/results/Emma_OPN_silent_mean_density_map.nrrd"
python calculate_voxel_mean.py $folder_path_1 --suffix "_binary.npy" --output "../Emma/results/Emma_control_mean_binary.nrrd"
python calculate_voxel_mean.py $folder_path_2 --suffix "_binary.npy" --output "../Emma/results/Emma_OPN_silent_mean_binary.nrrd"
#python voxel_t-stats.py $folder_path_1 $folder_path_2 --suffix "_density_map.nrrd" --alpha 0.05 --output "../Emma/results/Emma_results"