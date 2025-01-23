import sys
sys.path.append('../')

from inference import parse_args, generate, load_model, apply_chat_template
from dataset.load_dataset import format_dataset

model, finetune, sampling_params, cpu_offload_gb, tokenizer = parse_args()

llm, tokenizer, lora_request = load_model(model, finetune, cpu_offload_gb, tokenizer)

dataset = format_dataset("test", 200, False)
dataset = apply_chat_template(dataset, tokenizer)

outputs = generate(
    llm,
    dataset,
    sampling_params,
    f"{model.replace('/', '_')}-t{sampling_params.temperature}-top_p{sampling_params.top_p}{'-' + finetune if finetune is not None else ''}",
    lora_request
)
