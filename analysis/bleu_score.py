import sys
sys.path.append('../')

import os
import json
import polars as pl
from nltk.translate.bleu_score import sentence_bleu  # type: ignore
import re

from extract_yaml import extract_yaml, detect_infinite_loop
import env

import argparse

def bleu_score(model, results=None):
    def i_bleu_score(reference: str, candidate: str) -> float:
        if candidate is None:
            return 0.0

        score: float = sentence_bleu([reference.split()], candidate.split())

        return score


    def remove_comments(yaml_content):
        comment_pattern = re.compile(r'^\s*#.*$', re.MULTILINE)
        yaml_content_without_comments = re.sub(comment_pattern, '', yaml_content)
        lines = yaml_content_without_comments.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        return '\n'.join(non_empty_lines)

    def remove_empty_lines(yaml_content):
        lines = yaml_content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        return '\n'.join(non_empty_lines)

    if results is None:
        results = pl.read_ndjson(env.results_folder + "/" + model + ".jsonl")

    levels = {
        "level1": { "score": 0.0, "count": 0, },
        "level2": { "score": 0.0, "count": 0, },
        "level3": { "score": 0.0, "count": 0, },
        "level4": { "score": 0.0, "count": 0, },
        "level5": { "score": 0.0, "count": 0, },
    }

    infinite_loops = 0

    for result in results.iter_rows(named=True):
        if detect_infinite_loop(result["llm_response"]):
            infinite_loops += 1
            continue
        reference = extract_yaml(result["answer"])
        reference = reference.strip().lower()
        reference = remove_comments(reference)

        answer = extract_yaml(result["llm_response"])
        answer = answer.strip().lower()
        answer = remove_comments(answer)

        answer_level = result["level"]

        score = i_bleu_score(reference, answer)

        levels[answer_level]["score"] += score
        levels[answer_level]["count"] += 1

    if os.path.exists(env.results_folder + "/" + model) is False:
        os.makedirs(env.results_folder + "/" + model)
    with open(env.results_folder + "/" + model + "/bleu_score.json", "w") as file:
        json.dump(levels, file)

    print("BLEU scores:")
    print("level 1: ", levels["level1"]["score"] / levels["level1"]["count"] if levels["level1"]["count"] > 0 else 0)
    print("level 2: ", levels["level2"]["score"] / levels["level2"]["count"] if levels["level2"]["count"] > 0 else 0)
    print("level 3: ", levels["level3"]["score"] / levels["level3"]["count"] if levels["level3"]["count"] > 0 else 0)
    print("level 4: ", levels["level4"]["score"] / levels["level4"]["count"] if levels["level4"]["count"] > 0 else 0)
    print("level 5: ", levels["level5"]["score"] / levels["level5"]["count"] if levels["level5"]["count"] > 0 else 0)
    print("Infinite loops: ", infinite_loops)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str)
    args = parser.parse_args()

    if args.model is None:
        print("You need to specify the model.")
        exit()

    bleu_score(args.model)
