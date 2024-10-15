import re

def extract_yaml(text):
    pattern = r'```yaml[\n| ]?(.*)```'
    matches = re.match(pattern, text, re.DOTALL)
    if matches:
        return matches.group(1)
    else:
        return ""
