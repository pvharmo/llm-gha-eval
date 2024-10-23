import sys
sys.path.append('../')

from llama_cpp import Llama
from datasets import load_dataset
import json
from tqdm import tqdm

import env

dataset = load_dataset("pvharmo/llm-gha")["validation"]

repo_id = "Qwen/Qwen2.5-Coder-7B-Instruct-GGUF"
llm = Llama.from_pretrained(
    repo_id=repo_id,
    filename="qwen2.5-coder-7b-instruct-q8_0-00001-of-00003.gguf",
    additional_files=[
        "qwen2.5-coder-7b-instruct-q8_0-00002-of-00003.gguf",
        "qwen2.5-coder-7b-instruct-q8_0-00003-of-00003.gguf"],
    chat_format="llama-2"
)

for example in tqdm(dataset):
    messages = [
        {"role": "system", "content": example["system_prompt"]},
        {"role": "user", "content": example["user_prompt"]},
    ]

    output = llm.create_chat_completion(messages=messages)
    response = output["choices"][0]["message"]["content"]
    json_line = json.dumps({
        "llm_response": response,
        "answer": example["answer"]
    })
    with open(f"{env.results_folder}/{repo_id.replace('/','_')}.jsonl", "w") as f:
        f.write(json_line)
