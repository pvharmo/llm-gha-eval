import sys
import json
from tqdm import tqdm
import yaml
import sqlite3
import time
import polars as pl

import env
from utils.analysis.action_validation import action_validator
from utils.analysis.action_comparison import actions_comparison, bleu_score
from utils.analysis.deepdiff import deepdiff_compare
# from utils.analysis.llm_judge import llm_as_a_judge

def evaluate(run_id):
    con = sqlite3.connect("../results/gha_llm_benchmark.db")
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
        """, (eval_id, prediction_id, deepdiff, errors))
        cur.execute("""
            INSERT INTO actions_comparisons (
                eval_id, prediction_id, actions_comparison, errors
            ) VALUES (?, ?, ?, ?)
        """, (eval_id, prediction_id, actions_comparison, errors))
        con.commit()

    cur.execute("SELECT * FROM predictions WHERE run_id = ?", (run_id,))
    predictions = cur.fetchall()
    descriptions = pl.read_json(env.dataset_file)
    print("Evaluating " + str(len(predictions)) + " predictions")

    for prediction in tqdm(predictions):
        errors = []
        original = descriptions.filter(pl.col("id") == prediction["dataset_id"]).row(0, named=True)["yaml"]
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

    return eval_id

if __name__ == "__main__":
    try:
        run_id = int(sys.argv[1])
    except:
        raise Exception("Please provide a run_id as an argument")

    evaluate(run_id)