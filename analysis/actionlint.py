import sys
sys.path.append('../..')

import os
import argparse
import json
import subprocess
import polars as pl

import env
from extract_yaml import extract_yaml, detect_infinite_loop

def actionlint(model):
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

    results = pl.read_ndjson(env.results_folder + "/" + model + ".jsonl")

    levels = {
        "level1": { "score": 0.0, "count": 0, },
        "level2": { "score": 0.0, "count": 0, },
        "level3": { "score": 0.0, "count": 0, },
        "level4": { "score": 0.0, "count": 0, },
        "level5": { "score": 0.0, "count": 0, },
    }

    for result in results.iter_rows(named=True):
        if detect_infinite_loop(result["llm_response"]):
            continue
        answer = extract_yaml(result["llm_response"])

        answer_level = result["level"]

        lint_result = action_validator(answer)

        if lint_result and lint_result["valid"]:
            levels[answer_level]["score"] += 1

        levels[answer_level]["count"] += 1

    if os.path.exists(env.results_folder + "/" + model) is False:
        os.makedirs(env.results_folder + "/" + model)
    with open(env.results_folder + "/" + model + "/actionlint.json", "w") as file:
        json.dump(levels, file)

    print("Scores:")
    print("level 1: ", levels["level1"]["score"] / levels["level1"]["count"] if levels["level1"]["count"] > 0 else 0, " total: ", levels["level1"]["count"])
    print("level 2: ", levels["level2"]["score"] / levels["level2"]["count"] if levels["level2"]["count"] > 0 else 0, " total: ", levels["level2"]["count"])
    print("level 3: ", levels["level3"]["score"] / levels["level3"]["count"] if levels["level3"]["count"] > 0 else 0, " total: ", levels["level3"]["count"])
    print("level 4: ", levels["level4"]["score"] / levels["level4"]["count"] if levels["level4"]["count"] > 0 else 0, " total: ", levels["level4"]["count"])
    print("level 5: ", levels["level5"]["score"] / levels["level5"]["count"] if levels["level5"]["count"] > 0 else 0, " total: ", levels["level5"]["count"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str)
    args = parser.parse_args()

    if args.model is None:
        print("You need to specify the model.")
        exit()

    actionlint(args.model)
