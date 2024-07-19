import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import re as regex
import json
import pandas as pd
from tqdm import tqdm
import sqlite3
import time

from assistant import Assistant
import env

con = sqlite3.connect("results/gha_llm_benchmark.db")
cur = con.cursor()

system_prompts_attributes = json.loads(open("./config/system_prompts.json").read())
prompts = json.loads(open("./config/prompts.json").read())

models = pd.DataFrame([
    # {"name": "phi3 mini", "full name": "phi3:mini", "local": True,},
    # {"name": "phi3 medium", "full name": "phi3:medium", "local": True,},
    # {"name": "wizardlm-2 7b", "full name": "wizardlm2", "local": True,},
    # {"name": "zephyr 7b", "full name": "zephyr", "local": True,},
    # {"name": "mistral 7b instruct 0.3", "full name": "mistralai/Mistral-7B-Instruct-v0.3", "local": False,},
    # {"name": "llama3 8b", "full name": "meta-llama/Meta-Llama-3-8B-Instruct", "local": False,},
    {"name": "codellama 7b instruct", "full name": "pvharmo/codellama-7b-Instruct", "local": False,},
    # {"name": "mixtral 8x7b", "full name": "mistralai/Mixtral-8x7B-Instruct-v0.1", "local": False,},
    # {"name": "mixtral 22x7b", "full name": "mistralai/Mixtral-8x22B-v0.1", "local": False,},
    # {"name": "llama3 70b", "full name": "meta-llama/Meta-Llama-3-70B-Instruct", "local": False,},
    # {"name": "wizardlm-2 8x22b", "full name": "microsoft/WizardLM-2-8x22B", "local": False,},
    # {"name": "Qwen2 72b instruct", "full name": "Qwen/Qwen2-72B-Instruct", "local": False,},
])

system_prompt = "You are a software engineer. Please generate a YAML file based on the user's input below. No additional explanation is needed. The output format should be ```yaml <Workflow>```."

workflows = []

for owner in tqdm(os.listdir(env.repository_directories)):
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
        INSERT INTO predictions (
            run_id, owner, repository, name, model, description_id, description, response, workflow, error_type, error_text
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, results)
    con.commit()

cur.execute("INSERT INTO runs (started_at, models) VALUES (?, ?)", (int(time.time()), models.to_json()))
run_id = cur.lastrowid
con.commit()

print(f"Run ID: {run_id}")
for i, model_params in models.iterrows():
    print(f"- Running {model_params['name']}")

    yaml_parsing_failed = []

    for workflow_infos in tqdm(workflows):
        print(f"{workflow_infos['owner']}/{workflow_infos['repo_name']}/{workflow_infos['workflow_file']}")

        directory = workflow_infos["directory"]
        workflow_file = workflow_infos["workflow_file"]

        try:
            with open(directory + "/generated_descriptions/workflow_level_infos_" + workflow_file + ".txt") as file:
                workflow_level_infos = file.read()

            with open(directory + "/generated_descriptions/event_triggers_" + workflow_file + ".txt") as file:
                event_triggers = file.read()

            with open(directory + "/generated_descriptions/job_ids_" + workflow_file + ".txt") as file:
                job_ids = file.read()

            with open(directory + "/generated_descriptions/job_level_infos_" + workflow_file + ".txt") as file:
                job_level_infos = file.read()

            with open(directory + "/generated_descriptions/step_names_" + workflow_file + ".txt") as file:
                step_names = file.read()

            with open(directory + "/generated_descriptions/step_level_infos_" + workflow_file + ".txt") as file:
                step_level_infos = file.read()

            with open(directory + "/generated_descriptions/dependencies_" + workflow_file + ".txt") as file:
                dependencies = file.read()
        except FileNotFoundError as e:
            print(e)
            continue

        with open(directory + "/workflows/" + workflow_file) as file:
            original = file.read()

        print("Running inference")

        descriptions = {
            "p1": workflow_level_infos + event_triggers + job_ids,
            "p2": workflow_level_infos + event_triggers + job_ids + step_names,
            "p3": workflow_level_infos + event_triggers + job_ids + step_names + dependencies,
            "p4": workflow_level_infos + event_triggers + job_level_infos + step_names,
            "p5": workflow_level_infos + event_triggers + job_level_infos + step_level_infos,
        }

        for (description_id, description) in descriptions.items():
            assistant = Assistant(model=model_params["full name"], system_prompt=system_prompt)
            assistant.clear_messages()
            try:
                response = assistant.run(description)
            except Exception as e:
                print("### Error receiving a response")
                print(str(e))
                save_results((
                    run_id,
                    workflow_infos["owner"],
                    workflow_infos["repo_name"],
                    workflow_infos["workflow_file"],
                    model_params['name'],
                    description_id,
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

            save_results((
                run_id,
                workflow_infos["owner"],
                workflow_infos["repo_name"],
                workflow_infos["workflow_file"],
                model_params['name'],
                description_id,
                description,
                response,
                workflow,
                None, # error_type
                None # error_text
            ))
