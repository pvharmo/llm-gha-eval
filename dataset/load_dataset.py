import sys
sys.path.append('..')

import datasets
import env
from datasets import DatasetDict, Dataset, load_dataset, concatenate_datasets

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

def format_dataset(split, examples_per_level, with_answers=False):
    dataset: Dataset = load_dataset("pvharmo/llm-gha", token=env.hf_access_token)[split]

    unique_ids = list(set(dataset["id"]))[:examples_per_level]
    dataset = dataset.filter(lambda example: example["id"] in unique_ids)

    dataset_level1 = dataset.filter(lambda example: example["level"] == "level1").select(range(examples_per_level))
    dataset_level2 = dataset.filter(lambda example: example["level"] == "level2").select(range(examples_per_level))
    dataset_level3 = dataset.filter(lambda example: example["level"] == "level3").select(range(examples_per_level))
    dataset_level4 = dataset.filter(lambda example: example["level"] == "level4").select(range(examples_per_level))
    dataset_level5 = dataset.filter(lambda example: example["level"] == "level5").select(range(examples_per_level))

    dataset = concatenate_datasets([dataset_level1, dataset_level2, dataset_level3, dataset_level4, dataset_level5])

    if with_answers:
        return dataset.map(lambda example: {"text":
            [
                {"role": "system", "content": example["system_prompt"]},
                {"role": "user", "content": example["user_prompt"]},
                {"role": "assistant", "content": example["answer"]}
            ],
        })
    else:
        return dataset.map(lambda example: {"text":
            [
                {"role": "system", "content": example["system_prompt"]},
                {"role": "user", "content": example["user_prompt"]}
            ],
        })
