import sys
sys.path.append('../..')

import json
import subprocess
import polars as pl
# type: ignore
from nltk.translate.bleu_score import sentence_bleu
import re
import yaml
from deepdiff import DeepDiff

from extract_yaml import extract_yaml
from dataset.load_dataset import load_dataset

def deepdiff_compare(original, generated):
    try:
        original = yaml.safe_load(original)
        generated = yaml.safe_load(generated)
    except yaml.YAMLError as e:
        return None

    diff_events = DeepDiff(original, generated, ignore_order=True, verbose_level=2, get_deep_distance=True)

    return diff_events["deep_distance"] if "deep_distance" in diff_events else None

results = pl.read_ndjson("../../results/validation_all_sm_gpt-40_mini-ft.jsonl")

levels = {
    "level1": { "score": 0.0, "valid_count": 0, "errors": 0, "total": 0},
    "level2": { "score": 0.0, "valid_count": 0, "errors": 0, "total": 0},
    "level3": { "score": 0.0, "valid_count": 0, "errors": 0, "total": 0},
    "level4": { "score": 0.0, "valid_count": 0, "errors": 0, "total": 0},
    "level5": { "score": 0.0, "valid_count": 0, "errors": 0, "total": 0},
}

dataset = load_dataset("validation")

for result in results.iter_rows(named=True):
    reference = dataset.filter(lambda x: x["id"] == result["id"])
    reference = extract_yaml(reference["validation"][0]["answer"])
    answer = extract_yaml(result["answer"])

    answer_level = result["level"]

    score = deepdiff_compare(reference, answer)
    if score is not None:
        levels[answer_level]["score"] += score
        levels[answer_level]["valid_count"] += 1
    else:
        levels[answer_level]["errors"] += 1

    levels[answer_level]["total"] += 1

print("Scores:")
print("level 1: ", levels["level1"]["score"] / levels["level1"]["valid_count"], " -- errors: ", levels["level1"]["errors"] / levels["level1"]["total"])
print("level 2: ", levels["level2"]["score"] / levels["level2"]["valid_count"], " -- errors: ", levels["level2"]["errors"] / levels["level2"]["total"])
print("level 3: ", levels["level3"]["score"] / levels["level3"]["valid_count"], " -- errors: ", levels["level3"]["errors"] / levels["level3"]["total"])
print("level 4: ", levels["level4"]["score"] / levels["level4"]["valid_count"], " -- errors: ", levels["level4"]["errors"] / levels["level4"]["total"])
print("level 5: ", levels["level5"]["score"] / levels["level5"]["valid_count"], " -- errors: ", levels["level5"]["errors"] / levels["level5"]["total"])
