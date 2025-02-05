from nltk.translate.bleu_score import sentence_bleu  # type: ignore
import re

def i_bleu_score(reference: str, candidate: str) -> float:
    if candidate is None:
        return 0.0

    score: float = sentence_bleu([reference.split()], candidate.split())

    return score

def remove_comments(yaml_content):
    comment_pattern = re.compile(r'^\s*#.*$', re.MULTILINE)
    yaml_content_without_comments = re.sub(comment_pattern, '', yaml_content)
    lines = yaml_content_without_comments.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def remove_empty_lines(yaml_content):
    lines = yaml_content.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def bleu_score(reference, candidate):
    reference = reference.strip().lower()
    reference = remove_comments(reference)

    candidate = candidate.strip().lower()
    candidate = remove_comments(candidate)

    return i_bleu_score(reference, candidate)
