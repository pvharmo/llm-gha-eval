import sys

sys.path.append('../')

import os
import argparse
from transformers import AutoTokenizer
import json
from vllm import LLM, SamplingParams  # type: ignore
from vllm.lora.request import LoRARequest  # type: ignore

import env

def int_or_none(value):
    if value.lower() == 'none' or value == '':
        return None
    try:
        return int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not an integer or 'None'")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str)
    parser.add_argument("--top-p", type=float, default=0.8)
    parser.add_argument("-t", type=float, default=0.7)
    parser.add_argument("--cpu-offload-gb", type=float, default=10)
    parser.add_argument("--finetune", type=str, default=None)
    parser.add_argument("--tokenizer", type=str, default=None)
    parser.add_argument("--max_tokens", type=str, default=8192)
    parser.add_argument("--n", type=int_or_none, default=400, help="Number of prompts to use. If None, use all prompts.")
    parser.add_argument("--split", type=str, default="test")
    args = parser.parse_args()

    if args.model is None:
        print("You need to specify the model.")
        exit()

    sampling_params = SamplingParams(temperature=args.t, top_p=args.top_p, max_tokens=args.max_tokens)

    return args.model, args.finetune, sampling_params, args.cpu_offload_gb, args.tokenizer, args.max_tokens, args.n, args.split

def load_model(model, finetune=None, cpu_offload_gb=10, tokenizer=None, max_tokens=8192):
    # checkpoint_path = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
    checkpoint_path = env.models_folder + "/" + model
    tokenizer_path = env.models_folder + "/" + (model if tokenizer is None else tokenizer)

    lora_path = (env.models_folder + "/finetunes/" + model + "/" + finetune) if finetune is not None else None

    llm = LLM(
        model=checkpoint_path,
        tokenizer=tokenizer_path,
        dtype="bfloat16",
        cpu_offload_gb=cpu_offload_gb,
        max_model_len=max_tokens,
        enable_lora=finetune is not None,

    )
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)

    lora_request = LoRARequest("lora_adapter", 1, lora_path) if lora_path is not None else None

    return llm, tokenizer, lora_request

def apply_chat_template(dataset, tokenizer):
    return dataset.map(lambda example: {"tokens": tokenizer.apply_chat_template(
        example["text"],
        tokenize=False,
        add_generation_prompt=True
    )})

def generate(llm, dataset, sampling_params, id, lora_request=None):
    outputs = llm.generate(
        dataset["tokens"],
        sampling_params,
        use_tqdm=True,
        lora_request=lora_request
    )

    outputs = [{
        "id": example["id"],
        "level": example["level"],
        "llm_response": output.outputs[0].text,
        "answer": example["answer"],
        "prompt": example["prompt"]
    } for example, output in zip(dataset, outputs)]

    results_path = f"{env.results_folder}/{id}.jsonl"

    if os.path.exists(results_path):
        os.remove(results_path)

    with open(results_path, "a") as f:
        for output in outputs:
            json_line = json.dumps(output)

            f.write(json_line)
            f.write("\n")

    print(f"Results saved to {results_path}")

    return outputs
