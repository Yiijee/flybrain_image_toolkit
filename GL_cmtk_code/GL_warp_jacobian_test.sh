#!/bin/bash

#SBATCH --job-name=CMTK-jacobian  ## Name of the job for the scheduler
#SBATCH --account=jclowney0           ## Your PI's uniqname plus 0,99, or other number
#SBATCH --partition=standard          ## Name of the queue to submit the job to
#SBATCH --nodes=1                     ## Number of nodes you are requesting
#SBATCH --ntasks=1                    ## How many task spaces you want to reserve
#SBATCH --cpus-per-task=16            ## How many cores you want to use per task
#SBATCH --time=02:00:00               ## Maximum length of time you are reserving the resources for
#SBATCH --mem=32g                     ## Memory requested per core
#SBATCH --mail-user=yijiep@umich.edu  ## Send email notifications to the listed email
#SBATCH --mail-type=END               ## When to send email (e.g., END, FAIL)
#SBATCH --output=./%x-%j              ## Send output and error info to the file listed

module load cmtk/3.3.1

path_to_tifs='./Yijie/test' #the folder for tif images need to be registered 
path_to_template='./templates/16bit_OK107_template_female.nrrd' # template
image_name='YP-25-002_HU_1_ch3.nrrd' # image name
warp_basename='YP-25-002_HU_1_ch3_warped.nrrd' # warped image name
jacobian_basename='YP-25-002_HU_1_ch3_jacobian.nrrd' # jacobian image name

# cmtk make_initial_affine --principal-axes $path_to_template $path_to_tifs/$image_name $path_to_tifs/initial.xform
# cmtk registration --initial $path_to_tifs/initial.xform --nmi --dofs 6 --dofs 9 --nmi --exploration 16 --accuracy 0.8 --omit-original-data -o $path_to_tifs/affine.xform $path_to_template $path_to_tifs/$image_name
# cmtk warp --nmi --match-histograms --grid-spacing 80 --refine 4 --coarsest 8 --ic-weight 0 --output-intermediate --accuracy 0.4 -o $path_to_tifs/warp.xform $path_to_template $path_to_tifs/$image_name $path_to_tifs/affine.xform
# cmtk reformatx -v --pad-out 0 -o $path_to_tifs/$warp_basename --floating $path_to_tifs/$image_name $path_to_template $path_to_tifs/warp.xform
cmtk reformatx -v -o $path_to_tifs/$jacobian_basename $path_to_template --jacobian --inverse $path_to_tifs/warp.xform