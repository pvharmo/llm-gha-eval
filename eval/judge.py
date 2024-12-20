import sys
sys.path.append('../')

from inference import parse_args, generate, load_model, apply_chat_template
from dataset.load_dataset import format_dataset
import datasets
from analysis.extract_yaml import detect_infinite_loop

model, finetune, sampling_params, cpu_offload_gb = parse_args()

llm, tokenizer, lora_request = load_model(model, finetune, cpu_offload_gb)

dataset = format_dataset("test", 400, False)
dataset = apply_chat_template(dataset, tokenizer)

outputs1 = generate(
    llm,
    dataset,
    sampling_params,
    f"judge/{model.replace('/', '_')}-t{sampling_params.temperature}-top_p{sampling_params.top_p}{'-' + finetune if finetune is not None else ''}-intermediate-1",
    lora_request
)

outputs2 = generate(
    llm,
    dataset,
    sampling_params,
    f"judge/{model.replace('/', '_')}-t{sampling_params.temperature}-top_p{sampling_params.top_p}{'-' + finetune if finetune is not None else ''}-intermediate-2",
    lora_request
)

outputs = []

system_prompt = "You are an expert devops engineer. You will be provided two workflow and a prompt. You must determine which workflow is the best fit for the prompt. Explain your reasoning before choosing the best fit. Give your answer in the following format: 'I choose workflow {workflow number}.'"

for row1, row2 in zip(outputs1, outputs2):
    if detect_infinite_loop(row1["llm_response"]) or detect_infinite_loop(row2["llm_response"]):
        continue
    row = {
        "id": row1["id"],
        "level": row1["level"],
        "answer": row1["answer"],
        "prompt": row1["prompt"],
        "text": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"prompt: {row1['prompt']}\n\nworkflow 1: {row1['llm_response']}\n\n---\n\nworkflow 2: {row2['llm_response']}"},
        ],
    }
    outputs.append(row)

generated_dataset = datasets.Dataset.from_list(outputs)

generated_dataset = apply_chat_template(generated_dataset, tokenizer)

generate(
    llm,
    generated_dataset,
    sampling_params,
    f"judge/{model.replace('/', '_')}-t{sampling_params.temperature}-top_p{sampling_params.top_p}{'-' + finetune if finetune is not None else ''}",
    lora_request
)
