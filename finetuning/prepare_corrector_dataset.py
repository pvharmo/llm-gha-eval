import sys
sys.path.append('../')

from eval.inference import parse_args, generate, load_model, apply_chat_template
from dataset.load_dataset import format_dataset

model, finetune, sampling_params, cpu_offload_gb = parse_args()

llm, tokenizer, lora_request = load_model(model, finetune, cpu_offload_gb)

dataset = format_dataset("corrector_train", None, False)
dataset = apply_chat_template(dataset, tokenizer)

outputs = generate(
    llm,
    dataset,
    sampling_params,
    "train_generator_dataset",
    lora_request
)

dataset = format_dataset("validation", None, False)
dataset = apply_chat_template(dataset, tokenizer)

outputs = generate(
    llm,
    dataset,
    sampling_params,
    "validation_generator_dataset",
    lora_request
)

dataset = format_dataset("test", None, False)
dataset = apply_chat_template(dataset, tokenizer)

outputs = generate(
    llm,
    dataset,
    sampling_params,
    "test_generator_dataset",
    lora_request
)
