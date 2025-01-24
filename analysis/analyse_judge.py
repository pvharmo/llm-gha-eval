import sys
sys.path.append('../')

import argparse
import polars as pl
import re

import env
from actionlint import actionlint
from deepdiff_score import deepdiff_score
from bleu_score import bleu_score


parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str)
args = parser.parse_args()

if args.model is None:
    print("You need to specify the model.")
    exit()

results = pl.read_ndjson(env.results_folder + "/judge/" + args.model + ".jsonl")
intermediates1 = pl.read_ndjson(env.results_folder + "/judge/" + args.model + "-intermediate-1.jsonl")
intermediates2 = pl.read_ndjson(env.results_folder + "/judge/" + args.model + "-intermediate-2.jsonl")

formatted_results = []

for result, intermediate1, intermediate2 in zip(results.iter_rows(named=True), intermediates1.iter_rows(named=True), intermediates2.iter_rows(named=True)):
    regex = re.compile(r"I choose workflow ([1,2])")
    match = regex.search(result["llm_response"])
    if match is None:
        print("Could not find the workflow number in the response.")
        continue
    llm_response = intermediate1["llm_response"] if match.group(1) == "1" else intermediate2["llm_response"]
    formatted_results.append({
        "id": result["id"],
        "llm_response": llm_response,
        "level": result["level"],
        "answer": result["answer"]
    })

formatted_results = pl.from_dicts(formatted_results)

actionlint(args.model + "-judge-intermediate-1", intermediates1)
deepdiff_score(args.model + "-judge-intermediate-1", intermediates1)
bleu_score(args.model + "-judge-intermediate-1", intermediates1)


actionlint(args.model + "-judge-intermediate-2", intermediates2)
deepdiff_score(args.model + "-judge-intermediate-2", intermediates2)
bleu_score(args.model + "-judge-intermediate-2", intermediates2)


actionlint(args.model + "-judge", formatted_results)
deepdiff_score(args.model + "-judge", formatted_results)
bleu_score(args.model + "-judge", formatted_results)
