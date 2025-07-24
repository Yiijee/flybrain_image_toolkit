#!/bin/bash
                                       ## REQUIRED: #!/bin/bash must be on the 1st line
                                       ## and it must be the only string on the line
#SBATCH --job-name=mapping_TF       ## Name of the job for the scheduler
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
source activate connectome

python HAT_mapping.py TF_images/binary_20250703_ApMimic_adult_female_GFP488_nc82647_female_B4.nrrd --HAT_root_path ../FAFB_lineage --whole_neuron --cbf &
python HAT_mapping.py TF_images/binary_20250703_DsfGAL4UASGFP_adult_female_GFP488_nc82647_male.nrrd --HAT_root_path ../FAFB_lineage --whole_neuron --cbf &
python HAT_mapping.py TF_images/binary_20250703_Fer2Mimic_adult_female_GFP488_nc82647_female_B3.nrrd --HAT_root_path ../FAFB_lineage --whole_neuron --cbf &

python HAT_union.py ../FAFB_lineage