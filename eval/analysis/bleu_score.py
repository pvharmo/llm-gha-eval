import sys
sys.path.append('../..')

import polars as pl
# type: ignore
from nltk.translate.bleu_score import sentence_bleu
import re

from dataset.load_dataset import load_dataset

from extract_yaml import extract_yaml

def bleu_score(reference: str, candidate: str) -> float:
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

results = pl.read_ndjson("../../results/validation_all_sm_gpt-40_mini-ft.jsonl")

levels = {
    "level1": { "score": 0.0, "count": 0, },
    "level2": { "score": 0.0, "count": 0, },
    "level3": { "score": 0.0, "count": 0, },
    "level4": { "score": 0.0, "count": 0, },
    "level5": { "score": 0.0, "count": 0, },
}

dataset = load_dataset("validation")

for result in results.iter_rows(named=True):
    reference = dataset.filter(lambda x: x["id"] == result["id"])
    reference = extract_yaml(reference["validation"][0]["answer"])
    reference = reference.strip().lower()
    reference = remove_comments(reference)

    answer = extract_yaml(result["answer"])
    answer = answer.strip().lower()
    answer = remove_comments(answer)

    answer_level = result["level"]

    score = bleu_score(reference, answer)

    levels[answer_level]["score"] += score
    levels[answer_level]["count"] += 1

print("Scores:")
print("level 1: ", levels["level1"]["score"] / levels["level1"]["count"])
print("level 2: ", levels["level2"]["score"] / levels["level2"]["count"])
print("level 3: ", levels["level3"]["score"] / levels["level3"]["count"])
print("level 4: ", levels["level4"]["score"] / levels["level4"]["count"])
print("level 5: ", levels["level5"]["score"] / levels["level5"]["count"])
