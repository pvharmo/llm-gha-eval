import sys
sys.path.append('..')

from datasets import load_dataset
import env

load_dataset("pvharmo/llm-gha", token=env.hf_access_token)
