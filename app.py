import streamlit as st
from st_pages import Page, show_pages, add_page_title

add_page_title()

# Specify what pages should be shown in the sidebar, and what their titles and icons
# should be
show_pages(
    [
        # Page("app.py", "Home", "🏠"),
        Page("pages/run_llm_benchmark.py", "Run LLM benchmarks", "🚀"),
        Page("pages/visualize_benchmark_results.py", "Visualize benchmarks", "📊"),
    ]
)