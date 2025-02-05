import re

def extract_yaml(text):
    pattern = r'```yaml[\n| ]?(.*)```|```[\n| ]?(.*)```'
    matches = re.match(pattern, text.strip(), re.DOTALL)
    if matches:
        return matches.group(1) or matches.group(2)
    else:
        return ""

def detect_infinite_loop(response):
    pattern = r'(.*)```'
    matches = re.match(pattern, response.strip(), re.DOTALL)
    if matches and (matches.group(1)):
        return False
    else:
        return True
