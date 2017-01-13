#! /bin/bash
#SBATCH -n 1
#SBATCH -t 04:00:00
#SBATCH --mem-per-cpu=2500M
#SBATCH --array=39,63   #orig 0-63

#SBATCH
srun python all_to_all_stats.py $SLURM_ARRAY_TASK_ID 64
