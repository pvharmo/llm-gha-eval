import sys
sys.path.append('..')

import json

import env
from datasets import Dataset, load_dataset

def save_dataset(dataset: Dataset, path: str):
    with open(path, "a") as f:
        for row in dataset:
            f.write(json.dumps(row))
            f.write("\n")

dataset: Dataset = load_dataset("pvharmo/llm-gha", split="train", token=env.hf_access_token)  # type: ignore

dataset = dataset.filter(lambda example: example["yaml_tokens_count"] <= 1024)

unique_ids = sorted(list(set(dataset["id"])))
unique_ids_generator = unique_ids[:10000]
unique_ids_corrector = unique_ids[10000:20000]
unique_ids_judge = unique_ids[20000:30000]
dataset_generator = dataset.filter(lambda example: example["id"] in unique_ids_generator)
dataset_corrector = dataset.filter(lambda example: example["id"] in unique_ids_corrector)
dataset_judge = dataset.filter(lambda example: example["id"] in unique_ids_judge)

save_dataset(dataset_generator, "../dataset/generator_train.jsonl")
save_dataset(dataset_corrector, "../dataset/corrector_train.jsonl")
save_dataset(dataset_judge, "../dataset/judge_train.jsonl")

data_files = {
    "generator_train": "../dataset/generator_train.jsonl",
    "corrector_train": "../dataset/corrector_train.jsonl",
    "judge_train": "../dataset/judge_train.jsonl",
    "validation": "../dataset/validation.jsonl",
    "test": "../dataset/testing.jsonl"
}

dataset = load_dataset("json", data_files=data_files)  # type: ignore

print(dataset)

input("push to hub? (ctrl+c to cancel, enter to continue)")
dataset.push_to_hub("llm-gha")
