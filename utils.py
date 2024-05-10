import regex as re
import subprocess

def fill_personification(personification, job_title, qualifiers):
    return personification.replace("{{Job title}}", job_title).replace("{{Qualifier}}", qualifiers)

def build_promt(personification, task_description, qualifiers, job_title):
    return fill_personification(personification, job_title, qualifiers) + " " + task_description

def evaluate_results(response, markdown=True):
    if markdown:
        codes = re.findall(r'(?<=```yaml)([\s\S]*?)(?=```)', response)
    else:
        codes = [response]
    results = []
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
