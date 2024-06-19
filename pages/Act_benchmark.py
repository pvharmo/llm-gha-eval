import streamlit as st
from menu import menu
import regex as re
import subprocess

from assistant import Assistant
import env

st.set_page_config(
    page_title="Act benchmark",
    page_icon="📏",
    layout="wide",
    initial_sidebar_state="expanded",
)

menu()

st.title("📏 Act benchmark")

benchmark_configs = [
    ["1", "Create a minimal workflow to run tests on a push event for a node project."],
]

def run_benchmark():
    st.write("Running benchmark...")

    for location, prompt in benchmark_configs:
        assistant = Assistant(
            temperature=0.1,
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            description="""
You are an assistant that will be tasked to help a user create a Github Action workflow.
As a first step you will generate a description of a workflow that can be used to create the workflow yaml file.
Only give the description of the workflow. Do not include the yaml file.
Split the description in mutliple sections. The first section is about events that will trigger the workflow.
The second section is for the jobs. Give information about global options for each jobs, then give the steps for each job.
The next sections should only be present if they are specified by the user, don't include them if they are empty. These sections are: Environment variables, Secrets, Cache, Matrix, Services, Timeout and permissions.

Ask the user if the description is accurate and if they want to generate the yaml file.

If the user agrees to generate the yaml file, you will be tasked to generate the yaml file based on the description.
"""
        )

        with st.expander(location, expanded=True):
            st.write(prompt)
            x = assistant.run(prompt)
            st.write(x)

            st.write("yes")
            response = assistant.run("yes")
            st.write(response)

            workflow = re.findall(r'(?<=```yaml)([\s\S]*?)(?=```)', response)[0]
            st.write("# Workflow")
            st.code(workflow)

            with open(f"sandbox/{location}/.github/workflows/test.yml", 'w') as file:
                file.write(workflow)

            output = subprocess.run(["act", "--json"], text=True, check=False, capture_output=True, cwd=f"sandbox/{location}")

            st.write("# Act output")
            st.code(output.stdout)
            st.code(output.stderr)

            success = output.returncode == 0

            st.write(f"{location}: {success}")

    st.write("Done!")

st.button("Run benchmark", on_click=lambda: run_benchmark())