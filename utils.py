import regex as re
import subprocess
import yaml

def fill_personification(personification, job_title, qualifiers):
    return personification.replace("{{Job title}}", job_title).replace("{{Qualifier}}", qualifiers)

def build_promt(personification, task_description, qualifiers, job_title):
    return fill_personification(personification, job_title, qualifiers) + " " + task_description

def evaluate_results(response, markdown=True):
    print("response: ", response)
    if markdown:
        codes = re.findall(r'(?<=```yaml)([\s\S]*?)(?=```)', response)
    else:
        codes = [response]
    results = []
    print("codes: ", codes)
    for code in codes:
        with open('outputs/test.yml', 'w') as file:
            file.write(code)

        output = subprocess.run(["action-validator", "outputs/test.yml"], text=True, check=False, capture_output=True).stderr

        result = {
            "valid": len(output) == 0,
            "result_output": output,
            "code": code
        }
        results.append(result)

    return results

def compare_workflows(original_workflow, generated_workflow):
    parsed_original = yaml.parse(original_workflow)
    parsed_generated = yaml.parse(generated_workflow)

    parsed_original["on"] = parsed_generated["on"]