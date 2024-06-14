import streamlit as st
import json
import pandas as pd
from stqdm import stqdm
from menu import menu
from io import StringIO
import evaluate
import difflib as dl

from phi.assistant.assistant import Assistant
from phi.llm.ollama.chat import Ollama
from phi.llm.openai.like import OpenAILike

import env

st.set_page_config(
    page_title="Workflows comparison",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

menu()

st.title("🚀 Workflow Explanation")

# model = Ollama(model="llama3")
model = OpenAILike(model="meta-llama/Meta-Llama-3-70B-Instruct", api_key=env.api_key, base_url=env.base_url)

assistant_evaluator = Assistant(
    llm=model,
    description="""
    You will be given two Github Actions workflows.
    You will have to compare them and score it on their similarity. To do so, you must first split the workflows into events and jobs.
    you will compare and score events and jobs independently.
    For the events here is the scale:
    - Give a score of zero if one of the two workflows has an event that the other does not have.
    - Give a score of one if both workflows have events but not the same.
    - Give a score of two if both workflows have the some events that are the same.
    - Give a score of three if both workflows have the same events but none of the branches are the same.
    - Give a score of four if both workflows have the same events and some of the branches are the same.
    - Give a score of five if both workflows have the same events and all of the branches are the same or no branches are specified for both workflows.
    For the jobs, first explain what each workflow accomplishes, then rate the similarity of the jobs.
    Here is the scale you must use to rate the similarity of the jobs:
    - Give a score of zero if the workflows accomplishes completely different tasks.
    - Give a score of one if both workflows accomplishes different tasks but some steps are the same.
    - Give a score of two if both workflows accomplishes different tasks but most steps are the same.
    - Give a score of three if both workflows mostly accomplishes the same tasks but do in different steps or they split the task in different jobs.
    - Give a score of four if both workflows accomplishes the same tasks with mostly the same jobs but some steps may be slightly different and configurations may be different (such as OS and compiler). If both workflows use a matrix strategy, the matrix can be different.
    - Give a score of five if both workflows are the accomplishes the same tasks with mostly the same configurations but has some differences.
    - Give a score of six if both workflows are the same but has some difference in their naming.
    - Give a score of seven if both workflows are the exact same.

    Before giving a score, you must explain your reasoning in detail, then, based on your explanation, give a score. Wrap the score in braces.
    """,
    run_id=None,
)

uploaded_file1 = st.file_uploader("First github actions workflow", type=["yml", "yaml"], accept_multiple_files=False)
uploaded_file2 = st.file_uploader("Second github actions workflow", type=["yml", "yaml"], accept_multiple_files=False)

if uploaded_file1 is not None and uploaded_file2 is not None:
    stringio = StringIO(uploaded_file1.getvalue().decode("utf-8"))
    content1 = stringio.getvalue()

    stringio = StringIO(uploaded_file2.getvalue().decode("utf-8"))
    content2 = stringio.getvalue()

    response = assistant_evaluator.run(f'Here is the first GitHub Actions workflow: \n {content1} \n\nHere is the second GitHub Actions workflow: \n {content2}', stream=True)
    response = st.write_stream(response)