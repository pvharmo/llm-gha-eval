import sys
sys.path.append('../')
import argparse

from datetime import datetime
from openai import OpenAI
import tiktoken
import polars as pl
import env

parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str)
args = parser.parse_args()

if args.model is None:
    print("You need to specify the model to fine-tune.")
    exit()

client = OpenAI(api_key=env.openai_key)
encoding = tiktoken.encoding_for_model("gpt-4o-mini")

# To take advantage of the free tokens offered by OpenAI, we split the training dataset
# into 5 parts and fine-tune the model on each part for 5 days.
i = (datetime.now().day - 19) % 6
dataset = pl.read_ndjson(f"../dataset/train_parts/train_{i}.jsonl")
tokens_count = 0
for row in dataset.iter_rows(named=True):
    sentence = row["messages"][0]["content"] + row["messages"][1]["content"] + row["messages"][2]["content"]
    tokens_count += len(encoding.encode(sentence))
input(f"Starting training of part {i} with {dataset.height} examples with a total of {tokens_count} tokens. Press enter to continue...")

file = client.files.create(
  file=open(f"../dataset/train_parts/train_{i}.jsonl", "rb"),
  purpose="fine-tune"
)

res = client.fine_tuning.jobs.create(
  training_file=file.id,
  model=args.model,
  suffix="v1-" + datetime.now().strftime("%Y-%m-%d"),
  seed=1555677560,
  hyperparameters={
    "n_epochs": 1,
  }
)

print(f"New model is named {res.fine_tuned_model}")

with open("../tmp/latest_fine_tuned_model.txt", "w") as f:
    f.write(res.fine_tuned_model or "")

print("Fine-tuning started.")
