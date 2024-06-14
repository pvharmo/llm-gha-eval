import streamlit as st

def menu():
    st.sidebar.page_link("pages/Run_LLM_benchmark.py", label="🚀 Run LLM benchmarks")
    st.sidebar.page_link("pages/Visualize_benchmarks_results.py", label="📊 Visualize benchmarks")
    st.sidebar.page_link("pages/Build_dataset.py", label="📑 Build dataset")
    st.sidebar.page_link("pages/Assistant.py", label="🤖 Assitant")
    st.sidebar.page_link("pages/Explanation.py", label="🤖 Workflow Explanation")
    st.sidebar.page_link("pages/Compare.py", label="🚀 Workflows comparison")
