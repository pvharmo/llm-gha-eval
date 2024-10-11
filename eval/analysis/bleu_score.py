import polars as pl
# type: ignore
from nltk.translate.bleu_score import sentence_bleu
import re

from utils import extract_yaml

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

results = pl.read_ndjson("results/validation_level1_sm_gpt-4o-mini.jsonl")
references = pl.read_ndjson("dataset/validation_level1_sm.jsonl")

total_score = 0

for result in results.iter_rows(named=True):
    reference = extract_yaml(references.filter(pl.col("id") == result["custom_id"])[0].to_dicts()[0]["answer"][0]["content"])
    reference = reference.strip().lower()
    reference = remove_comments(reference)
    answer = extract_yaml(result["response"]["body"]["choices"][0]["message"]["content"])
    answer = answer.strip().lower()
    answer = remove_comments(answer)

    # print(reference)
    # print("****************************************************************************************")
    # print(answer)
    # print("########################################################################################")

    score = bleu_score(reference, answer)
    total_score += score
    print(score)
    # input("press enter to continue...")

print("total: ", total_score / len(results))
