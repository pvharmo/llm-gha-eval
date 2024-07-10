import streamlit as st
import json
import os
from os.path import isfile, join
from menu import menu
import sqlite3

st.set_page_config(
    page_title="Visualize benchmarks",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

menu()

st.title("📊 Visualize benchmarks")

con = sqlite3.connect("results/results.db")
cur = con.cursor()

cur.execute("SELECT * FROM runs")
output = cur.fetchall()

runs = [x[0] for x in output]

model_name = st.selectbox("Select a run", runs)

cur.execute("SELECT * FROM runs")
output = cur.fetchall()

for model in output[2]:

    results = json.loads(open(f"results/{model_name}.json").read())

    avg_jaccard = 0
    avg_diff_nb_steps = 0
    avg_events_dist = 0
    avg_jobs_dist = 0
    avg_event_judge = 0
    avg_jobs_judge = 0
    for result in results:
        avg_jaccard += result["actions similarities"]["jaccard_index"]
        avg_diff_nb_steps += result["actions similarities"]["diff_nb_steps"]
        avg_events_dist += result["deepdiff"]["events"]["distance"]
        avg_jobs_dist += result["deepdiff"]["jobs"]["distance"]
        avg_event_judge += result["LLM-as-a-Judge results"]["events"]
        avg_jobs_judge += result["LLM-as-a-Judge results"]["jobs"]

    avg_jaccard = avg_jaccard / len(results)
    avg_diff_nb_steps = avg_diff_nb_steps / len(results)
    avg_events_dist = avg_events_dist / len(results)
    avg_jobs_dist = avg_jobs_dist / len(results)
    avg_event_judge = avg_event_judge / len(results)
    avg_jobs_judge = avg_jobs_judge / len(results)

    st.write(f"""
        ## Average results
        - Jaccard index: {avg_jaccard}
        - Diff nb steps: {avg_diff_nb_steps}
        - Events distance: {avg_events_dist}
        - Jobs distance: {avg_jobs_dist}
        - LLM-as-a-Judge events: {avg_event_judge}
        - LLM-as-a-Judge jobs: {avg_jobs_judge}
        """)

    st.write("## Results")

    for result in results:
        st.write("### Prompt")
        st.write(result["description"])
        st.write("### System Prompt")
        st.write(result["system_prompt"])
        st.write("### Response")
        with st.expander("Show"):
            st.write(result["response"])
        st.write("### Test Results")
        for test_result in result["test results"]:
            st.write("#### Actions similarities")
            st.json(test_result["actions similarities"])
            st.write("#### Analysis output")
            with st.expander("Show"):
                st.code(test_result["result_output"])
            st.write("#### Generated code")
            with st.expander("Show"):
                st.code(test_result["response"], language="yaml")
