import polars as pl

types = ["testing", "validation"]
levels = ["level1", "level2", "level3", "level4", "level5", "all"]
for type in types:
    for level in levels:
        pl.read_ndjson(f"../dataset/intermediate/{type}_{level}.jsonl").sample(n=200, shuffle=True).write_ndjson(f"../dataset/{type}_{level}_sm.jsonl")
