from datasets import load_dataset

data_files = {
    "generator_train": "../dataset/generator_train.jsonl",
    "corrector_train": "../dataset/corrector_train.jsonl",
    "judge_train": "../dataset/judge_train.jsonl",
    "train": "../dataset/finetuning.jsonl",
    "validation": "../dataset/validation.jsonl",
    "test": "../dataset/testing.jsonl"
}
dataset = load_dataset("json", data_files=data_files)

print(dataset)

input("push to hub? (ctrl+c to cancel, enter to continue)")
dataset.push_to_hub("llm-gha")  # type: ignore
