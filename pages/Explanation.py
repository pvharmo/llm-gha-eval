import streamlit as st
import json
import pandas as pd
from stqdm import stqdm
from menu import menu
from io import StringIO

from phi.assistant.assistant import Assistant
from phi.llm.ollama.chat import Ollama
from phi.llm.openai.like import OpenAILike

import env
from utils import build_promt, evaluate_results

st.set_page_config(
    page_title="Run LLM benchmarks",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

menu()

st.title("🚀 Workflow Explanation")

model = Ollama(model="llama3")

assistant = Assistant(
    llm=model,
    description="You will be given a github actions workflow and you will have to explane in less than three sentences what it does.",
    run_id=None
)

uploaded_file = st.file_uploader("Upload a github actions workflow", type=["yml"], accept_multiple_files=False)

if uploaded_file is not None:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    content = stringio.getvalue()
    response = assistant.run(content, stream=False)
    st.write(response)