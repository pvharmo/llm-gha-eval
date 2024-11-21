from utils import init, generate
import json

llm, sampling_params, tokenizer, dataset, results_path, lora_request = init()

dataset = dataset.map(lambda example: {"tokens": tokenizer.apply_chat_template(
    [
        {"role": "system", "content": example["system_prompt"]},
        {"role": "user", "content": example["user_prompt"]}
    ],
    tokenize=False,
    add_generation_prompt=True
)})

outputs = generate(llm, dataset, sampling_params, "test", lora_request)

with open(results_path, "a") as f:
    for example, output in zip(dataset, outputs):
        json_line = json.dumps({
            "id": example["id"],
            "level": example["level"],
            "llm_response": output.outputs[0].text,
            "answer": example["answer"]
        })

        f.write(json_line)
        f.write("\n")

print(f"Results saved to {results_path}")
