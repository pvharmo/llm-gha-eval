from tqdm import tqdm
from utils.description import generate_description
from utils.analysis.action_validation import action_validator
import yaml
import json
import polars as pl

import env

ids = [
    "63c5c81ac779603593ca4a0a",
    "63c4957c7843b61269a07e82",
    "63c494547843b61269a0088c",
    "63c49ceb33b087f6bde55eee",
    "63c498a6b008460c1df228cb",
    "63c496f433b087f6bde2f6b5",
    "63c494718052faa2781ab3ad",
    "63c4962d6fc19abdf9c9a59d",
    "63c49e98517fc08c1ef04736",
    "63c497781e33648075781305",
    "63c497d26fc19abdf9ca518f",
    "63c4a074736e7f0ed8c74c8d",
    "63c49aa61e336480757959ec",
    "63c499a1cbc73931bb18ee43",
    "63c493f78052faa2781a836b",
    "63c496941e3364807577b88d",
    "63c49ba0517fc08c1eef1895",
    "63c4a03d517fc08c1ef0eae2",
    "63c49b7f1e3364807579ae92",
    "63c5c692ac4f2678a5bd8deb",
]

workflows = pl.read_csv(env.dataset_file, truncate_ragged_lines=True, batch_size=1000)
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
}).filter(pl.col("id").is_in(ids))

descriptions = []

for workflow_infos in tqdm(workflows.iter_rows(named=True)):
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