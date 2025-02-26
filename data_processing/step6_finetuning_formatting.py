from tqdm import tqdm
import json
from transformers import AutoTokenizer


levels = ["level1", "level2", "level3", "level4", "level5"]
types = ["finetuning", "testing"]

all_conversations = []

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-Coder-1.5B-Instruct")

for type in types:
    docs = json.load(open(f"../dataset/intermediate/{type}.json"))
    with open(f"../dataset/{type}.jsonl", "w") as f_all:
        for level in levels:
            conversations = []
            for doc in tqdm(docs):
                conversation = {
                    "id": doc["id"],
                    "group": doc["combination_group"],
                    "level": level,
                    "user_prompt": doc["info"][level],
                    "answer": "```yaml " + doc["yaml"] + "```",
                    "yaml_tokens_count": len(tokenizer.encode(doc["yaml"]))
                }

                json.dump(conversation, f_all)
                f_all.write("\n")
