import polars as pl
from env import base_url, api_key
import httpx

dataset = pl.read_ndjson("dataset/validation_level1_sm.jsonl")
model = ""
temperature = 0.9
top_p = 0.9

file = f"results/validation_level1_sm_{model}.jsonl"

for data in dataset.iter_rows(named=True):
    print(data)
    res = httpx.post(
        base_url + "/chat/completions",
        headers={"Authorization": "bearer " + api_key, "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": data["messages"],
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": None
        },
        timeout = 60
    )

    response = res.json()["choices"][0]["message"]["content"]
