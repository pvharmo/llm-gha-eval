import argparse
from finetune import finetune

parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str)
args = parser.parse_args()

if args.model == "qwen2.5-1.5b":
    model = "Qwen2.5-Coder-1.5B-Instruct"
else:
    model = "Qwen2.5-Coder-7B-Instruct"

finetune(model)
