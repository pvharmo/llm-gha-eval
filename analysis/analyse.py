import sys
sys.path.append('../')

import argparse
import os
import json
import polars as pl

import env
from utils.actionlint import validate_action
from utils.bleu_score import bleu_score
from extract_yaml import extract_yaml, detect_infinite_loop

parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str)
args = parser.parse_args()

if args.model is None:
    print("You need to specify the model.")
    exit()

results = pl.read_ndjson(env.results_folder + "/" + args.model + ".jsonl")

scores = []
for result in results.iter_rows(named=True):
    if detect_infinite_loop(result["llm_response"]):
        result["infinite_loop"] = True
        result["lint_score"] = None
        result["bleu_score"] = None
        scores.append(result)
        continue

    yaml_answer = extract_yaml(result["answer"])
    yaml_llm_response = extract_yaml(result["llm_response"])

    result["infinite_loop"] = False
    result["lint_score"] = validate_action(yaml_llm_response)
    result["bleu_score"] = bleu_score(yaml_answer, yaml_llm_response)
    scores.append(result)

if os.path.exists(env.results_folder + "/" + args.model) is False:
    os.makedirs(env.results_folder + "/" + args.model)
with open(env.results_folder + "/" + args.model + "/scores.json", "w") as file:
    json.dump(scores, file)

levels = {
    "level1": {
        "lint_score": { "score": 0.0, "count": 0, },
        "bleu_score": { "score": 0.0, "count": 0, },
    },
    "level2": {
        "lint_score": { "score": 0.0, "count": 0, },
        "bleu_score": { "score": 0.0, "count": 0, },
    },
    "level3": {
        "lint_score": { "score": 0.0, "count": 0, },
        "bleu_score": { "score": 0.0, "count": 0, },
    },
    "level4": {
        "lint_score": { "score": 0.0, "count": 0, },
        "bleu_score": { "score": 0.0, "count": 0, },
    },
    "level5": {
        "lint_score": { "score": 0.0, "count": 0, },
        "bleu_score": { "score": 0.0, "count": 0, },
    },
}

infinite_loops = 0

for score in scores:
    answer_level = score["level"]

    if score["infinite_loop"]:
        infinite_loops += 1
        continue

    if score["lint_score"] is not None and score["lint_score"]["valid"]:
        levels[answer_level]["lint_score"]["score"] += 1
    levels[answer_level]["lint_score"]["count"] += 1

    if score["bleu_score"] is not None:
        levels[answer_level]["bleu_score"]["score"] += score["bleu_score"]
    levels[answer_level]["bleu_score"]["count"] += 1


def get_score(levels, level, score_type):
    return levels[level][score_type]["score"] / levels[level][score_type]["count"] if levels[level][score_type]["count"] > 0 else 0

print("BLEU scores:")
print("level 1: ", get_score(levels, "level1", "bleu_score"))
print("level 2: ", get_score(levels, "level2", "bleu_score"))
print("level 3: ", get_score(levels, "level3", "bleu_score"))
print("level 4: ", get_score(levels, "level4", "bleu_score"))
print("level 5: ", get_score(levels, "level5", "bleu_score"))
print("LINT scores:")
print("level 1: ", get_score(levels, "level1", "lint_score"))
print("level 2: ", get_score(levels, "level2", "lint_score"))
print("level 3: ", get_score(levels, "level3", "lint_score"))
print("level 4: ", get_score(levels, "level4", "lint_score"))
print("level 5: ", get_score(levels, "level5", "lint_score"))
print("Infinite loops: ", infinite_loops)
