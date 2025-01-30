#!/bin/bash
#SBATCH --gres=gpu:1       # Request GPU "generic resources"
#SBATCH --cpus-per-task=1  # Cores proportional to GPUs: 6 on Cedar, 16 on Graham.
#SBATCH --mem=32000M       # Memory proportional to GPUs: 32000 Cedar, 64000 Graham.
#SBATCH --time=0-32:00
#SBATCH --output=finetune_qwen-7_%N-%j.out
#SBATCH --array=1
#SBATCH --mail-user=jonathan.caron-roberge.1@ulaval.ca
#SBATCH --mail-type=ALL

module load python/3.12.4 scipy-stack gcc arrow/17.0.0 cuda cudnn

source /home/pvharmo/projects/def-masai45/pvharmo/venv/bin/activate
mkdir -p /home/pvharmo/scratch/Qwen2.5-Coder-7B-Instruct/checkpoints

cd /home/pvharmo/llm-gha-eval/finetuning
python finetune.py --model Qwen2.5-Coder-7B-Instruct --epochs $SLURM_ARRAY_TASK_ID
