#!/bin/bash
#SBATCH --gres=gpu:1       # Request GPU "generic resources"
#SBATCH --cpus-per-task=1  # Cores proportional to GPUs: 6 on Cedar, 16 on Graham.
#SBATCH --mem=16000M       # Memory proportional to GPUs: 32000 Cedar, 64000 Graham.
#SBATCH --time=0-6:00
#SBATCH --output=finetune_prepare_corrector_dataset0.5b_%A_%N-%j.out
#SBATCH --mail-user=jonathan.caron-roberge.1@ulaval.ca
#SBATCH --mail-type=ALL

module load python/3.12.4 scipy-stack gcc arrow/17.0.0 cuda cudnn

source /home/pvharmo/projects/def-masai45/pvharmo/venv/bin/activate

cd /home/pvharmo/llm-gha-eval/finetuning/
python inference_vllm.py --model Qwen2.5-Coder-0.5B-Instruct --cpu-offload-gb 0 --finetune e2-nAll --n None --split corrector_train
