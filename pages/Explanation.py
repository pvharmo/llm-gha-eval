import streamlit as st
import json
import pandas as pd
from stqdm import stqdm
from menu import menu
from io import StringIO
# import evaluate
import difflib as dl
import os

from assistant import Assistant

import env

st.set_page_config(
    page_title="Run LLM benchmarks",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

menu()

st.title("🚀 Workflow Explanation")

detailed_description_system_prompt="""
You will be given a github actions workflow and you will have to explain what it does. Add enough details so the workflow can be reproduced only from this description.
Split your description in these sections if they are present in the workflow: Trigger, Jobs with their steps, Environment variables, Secrets, Cache, Matrix, Services, Timeout and permissions.
Use bullet points to describe elements of each section. do not include sections if they are not in the workflow.
"""

medium_description_system_prompt="""
You will be given a github actions workflow and you will have to explain what it does. Add enough details so the workflow can be reproduced only from this description.
Do not include sections if they are not in the workflow.
"""

brief_description_system_prompt="""
You will be given a github actions workflow and you will have to explain what it does in two sentences. Add only the most important information such as the jobs to run and the events to trigger the workflow.
Do not include sections if they are not in the workflow.
"""

workflows = []

for owner in stqdm(os.listdir(env.repository_directories)):
    for repo_name in os.listdir(env.repository_directories + "/" + owner):
        directory = env.repository_directories + "/" + owner + "/" + repo_name
        for workflow_file in os.listdir(directory + "/workflows"):
            workflows.append({
                "owner": owner,
                "repo_name": repo_name,
                "workflow_file": workflow_file,
                "directory": directory
            })

with st.form("my_form"):
    submit = st.form_submit_button(label="Submit")

if submit:
    for workflow_infos in stqdm(workflows):
        if workflow_infos["owner"] != "vercel":
                continue
        assistant = Assistant(model="Qwen/Qwen2-72B-Instruct", system_prompt=detailed_description_system_prompt)

        with st.expander(workflow_infos["owner"] + "/" + workflow_infos["repo_name"] + "/" + workflow_infos["workflow_file"], expanded=True):
            with open(workflow_infos["directory"] + "/workflows/" + workflow_infos["workflow_file"]) as file:
                workflow = file.read()

            description = assistant.run(workflow)

            os.makedirs(workflow_infos["directory"] + "/detailed_descriptions", exist_ok=True)
            with open(workflow_infos["directory"] + "/detailed_descriptions/" + workflow_infos["workflow_file"] + ".md", "w") as file:
                file.write(description)

            # # st.write("## Evaluation")
            # # bleu = evaluate.load("bleu")
            # # st.write(bleu.compute(references=[content], predictions=[generated_workflow]))

            # # col1, col2 = st.columns(2)

            # # with col1:
            # #     st.write("## Generated description")
            # #     generated_workflow_description = assistant_explainer.run(generated_workflow, stream=True)
            # #     generated_workflow_description = st.write_stream(generated_workflow_description)

            # # with col2:
            # #     st.write("## Original description")
            # #     st.write(original_workflow_description)

            # # st.write(bleu.compute(references=[original_workflow_description], predictions=[generated_workflow_description]))

            # assistant_evaluator = Assistant(
            #     llm=model,
            #     description=f"""
            #     You will be given a github actions workflow and you will rate how well it follows the description on a scale from one to five.
            #     - Give a score of one if the workflow does not follow the description at all.
            #     - Give a score of two if the workflow has one element that follows the description.
            #     - Give a score of three if the workflow follows the goal of the description but does not follow any more elements of the description.
            #     - Give a score of four if the workflow follows the goal of the description and some of the details.
            #     - Give a score of five if the workflow follows the goal of the description and all of the details.
            #     Before giving a score, you must explain your reasoning in detail, then, based on your explanation, give a score. Wrap the score in braces.
            #     """,
            #     run_id=None,
            # )

            # st.write("### Without example")
            # response = assistant_evaluator.run(f'Here is the description:\n{original_workflow_description}\n\nHere is a generated GitHub Actions workflow:\n{generated_workflow}', stream=True)
            # st.write_stream(response)
            # # st.write("### With example")
            # # response = assistant_evaluator.run(f'Here is the example of a GitHub Actions workflow that would receive a score of five:\n{content}\n\nHere is the description:\n{original_workflow_description}\n\nHere is a generated GitHub Actions workflow:\n{generated_workflow}', stream=True)
            # # st.write_stream(response)
