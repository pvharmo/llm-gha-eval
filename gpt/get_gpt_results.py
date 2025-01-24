import sys
sys.path.append('../')
from openai import OpenAI
from env import openai_key
import json
import polars as pl

client = OpenAI(api_key=openai_key)

with open("../dataset/intermediate/gpt/current_batch_id.txt", "r") as f:
    batch_id = f.read()

res = client.batches.retrieve(batch_id)

if res.status == "completed":
    if res.output_file_id is None:
        print("Batch is completed but output file is missing")
    else:

        output = client.files.content(res.output_file_id)
        json_output = output.write_to_file("../tmp/validation_all_sm_gpt-40_mini-ft.jsonl")
        json_lines = pl.read_ndjson("../tmp/validation_all_sm_gpt-40_mini-ft.jsonl").to_dicts()

        with open("../results/validation_all_sm_gpt-40_mini-ft.jsonl", "w") as f:
            for element in json_lines:
                result = {
                    "id": element["custom_id"][:-7],
                    "level": element["custom_id"][-6:],
                    "answer": element["response"]["body"]["choices"][0]["message"]["content"]
                }
                f.write(json.dumps(result) + "\n")

elif res.status == "in_progress":
    print("Batch is still in progress")
else:
    print(f"Batch status: {res.status}")
