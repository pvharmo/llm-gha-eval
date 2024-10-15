import sys
sys.path.append('../')
import json
import polars as pl

from dataset.load_dataset import load_dataset

dataset = load_dataset("train")["train"]

with open("../dataset/train.jsonl", "w") as f:
    for row in dataset.to_iterable_dataset():
        line = {
            "messages" : [
                {"role": "system", "content": row["system_prompt"]},
                {"role": "user", "content": row["user_prompt"]},
                {"role": "assistant", "content": row["answer"]}
            ]
        }

        f.write(json.dumps(line) + "\n")

train_dataset = pl.read_ndjson("../dataset/train.jsonl")
count = train_dataset.height
slice_len = count // 10

for i in range(0, 10):
    train_dataset.slice(i * slice_len, (i + 1) * slice_len).write_ndjson(f"../dataset/train_parts/train_{i}.jsonl")
