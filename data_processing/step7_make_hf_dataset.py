from datasets import load_dataset

data_files = {
    "train": "../dataset/finetuning.jsonl",
    "validation": "../dataset/validation.jsonl",
    "test": "../dataset/testing.jsonl"
}
dataset = load_dataset("json", data_files=data_files)

print(dataset)

input("push to hub? (ctrl+c to cancel, enter to continue)")
dataset.push_to_hub("llm-gha")
