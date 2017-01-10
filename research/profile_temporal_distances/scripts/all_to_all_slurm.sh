#! /bin/bash
#SBATCH -n 1
#SBATCH -t 04:00:00
#SBATCH ---mem-per-cpu=2500
#SBATCH --array=0-1

#SBATCH
srun python all_to_all_stats.py $SLURM_ARRAY_TASK_ID 1000
