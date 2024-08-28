import sys
import os
from typing_extensions import Dict
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import re as regex
import json
import pandas as pd
from tqdm import tqdm
import time
import yaml

from assistant import Assistant
import env

# results = {
#     'triggers_count': {1: 11428, 2: 13358, 3: 6327},
#     'actions_count': {1: 6101, 2: 8499, 3: 5317, 4: 4212, 5: 5786},
#     'reusable_workflows_count': {0: 29959, 1: 1679},
#     'jobs_count': {1: 24284, 2: 5125, 4: 1975},
#     'steps_count': {0: 1253, 1: 4217, 3: 26314, 7: 0, 11: 0},
#     'cyclomatic_complexity': {1: 20590, 2: 5267, 3: 5019}
# }
# for key, value in results.items():
#     print(key)
#     total = sum(value.values())
#     for k, v in value.items():
#         print(f"{k}: {v/total:.2%}")

# raise Exception("Stop here")

def calculate_cyclomatic_complexity(workflow) -> int:
    complexity = 1  # Base complexity

    for job in workflow['jobs'].values():
        if 'if' in job and job['if'] != False:
            complexity += 1
        if 'steps' in job and job['steps'] is not None:
            for step in job.get('steps', []):
                if 'if' in step and step['if'] != False:
                    complexity += 1

    return complexity

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

workflows_complexity = []

for workflow_infos in tqdm(workflows):
    try:
        with open(workflow_infos["directory"] + "/workflows/" + workflow_infos["workflow_file"], "r") as f:
            workflow = yaml.safe_load(f)
    except:
        continue
    # print(workflow_infos["directory"] + "/workflows/" + workflow_infos["workflow_file"])

    actions_count = 0
    jobs_count = 0
    steps_count = 0
    reusable_workflows_count = 0
    if not isinstance(workflow, Dict) or "jobs" not in workflow:
        continue
    for job_name in workflow["jobs"]:
        jobs_count += 1
        job = workflow["jobs"][job_name]
        if "uses" in job:
            reusable_workflows_count += 1
        if "steps" in job and job["steps"] is not None:
            for step in job["steps"]:
                steps_count += 1
                if "uses" in step:
                    actions_count += 1

    triggers_count = 0
    if True in workflow:
        for trigger in workflow[True]:
            triggers_count += 1

    workflows_complexity.append({
        "owner": workflow_infos["owner"],
        "repo_name": workflow_infos["repo_name"],
        "workflow_file": workflow_infos["workflow_file"],
        "actions_count": actions_count,
        "jobs_count": jobs_count,
        "steps_count": steps_count,
        "triggers_count": triggers_count,
        "reusable_workflows_count": reusable_workflows_count,
        "cyclomatic_complexity": calculate_cyclomatic_complexity(workflow)
    })

buckets = {
    "triggers_count": {
        1: 0,
        2: 0,
        3: 0,
    },
    "actions_count": {
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
    },
    "reusable_workflows_count": {
        0: 0,
        1: 0,
    },
    "jobs_count": {
        1: 0,
        2: 0,
        4: 0,
    },
    "steps_count": {
        0: 0,
        1: 0,
        3: 0,
        7: 0,
        11: 0,
    },
    "cyclomatic_complexity": {
        1: 0,
        2: 0,
        3: 0,
    }
}

for workflow_complexity in workflows_complexity:
    if workflow_complexity["triggers_count"] == 1:
        buckets["triggers_count"][1] += 1
    elif workflow_complexity["triggers_count"] == 2:
        buckets["triggers_count"][2] += 1
    elif workflow_complexity["triggers_count"] >= 3 and workflow_complexity["triggers_count"] <= 6:
        buckets["triggers_count"][3] += 1

    if workflow_complexity["actions_count"] == 0 or workflow_complexity["actions_count"] == 1:
        buckets["actions_count"][1] += 1
    elif workflow_complexity["actions_count"] == 2:
        buckets["actions_count"][2] += 1
    elif workflow_complexity["actions_count"] == 3:
        buckets["actions_count"][3] += 1
    elif workflow_complexity["actions_count"] == 4:
        buckets["actions_count"][4] += 1
    elif workflow_complexity["actions_count"] >= 5 and workflow_complexity["actions_count"] <= 10:
        buckets["actions_count"][5] += 1

    if workflow_complexity["reusable_workflows_count"] == 0:
        buckets["reusable_workflows_count"][0] += 1
    elif workflow_complexity["reusable_workflows_count"] >= 1 and workflow_complexity["reusable_workflows_count"] <= 4:
        buckets["reusable_workflows_count"][1] += 1

    if workflow_complexity["jobs_count"] == 1:
        buckets["jobs_count"][1] += 1
    elif workflow_complexity["jobs_count"] == 2 or workflow_complexity["jobs_count"] == 3:
        buckets["jobs_count"][2] += 1
    elif workflow_complexity["jobs_count"] >= 4 and workflow_complexity["jobs_count"] <= 8:
        buckets["jobs_count"][4] += 1

    if workflow_complexity["steps_count"] == 0:
        buckets["steps_count"][0] += 1
    elif workflow_complexity["steps_count"] == 1 or workflow_complexity["steps_count"] == 2:
        buckets["steps_count"][1] += 1
    elif workflow_complexity["steps_count"] >= 3 and workflow_complexity["steps_count"] <= 6:
        buckets["steps_count"][3] += 1
    elif workflow_complexity["steps_count"] >= 7 and workflow_complexity["steps_count"] <= 10:
        buckets["steps_count"][7] += 1
    elif workflow_complexity["steps_count"] >= 11 and workflow_complexity["steps_count"] <= 21:
        buckets["steps_count"][11] += 1

    if workflow_complexity["cyclomatic_complexity"] == 1:
        buckets["cyclomatic_complexity"][1] += 1
    elif workflow_complexity["cyclomatic_complexity"] == 2:
        buckets["cyclomatic_complexity"][2] += 1
    elif workflow_complexity["cyclomatic_complexity"] >= 3 and workflow_complexity["cyclomatic_complexity"] <= 8:
        buckets["cyclomatic_complexity"][3] += 1

print(buckets)
