import yaml
from ruamel.yaml import YAML, yaml_object
from collections import OrderedDict
import sys


ryaml=YAML()
ryaml.preserve_quotes = True
ryaml.default_flow_style = False
ryaml.indent(mapping=2, sequence=4, offset=2)
ryaml.width = 9999

with open("../grammar/test2.yml") as f:
    content = yaml.safe_load(f)

ordered_content = {}

keys = ["name", "run-name", "on", "permissions", "env", "defaults", "concurrency", "jobs"]

for key in keys:
    if key in content:
        ordered_content[key] = content[key]

ryaml.dump(ordered_content, sys.stdout)
