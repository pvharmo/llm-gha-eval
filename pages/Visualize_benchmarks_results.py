import streamlit as st
import json
import os
from os.path import isfile, join
from menu import menu

st.set_page_config(
    page_title="Visualize benchmarks",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

menu()

st.title("📊 Visualize benchmarks")

files = [f[:-5] for f in os.listdir("./results") if isfile(join("./results", f)) and f.endswith(".json")]

model_name = st.selectbox("Select a model", files)

results = json.loads(open(f"results/{model_name}.json").read())

total_success = 0
count = 0
for result in results:
    count += 1
    for test_result in result["test results"]:
        if test_result["valid"] == True:
            total_success += 1
            break

print(total_success / count)

st.write("## Results")

for result in results:
    st.write("### Prompt")
    st.write(result["prompt"])
    st.write("### System Prompt")
    st.write(result["system_prompt"])
    st.write("### Response")
    with st.expander("Show"):
        st.write(result["response"])
    st.write("### Test Results")
    for test_result in result["test results"]:
        st.write("#### Valid")
        st.write(test_result["valid"])
        st.write("#### Analysis output")
        with st.expander("Show"):
            st.code(test_result["result_output"])
        st.write("#### Generated code")
        with st.expander("Show"):
            st.code(test_result["code"], language="yaml")
