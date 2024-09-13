from tqdm import tqdm
from utils.description import generate_description
from utils.analysis.action_validation import action_validator
import yaml
import json
import polars as pl

import env

workflows = pl.read_csv(env.dataset_file)
workflows = workflows.select(pl.col(
    "workflow_name",
    "workflow_path",
    "workflow_yaml",
    "_id",
    "repo_metadata.language",
    "repo_metadata.default_branch",
    "repo_metadata.full_name",
    "repo_metadata.id",
)).rename({
    "_id": "id",
    "repo_metadata.language": "language",
    "repo_metadata.default_branch": "default_branch",
    "repo_metadata.full_name": "full_name",
    "repo_metadata.id": "repo_id",
})

descriptions = []

for workflow_infos in workflows.iter_rows(named=True):
    validation = action_validator(workflow_infos["workflow_yaml"])
    if validation is None:
        continue
    print(validation["output"])
    valid = True
    for output in validation["output"]:
        if output["kind"] == "syntax-check":
            valid = False
            break
    if not valid:
        print("Syntax error in " + workflow_infos["full_name"] + " -- " + workflow_infos["workflow_name"])
        continue
    try:
        workflow = yaml.safe_load(workflow_infos["workflow_yaml"])
    except:
        continue

    print("----------------------------------------------------------------------------")
    print(workflow_infos["workflow_yaml"])

    description = generate_description(workflow, workflow_infos["language"])

    if description is None:
        continue
    description["repo_id"] = workflow_infos["repo_id"]
    description["id"] = workflow_infos["id"]
    description["yaml"] = workflow_infos["workflow_yaml"]
    descriptions.append(description)
    print("Generated description for " + workflow_infos["full_name"] + " -- " + workflow_infos["workflow_name"])

json.dump(descriptions, open(env.descriptions_file, "w"), indent=4)

prompts = []

for description in descriptions:
    prompts.append({
        "id": description["id"],
        "yaml": description["yaml"],
        "prompt1": description["workflow_level_infos"] + description["event_triggers"] + description["job_ids"],
        "prompt2": description["workflow_level_infos"] + description["event_triggers"] + description["job_ids"] + description["step_names"],
        "prompt3": description["workflow_level_infos"] + description["event_triggers"] + description["job_ids"] + description["step_names"] + description["dependencies"],
        "prompt4": description["workflow_level_infos"] + description["event_triggers"] + description["job_level_infos"] + description["step_names"],
        "prompt5": description["workflow_level_infos"] + description["event_triggers"] + description["job_level_infos"] + description["step_level_infos"],
    })

json.dump(prompts, open(env.prompts_file, "w"), indent=4)