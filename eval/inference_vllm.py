import sys
sys.path.append('../')

import os
import argparse
from transformers import AutoTokenizer
from datasets import Dataset, concatenate_datasets, load_dataset
import json
from tqdm import tqdm
from vllm import LLM, SamplingParams


import env

parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str)
parser.add_argument("--finetune", action=argparse.BooleanOptionalAction)
args = parser.parse_args()

if args.model is None:
    print("You need to specify the model to fine-tune.")
    exit()

# checkpoint_path = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
checkpoint_path = env.models_folder + ("/finetunes/" if args.finetune else "/") + args.model
llm = LLM(model=checkpoint_path)
tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)
sampling_params = SamplingParams(temperature=0.7, top_p=0.8, repetition_penalty=1.05, max_tokens=4096)

test_dataset: Dataset = load_dataset("pvharmo/llm-gha", token=env.hf_access_token)["test"]

example_per_level = 200
unique_ids = list(set(test_dataset["id"]))[:200]
test_dataset = test_dataset.filter(lambda example: example["id"] in unique_ids)

test_dataset_level1 = test_dataset.filter(lambda example: example["level"] == "level1").select(range(example_per_level))
test_dataset_level2 = test_dataset.filter(lambda example: example["level"] == "level2").select(range(example_per_level))
test_dataset_level3 = test_dataset.filter(lambda example: example["level"] == "level3").select(range(example_per_level))
test_dataset_level4 = test_dataset.filter(lambda example: example["level"] == "level4").select(range(example_per_level))
test_dataset_level5 = test_dataset.filter(lambda example: example["level"] == "level5").select(range(example_per_level))

test_dataset = concatenate_datasets([test_dataset_level1, test_dataset_level2, test_dataset_level3, test_dataset_level4, test_dataset_level5])

test_dataset = test_dataset.map(lambda example: {"tokens":tokenizer.apply_chat_template(
    [
        {"role": "system", "content": example["system_prompt"]},
        {"role": "user", "content": example["user_prompt"]}
    ],
    tokenize=False,
    add_generation_prompt=True
)})

results_path = f"{env.results_folder}/{args.model.replace('/','_')}.jsonl"

if os.path.exists(results_path):
    os.remove(results_path)

outputs = llm.generate(test_dataset["tokens"], sampling_params)

with open(results_path, "a") as f:
    for example, output in tqdm(zip(test_dataset, outputs)):
        json_line = json.dumps({
            "id": example["id"],
            "level": example["level"],
            "llm_response": output,
            "answer": example["answer"]
        })

        f.write(json_line)
        f.write("\n")
