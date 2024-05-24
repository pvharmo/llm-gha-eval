import streamlit as st
from menu import menu

from phi.assistant.assistant import Assistant
from phi.llm.ollama.chat import Ollama
from phi.llm.openai.like import OpenAILike

from assistants.assistant import assistant

st.set_page_config(
    page_title="Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

menu()

st.title("🤖 Assitant")

if "messages" not in st.session_state:
    st.session_state.messages = []

st.button("Reset", on_click=lambda: st.session_state.messages.clear())

message = st.chat_message("assistant")
message.write("Welcome to the GHA Assistant! What kind of workflow do you need today?")

for message in st.session_state.messages:
    chat_msg = st.chat_message(message["role"])
    chat_msg.write(message["content"])

question = st.chat_input("Describe the workflow you need here...")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    chat_msg = st.chat_message("user")
    chat_msg.write(question)
    assistant_response = assistant.run(question, stream=True)

    with st.chat_message("assistant"):
        with st.spinner("Working..."):
            response = ""
            resp_container = st.empty()
            for delta in assistant.run(question):
                response += delta  # type: ignore
                resp_container.markdown(response)

    placeholder = st.empty()
    message_streamed = placeholder.write_stream(assistant_response)
    st.session_state.messages.append({"role": "assistant", "content": message_streamed})
    placeholder.empty()
    st.chat_message("assistant").write(message_streamed)