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
parser.add_argument("--top-p", type=float, default=0.8)
parser.add_argument("-t", type=float, default=0.7)
parser.add_argument("--cpu-offload-gb", type=float, default=10)
parser.add_argument("--finetune", action=argparse.BooleanOptionalAction)
args = parser.parse_args()

if args.model is None:
    print("You need to specify the model to fine-tune.")
    exit()

# checkpoint_path = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
checkpoint_path = env.models_folder + ("/finetunes/" if args.finetune else "/") + args.model
llm = LLM(model=checkpoint_path)
tokenizer = AutoTokenizer.from_pretrained(checkpoint_path, cpu_offload_gb=args.cpu_offload_gb)
sampling_params = SamplingParams(temperature=args.t, top_p=args.top_p, max_tokens=4096)

test_dataset: Dataset = load_dataset("pvharmo/llm-gha", token=env.hf_access_token)["test"]

example_per_level = 200
unique_ids = list(set(test_dataset["id"]))[:200]
test_dataset = test_dataset.filter(lambda example: example["id"] in unique_ids)

for level in ["level1", "level2", "level3", "level4", "level5"]:
    dataset = test_dataset.filter(lambda example: example["level"] == level).select(range(example_per_level))
    dataset = dataset.map(lambda example: {"tokens":tokenizer.apply_chat_template(
        [
            {"role": "system", "content": example["system_prompt"]},
            {"role": "user", "content": example["user_prompt"]}
        ],
        tokenize=False,
        add_generation_prompt=True
    )})

    results_path = f"{env.results_folder}/{args.model.replace('/','_')}-t{args.t}-top_p{args.top_p}{'-finetune' if args.finetune else ''}.jsonl"

    if os.path.exists(results_path):
        os.remove(results_path)

    outputs = llm.generate(dataset["tokens"], sampling_params, use_tqdm=True)

    with open(results_path, "a") as f:
        for example, output in tqdm(zip(test_dataset, outputs)):
            json_line = json.dumps({
                "id": example["id"],
                "level": example["level"],
                "llm_response": output.outputs[0].text,
                "answer": example["answer"]
            })

            f.write(json_line)
            f.write("\n")