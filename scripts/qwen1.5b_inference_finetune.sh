#!/bin/bash
#SBATCH --gres=gpu:1       # Request GPU "generic resources"
#SBATCH --cpus-per-task=1  # Cores proportional to GPUs: 6 on Cedar, 16 on Graham.
#SBATCH --mem=32000M       # Memory proportional to GPUs: 32000 Cedar, 64000 Graham.
#SBATCH --time=0-6:00
#SBATCH --output=inference_finetune_qwen1.5b_%A_%N-%j.out
#SBATCH --array=1-3

module load python/3.12.4 scipy-stack gcc arrow/17.0.0 cuda cudnn

source /home/pvharmo/llm-gha-eval/venv/bin/activate

cd /home/pvharmo/llm-gha-eval/eval/
python inference_vllm.py --model Qwen2.5-Coder-1.5B-Instruct --cpu-offload-gb 0 --finetune e1-n$((1000 * $SLURM_ARRAY_TASK_ID))