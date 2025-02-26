import polars as pl

docs = pl.read_json("../dataset/intermediate/step4_workflows_filtered_and_grouped.json", infer_schema_length=25000).sample(fraction=1, shuffle=True)
total = docs.height
finetuning_count = int(total*0.9)
finetuning_docs = docs[:finetuning_count]
testing_docs = docs[finetuning_count:]

print(f"Finetuning: {finetuning_docs.height}")
print(f"Testing: {testing_docs.height}")

finetuning_docs.write_json("../dataset/intermediate/finetuning.json")
testing_docs.write_json("../dataset/intermediate/testing.json")
