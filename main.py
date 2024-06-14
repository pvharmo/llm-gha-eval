from phi.assistant.assistant import Assistant
from phi.llm.ollama.chat import Ollama
# from phi.llm.openai.like import OpenAILike
import json
from tqdm import tqdm
import yaml
import json

from utils import compare_workflows

paths = [
    "dataset/chrta/sip_call/workflows/compile.yml",
    "dataset/chrta/sip_call/workflows/compile copy.yml",
    "dataset/aeshell/aesh/workflows/main.yml",
    "dataset/oysteinmyrmo/bezier/workflows/test_linux.yml",
    "dataset/splintered-reality/py_trees/workflows/pre-merge.yaml",
    "dataset/splintered-reality/py_trees/workflows/push_poetry_container.yaml",
    "dataset/wb2osz/direwolf/workflows/codeql-analysis.yml"
]

file1 = yaml.safe_load(open("dataset/chrta/sip_call/workflows/compile.yml"))
file2 = yaml.safe_load(open("dataset/chrta/sip_call/workflows/compile copy.yml"))

print(json.dumps(file1[True], indent=4))
print(json.dumps(file2[True], indent=4))
if isinstance(file1[True], dict):
    ev1 = file1[True].keys()
else:
    ev1 = file1[True]

if isinstance(file2[True], dict):
    ev2 = file2[True].keys()
else:
    ev2 = file2[True]
print(ev1 == ev2)

# for path in paths:
#     file = yaml.safe_load(open(path))

#     print(yaml.safe_dump(file[True]))
#     print()
#     print("-----------------")


