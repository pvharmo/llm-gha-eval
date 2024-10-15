import sys
sys.path.append('../')

from datetime import datetime
from openai import OpenAI
import env

client = OpenAI(api_key=env.openai_key)

# To take advantage of the free tokens offered by OpenAI, we split the training dataset
# into 10 parts and fine-tune the model on each part for 10 days.
i = (datetime.now().day - 15) % 10
input(f"Starting training of part {i}. Press enter to continue...")

file = client.files.create(
  file=open(f"../dataset/train_parts/train_{i}.jsonl", "rb"),
  purpose="fine-tune"
)

client.fine_tuning.jobs.create(
  training_file=file.id,
  model="gpt-4o-mini-2024-07-18",
  suffix="v1-" + datetime.now().strftime("%Y-%m-%d"),
  seed=1555677560,
  hyperparameters={
    "n_epochs": 1,
  }
)

print("Fine-tuning started.")
