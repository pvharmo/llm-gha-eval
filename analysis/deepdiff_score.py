import os
import sys
sys.path.append('../')

import json
import polars as pl
import yaml
from deepdiff import DeepDiff
import argparse

from extract_yaml import extract_yaml
import env

def deepdiff_score(model, results=None):
    def deepdiff_compare(original, generated):
        try:
            original = yaml.safe_load(original)
            generated = yaml.safe_load(generated)
        except yaml.YAMLError:
            return None

        diff_events = DeepDiff(original, generated, ignore_order=True, verbose_level=2, get_deep_distance=True)

        return diff_events["deep_distance"] if "deep_distance" in diff_events else None

    if results is None:
        results = pl.read_ndjson(env.results_folder + "/" + model + ".jsonl")

    levels = {
        "level1": { "score": 0.0, "valid_count": 0, "errors": 0, "total": 0},
        "level2": { "score": 0.0, "valid_count": 0, "errors": 0, "total": 0},
        "level3": { "score": 0.0, "valid_count": 0, "errors": 0, "total": 0},
        "level4": { "score": 0.0, "valid_count": 0, "errors": 0, "total": 0},
        "level5": { "score": 0.0, "valid_count": 0, "errors": 0, "total": 0},
    }

    for result in results.iter_rows(named=True):
        reference = extract_yaml(result["answer"])
        answer = extract_yaml(result["llm_response"])

        answer_level = result["level"]

        score = deepdiff_compare(reference, answer)
        if score is not None:
            levels[answer_level]["score"] += score
            levels[answer_level]["valid_count"] += 1
        else:
            levels[answer_level]["errors"] += 1

        levels[answer_level]["total"] += 1

    if os.path.exists(env.results_folder + "/" + model) is False:
        os.makedirs(env.results_folder + "/" + model)
    with open(env.results_folder + "/" + model + "/deepdiff.json", "w") as file:
        json.dump(levels, file)

    print("Scores:")
    print("level 1: ", levels["level1"]["score"] / levels["level1"]["valid_count"] if levels["level1"]["valid_count"] > 0 else 0, " -- errors: ", levels["level1"]["errors"] / levels["level1"]["total"] if levels["level1"]["total"] > 0 else 0)
    print("level 2: ", levels["level2"]["score"] / levels["level2"]["valid_count"] if levels["level2"]["valid_count"] > 0 else 0, " -- errors: ", levels["level2"]["errors"] / levels["level2"]["total"] if levels["level2"]["total"] > 0 else 0)
    print("level 3: ", levels["level3"]["score"] / levels["level3"]["valid_count"] if levels["level3"]["valid_count"] > 0 else 0, " -- errors: ", levels["level3"]["errors"] / levels["level3"]["total"] if levels["level3"]["total"] > 0 else 0)
    print("level 4: ", levels["level4"]["score"] / levels["level4"]["valid_count"] if levels["level4"]["valid_count"] > 0 else 0, " -- errors: ", levels["level4"]["errors"] / levels["level4"]["total"] if levels["level4"]["total"] > 0 else 0)
    print("level 5: ", levels["level5"]["score"] / levels["level5"]["valid_count"] if levels["level5"]["valid_count"] > 0 else 0, " -- errors: ", levels["level5"]["errors"] / levels["level5"]["total"] if levels["level5"]["total"] > 0 else 0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str)
    args = parser.parse_args()

    if args.model is None:
        print("You need to specify the model.")
        exit()

    deepdiff_score(args.model)
