import re
import subprocess
import yaml
from assistant import Assistant
from deepdiff import DeepDiff
import pprint
import json

def action_validator(workflow):
    results = []
    with open('outputs/test.yml', 'w') as file:
        file.write(workflow)

    output = subprocess.run(["actionlint", "-format", "'{{json .}}'", "outputs/test.yml"], text=True, capture_output=True).stdout

    json_output = json.loads(output[1:-1])

    result = {
        "valid": len(json_output) == 0,
        "output": json_output,
    }
    results.append(result)

    return results

def deepdiff_compare(original, generated):
    # For some reason the yaml parser replaces the key "on" by True
    generated_events = generated[True] if True in generated else yaml.safe_load("{}")
    generated_jobs = generated["jobs"] if "jobs" in generated else yaml.safe_load("{}")
    original_events = original[True] if True in original else yaml.safe_load("{}")
    original_jobs = original["jobs"] if "jobs" in original else yaml.safe_load("{}")

    diff_events = DeepDiff(original_events, generated_events, ignore_order=True, verbose_level=2, get_deep_distance=True)
    diff_jobs = DeepDiff(original_jobs, generated_jobs, ignore_order=True, verbose_level=2, get_deep_distance=True)

    return {
        "events": {
            "stats": diff_events.get_stats(),
            "distance": diff_events["deep_distance"] if "deep_distance" in diff_events else None
        },
        "jobs": {
            "stats": diff_jobs.get_stats(),
            "distance": diff_jobs["deep_distance"] if "deep_distance" in diff_jobs else None
        }
    }

def llm_as_a_judge(response, description, model):
    assistant_evaluator = Assistant(
        model=model,
        # system_prompt="""
        # You will be given two Github Actions workflows.
        # You will have to compare them and score it on their similarity. To do so, you must first split the workflows into events and jobs.
        # you will compare and score events and jobs independently.
        # For the events here is the scale:
        # - Give a score of zero if one of the two workflows has an event that the other does not have.
        # - Give a score of one if both workflows have events but not the same.
        # - Give a score of two if both workflows have the some events that are the same.
        # - Give a score of three if both workflows have the same events but none of the branches are the same.
        # - Give a score of four if both workflows have the same events and some of the branches are the same.
        # - Give a score of five if both workflows have the same events and all of the branches are the same or no branches are specified for both workflows.
        # For the jobs, first explain what each workflow accomplishes, then rate the similarity of the jobs.
        # Here is the scale you must use to rate the similarity of the jobs:
        # - Give a score of zero if the workflows accomplishes completely different tasks.
        # - Give a score of one if both workflows accomplishes different tasks but some steps are the same.
        # - Give a score of two if both workflows accomplishes different tasks but most steps are the same.
        # - Give a score of three if both workflows mostly accomplishes the same tasks but do in different steps or they split the task in different jobs.
        # - Give a score of four if both workflows accomplishes the same tasks with mostly the same jobs but some steps may be slightly different and configurations may be different (such as OS and compiler). If both workflows use a matrix strategy, the matrix can be different.
        # - Give a score of five if both workflows are the accomplishes the same tasks with mostly the same configurations but has some differences.
        # - Give a score of six if both workflows are the same but has some difference in their naming.
        # - Give a score of seven if both workflows are the exact same.

        # Before giving a score, you must explain your reasoning in detail, then, based on your explanationd, give a score. Wrap the scores in double parenthesis and prefix the score with event for the evaluation of events and with jobs for the evaluation of jobs.
        # Here is anexample of how you should format the score: ((event: x)) ((jobs: y)) where x and y are the scores for the events and jobs respectively.
        # """,
        system_prompt="""
            You will be given a github actions workflow and you will rate how well it follows the description on a scale from one to five. Give two scores, one for the events and one for the jobs:
            - Give a score of one if the workflow does not follow the description at all.
            - Give a score of two if the workflow has one element that follows the description.
            - Give a score of three if the workflow follows the goal of the description but does not follow any more elements of the description.
            - Give a score of four if the workflow follows the goal of the description and some of the details.
            - Give a score of five if the workflow follows the goal of the description and all of the details.
            Before giving a score, you must explain your reasoning in detail, then, based on your explanationd, give a score. Wrap the scores in double parenthesis and prefix the score with event for the evaluation of events and with jobs for the evaluation of jobs.
            Here is anexample of how you should format the score: ((event: x)) ((jobs: y)) where x and y are the scores for the events and jobs respectively.
        """
    )

    res = assistant_evaluator.run(f"Here is the description: {description} and here is the workflow: {response}")
    pattern_event = r'\(\(event:\s*(\S+)\)\)'
    pattern_jobs = r'\(\(jobs:\s*(\S+)\)\)'

    events_result = re.search(pattern_event, res)
    jobs_result = re.search(pattern_jobs, res)

    return {
        "response": res,
        "events": int(events_result.group(1)) if events_result else None,
        "jobs": int(jobs_result.group(1)) if jobs_result else None
    }

def actions_comparison(original, generated):
    nb_steps_original = 0
    nb_steps_generated = 0

    original_actions = []
    generated_actions = []


    for job in original["jobs"]:
        if "steps" in original["jobs"][job]:
            for step in original["jobs"][job]["steps"]:
                nb_steps_original += 1
                if "uses" in step:
                    original_actions.append(step["uses"])


    for job in generated["jobs"]:
        if "steps" in generated["jobs"][job]:
            for step in generated["jobs"][job]["steps"]:
                nb_steps_generated += 1
                if "uses" in step:
                    generated_actions.append(step["uses"])

    union = len(set(original_actions).union(generated_actions))
    jaccard_index = len(set(original_actions).intersection(generated_actions)) / union if union > 0 else 0
    # edit_distance_value = edit_distance(original_actions, generated_actions, len(original_actions), len(generated_actions))

    return {
        "jaccard_index": jaccard_index,
        # "edit_distance": edit_distance_value,
        "diff_nb_steps": nb_steps_original - nb_steps_generated,
        "ration_nb_steps": nb_steps_generated / nb_steps_original
    }

# Recusive implementation of the edit distance algorithm
def edit_distance(arr1, arr2, m, n):
    if m == 0:
        return n

    if n == 0:
        return m

    if arr1[m-1] == arr2[n-1]:
        return edit_distance(arr1, arr2, m-1, n-1)

    return 1 + min(
        edit_distance(arr1, arr2, m, n-1),    # Insert
        edit_distance(arr1, arr2, m-1, n),    # Remove
        edit_distance(arr1, arr2, m-1, n-1)    # Replace
    )
