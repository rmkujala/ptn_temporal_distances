#! /bin/bash
#SBATCH -n 1
#SBATCH -t 02:00:00
#SBATCH ---mem-per-cpu=2500M
#SBATCH --array=0-127

#SBATCH
srun python all_to_all_stats.py $SLURM_ARRAY_TASK_ID 128
