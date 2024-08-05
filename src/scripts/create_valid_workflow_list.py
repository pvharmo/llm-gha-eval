import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from tqdm import tqdm

import env
from utils.action_validation import action_validator

workflows = []

for owner in tqdm(os.listdir(env.repository_directories)):
    for repo_name in os.listdir(env.repository_directories + "/" + owner):
        directory = env.repository_directories + "/" + owner + "/" + repo_name
        for workflow_file in os.listdir(directory + "/workflows"):
            if workflow_file.endswith(".yml") or workflow_file.endswith(".yaml"):
                workflows.append({
                    "owner": owner,
                    "repo_name": repo_name,
                    "workflow_file": workflow_file,
                    "directory": directory
                })

valid_workflows = []

nb_workflows = 0
for workflow_infos in tqdm(workflows):
    with open(workflow_infos["directory"] + "/workflows/" + workflow_infos["workflow_file"]) as file:
        yaml_content = file.read()
    validation = action_validator(yaml_content)
    if validation is None:
        continue
    # print(validation)
    if validation["valid"] is True or any(item.get('kind') == 'syntax-check' for item in validation['output']):
        # print("***************** Valid workflow *****************")
        valid_workflows.append(workflow_infos)
        nb_workflows += 1

with open(env.valid_workflows_list, 'w') as file:
    for workflow in valid_workflows:
        file.write(f"\"{workflow['owner']}\",\"{workflow['repo_name']}\",\"{workflow['workflow_file']}\",\"{workflow['directory']}\"\n")
