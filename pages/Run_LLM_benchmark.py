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
from utils import action_validator, llm_as_a_judge, deepdiff_compare, actions_comparison

st.set_page_config(
    page_title="Run LLM benchmarks",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

menu()

st.title("🚀 Run LLM benchmarks")

con = sqlite3.connect("results/gha_llm_benchmark.db")
cur = con.cursor()

system_prompts_attributes = json.loads(open("./config/system_prompts.json").read())
prompts = json.loads(open("./config/prompts.json").read())

models = pd.DataFrame([
    {"run": False, "name": "phi3 mini", "full name": "phi3:mini", "local": True,},
    {"run": False, "name": "phi3 medium", "full name": "phi3:medium", "local": True,},
    {"run": False, "name": "wizardlm-2 7b", "full name": "wizardlm2", "local": True,},
    {"run": False, "name": "zephyr 7b", "full name": "zephyr", "local": True,},
    {"run": False, "name": "mistral 7b instruct 0.3", "full name": "mistralai/Mistral-7B-Instruct-v0.3", "local": False,},
    {"run": False, "name": "llama3 8b", "full name": "meta-llama/Meta-Llama-3-8B-Instruct", "local": False,},
    {"run": False, "name": "mixtral 8x7b", "full name": "mistralai/Mixtral-8x7B-Instruct-v0.1", "local": False,},
    {"run": False, "name": "mixtral 22x7b", "full name": "mistralai/Mixtral-8x22B-v0.1", "local": False,},
    {"run": False, "name": "llama3 70b", "full name": "meta-llama/Meta-Llama-3-70B-Instruct", "local": False,},
    {"run": False, "name": "wizardlm-2 8x22b", "full name": "microsoft/WizardLM-2-8x22B", "local": False,},
    {"run": False, "name": "Qwen2 72b instruct", "full name": "Qwen/Qwen2-72B-Instruct", "local": False,},
])

with st.form("my_form"):
    st.write("### Models")
    models = st.data_editor(models, hide_index=True, disabled=["name", "full name", "local"], use_container_width=True)

    submit = st.form_submit_button(label="Submit")

system_prompt = "You will be given a description of a GitHub Action workflow file. You will have to generate the workflow file based on the description. Answer only with the file code. Do not add any additional information."

workflows = []

for owner in stqdm(os.listdir(env.repository_directories)):
    for repo_name in os.listdir(env.repository_directories + "/" + owner):
        directory = env.repository_directories + "/" + owner + "/" + repo_name
        for workflow_file in os.listdir(directory + "/workflows"):
            workflows.append({
                "owner": owner,
                "repo_name": repo_name,
                "workflow_file": workflow_file,
                "directory": directory
            })

def save_results(results):
    cur.execute("""
        INSERT INTO results (
            run_id, owner, repository, name, model, description, response, workflow, error_type, error_text
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, results)
    con.commit()

st.write("## Benchmarks running")
if submit and len(models.loc[models["run"]]) > 0:
    cur.execute("INSERT INTO runs (started_at, models) VALUES (?, ?)", (int(time.time()), models.loc[models["run"]].to_json()))
    run_id = cur.lastrowid
    con.commit()

    st.write(f"Run ID: {run_id}")
    for i, model_params in models.loc[models["run"]].iterrows():
        st.write(f"- Running {model_params['name']}")

        yaml_parsing_failed = []

        for workflow_infos in stqdm(workflows):
            with st.expander(f"{workflow_infos['owner']}/{workflow_infos['repo_name']}/{workflow_infos['workflow_file']}"):
                assistant = Assistant(model=model_params["full name"], system_prompt=system_prompt)
                assistant.clear_messages()
                st.write("messages count : " + str(len(assistant.get_messages())))
                # if not (workflow_infos["owner"] == "web-infra-dev" and workflow_infos["workflow_file"] == "issue-close-require.yml"):
                if workflow_infos["owner"] != "web-infra-dev":
                    continue
                directory = workflow_infos["directory"]
                workflow_file = workflow_infos["workflow_file"]

                st.write("reading description...")
                with open(directory + "/detailed_descriptions/" + workflow_file + ".md") as file:
                    description = file.read()

                st.write("reading workflow...")
                with open(directory + "/workflows/" + workflow_file) as file:
                    original = file.read()

                st.write("running agent...")
                try:
                    response = assistant.run(description)
                    st.write("### Response")
                    st.write(response)
                except Exception as e:
                    st.write("### Error receiving a response")
                    st.write(str(e))
                    save_results((
                        run_id,
                        workflow_infos["owner"],
                        workflow_infos["repo_name"],
                        workflow_infos["workflow_file"],
                        model_params['name'],
                        description,
                        None, # response
                        None, # workflow
                        "Workflow generation failed", # error_type
                        str(e) # error_text
                    ))
                    continue

                if "```yaml" in response:
                    workflow = regex.search(r'(?<=```yaml)([\s\S]*?)(?=```)', response)
                    workflow = workflow.group(0) if workflow else response
                elif "```" in response:
                    workflow = regex.search(r'(?<=```)([\s\S]*?)(?=```)', response)
                    workflow = workflow.group(0) if workflow else response
                else:
                    workflow = response

                st.write("### Workflow")
                st.code(workflow, language="yaml")

                st.write("Saving results...")
                save_results((
                    run_id,
                    workflow_infos["owner"],
                    workflow_infos["repo_name"],
                    workflow_infos["workflow_file"],
                    model_params['name'],
                    description,
                    response,
                    workflow,
                    None, # error_type
                    None # error_text
                ))
                st.write("Saved results")
