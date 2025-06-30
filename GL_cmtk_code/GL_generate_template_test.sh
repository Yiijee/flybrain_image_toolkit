#!/bin/bash

#SBATCH --job-name=CMTK-template-gen  ## Name of the job for the scheduler
#SBATCH --account=jclowney0           ## Your PI's uniqname plus 0,99, or other number
#SBATCH --partition=standard          ## Name of the queue to submit the job to
#SBATCH --nodes=1                     ## Number of nodes you are requesting
#SBATCH --ntasks=1                    ## How many task spaces you want to reserve
#SBATCH --cpus-per-task=16            ## How many cores you want to use per task
#SBATCH --time=06:00:00               ## Maximum length of time you are reserving the resources for
#SBATCH --mem=32g                     ## Memory requested per core
#SBATCH --mail-user=yijiep@umich.edu  ## Send email notifications to the listed email
#SBATCH --mail-type=END               ## When to send email (e.g., END, FAIL)
#SBATCH --output=./%x-%j              ## Send output and error info to the file listed

# Load the necessary modules
module load cmtk/3.3.1

# cmtk groupwise_init -O "Yijie/test/groupwise/initial" --align-centers-of-mass --no-output-average \
#    Yijie/test/YP-25-025_attp2_1_ch3.nrrd Yijie/test/YP-25-025_attp2_1_ch3.nrrd Yijie/test/YP-25-025_attp2_1_ch3.nrrd
# echo "Performing groupwise affine..."
# cmtk groupwise_affine --rmi -o "Yijie/test/groupwise/affine" --match-histograms \
#     --dofs 6 --dofs 9 --zero-sum \
#     --downsample-from 4 --downsample-to 1 --exploration 8 -a 0.5 \
#     --sampling-density 0.1 --force-background 0 \
#     Yijie/test/rigid_YP-25-025_attp2_1_ch3.nrrd Yijie/test/flipped_rigid_YP-25-025_attp2_1_ch3.nrrd Yijie/test/rigid_YP-25-025_attp2_2_ch3.nrrd Yijie/test/flipped_rigid_YP-25-025_attp2_2_ch3.nrrd
    #"Yijie/test/groupwise/initial/groupwise.xforms.gz"
echo "Performing groupwise warp..."
# cmtk groupwise_warp --congeal -O "Yijie/test/groupwise/warp" --match-histograms \
#     --zero-sum-no-affine --downsample-from 8 --downsample-to 1 --exploration 6.4 --accuracy 0.4 \
#     --force-background 0 Yijie/test/groupwise/affine/groupwise.xforms
# this work
#cmtk groupwise_warp --congeal -O Yijie/test/groupwise/warp -v --match-histograms --grid-spacing 100 --grid-spacing-fit --refine-grid 2 --zero-sum-no-affine --downsample-from 8 --downsample-to 4 --exploration 6 --accuracy 0.4 -z Yijie/test/groupwise/affine/groupwise.xforms
cmtk groupwise_warp --congeal -O Yijie/test/groupwise/warp -v --match-histograms --grid-spacing 80 --grid-spacing-fit --refine-grid 2 --zero-sum-no-affine --downsample-from 6 --downsample-to 2 --exploration 6 --accuracy 0.4 -z Yijie/test/groupwise/affine/groupwise.xforms
