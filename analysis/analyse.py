import argparse

from actionlint import actionlint
from deepdiff_score import deepdiff_score
from bleu_score import bleu_score

parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str)
args = parser.parse_args()

if args.model is None:
    print("You need to specify the model.")
    exit()

actionlint(args.model)
deepdiff_score(args.model)
bleu_score(args.model)
