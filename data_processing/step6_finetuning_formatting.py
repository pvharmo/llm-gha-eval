import polars as pl
from tqdm import tqdm
import json


levels = ["level1", "level2", "level3", "level4", "level5"]
types = ["finetuning", "validation", "testing"]

all_conversations = []

for type in types:
    docs = pl.read_json(f"../dataset/intermediate/{type}.json")
    with open(f"../dataset/intermediate/{type}_all.jsonl", "w") as f_all:
        for level in levels:
            conversations = []
            with open(f"../dataset/intermediate/{type}_{level}.jsonl", "w") as f:
                for doc in tqdm(docs.iter_rows(named=True)):
                    system_promtp = "You are an expert devops engineer. Please generate a YAML file based on the user's input below. No additional explanation is needed. The output format should be ```yaml <Workflow>```."
                    conversation = {
                        "id": doc["id"],
                        "messages": [
                            {
                                "role": "system",
                                "content": system_promtp
                            },
                            {
                                "role": "user",
                                "content": doc["info"][level]
                            },
                            {
                                'role': 'assistant',
                                'content': "```yaml " + doc["yaml"] + "```"
                            }
                        ],
                    }

                    json.dump(conversation, f)
                    f.write("\n")
                    json.dump(conversation, f_all)
                    f_all.write("\n")
