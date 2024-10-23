import os
import sys
sys.path.append('../')
import json
import polars as pl

from dataset.load_dataset import load_dataset

dataset = load_dataset("train")["train"]

train_path = "../dataset/train.jsonl"

if os.path.exists(train_path):
    os.remove(train_path)
with open(train_path, "w") as f:
    for row in dataset.to_iterable_dataset():
        line = {
            "messages" : [
                {"role": "system", "content": row["system_prompt"]},
                {"role": "user", "content": row["user_prompt"]},
                {"role": "assistant", "content": row["answer"]}
            ]
        }

        f.write(json.dumps(line) + "\n")

train_dataset = pl.read_ndjson(train_path)
count = train_dataset.height
slice_len = count // 5

for i in range(0, 5):
    path = f"../dataset/train_parts/train_{i}.jsonl"
    if os.path.exists(path):
        os.remove(path)
    train_dataset.slice(i * slice_len, slice_len).write_ndjson(path)
