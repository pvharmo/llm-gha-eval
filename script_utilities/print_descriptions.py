import sys
sys.path.append('../')

import argparse
import polars as pl

parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str)
args = parser.parse_args()

if args.model is None:
    print("You need to specify the model.")
    exit()

results = pl.read_ndjson("../dataset/generator_train.jsonl")

for result in results.iter_rows(named=True):
# for result in results.head(10).iter_rows(named=True):
    # print(result["id"])
    # print(result["user_prompt"])
    if result["id"] == "63c496346fc19abdf9c9a885":
        print(result["user_prompt"])
        print("\n***************************************************************\n")
