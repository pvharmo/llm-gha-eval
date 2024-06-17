import streamlit as st
from menu import menu

from assistant import Assistant
import env

st.set_page_config(
    page_title="Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

menu()

st.title("🤖 Assitant")

if st.session_state.get("messages") is None:
    st.session_state["messages"] = [{"role": "assistant", "content": "Welcome to the GHA Assistant! What kind of workflow do you need today?"}]

assistant = Assistant(
    model="meta-llama/Meta-Llama-3-70B-Instruct",
    description="""
        You are an assistant that will be tasked to help a user create a Github Action workflow.
        As a first step you will generate a description of a workflow that can be used to create the workflow yaml file.
        Only give the description of the workflow. Do not include the yaml file.
        Split the description in mutliple sections. The first section is about events that will trigger the workflow.
        The second section is for the jobs. Give information about global options for each jobs, then give the steps for each job.
        The next sections should only be present if they are specified by the user, don't include them if they are empty. These sections are: Environment variables, Secrets, Cache, Matrix, Services, Timeout and permissions.

        Ask the user if the description is accurate and if they want to generate the yaml file.

        If the user agrees to generate the yaml file, you will be tasked to generate the yaml file based on the description.
    """,
    messages = st.session_state["messages"]
)

for message in st.session_state.messages:
    if message["role"] == "system":
        continue
    chat_msg = st.chat_message(message["role"])
    chat_msg.write(message["content"])

question = st.chat_input("Describe the workflow you need here...")
if question:
    chat_msg = st.chat_message("user")
    chat_msg.write(question)
    assistant_response = assistant.run(question, stream=True)

    with st.chat_message("assistant"):
        with st.spinner("Working..."):
            response = ""
            resp_container = st.empty()
            for delta in assistant.run(question, stream=True):
                response += delta  # type: ignore
                resp_container.markdown(response)

st.session_state.messages = assistant.get_messages()
