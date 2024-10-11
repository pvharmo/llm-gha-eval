import polars as pl

pl.read_ndjson("../dataset/finetuning_all.jsonl").sample(n=200, shuffle=True).write_ndjson("../dataset/finetuning_sm.jsonl")
pl.read_ndjson("../dataset/validation_all.jsonl").sample(n=200, shuffle=True).write_ndjson("../dataset/validation_sm.jsonl")
pl.read_ndjson("../dataset/testing_all.jsonl").sample(n=200, shuffle=True).write_ndjson("../dataset/testing_sm.jsonl")
