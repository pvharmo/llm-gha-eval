import yaml
from deepdiff import DeepDiff

def deepdiff_compare(original, generated):
    # For some reason the yaml parser replaces the key "on" by True
    generated_events = generated[True] if True in generated else yaml.safe_load("{}")
    generated_jobs = generated["jobs"] if "jobs" in generated else yaml.safe_load("{}")
    original_events = original[True] if True in original else yaml.safe_load("{}")
    original_jobs = original["jobs"] if "jobs" in original else yaml.safe_load("{}")

    diff_events = DeepDiff(original_events, generated_events, ignore_order=True, verbose_level=2, get_deep_distance=True)
    diff_jobs = DeepDiff(original_jobs, generated_jobs, ignore_order=True, verbose_level=2, get_deep_distance=True)

    return {
        "events": {
            "stats": diff_events.get_stats(),
            "distance": diff_events["deep_distance"] if "deep_distance" in diff_events else None
        },
        "jobs": {
            "stats": diff_jobs.get_stats(),
            "distance": diff_jobs["deep_distance"] if "deep_distance" in diff_jobs else None
        }
    }
