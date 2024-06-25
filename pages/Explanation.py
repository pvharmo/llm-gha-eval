import streamlit as st
import json
import pandas as pd
from stqdm import stqdm
from menu import menu
from io import StringIO
# import evaluate
import difflib as dl

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

assistant_explainer = Assistant(
    model="meta-llama/Meta-Llama-3-70B-Instruct",
    system_prompt="""
        You will be given a github actions workflow and you will have to explain what it does. Add enough details so the workflow can be reproduced only from this description.
        Split your description in these sections if they are present in the workflow: Trigger, Jobs with their steps, Environment variables, Secrets, Cache, Matrix, Services, Timeout and permissions.
        Use bullet points to describe elements of each section. do not include sections if they are not in the workflow.
        """,
    # description="""
    #     You will be given a github actions workflow and you will have to explain what it does. Add enough details so the workflow can be reproduced only from this description.
    #     """,
)

uploaded_files = st.file_uploader("Upload a github actions workflow", type=["yml","yaml"], accept_multiple_files=True)

for uploaded_file in uploaded_files:
    for i in range(1):
        with st.expander(uploaded_file.name + " - " + str(i), expanded=True):
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            content = stringio.getvalue()
            original_workflow_description = assistant_explainer.run(content)
            st.write(original_workflow_description)

            print(original_workflow_description)

            # assistant_modifier = Assistant(
            #     llm=model,
            #     description="You will be given a description of a github actions workflow. Give the best prompt which can be fed to a llm to generate the workflow yaml file Add enough details in the prompt to be able to generate the exact workflow from the description. Answer only with the prompt. Do not say Here's a prompt that can be used to generate the workflow yaml file. Just give the prompt.",
            #     run_id=None,
            # )

            # st.write("## Generated prompt")

            # generated_prompt = assistant_modifier.run(original_workflow_description, stream=True)
            # generated_prompt = st.write_stream(generated_prompt)

            # assistant_generator = Assistant(
            #     llm=model,
            #     description="You will be given a description of a GitHub Action workflow file. You will have to generate the workflow file based on the description. Answer only with the file code. Do not add any additional information.",
            #     run_id=None,
            # )

            # col1, col2 = st.columns(2)

            # with col1:
            #     st.write("## Generated")
            #     generated_workflow = assistant_generator.run(original_workflow_description, stream=False)
            #     st.code(generated_workflow)

            # with col2:
            #     st.write("## Original")
            #     st.code(content)

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
