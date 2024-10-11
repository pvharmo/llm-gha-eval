import sys
sys.path.append('../')
from openai import OpenAI
from env import openai_key
import polars as pl
import json
import os

client = OpenAI(api_key=openai_key)

data = pl.read_ndjson("../dataset/validation_level1_sm.jsonl")
intermediate_file = "../dataset/intermediate/gpt/validation_level1_sm.jsonl"
if os.path.exists(intermediate_file):
    os.remove(intermediate_file)
with open(intermediate_file, "w") as f:
    for row in data.iter_rows(named=True):
        new_row = {
            "custom_id": row["id"],
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model" : "gpt-4o-mini",
                "messages": row["messages"],
                "max_tokens": 4096
            }
        }
        f.write(json.dumps(new_row) + "\n")

batch_input_file = client.files.create(
  file=open("../dataset/intermediate/gpt/validation_level1_sm.jsonl", "rb"),
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
