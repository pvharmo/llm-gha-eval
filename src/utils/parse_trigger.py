import streamlit as st
from typing import Dict, Any, Union

def parse_workflow(workflow: dict):
    triggers = workflow.get(True, {})
    env = workflow.get('env', {})

    trigger_descriptions = []
    if isinstance(triggers, str):
        trigger_descriptions.append(parse_trigger(triggers))
    elif isinstance(triggers, dict):
        trigger_descriptions.extend([parse_trigger({k: v}) for k, v in triggers.items() if k != 'on'])
    else:
        return "Invalid workflow format."

    description = " Additionally, ".join(trigger_descriptions)
    description += parse_env_variables(env)

    permissions = workflow.get('permissions', None)
    if permissions is not None:
        description += parse_permissions(permissions)

    concurrency = workflow.get('concurrency', None)
    if concurrency is not None:
        description += parse_concurrency(concurrency)

    return description

def parse_trigger(trigger):
    if isinstance(trigger, str):
        return f"The workflow would run on any {trigger} event."
    elif isinstance(trigger, dict):
        event_type = list(trigger.keys())[0]
        event_config = trigger[event_type]
        if event_config is None:
            return f"The workflow would run on any {event_type} event."
        if event_type == "push":
            return parse_push_event(event_config)
        elif event_type == "pull_request":
            return parse_pull_request_event(event_config)
        elif event_type == "schedule":
            return parse_schedule_event(event_config)
        elif event_type == "workflow_dispatch":
            return parse_workflow_dispatch_event(event_config)
        elif event_type == "workflow_run":
            return parse_workflow_run_event(event_config)
        elif event_type == "workflow_call":
            return parse_workflow_call_event(event_config)
        else:
            return f"The workflow would run on a {event_type} event with specific configurations."
    else:
        return "Invalid trigger format."

def parse_push_event(event_config):
    conditions = ""
    if "branches" in event_config:
        if event_config["branches"] is None:
            conditions += "any branches"
        else:
            conditions += f"branches {format_list(event_config['branches'])}"
    if "tags" in event_config:
        if "branches" in event_config:
            conditions += " and "
        if event_config["tags"] is None:
            conditions += "any tags"
        else:
            conditions += f"tags {format_list(event_config['tags'])}"
    if "branches" not in event_config and "branches-ignore" in event_config:
        conditions += " any branches"
    if "tags" not in event_config and "tags-ignore" in event_config:
        if "branches" in event_config:
            conditions += " and"
        conditions += " any tags"
    if "branches-ignore" in event_config and event_config["branches-ignore"] is not None:
        ignored_branches = event_config["branches-ignore"]
        conditions += f" but ignores branches {format_list(ignored_branches)}"
    if "tags-ignore" in event_config and event_config["tags-ignore"] is not None:
        if "branches-ignore" in event_config:
            conditions += " and"
        else:
            conditions += " but ignores"
        ignored_tags = event_config["tags-ignore"]
        conditions += f" tags {format_list(ignored_tags)}"

    # Add path conditions
    path_conditions = parse_path_conditions(event_config, "branches" in event_config or "tags" in event_config or "branches-ignore" in event_config or "tags-ignore" in event_config)
    if path_conditions:
        if conditions:
            conditions += "."
        conditions += path_conditions

    if conditions:
        return f"The workflow would run on a push event to {conditions}."
    else:
        return "The workflow would run on any push event."

def parse_pull_request_event(event_config):
    conditions = ""
    if "types" in event_config:
        pr_types = event_config["types"]
        conditions += f" when a pull request is {format_list(pr_types, 'or')}"
    if "branches" in event_config:
        conditions += f" to branches {format_list(event_config['branches'])}"
    if "branches-ignore" in event_config:
        ignored_branches = event_config["branches-ignore"]
        if "branches" in event_config:
            conditions += f" but ignores branches {format_list(ignored_branches)}"
        else:
            conditions += f" to any branches except {format_list(ignored_branches)}"

    if "types" in event_config or "branches" in event_config or "branches-ignore" in event_config:
        conditions += "."

    # Add path conditions
    path_conditions = parse_path_conditions(event_config, "types" in event_config or "branches" in event_config or "branches-ignore" in event_config)
    if path_conditions:
        conditions += path_conditions

    if conditions:
        return f"The workflow would run {conditions}"
    else:
        return "The workflow would run on any pull request event."

def parse_schedule_event(event_config):
    if isinstance(event_config, list):
        cron_expressions = [schedule['cron'] for schedule in event_config]
        return f"The workflow would run on a schedule defined by the following cron expression(s): {', '.join(cron_expressions)}."
    else:
        return "Invalid schedule event format."

def format_list(items, conjunction="or"):
    if len(items) == 1:
        return f'"{items[0]}"'
    elif len(items) == 2:
        return f'"{items[0]}" {conjunction} "{items[1]}"'
    else:
        return ", ".join(f'"{item}"' for item in items[:-1]) + f', {conjunction} "{items[-1]}"'

def parse_workflow_dispatch_event(event_config):
    description = "The workflow can be manually triggered"

    if "inputs" in event_config:
        input_descriptions = []
        for input_name, input_config in event_config["inputs"].items():
            input_desc = f"'{input_name}' (type: {input_config.get('type', 'string')}"
            if input_config.get('required', False):
                input_desc += ", required"
            else:
                input_desc += ", optional"

            if input_config.get('type', 'string') == 'choice':
                input_desc += f", choices: {format_list(input_config['options'])}"
            input_desc += ")"
            input_descriptions.append(input_desc)

        if input_descriptions:
            description += f" with the following inputs: {', '.join(input_descriptions)}"

    return description + "."

def parse_path_conditions(event_config, also: bool):
    path_conditions = []
    if "paths" in event_config:
        path_conditions.append(f" It {'also' if also else ''} triggers on changes that are made to files matching {format_list(event_config['paths'])}")
    if "paths-ignore" in event_config:
        if "paths" in event_config:
            path_conditions.append(f"ignoring changes to files matching {format_list(event_config['paths-ignore'])}")
        else:
            path_conditions.append(f" It {'also' if also else ''} triggers on changes that are made to any files except those matching {format_list(event_config['paths-ignore'])}")

    return " and ".join(path_conditions)

def parse_env_variables(env: Dict[str, str]) -> str:
    if not env:
        return ""

    env_vars = [f"'{key}' (value: '{value}')" for key, value in env.items()]
    if len(env_vars) == 1:
        return f"The workflow sets the environment variable {env_vars[0]}."
    elif len(env_vars) == 2:
        return f"The workflow sets the environment variables {env_vars[0]} and {env_vars[1]}."
    else:
        return f"The workflow sets the following environment variables: {', '.join(env_vars[:-1])}, and {env_vars[-1]}."

def parse_permissions(permissions: Union[str, Dict[str, str]]) -> str:
    if isinstance(permissions, str):
        return f" The workflow sets overall permissions to '{permissions}'."
    elif isinstance(permissions, dict):
        perm_list = [f"'{key}': {value}" for key, value in permissions.items()]
        if len(perm_list) == 0:
            return f" The workflow sets overall permissions to default."
        if len(perm_list) == 1:
            return f" The workflow sets the following permission: {perm_list[0]}."
        elif len(perm_list) == 2:
            return f" The workflow sets the following permissions: {perm_list[0]} and {perm_list[1]}."
        else:
            return f" The workflow sets the following permissions: {', '.join(perm_list[:-1])}, and {perm_list[-1]}."
    else:
        return ""

def parse_concurrency(concurrency: Union[str, Dict[str, Any]]) -> str:
    if isinstance(concurrency, str):
        return f" The workflow uses concurrency group '{concurrency}'."
    elif isinstance(concurrency, dict):
        group = concurrency.get('group', '')
        cancel_in_progress = concurrency.get('cancel-in-progress', False)
        result = f" The workflow uses concurrency group '{group}'"
        if cancel_in_progress:
            result += " and will cancel any in-progress job or run in this group."
        else:
            result += "."
        return result
    return ""

def parse_defaults(defaults: Dict[str, Any]) -> str:
    result = ""
    if 'run' in defaults:
        run_defaults = defaults['run']
        if 'shell' in run_defaults:
            result += f" The default shell is '{run_defaults['shell']}'."
        if 'working-directory' in run_defaults:
            result += f" The default working directory is '{run_defaults['working-directory']}'."
    return result

def parse_workflow_run_event(event_config):
    description = "The workflow would run after another workflow's job"

    if "workflows" in event_config:
        workflows = event_config["workflows"]
        description += f" in the following workflow(s): {format_list(workflows)}"

    if "types" in event_config:
        types = event_config["types"]
        description += f" when the other workflow's job is {format_list(types, 'or')}"

    if "branches" in event_config:
        branches = event_config["branches"]
        description += f" on branches {format_list(branches)}"

    if "branches-ignore" in event_config:
        ignored_branches = event_config["branches-ignore"]
        if "branches" in event_config:
            description += f" but ignores branches {format_list(ignored_branches)}"
        else:
            description += f" on any branches except {format_list(ignored_branches)}"

    return description + "."

def parse_workflow_call_event(event_config):
    description = "The workflow can be called by another workflow"

    if "inputs" in event_config:
        input_descriptions = []
        for input_name, input_config in event_config["inputs"].items():
            input_desc = f"'{input_name}' (type: {input_config.get('type', 'string')}"
            if input_config.get('required', False):
                input_desc += ", required"
            else:
                input_desc += ", optional"
            if 'default' in input_config:
                input_desc += f", default: '{input_config['default']}'"
            input_desc += ")"
            input_descriptions.append(input_desc)

        if len(input_descriptions) > 0:
            description += f" with the following inputs: {', '.join(input_descriptions)}"

    if "secrets" in event_config:
        secret_descriptions = []
        for secret_name, secret_config in event_config["secrets"].items():
            secret_desc = f"'{secret_name}'"
            if secret_config.get('required', False):
                secret_desc += " (required)"
            else:
                secret_desc += " (optional)"
            secret_descriptions.append(secret_desc)

        if secret_descriptions:
            description += f" and accepts the following secrets: {', '.join(secret_descriptions)}"

    return description + "."
