import sys

sys.path.append('../')

from dataset.load_dataset import format_dataset
import os
import argparse
from transformers import AutoTokenizer
from datasets import Dataset
import json
from tqdm import tqdm
from vllm import LLM, SamplingParams
from vllm.lora.request import LoRARequest

import env

def init():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str)
    parser.add_argument("--top-p", type=float, default=0.8)
    parser.add_argument("-t", type=float, default=0.7)
    parser.add_argument("--cpu-offload-gb", type=float, default=10)
    parser.add_argument("--dtype", type=str, default="float16")
    parser.add_argument("--finetune", type=str, default=None)
    parser.add_argument("--enable_prefix_caching", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--enable_chunked_prefill", action=argparse.BooleanOptionalAction, default=False)
    args = parser.parse_args()

    if args.model is None:
        print("You need to specify the model to fine-tune.")
        exit()

    # checkpoint_path = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
    checkpoint_path = env.models_folder + "/" + args.model

    lora_path = (env.models_folder + "/finetunes/" + args.model + "/" + args.finetune) if args.finetune is not None else None

    llm = LLM(
        model=checkpoint_path,
        dtype=args.dtype,
        cpu_offload_gb=args.cpu_offload_gb,
        enable_prefix_caching=args.enable_prefix_caching,
        enable_chunked_prefill=args.enable_chunked_prefill,
        max_model_len=8192,
        enable_lora=args.finetune is not None,
    )
    tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)
    sampling_params = SamplingParams(temperature=args.t, top_p=args.top_p, max_tokens=8192)

    dataset: Dataset = format_dataset("test", 10, False)

    results_path = f"{env.results_folder}/{args.model.replace('/', '_')}-t{args.t}-top_p{args.top_p}{'-' + args.finetune if args.finetune is not None else ''}.jsonl"

    if os.path.exists(results_path):
        os.remove(results_path)

    lora_request = LoRARequest("lora_adapter", 1, lora_path) if lora_path is not None else None

    return llm, sampling_params, tokenizer, dataset, results_path, lora_request

def generate(llm, dataset, sampling_params, id, lora_request=None):
    outputs = llm.generate(
        dataset["tokens"],
        sampling_params,
        use_tqdm=True,
        lora_request=lora_request
    )

    with open(env.intermediate_path + "/" + id + ".json", "a") as f:
        for example, output in tqdm(zip(dataset, outputs)):
            json_line = json.dumps({
                "id": example["id"],
                "level": example["level"],
                "llm_response": output.outputs[0].text,
                "answer": example["answer"]
            })

            f.write(json_line)
            f.write("\n")

    print(f"Results saved to {env.intermediate_path + "/" + id + ".json"}")

    return outputs
