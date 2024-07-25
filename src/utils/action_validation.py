import json
import subprocess

def action_validator(workflow):
    if workflow is None:
        return None
    with open('outputs/test.yml', 'w') as file:
        file.write(workflow)

    output = subprocess.run(["actionlint", "-format", "'{{json .}}'", "outputs/test.yml"], text=True, capture_output=True).stdout

    json_output = json.loads(output[1:-1])

    return {
        "valid": len(json_output) == 0,
        "output": json_output,
    }