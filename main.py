from phi.assistant.assistant import Assistant
from phi.llm.ollama.chat import Ollama
# from phi.llm.openai.like import OpenAILike
import json
from tqdm import tqdm

from utils import build_promt, evaluate_results
import env

system_prompts_attributes = json.loads(open("system_prompts.json").read())
prompts = json.loads(open("prompts.json").read())

results = []

models = [
    {"name": "phi3", "llm": Ollama(model="phi3")},
    {"name": "mistral-7b", "llm": Ollama(model="mistral")},
    {"name": "mistral-instruct", "llm": Ollama(model="mistral:instruct")},
    {"name": "zephyr-7b", "llm": Ollama(model="zephyr")},
    # {"name": "llama3-8b", "llm": Ollama(model="llama3")},
    # {"name": "mixtral-8x7b", "llm": OpenAILike(model="mistralai/Mixtral-8x7B-Instruct-v0.1", api_key=env.api_key, base_url=env.base_url)},
    # {"name": "mixtral-8x22b", "llm": OpenAILike(model="mistralai/Mixtral-8x22B-v0.1", api_key=env.api_key, base_url=env.base_url)},
    # {"name": "llama3-70b", "llm": OpenAILike(model="meta-llama/Meta-Llama-3-70B-Instruct", api_key=env.api_key, base_url=env.base_url)},
    # {"name": "wizardlm-2-7b", "llm": OpenAILike(model="microsoft/WizardLM-2-7B", api_key=env.api_key, base_url=env.base_url)},
]

system_prompts = []

for personification in system_prompts_attributes["personification"]:
    for task_description in system_prompts_attributes["task_description"]:
        for qualifiers in system_prompts_attributes["qualifiers"]:
            for job_title in system_prompts_attributes["job_title"]:
                system_prompts.append(build_promt(personification, task_description, qualifiers, job_title))

for model in models:
    for system_prompt in tqdm(system_prompts):
        for prompt in prompts["requests"]:
            assistant = Assistant(
                llm=model["llm"],
                description=system_prompt,
                run_id=None
            )
            response = assistant.run(prompt, stream=False)

            result = {
                "prompt": prompt,
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

    with open(f'results/{model["name"]}.json', "w") as file:
        json.dump(results , file)

# read response.txt
# response = open("response.txt").read()

# evaluate_results(response, markdown=True)
