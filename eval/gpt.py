import sys
sys.path.append('../')
from openai import OpenAI
from env import openai_key
import polars as pl
import json
import os

from dataset.load_dataset import load_dataset

client = OpenAI(api_key=openai_key)

dataset = load_dataset("validation")["validation"]
intermediate_file = "../dataset/intermediate/gpt/validation_all_sm_finetuned.jsonl"
if os.path.exists(intermediate_file):
    os.remove(intermediate_file)
with open(intermediate_file, "w") as f:
    for row in dataset.to_iterable_dataset():
        new_row = {
            "custom_id": row["id"] + "_" + row["level"],
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model" : "ft:gpt-4o-mini-2024-07-18:personal:200examples-all:AHAf0ozi",
                "messages": [
                    {
                        "role": "system",
                        "content": row["system_prompt"]
                    },
                    {
                        "role": "user",
                        "content": row["user_prompt"]
                    }
                ],
                "max_tokens": 4096
            }
        }
        f.write(json.dumps(new_row) + "\n")


input("Start the batch job?")
batch_input_file = client.files.create(
  file=open(intermediate_file, "rb"),
  purpose="batch"
)

batch = client.batches.create(
    input_file_id=batch_input_file.id,
    endpoint="/v1/chat/completions",
    completion_window="24h",
    metadata={
      "description": "nightly eval job",
    }
)

with open("../dataset/intermediate/gpt/current_batch_id.txt", "w") as f:
    f.write(batch.id)
