import os
from tqdm import tqdm
import polars as pl

import env
from utils.analysis.action_validation import action_validator

workflows = pl.read_csv("../dataset/intermediate/workflows_100_stargazers_plus.csv", truncate_ragged_lines=True, batch_size=1000)
count = workflows.height

print(f"Total number of workflows: {count}")

valid_workflows = []

wf_file = "../tmp/workflow.yaml"

nb_workflows = 0
for workflow_infos in tqdm(workflows.iter_rows(named=True), total=count):
    yaml_content = workflow_infos['workflow_yaml']
    validation = action_validator(yaml_content)
    if validation is None:
        continue
    if validation["valid"] is True or any(item.get('kind') == 'syntax-check' for item in validation['output']):
        valid_workflows.append(workflow_infos)
        nb_workflows += 1

print(f"Number of valid workflows: {len(valid_workflows)}")
pl.DataFrame(valid_workflows, infer_schema_length=41003).write_csv("../dataset/intermediate/step1_valid_workflows.csv")
