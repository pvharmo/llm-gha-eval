import re

def extract_yaml(text):
    pattern = r'```yaml[\n| ]?(.*)```|```[\n| ]?(.*)```'
    matches = re.match(pattern, text.strip(), re.DOTALL)
    if matches:
        return matches.group(1) or matches.group(2)
    else:
        return ""

def detect_infinite_loop(response, max_iterations=10, max_length=10000):
    """
    Detect if a language model response has entered an infinite loop.

    Args:
    - response (str): The response from the language model.
    - max_iterations (int): The maximum number of iterations to check for repetitive patterns.
    - max_length (int): The maximum length of the response to consider it suspiciously long.

    Returns:
    - bool: True if an infinite loop is detected, False otherwise.
    """
    # Check if the response is excessively long
    if len(response) > max_length:
        return True

    # Split the response into words
    words = response.split()

    # Check for repetitive patterns
    word_count = {}
    for word in words:
        if word in word_count:
            word_count[word] += 1
        else:
            word_count[word] = 1

    # Check if any word appears more than max_iterations times
    for count in word_count.values():
        if count > max_iterations:
            return True

    return False
