import sys
sys.path.append('../')
from openai import OpenAI
from env import openai_key

client = OpenAI(api_key=openai_key)

with open("../dataset/intermediate/gpt/current_batch_id.txt", "r") as f:
    batch_id = f.read()

res = client.batches.retrieve(batch_id)

if res.status == "completed":
    if res.output_file_id is None:
        print("Batch is completed but output file is missing")
    else:
        output = client.files.content(res.output_file_id)
        output.write_to_file("../results/validation_level1_sm.jsonl")

elif res.status == "in_progress":
    print("Batch is still in progress")
else:
    print(f"Batch status: {res.status}")
