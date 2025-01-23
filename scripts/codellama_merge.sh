#!/bin/bash
#SBATCH --gres=gpu:1       # Request GPU "generic resources"
#SBATCH --cpus-per-task=1  # Cores proportional to GPUs: 6 on Cedar, 16 on Graham.
#SBATCH --mem=32000M       # Memory proportional to GPUs: 32000 Cedar, 64000 Graham.
#SBATCH --time=0-3:00
#SBATCH --output=merge_codellama_%N-%j.out
#SBATCH --mail-user=jonathan.caron-roberge.1@ulaval.ca
#SBATCH --mail-type=ALL

module load python/3.12.4 scipy-stack gcc arrow/17.0.0 cuda cudnn

source /home/pvharmo/projects/def-masai45/pvharmo/venv/bin/activate

cd /home/pvharmo/llm-gha-eval/finetuning/
python merge_model.py --model CodeLlama-7b-Instruct-hf --finetune final-checkpoint
