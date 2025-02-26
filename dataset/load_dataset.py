import sys
sys.path.append('..')

import datasets
import env
from datasets import Dataset, load_dataset, concatenate_datasets

datasets.logging.set_verbosity_warning()

# def load_dataset(split = None) -> datasets.DatasetDict:
#     if split == "train":
#         data_files = {"train": dataset_directory + "/finetuning.jsonl"}
#     elif split == "validation":
#         data_files = {"validation": dataset_directory + "/validation.jsonl"}
#     elif split == "test":
#         data_files = {"test": dataset_directory + "/testing.jsonl"}
#     else:
#         data_files = {"train": dataset_directory + "/finetuning.jsonl", "validation": dataset_directory + "/validation.jsonl", "test": dataset_directory + "/testing.jsonl"}
#     dataset = datasets.load_dataset("json", data_files=data_files)
#     if isinstance(dataset, datasets.DatasetDict):
#         return dataset
#     else:
#         raise TypeError("The dataset is not a valid dataset object")

def format_dataset(split, examples_per_level=None, with_answers=False, tokens_limit=1024, system_prompt=None):
    data_files = {
        "generator_train": "../dataset/generator_train.jsonl",
        "corrector_train": "../dataset/corrector_train.jsonl",
        "judge_train": "../dataset/judge_train.jsonl",
        "validation": "../dataset/validation.jsonl",
        "test": "../dataset/testing.jsonl"
    }

    dataset = load_dataset("json", data_files=data_files, split=split)
    # dataset: Dataset = load_dataset("pvharmo/llm-gha", split=split, token=env.hf_access_token)  # type: ignore

    dataset = dataset.filter(lambda example: example["yaml_tokens_count"] <= tokens_limit)

    unique_ids = sorted(list(set(dataset["id"])))
    unique_ids = unique_ids if examples_per_level is None else unique_ids[:examples_per_level]
    dataset = dataset.filter(lambda example: example["id"] in unique_ids)

    if examples_per_level is not None:
        dataset_level1 = dataset.filter(lambda example: example["level"] == "level1").select(range(examples_per_level))
        dataset_level2 = dataset.filter(lambda example: example["level"] == "level2").select(range(examples_per_level))
        dataset_level3 = dataset.filter(lambda example: example["level"] == "level3").select(range(examples_per_level))
        dataset_level4 = dataset.filter(lambda example: example["level"] == "level4").select(range(examples_per_level))
        dataset_level5 = dataset.filter(lambda example: example["level"] == "level5").select(range(examples_per_level))

        dataset = concatenate_datasets([dataset_level1, dataset_level2, dataset_level3, dataset_level4, dataset_level5])

    if system_prompt is None:
        system_prompt = "You are an expert devops engineer. Please generate a YAML file based on the user's input below. No additional explanation is needed. The output format should be ```yaml <Workflow>```."

    if with_answers:
        return dataset.map(lambda example: {
            "text":
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": example["user_prompt"]},
                    {"role": "assistant", "content": example["answer"]}
                ],
            "prompt": example["user_prompt"],
        })
    else:
        return dataset.map(lambda example: {
            "text":
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": example["user_prompt"]}
                ],
            "prompt": example["user_prompt"],
        })

def load_per_group(split, examples_per_group, with_answers=False):
    dataset: Dataset = load_dataset("pvharmo/llm-gha", token=env.hf_access_token)  # type: ignore
    dataset = concatenate_datasets([dataset["train"], dataset["validation"], dataset["test"]])  # type: ignore
    unique_groups = sorted(list(set(dataset["group"])))
    dataset_level1 = dataset.filter(lambda example: example["level"] == "level1")
    groups = {}
    for group in unique_groups:
        groups[group] = dataset_level1.filter(lambda example: example["group"] == group)

    total = 0
    for (group, value) in groups.items():
        if len(value) >= examples_per_group:
            total += 1
    print(total)
