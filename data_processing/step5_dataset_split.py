import polars as pl

docs = pl.read_json("../dataset/intermediate/step4_workflows_filtered_and_grouped.json").sample(fraction=1, shuffle=True)
total = docs.height
finetuning_count = int(total*0.1)
validation_count = int(total*0.1)
finetuning_docs = docs[:finetuning_count]
validation_docs = docs[finetuning_count:finetuning_count+validation_count]
testing_docs = docs[finetuning_count+validation_count:]

print(f"Finetuning: {finetuning_docs.height}")
print(f"Validation: {validation_docs.height}")
print(f"Testing: {testing_docs.height}")

finetuning_docs.write_json("../dataset/intermediate/finetuning.json")
validation_docs.write_json("../dataset/intermediate/validation.json")
testing_docs.write_json("../dataset/intermediate/testing.json")
