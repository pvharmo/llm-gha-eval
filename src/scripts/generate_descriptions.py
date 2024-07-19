import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from tqdm import tqdm

import env
from utils.description import prepare_workflow

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

nb_workflows = 0
for workflow_infos in tqdm(workflows):
    prepare_workflow(workflow_infos)
    nb_workflows += 1
