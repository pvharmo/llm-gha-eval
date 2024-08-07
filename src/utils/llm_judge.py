from assistant import Assistant
import re

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
