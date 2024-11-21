#!/bin/bash
#SBATCH --gres=gpu:1       # Request GPU "generic resources"
#SBATCH --cpus-per-task=1  # Cores proportional to GPUs: 6 on Cedar, 16 on Graham.
#SBATCH --mem=32000M       # Memory proportional to GPUs: 32000 Cedar, 64000 Graham.
#SBATCH --time=0-23:00
#SBATCH --output=%N-%j.out
#SBATCH --mail-user=jonathan.caron-roberge.1@ulaval.ca
#SBATCH --mail-type=ALL

module load python/3.12.4 scipy-stack gcc arrow/17.0.0 cuda cudnn

source /home/pvharmo/llm-gha-eval/venv/bin/activate
mkdir -p /home/pvharmo/scratch/Qwen2.5-Coder-7B-Instruct/checkpoints

cd /home/pvharmo/llm-gha-eval/finetuning
python qwen_finetune.py --model qwen2.5-7b
