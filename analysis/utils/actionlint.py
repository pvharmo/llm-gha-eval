import json
import subprocess

def validate_action(workflow):
    if workflow is None:
        return None
    with open('../tmp/test.yml', 'w') as file:
        file.write(workflow)

    output = subprocess.run(["actionlint", "-format", "'{{json .}}'", "../tmp/test.yml"], text=True, capture_output=True).stdout

    json_output = json.loads(output[1:-1])

    for values in json_output:
        if values["kind"] == "syntax-check":
            return {
                "valid": False,
                "output": json_output,
            }

    return {
        "valid": True,
        "output": json_output,
    }
