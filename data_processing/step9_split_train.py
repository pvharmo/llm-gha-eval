import polars as pl

dataset = pl.read_ndjson("../dataset/finetuning.jsonl")
testing_dataset = pl.read_ndjson("../dataset/testing.jsonl")

dataset = dataset.filter(pl.col("yaml_tokens_count") <= 1024)
testing_dataset = testing_dataset.filter(pl.col("yaml_tokens_count") <= 1024)

unique_ids = sorted(list(set(dataset["id"])))
unique_ids_generator = unique_ids[:10000]
unique_ids_corrector = unique_ids[10000:20000]
unique_ids_judge = unique_ids[20000:30000]
dataset_generator = dataset.filter(pl.col("id").is_in(unique_ids_generator))
dataset_corrector = dataset.filter(pl.col("id").is_in(unique_ids_corrector))
dataset_judge = dataset.filter(pl.col("id").is_in(unique_ids_judge))

print("generator dataset size: ", len(dataset_generator))
print("corrector dataset size: ", len(dataset_corrector))
print("judge dataset size: ", len(dataset_judge))
print("total dataset size: ", len(dataset))

dataset_generator.write_ndjson("../dataset/generator_train.jsonl")
dataset_corrector.write_ndjson("../dataset/corrector_train.jsonl")
dataset_judge.write_ndjson("../dataset/judge_train.jsonl")

print("testing dataset size: ", len(testing_dataset))
testing_dataset.write_ndjson("../dataset/testing.jsonl")
