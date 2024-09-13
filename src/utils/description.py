from utils.count import count
from utils.parse_trigger import parse_workflow
from utils.parse_steps import step_names, step_names_with_details
from utils.parse_jobs import parse_workflow_jobs
import streamlit as st
import yaml
import json
import os
import polars as pl

def generate_description(workflow: dict, main_language):

    if not isinstance(workflow, dict) or "name" not in workflow.keys() or "jobs" not in workflow.keys():
        print(workflow)
        print("invalid workflow dictionnary")
        return None

    valid_workflow = True
    for job in workflow["jobs"]:
        if "steps" not in workflow["jobs"][job].keys():
            valid_workflow = False
            break
        for step in workflow["jobs"][job]["steps"]:
            has_name = "name" in step.keys()
            is_checkout_action = "uses" in step.keys() and step["uses"].startswith("actions/checkout@")
            if not (has_name or is_checkout_action):
                valid_workflow = False
                break

    if not valid_workflow:
        print("Workflow does not have names on all steps")
        return None

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
    job_ids = f' The workflow has {count[len(workflow["jobs"])] if len(workflow["jobs"]) < 100 else "over one hundred"} job{"s" if len(workflow["jobs"]) > 1 else ""}.'
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
