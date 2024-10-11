import polars as pl

types = ["testing", "validation"]
levels = ["level1", "level2", "level3", "level4", "level5", "all"]
for type in types:
    for level in levels:
        data = pl.read_ndjson(f"../dataset/intermediate/{type}_{level}.jsonl")
        # Split messages in two parts: first two messages as messages and the third message as answer
        data.select([
            pl.col("messages").list.slice(0, 2),
            pl.col("id"),
            pl.col("messages").list.slice(2, 1).alias("answer")
        ]).write_ndjson(f"../dataset/intermediate/{type}_{level}.jsonl")
