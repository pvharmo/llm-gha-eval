import sys
sys.path.append('..')

from dataset.load_dataset import format_dataset
import os
import env
import subprocess
# import polars as pl
import re
from ruamel.yaml import YAML

yaml = YAML()
yaml.preserve_quotes = True
yaml.default_flow_style = False
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.width = 9999

examples = format_dataset("train", 2000, True)

def test_grammar():
    return subprocess.run([f"{env.llama_cpp_dir}/llama-gbnf-validator", "grammar.gbnf", "./test_dataset.yml"], capture_output=True, text=True)

def extract_yaml(text):
    pattern = r'```yaml[\n| ]?(.*)```|```[\n| ]?(.*)```'
    matches = re.match(pattern, text.strip(), re.DOTALL)
    if matches:
        return matches.group(1) or matches.group(2)
    else:
        return ""

for example in examples:
    val = extract_yaml(example["answer"]).encode('utf-8', errors='ignore').decode('utf-8')
    val = re.sub(r'[^\x00-\x7F]+', '', val)
    data = yaml.load(val)

    with open("./test_dataset.yml", 'w') as file:
        yaml.dump(data, file)

    res = test_grammar()
    retry = True
    while (res.stdout.startswith("Input string is invalid according to the grammar.") or res.returncode != 0) and retry:
        if res.returncode != 0:
            print("Error running the grammar validator.")
            print(res.stderr)
            i = input()
        else:
            print(res.stdout)
            i = input()
            os.system('clear')

        if i == "c":
            retry = False
        else:
            res = test_grammar()
    print("Workflow compatible with grammar.")
