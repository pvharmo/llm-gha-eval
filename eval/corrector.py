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
    f"corrector/{model.replace('/', '_')}-t{sampling_params.temperature}-top_p{sampling_params.top_p}{'-' + finetune if finetune is not None else ''}-intermediate",
    lora_request
)

outputs = []

system_prompt = "You are an expert devops engineer. You will be provided a workflow and a prompt. You must fix any error in the workflow. No additional explanation is needed. The output format should be ```yaml <Workflow>```."

for row in outputs1:
    if detect_infinite_loop(row["llm_response"]):
        continue
    new_row = {
        "text": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"prompt: {row['prompt']}\n\nworkflow: {row['llm_response']}"},
        ],
    }
    outputs.append(new_row)

generated_dataset = datasets.Dataset.from_list(outputs)

generated_dataset = apply_chat_template(generated_dataset, tokenizer)

generate(
    llm,
    generated_dataset,
    sampling_params,
    f"corrector/{model.replace('/', '_')}-t{sampling_params.temperature}-top_p{sampling_params.top_p}{'-' + finetune if finetune is not None else ''}",
    lora_request
)
