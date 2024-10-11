import json
import subprocess
import polars as pl
# type: ignore
from nltk.translate.bleu_score import sentence_bleu
import re

from utils import extract_yaml

def action_validator(workflow):
    if workflow is None:
        return None
    with open('../outputs/test.yml', 'w') as file:
        file.write(workflow)

    output = subprocess.run(["actionlint", "-format", "'{{json .}}'", "../outputs/test.yml"], text=True, capture_output=True).stdout

    json_output = json.loads(output[1:-1])

    return {
        "valid": len(json_output) == 0,
        "output": json_output,
    }

results = pl.read_ndjson("results/validation_level1_sm_gpt-4o-mini.jsonl")

total_score = 0

for result in results.iter_rows(named=True):
    answer = extract_yaml(result["response"]["body"]["choices"][0]["message"]["content"])

    score = action_validator(answer)
    print(score)

print("total: ", total_score / len(results))
