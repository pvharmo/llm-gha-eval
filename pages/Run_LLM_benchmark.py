import streamlit as st
import json
import pandas as pd
from stqdm import stqdm
from menu import menu

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

st.title("🚀 Run LLM benchmarks")

system_prompts_attributes = json.loads(open("./config/system_prompts.json").read())
prompts = json.loads(open("./config/prompts.json").read())

models = pd.DataFrame([
    {"run": False, "name": "phi3", "full name": "phi3", "local": True,},
    {"run": False, "name": "phi3 small", "full name": "phi3", "local": True,},
    {"run": False, "name": "mistral 7b", "full name": "mistral", "local": True,},
    {"run": False, "name": "mistral instruct", "full name": "mistral:instruct", "local": True,},
    {"run": False, "name": "zephyr 7b", "full name": "zephyr", "local": True,},
    {"run": False, "name": "llama3 8b", "full name": "llama3", "local": True,},
    {"run": False, "name": "wizardlm-2 7b", "full name": "wizardlm2", "local": True,},
    {"run": False, "name": "mixtral 8x7b", "full name": "mistralai/Mixtral-8x7B-Instruct-v0.1", "local": False,},
    {"run": False, "name": "mixtral 22x7b", "full name": "mistralai/Mixtral-8x22B-v0.1", "local": False,},
    {"run": False, "name": "llama3 70b", "full name": "meta-llama/Meta-Llama-3-70B-Instruct", "local": False,},
    {"run": False, "name": "wizardlm-2 8x22b", "full name": "microsoft/WizardLM-2-8x22B", "local": False,},
])

personifications = pd.DataFrame(system_prompts_attributes["personification"], columns=["personification"])
personifications.insert(0, "run", False)
tasks_description = pd.DataFrame(system_prompts_attributes["task_description"], columns=["task description"])
tasks_description.insert(0, "run", False)
qualifiers = pd.DataFrame(system_prompts_attributes["qualifiers"], columns=["qualifier"])
qualifiers.insert(0, "run", False)
job_titles = pd.DataFrame(system_prompts_attributes["job_title"], columns=["job title"])
job_titles.insert(0, "run", False)
prompts = pd.DataFrame(prompts["requests"], columns=["prompt"])
prompts.insert(0, "run", False)

with st.form("my_form"):
    st.write("### Models")
    models = st.data_editor(models, hide_index=True, disabled=["name", "full name", "local"], use_container_width=True)
    st.write("### System prompt templates")
    personifications = st.data_editor(personifications, hide_index=True, disabled=["personification"], use_container_width=True)
    st.write("### Task desciptions")
    tasks_description = st.data_editor(tasks_description, hide_index=True, disabled=["task description"], use_container_width=True)
    st.write("### Qualifiers")
    qualifiers = st.data_editor(qualifiers, hide_index=True, disabled=["qualifier"], use_container_width=True)
    st.write("### Job titles")
    job_titles = st.data_editor(job_titles, hide_index=True, disabled=["job title"], use_container_width=True)
    st.write("### Prompts")
    prompts = st.data_editor(prompts, hide_index=True, disabled=["prompt"], use_container_width=True)

    submit = st.form_submit_button(label="Submit")

system_prompts = []


st.write("## System prompts")
for _, personification in personifications[personifications["run"]].iterrows():
    for _, task_description in tasks_description[tasks_description["run"]].iterrows():
        for _, qualifier in qualifiers[qualifiers["run"]].iterrows():
            for _, job_title in job_titles[job_titles["run"]].iterrows():
                system_prompt = build_promt(personification[1], task_description[1], qualifier[1], job_title[1])
                st.write("- " + system_prompt)
                system_prompts.append(system_prompt)

st.write("## Prompts")
for _, prompt in prompts[prompts["run"]].iterrows():
    st.write("- " + prompt["prompt"])

st.write("## Benchmarks running")
if submit:
    for i, model_params in models.loc[models["run"]].iterrows():
        st.write(f"- Running {model_params['name']}")
        if model_params["local"]:
            model = Ollama(model=model_params["full name"])
        else:
            model = OpenAILike(model=model_params["full name"], api_key=env.api_key, base_url=env.base_url)

        results = []

        for system_prompt in stqdm(system_prompts):
            for _, prompt in prompts[prompts["run"]].iterrows():
                assistant = Assistant(
                    llm=model,
                    description=system_prompt,
                    run_id=None
                )
                response = assistant.run(prompt["prompt"], stream=False)

                result = {
                    "prompt": prompt["prompt"],
                    "system_prompt": system_prompt,
                    "code-limit-prompt": None,
                    "response": response,
                    "test results": evaluate_results(response, markdown=True)
                }

                results.append(result)

                # for code_limit in system_prompts_attributes["code-limit-prompts"]:
                #     assistant = Assistant(
                #         llm=model["llm"],
                #         description=system_prompt,
                #         instructions=[code_limit]
                #     )
                #     response = assistant.run(prompt, stream=False)

                #     result = {
                #         "prompt": prompt,
                #         "system_prompt": system_prompt,
                #         "code-limit-prompt": code_limit,
                #         "response": response,
                #         "test results": evaluate_results(response, markdown=False)
                #     }

                #     results.append(result)

        print(results)
        with open(f'results/{model_params["name"]}.json', "w") as file:
            json.dump(results , file)