import sys
sys.path.append('../')

import argparse

from dataset.load_dataset import format_dataset
from finetune import finetune

parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str)
parser.add_argument("--epochs", type=int)
parser.add_argument("--nb_examples", type=int)
args = parser.parse_args()

train_dataset = format_dataset("train", args.nb_examples, True)
validation_dataset = format_dataset("validation", args.nb_examples, True)

dataset = {
    "train": train_dataset,
    "validation": validation_dataset
}

finetune(args.model, args.nb_examples, args.epochs, dataset, "train")
