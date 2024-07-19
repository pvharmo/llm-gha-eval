from utils.count import count
from utils.parse_trigger import parse_workflow
from utils.parse_steps import step_names, step_names_with_details
from utils.parse_jobs import parse_workflow_jobs
import streamlit as st
import yaml
import json
import os

def prepare_workflow(workflow_infos):
    directory = workflow_infos["directory"]
    workflow_file = workflow_infos["workflow_file"]

    with open(directory + "/workflows/" + workflow_file) as file:
        yaml_content = file.read()

    # with open("./sandbox/test.yml") as file:
    #     yaml_content = file.read()

    try:
        workflow = yaml.safe_load(yaml_content)
    except:
        return

    if not isinstance(workflow, dict):
        return

    # try:
    #     if os.path.exists(directory + "/detailed_descriptions/" + workflow_file + ".md"):
    #         continue
    # except:
    #     continue

    try:
        with open(directory + "/properties.json", 'r') as file:
            metadata = json.load(file)
    except:
        return

    print("generating description for " + workflow_infos["owner"] + "/" + workflow_infos["repo_name"] + "/" + workflow_file)
    description = generate_description(workflow, metadata)

    if description is None:
        return

    print("# " + workflow_infos["owner"] + "/" + workflow_infos["repo_name"] + " - " + workflow_file)

    if not os.path.exists(directory + "/generated_descriptions"):
        os.makedirs(directory + "/generated_descriptions")

    for key, value in description.items():
        with open(directory + "/generated_descriptions/" + key + "_" + workflow_file + ".txt", "w") as file:
            file.write(value)

def generate_description(workflow: dict, metadata):
    valid_workflow = True

    if not isinstance(workflow, dict) or "name" not in workflow.keys() or "jobs" not in workflow.keys():
        return

    for job in workflow["jobs"]:
        if "steps" not in workflow["jobs"][job].keys():
            valid_workflow = False
            break
        for step in workflow["jobs"][job]["steps"]:
            if "name" not in step.keys():
                valid_workflow = False
                break
                break

    if not valid_workflow:
        return

    languages = metadata['languages']

    main_language = max(languages, key=languages.get)

    return {
        "workflow_level_infos": workflow_level_infos(workflow, main_language),
        "event_triggers": parse_workflow(workflow),
        "job_ids": job_ids(workflow),
        "job_level_infos": parse_workflow_jobs(workflow["jobs"]),
        "step_names": step_names(workflow),
        "step_level_infos": step_names_with_details(workflow),
        "dependencies": dependencies(workflow)
    }

def workflow_level_infos(workflow, main_language):
    return f'Generate a GitHub Workflow named "{workflow["name"]}" for a GitHub repository whose main programming language is {main_language}.'

def job_ids(workflow):
    job_ids = f' The workflow has {count[len(workflow["jobs"])]} job{"s" if len(workflow["jobs"]) > 1 else ""}.'
    for i, job_name in enumerate(workflow["jobs"]):
        job_ids += f' The job id of the {i+1}{"st" if i == 0 else "nd" if i == 1 else "rd" if i == 2 else "th"} job is "{job_name}".'
    return job_ids

def dependencies(workflow):
    dependencies = " Here are some Github Actions that might be used in the workflow:"
    has_actions = False
    for i, job_name in enumerate(workflow["jobs"]):
        for i, step in enumerate(workflow["jobs"][job_name]["steps"]):
            if "uses" in step.keys():
                has_actions = True
                action = step["uses"].split("@")
                if len(action) == 1:
                    dependencies += f' {action[0]}'
                else:
                    dependencies += f' {action[1]} version of {action[0]}'
                if i < len(workflow["jobs"][job_name]["steps"]) - 1:
                    dependencies += ","
                else:
                    dependencies += "."
    if has_actions:
        return dependencies
    else:
        return " No actions are used in the workflow."
