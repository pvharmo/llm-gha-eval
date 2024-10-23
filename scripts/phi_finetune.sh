#!/bin/bash
#SBATCH --gres=gpu:2       # Request GPU "generic resources"
#SBATCH --cpus-per-task=1  # Cores proportional to GPUs: 6 on Cedar, 16 on Graham.
#SBATCH --mem=32000M       # Memory proportional to GPUs: 32000 Cedar, 64000 Graham.
#SBATCH --time=0-11:00
#SBATCH --output=%N-%j.out

module load python/3.12.4 scipy-stack gcc arrow/17.0.0 cuda cudnn

source /home/pvharmo/llm-gha-eval/venv/bin/activate
mkdir $SLURM_TMPDIR/data
mkdir -p /home/pvharmo/scratch/Phi-3.5-mini-instruct/checkpoints

cd ../finetuning
accelerate launch /home/pvharmo/llm-gha-eval/finetuning/phi_finetune.py
