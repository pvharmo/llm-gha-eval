import json
import subprocess
import polars as pl
# type: ignore
from nltk.translate.bleu_score import sentence_bleu
import re

from extract_yaml import extract_yaml

def action_validator(workflow):
    if workflow is None:
        return None
    with open('../../tmp/test.yml', 'w') as file:
        file.write(workflow)

    output = subprocess.run(["actionlint", "-format", "'{{json .}}'", "../../tmp/test.yml"], text=True, capture_output=True).stdout

    json_output = json.loads(output[1:-1])

    for values in json_output:
        if values["kind"] == "syntax-check":
            return {
                "valid": False,
                "output": json_output,
            }

    return {
        "valid": True,
        "output": json_output,
    }

results = pl.read_ndjson("../../results/validation_all_sm_gpt-40_mini-ft.jsonl")

levels = {
    "level1": { "score": 0.0, "count": 0, },
    "level2": { "score": 0.0, "count": 0, },
    "level3": { "score": 0.0, "count": 0, },
    "level4": { "score": 0.0, "count": 0, },
    "level5": { "score": 0.0, "count": 0, },
}

for result in results.iter_rows(named=True):
    answer = extract_yaml(result["answer"])

    answer_level = result["level"]

    lint_result = action_validator(answer)

    if lint_result and lint_result["valid"]:
        levels[answer_level]["score"] += 1

    levels[answer_level]["count"] += 1

print("Scores:")
print("level 1: ", levels["level1"]["score"] / levels["level1"]["count"])
print("level 2: ", levels["level2"]["score"] / levels["level2"]["count"])
print("level 3: ", levels["level3"]["score"] / levels["level3"]["count"])
print("level 4: ", levels["level4"]["score"] / levels["level4"]["count"])
print("level 5: ", levels["level5"]["score"] / levels["level5"]["count"])
