import streamlit as st

def menu():
    st.sidebar.page_link("pages/Run_LLM_benchmark.py", label="🚀 Run LLM benchmarks")
    st.sidebar.page_link("pages/Visualize_benchmarks_results.py", label="📊 Visualize benchmarks")