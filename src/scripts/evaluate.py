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
from utils.action_comparison import actions_comparison, workflows_comparison
from utils.deepdiff import deepdiff_compare
from utils.llm_judge import llm_as_a_judge

try:
    run_id = int(sys.argv[1])
except:
    print("Please provide a run_id as an argument")

con = sqlite3.connect("results/gha_llm_benchmark.db")
con.row_factory = sqlite3.Row
cur = con.cursor()

def save_results(results):
    cur.execute("""
        INSERT INTO results (
            prediction_id, workflows_comparison, actions_comparison, deepdiff, lint, llm_as_a_judge, errors
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, results)
    con.commit()

cur.execute("SELECT * FROM predictions WHERE run_id = ?", (run_id,))
predictions = cur.fetchall()

for prediction in predictions:
    print("Evaluating " + prediction["owner"] + "/" + prediction["repository"] + "/" + prediction["name"])
    errors = []
    original_workflow_directory = env.repository_directories + "/" + prediction["owner"] + "/" + prediction["repository"] + "/workflows/" + prediction["name"]
    with open(original_workflow_directory) as file:
        original = file.read()
    # try:
    #     parsed_workflow = yaml.safe_load(prediction["workflow"])
    #     parsed_original = yaml.safe_load(original)

    #     actions_comparison_result = json.dumps(actions_comparison(parsed_original, parsed_workflow))

    #     deepdiff_result = json.dumps(deepdiff_compare(parsed_original, parsed_workflow))
    # except yaml.YAMLError as e:
    #     errors.append({
    #         "type": "yaml parsing error",
    #         "error": str(e)
    #     })
    actions_comparison_result = None
    deepdiff_result = None

    judge_result = None
    # try:
    #     judge_result = json.dumps(llm_as_a_judge(prediction["workflow"], prediction["descrition"], "Qwen/Qwen2-72B-Instruct"))
    # except Exception as e:
    #     errors.append({
    #         "type": "Judge failed",
    #         "error": str(e)
    #     })

    workflow_validation = json.dumps(action_validator(prediction["workflow"]))

    workflows_comparison_result = json.dumps(workflows_comparison(original, prediction["workflow"]))

    save_results((
        prediction["id"],
        workflows_comparison_result,
        actions_comparison_result,
        deepdiff_result,
        workflow_validation,
        judge_result,
        json.dumps(errors)
    ))
