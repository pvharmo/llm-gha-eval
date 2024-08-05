import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import re as regex
import json
import pandas as pd
from tqdm import tqdm
import yaml
import sqlite3
import time

from assistant import Assistant

import env
from utils.action_validation import action_validator
from utils.action_comparison import actions_comparison, bleu_score
from utils.deepdiff import deepdiff_compare
from utils.llm_judge import llm_as_a_judge

try:
    run_id = int(sys.argv[1])
except:
    raise Exception("Please provide a run_id as an argument")

con = sqlite3.connect("results/gha_llm_benchmark.db")
con.row_factory = sqlite3.Row
cur = con.cursor()

cur.execute("INSERT INTO evaluations (started_at, run_id) VALUES (?, ?)", (int(time.time()), run_id))
eval_id = cur.lastrowid
con.commit()

print("eval_id: " + str(eval_id))

def save_results(prediction_id, bleu_score, lint, deepdiff, actions_comparison, errors = None):
    cur.execute("""
        INSERT INTO bleu_scores (
            eval_id, prediction_id, score, errors
        ) VALUES (?, ?, ?, ?)
    """, (eval_id, prediction_id, bleu_score, None))
    cur.execute("""
        INSERT INTO lints (
            eval_id, prediction_id, lint, errors
        ) VALUES (?, ?, ?, ?)
    """, (eval_id, prediction_id, lint, None))
    cur.execute("""
        INSERT INTO deepdiffs (
            eval_id, prediction_id, deepdiff, errors
        ) VALUES (?, ?, ?, ?)
    """, (eval_id, prediction_id, lint, errors))
    cur.execute("""
        INSERT INTO actions_comparisons (
            eval_id, prediction_id, actions_comparison, errors
        ) VALUES (?, ?, ?, ?)
    """, (eval_id, prediction_id, lint, errors))
    con.commit()

cur.execute("SELECT * FROM predictions WHERE run_id = ?", (run_id,))
predictions = cur.fetchall()

columns = ['owner', 'repo', 'filename', 'path']

valid_workflows = pd.read_csv(env.valid_workflows_list, header=None, names=columns)

for prediction in tqdm(predictions):
    exists = ((valid_workflows.owner == prediction["owner"]) & (valid_workflows.repo == prediction["repository"]) & (valid_workflows.filename == prediction["name"])).any()
    if not exists:
        continue
    # print("Evaluating " + prediction["owner"] + "/" + prediction["repository"] + "/" + prediction["name"])
    errors = []
    original_workflow_directory = env.repository_directories + "/" + prediction["owner"] + "/" + prediction["repository"] + "/workflows/" + prediction["name"]
    with open(original_workflow_directory) as file:
        original = file.read()
    if prediction["workflow"] is not None:
        try:
            parsed_workflow = yaml.safe_load(prediction["workflow"])
            parsed_original = yaml.safe_load(original)

            try:
                actions_comparison_result = json.dumps(actions_comparison(parsed_original, parsed_workflow))
            except KeyError as e:
                errors.append({
                    "type": "key error",
                    "error": str(e)
                })
                actions_comparison_result = None
            except TypeError as e:
                errors.append({
                    "type": "type error",
                    "error": str(e)
                })
                actions_comparison_result = None

            try:
                deepdiff_result = json.dumps(deepdiff_compare(parsed_original, parsed_workflow))
            except TypeError as e:
                errors.append({
                    "type": "type error",
                    "error": str(e)
                })
                deepdiff_result = None
        except yaml.YAMLError as e:
            errors.append({
                "type": "yaml parsing error",
                "error": str(e)
            })
            actions_comparison_result = None
            deepdiff_result = None
    else:
        actions_comparison_result = None
        deepdiff_result = None


    workflow_validation = json.dumps(action_validator(prediction["workflow"]))

    bleu_score_result = bleu_score(original, prediction["workflow"])

    save_results(
        prediction_id = prediction["id"],
        bleu_score = bleu_score_result,
        actions_comparison = actions_comparison_result,
        deepdiff = deepdiff_result,
        lint = workflow_validation,
        errors = json.dumps(errors)
    )
