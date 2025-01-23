import sys

sys.path.append('../')

import torch
from transformers import AutoModelForCausalLM
from peft import PeftModel
import argparse

import env

parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str)
parser.add_argument("--finetune", type=str, default=None)
args = parser.parse_args()

base_model = AutoModelForCausalLM.from_pretrained(env.models_folder + "/" + args.model, torch_dtype=torch.float16, device_map="auto")

model_to_merge = PeftModel.from_pretrained(base_model.to("cuda"), env.models_folder + "/finetunes/" + args.model + "/" + args.finetune)
merged_model = model_to_merge.merge_and_unload()
merged_model.save_pretrained(env.tmp_fodler + "/" + args.model + "_ft_merged")
