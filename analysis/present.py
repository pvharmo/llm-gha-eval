import sys
sys.path.append("../")

import env
import yaml
import argparse
from plotnine import ggplot, labs, aes, geom_line, geom_point, geom_text, theme
import polars as pl
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--config", type=str)
args = parser.parse_args()

if args.config is None:
    print("Select a config with --config")
    exit()

configs = yaml.safe_load(open(env.results_folder + "/presentation_configs.yaml"))

plot = ggplot() + labs(x="Model size", y="BLEU Score", title="BLEU Score by model size")
plot2 = ggplot() + labs(x="Model size", y="Lint Score", title="Lint Score by model size")

averages = None

for i, (model, label) in enumerate(configs[args.config].items()):
    results = pl.read_json(env.results_folder + "/" + model + "/scores.json").unnest("lint_score")
    split_label = label.split(" ")
    average = results.filter(pl.col("infinite_loop") == False).with_columns(
        size=pl.lit(split_label[0]),
        finetuned=pl.lit(split_label[1]),
        model=pl.lit(label)
    ).group_by("model").agg(
        lint_score=pl.col("valid").mean(),
        bleu_score=pl.col("bleu_score").mean(),
        size=pl.col("size").first(),
        finetuned=pl.col("finetuned").first()
    )
    if averages is None:
        averages = average
    else:
        averages = averages.vstack(average)

print(averages)
if averages is None:
    print("No data to plot")
    exit()

def make_plot(plot, data, x, y, group, color, text=True):
    plot += geom_line(data=data, mapping=aes(x=x, y=y, group=group, color=color))
    plot += geom_point(data=data, mapping=aes(x=x, y=y, group=group, color=color))
    if text:
        plot += geom_text(data=data, mapping=aes(
            x=x,
            y=y,
            label=y),
            format_string="{:.2f}",
            va="bottom")
    plot += theme(legend_position="top", legend_direction="horizontal")
    return plot

plot = make_plot(plot, averages, "size", "bleu_score", "finetuned", "finetuned")
plot2 = make_plot(plot2, averages, "size", "lint_score", "finetuned", "finetuned")

plot.save("test.png", width=5, height=5, dpi=600)
# plot2.show()
