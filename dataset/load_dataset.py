import sys
sys.path.append('..')

import datasets
from env import dataset_directory

datasets.logging.set_verbosity_warning()

def load_dataset(split = None) -> datasets.DatasetDict:
    if split == "train":
        data_files = {"train": dataset_directory + "/finetuning.jsonl"}
    elif split == "validation":
        data_files = {"validation": dataset_directory + "/validation.jsonl"}
    elif split == "test":
        data_files = {"test": dataset_directory + "/testing.jsonl"}
    else:
        data_files = {"train": dataset_directory + "/finetuning.jsonl", "validation": dataset_directory + "/validation.jsonl", "test": dataset_directory + "/testing.jsonl"}
    dataset = datasets.load_dataset("json", data_files=data_files)
    if isinstance(dataset, datasets.DatasetDict):
        return dataset
    else:
        raise TypeError("The dataset is not a valid dataset object")
