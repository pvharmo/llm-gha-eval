import json
import polars as pl
import yaml

from tqdm import tqdm

import argus_components

def extract_dependencies(workflow):
    workflow = yaml.safe_load(workflow)
    actions = []
    workflows_dependencies = []
    for i, job_name in enumerate(workflow["jobs"]):
        if "steps" in workflow["jobs"][job_name].keys():
            for i, step in enumerate(workflow["jobs"][job_name]["steps"]):
                if "uses" in step.keys():
                    action = step["uses"].split("@")
                    actions.append({"version": action[1] if len(action) > 1 else None, "name": action[0]})

    for job_name in workflow["jobs"]:
        if "uses" in workflow["jobs"][job_name].keys():
            wf_dependency = workflow["jobs"][job_name]["uses"].split("@")
            workflows_dependencies.append({"version": wf_dependency[1] if len(wf_dependency) > 1 else None, "name": wf_dependency[0]})

    return {"actions": actions, "workflows": workflows_dependencies}

workflows = pl.read_csv("../dataset/intermediate/step1_valid_workflows.csv", truncate_ragged_lines=True, batch_size=1000)
count = workflows.height
descriptions = []
skip_count = 0
for document in tqdm(workflows.iter_rows(named=True), total=count):
    try:
        repo_lang = document['repo_metadata.language']
        repo_lang = "none" if not repo_lang else repo_lang

        yaml_file = document['workflow_yaml']
        dependencies = extract_dependencies(yaml_file)
        dependencies['vars'] = json.loads(document['ir.CIvars_set'])
        dependencies_str = json.dumps(dependencies)

        workflow = yaml.safe_load(yaml_file)

        skip = False

        for i, job_name in enumerate(workflow["jobs"]):
            if "steps" in workflow["jobs"][job_name].keys():
                for i, step in enumerate(workflow["jobs"][job_name]["steps"]):
                    if not ("name" in step.keys() or ("uses" in step.keys() and "actions/checkout" not in step["uses"])):
                        skip = True
                        break

        if skip:
            skip_count += 1
            continue

        stats = argus_components.Stats(yaml_file, repo_lang, dependencies)
        data = stats.translate_nl()

        document['info'] = data
        descriptions.append({
            "id": document["_id"],
            "yaml": yaml_file,
            "info": data
        })

    except Exception as e:
        print(f"Error {e}")
        pass

print("Skip count:", skip_count)
print("Descriptions count:", len(descriptions))

with open("../dataset/intermediate/step2_workflows_descriptions.json", "w") as f:
    json.dump(descriptions, f)
