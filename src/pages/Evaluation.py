import os
import re as regex
import streamlit as st
import json
import pandas as pd
from stqdm import stqdm
from menu import menu
from pathlib import Path
import yaml
import sqlite3
import time

from assistant import Assistant

import env
from utils.action_validation import action_validator
from utils.action_comparison import actions_comparison
from utils.deepdiff import deepdiff_compare
from utils.llm_judge import llm_as_a_judge

st.set_page_config(
    page_title="Evaluation",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

menu()

st.title("🚀 Evaluate predictions")

con = sqlite3.connect("results/gha_llm_benchmark.db")
cur = con.cursor()

system_prompts_attributes = json.loads(open("./config/system_prompts.json").read())
prompts = json.loads(open("./config/prompts.json").read())

with st.form("my_form"):
    st.write("### Models")
    run_id = st.number_input(label="Run ID")

    submit = st.form_submit_button(label="Submit")

def save_results(results):
    cur.execute("""
        INSERT INTO results (
            run_id, owner, repository, name, model, description, response, workflow, actions_comparison, deepdiff, lint, llm_as_a_judge, error_type, error_text
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, results)
    con.commit()

st.write("## Benchmarks running")
if submit:
    cur.execute("SELECT INTO predictions * WHERE run_id = ?", (run_id,))
    results = cur.fetchall()

    # for result in results:
    #     st.write(result)
    #     try:
    #         parsed_workflow = yaml.safe_load(workflow)
    #         parsed_original = yaml.safe_load(original)
    #     except yaml.YAMLError as e:
    #         yaml_parsing_failed.append({
    #             "response": response,
    #             "workflow": workflow,
    #             "description": description,
    #             "error": str(e)
    #         })
    #         continue
        # st.write("comparing actions with judge...")
        # try:
        #     judge_result = json.dumps(llm_as_a_judge(workflow, description, "Qwen/Qwen2-72B-Instruct"))
        # except Exception as e:
        #     st.write("### Error from the judge")
        #     st.write(str(e))
        #     save_results((
        #         run_id,
        #         workflow_infos["owner"],
        #         workflow_infos["repo_name"],
        #         workflow_infos["workflow_file"],
        #         model_params['name'],
        #         description,
        #         response,
        #         workflow,
        #         None, # actions_comparison
        #         None, # deepdiff
        #         None, # lint
        #         None, # llm_as_a_judge
        #         "Judge failed", # error_type
        #         str(e) # error_text
        #     ))
        #     continue
        # st.write(judge_result)

        # st.write("comparing actions algorithmically...")
        # actions_comparison_result = json.dumps(actions_comparison(parsed_original, parsed_workflow))
        # st.json(actions_comparison_result)

        # st.write("comparing actions with deepdiff...")
        # deepdiff_result = json.dumps(deepdiff_compare(parsed_original, parsed_workflow))
        # st.json(deepdiff_result)

        # st.write("validating workflow...")
        # workflow_validation = json.dumps(action_validator(workflow))
        # st.json(workflow_validation)

        # st.write("Saving results...")
        # save_results((
        #     run_id,
        #     workflow_infos["owner"],
        #     workflow_infos["repo_name"],
        #     workflow_infos["workflow_file"],
        #     model_params['name'],
        #     description,
        #     response,
        #     workflow,
        #     actions_comparison_result,
        #     deepdiff_result,
        #     workflow_validation,
        #     judge_result,
        #     None, # error_type
        #     None # error_text
        # ))
        # st.write("Saved results")
