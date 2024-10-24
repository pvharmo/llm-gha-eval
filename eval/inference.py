import sys
sys.path.append('../')

import os
import argparse
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import Dataset, concatenate_datasets, load_dataset
import json
from tqdm import tqdm

import env

parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str)
parser.add_argument("--finetune", action=argparse.BooleanOptionalAction)
args = parser.parse_args()

if args.model is None:
    print("You need to specify the model to fine-tune.")
    exit()

# checkpoint_path = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
checkpoint_path = env.models_folder + ("/finetunes/" if args.finetune else "/") + args.model

print("Loading model ", checkpoint_path)

model = AutoModelForCausalLM.from_pretrained(
    checkpoint_path,
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(checkpoint_path, padding_side='left')

test_dataset: Dataset = load_dataset("pvharmo/llm-gha", token=env.hf_access_token)["test"]

example_per_level = 200
unique_ids = list(set(test_dataset["id"]))[:200]
test_dataset = test_dataset.filter(lambda example: example["id"] in unique_ids)

test_dataset_level1 = test_dataset.filter(lambda example: example["level"] == "level1").select(range(example_per_level))
test_dataset_level2 = test_dataset.filter(lambda example: example["level"] == "level2").select(range(example_per_level))
test_dataset_level3 = test_dataset.filter(lambda example: example["level"] == "level3").select(range(example_per_level))
test_dataset_level4 = test_dataset.filter(lambda example: example["level"] == "level4").select(range(example_per_level))
test_dataset_level5 = test_dataset.filter(lambda example: example["level"] == "level5").select(range(example_per_level))

test_dataset = concatenate_datasets([test_dataset_level1, test_dataset_level2, test_dataset_level3, test_dataset_level4, test_dataset_level5])

results_path = f"{env.results_folder}/{args.model.replace('/','_')}.jsonl"

if os.path.exists(results_path):
    os.remove(results_path)

for example in tqdm(test_dataset):
    messages = [
        {"role": "system", "content": example["system_prompt"]},
        {"role": "user", "content": example["user_prompt"]}
    ]

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=4096
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

    json_line = json.dumps({
        "id": example["id"],
        "level": example["level"],
        "llm_response": response,
        "answer": example["answer"]
    })

    with open(results_path, "a") as f:
        f.write(json_line)
        f.write("\n")
