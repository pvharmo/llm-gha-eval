#!/bin/bash
#SBATCH --gres=gpu:1       # Request GPU "generic resources"
#SBATCH --cpus-per-task=1  # Cores proportional to GPUs: 6 on Cedar, 16 on Graham.
#SBATCH --mem=32000M       # Memory proportional to GPUs: 32000 Cedar, 64000 Graham.
#SBATCH --time=0-16:00
#SBATCH --output=finetune_qwen-1.5_%N-%j.out
#SBATCH --array=1-3

module load python/3.12.4 scipy-stack gcc arrow/17.0.0 cuda cudnn

source /home/pvharmo/llm-gha-eval/venv/bin/activate
mkdir -p /home/pvharmo/scratch/Qwen2.5-Coder-1.5B-Instruct/checkpoints

cd /home/pvharmo/llm-gha-eval/finetuning
python finetune.py --model Qwen2.5-Coder-1.5B-Instruct --nb_examples $((1000 * $SLURM_ARRAY_TASK_ID)) --epochs 1
