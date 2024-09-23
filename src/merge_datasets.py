import polars as pl
import env

# my_prompts = pl.read_json(env.prompts_file)
their_prompts = pl.read_json("../dataset/wfsgen-eval-small.json").sample(20).write_json("dataset/dataset-sm.json")

# merged_prompts = my_prompts.join(their_prompts, on="id", how="inner")

# merged_prompts.write_json("dataset/merged_prompts.json")

# for merged_prompt in merged_prompts.iter_rows():
#     print(merged_prompt)