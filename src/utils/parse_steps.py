from utils.count import count
from utils.parse_trigger import parse_env_variables
from typing import Dict, Any

def step_names(workflow):
    step_names = ""
    for i, job_name in enumerate(workflow["jobs"]):
        job = workflow["jobs"][job_name]

        step_names = f' The job {job_name} has {count[len(job["steps"])]} step{"s" if len(job["steps"]) > 1 else ""}.'
        if len(job["steps"]) == 1:
            step_names += f' The step is named "{job["steps"][0]["name"]}".'
        else:
            for i, step in enumerate(job["steps"]):
                if "name" in step:
                    step_names += f' The {i+1}{"st" if i == 0 else "nd" if i == 1 else "rd" if i == 2 else "th"} step is named "{step["name"]}".'
                elif "uses" in step and step["uses"].startswith("actions/checkout@"):
                    step_names += f' The {i+1}{"st" if i == 0 else "nd" if i == 1 else "rd" if i == 2 else "th"} step is a "Checkout code".'

    return step_names

# def step_names_with_details(workflow):
#     step_names = ""
#     for i, job_name in enumerate(workflow["jobs"]):
#         job = workflow["jobs"][job_name]

#         step_names = f' The job {job_name} has {count[len(job["steps"])]} step{"s" if len(job["steps"]) > 1 else ""}.'
#         if len(job["steps"]) == 1:
#             step_names += f' The step is named "{job["steps"][0]["name"]}".'
#         else:
#             for i, step in enumerate(job["steps"]):
#                 step_names += f' The {i+1}{"st" if i == 0 else "nd" if i == 1 else "rd" if i == 2 else "th"} step is named "{step["name"]}".'
#     return step_names
def step_names_with_details(workflow):
    output = ""
    for job_id, job in workflow['jobs'].items():
        steps = job.get('steps', [])

        output += f'The job "{job_id}" has {count[len(job["steps"])]} step{"s" if len(steps) > 1 else ""}. '
        for i, step in enumerate(steps, 1):
            output += parse_step(step, i) + ' '
    return output

def parse_step(step: Dict[str, Any], step_number: int) -> str:
    step_info = f"The {ordinal(step_number)} step "

    if 'name' in step:
        step_info += f'is named "{step["name"]}". '
    else:
        step_info += 'is unnamed. '

    if 'uses' in step:
        action, tag = step['uses'].split('@') if '@' in step['uses'] else (step['uses'], None)
        step_info += f'This step runs action "{action}"'
        if tag:
            step_info += f' tagged as {tag}'
        step_info += '. '

    if 'run' in step:
        step_info += f'This step runs a script: "{step["run"]}". '

    if 'with' in step:
        step_info += f"The step defines {len(step['with'])} input parameter{'s' if len(step['with']) > 1 else ''} for the action: "
        params = [f'"{k}" is set to "{v}"' for k, v in step['with'].items()]
        step_info += ' and '.join(params) + '. '

    for key in ['if', 'working-directory', 'shell', 'env', 'continue-on-error', 'timeout-minutes']:
        if key in step:
            step_info += f'The step has {key} set to "{step[key]}". '

    return step_info.strip()

def ordinal(n: int) -> str:
    suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    return str(n) + suffix

# def step_names_with_details(workflow_yaml: str) -> str:


#     def ordinal(n: int) -> str:
#         suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
#         if 11 <= (n % 100) <= 13:
#             suffix = 'th'
#         return str(n) + suffix

#     workflow = yaml.safe_load(workflow_yaml)

#     output = ""
#     for job_id, job in workflow['jobs'].items():
#         steps = job.get('steps', [])
#         output += f'The job "{job_id}" has {len(steps)} step{"s" if len(steps) > 1 else ""}. '

#         for i, step in enumerate(steps, 1):
#             output += parse_step(step, i) + ' '

#     return output.strip()
