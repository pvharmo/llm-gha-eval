import yaml
# import nltk
# from nltk.tokenize import word_tokenize
from nltk.translate.bleu_score import sentence_bleu

def actions_comparison(original, generated):
    nb_steps_original = 0
    nb_steps_generated = 0

    original_actions = []
    generated_actions = []


    for job in original["jobs"]:
        if "steps" in original["jobs"][job]:
            for step in original["jobs"][job]["steps"]:
                nb_steps_original += 1
                if "uses" in step:
                    original_actions.append(step["uses"])

    print(generated)
    for job in generated["jobs"]:
        if "steps" in generated["jobs"][job]:
            for step in generated["jobs"][job]["steps"]:
                nb_steps_generated += 1
                if "uses" in step:
                    generated_actions.append(step["uses"])

    union = len(set(original_actions).union(generated_actions))
    jaccard_index = len(set(original_actions).intersection(generated_actions)) / union if union > 0 else 0
    # edit_distance_value = edit_distance(original_actions, generated_actions, len(original_actions), len(generated_actions))

    return {
        "jaccard_index": jaccard_index,
        # "edit_distance": edit_distance_value,
        "diff_nb_steps": nb_steps_original - nb_steps_generated,
        "ration_nb_steps": nb_steps_generated / nb_steps_original,
    }

# Recusive implementation of the edit distance algorithm (it is very slow)
def edit_distance(arr1, arr2, m, n):
    if m == 0:
        return n

    if n == 0:
        return m

    if arr1[m-1] == arr2[n-1]:
        return edit_distance(arr1, arr2, m-1, n-1)

    return 1 + min(
        edit_distance(arr1, arr2, m, n-1),    # Insert
        edit_distance(arr1, arr2, m-1, n),    # Remove
        edit_distance(arr1, arr2, m-1, n-1)    # Replace
    )

def workflows_comparison(original, generated):
    return {
        "bleu_score": bleu_score(original, generated)
    }

def bleu_score(reference, candidate):
    if candidate is None:
        return 0
    # # Download the necessary NLTK data (if not already downloaded)
    # try:
    #     nltk.data.find('tokenizers/punkt')
    # except LookupError:
    #     nltk.download('punkt')

    # # Tokenize the reference and candidate strings
    # reference_tokens = word_tokenize(reference)
    # candidate_tokens = word_tokenize(candidate)

    # Calculate BLEU score
    score = sentence_bleu([reference.split(" ")], candidate.split(" "))

    return score