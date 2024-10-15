import polars as pl
from tqdm import tqdm
import json


levels = ["level1", "level2", "level3", "level4", "level5"]
types = ["finetuning", "validation", "testing"]

all_conversations = []

for type in types:
    docs = pl.read_json(f"../dataset/intermediate/{type}.json")
    with open(f"../dataset/{type}.jsonl", "w") as f_all:
        for level in levels:
            conversations = []
            for doc in tqdm(docs.iter_rows(named=True)):
                system_promtp = "You are an expert devops engineer. Please generate a YAML file based on the user's input below. No additional explanation is needed. The output format should be ```yaml <Workflow>```."
                conversation = {
                    "id": doc["id"],
                    "level": level,
                    "system_prompt": system_promtp,
                    "user_prompt": doc["info"][level],
                    "answer": "```yaml " + doc["yaml"] + "```"
                }

                json.dump(conversation, f_all)
                f_all.write("\n")
