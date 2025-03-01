import sys
sys.path.append("../")

import env
import yaml
from plotnine import ggplot, labs, aes, geom_line, geom_point, geom_text, theme, scale_color_manual
import polars as pl
import sys

def make_plot(plot, data, x, y, group, color, legend_direction="horizontal", text=True, colors=None):
    plot += geom_line(data=data, mapping=aes(x=x, y=y, group=group, color=color))
    plot += geom_point(data=data, mapping=aes(x=x, y=y, group=group, color=color))
    if text:
        plot += geom_text(data=data, mapping=aes(
            x=x,
            y=y,
            label=y),
            format_string="{:.2f}",
            va="bottom")
    if group is not None:
        plot += theme(legend_position="top", legend_direction=legend_direction)
    else:
        plot += theme(legend_position="none")
    if colors is not None:
        plot += scale_color_manual(colors)
        
    return plot

def save_graphs(data, x, group, name, legend_direction="horizontal", text=True, colors=None):
    plot = ggplot() + labs(x=x.capitalize(), y="BLEU Score", title=f"BLEU Score")
    plot = make_plot(plot, data, x=x, y="bleu_score", group=group, color=group, legend_direction=legend_direction, text=text, colors=colors)
    plot.save(f"../tmp/{name}-{x}-bleu.png", width=4, height=6, dpi=600)

    plot2 = ggplot() + labs(x=x.capitalize(), y="Lint Score", title=f"Lint Score")
    plot2 = make_plot(plot2, data, x=x, y="lint_score", group=group, color=group, legend_direction=legend_direction, text=text, colors=colors)
    plot2.save(f"../tmp/{name}-{x}-lint.png", width=4, height=6, dpi=600)

configs = yaml.safe_load(open(env.results_folder + "/presentation_configs.yaml"))

averages = None

for i, (model, label) in enumerate(configs["size-comparison"].items()):
    results = pl.read_json(env.results_folder + "/" + model + "/scores.json").unnest("lint_score")
    split_label = label.split(" ")
    average = results.filter(pl.col("infinite_loop") == False).with_columns(
        size=pl.lit(split_label[0]),
        finetuned=pl.lit(split_label[1]),
        model=pl.lit(label)
    ).group_by("model").agg(
        pl.col("valid").mean().alias("lint_score"),
        pl.col("bleu_score").mean().alias("bleu_score"),
        pl.col("size").first().alias("model size"),
        pl.col("finetuned").first().alias("model version")
    )
    if averages is None:
        averages = average
    else:
        averages = averages.vstack(average)

save_graphs(data=averages, x="model size", group="model version", name="size-comparison")

examples_comparisons = None

for i, (model, label) in enumerate(configs["examples-comparison"].items()):
    results = pl.read_json(env.results_folder + "/" + model + "/scores.json").unnest("lint_score")
    examples_comparison = results.filter(pl.col("infinite_loop") == False).with_columns(
        pl.lit(label).alias("nb examples").cast(pl.Float32),
    ).group_by("nb examples").agg(
        pl.col("valid").mean().alias("lint_score"),
        pl.col("bleu_score").mean().alias("bleu_score"),
        pl.col("nb examples").first().alias("number of examples").cast(pl.Float32),
    )
    if examples_comparisons is None:
        examples_comparisons = examples_comparison
    else:
        examples_comparisons = examples_comparisons.vstack(examples_comparison)

save_graphs(data=examples_comparisons, x="number of examples", group=None, name="examples-comparison")

models_comparisons = None

for i, (model, label) in enumerate(configs["codellama-qwen"].items()):
    results = pl.read_json(env.results_folder + "/" + model + "/scores.json").unnest("lint_score")
    models_comparison = results.filter(pl.col("infinite_loop") == False).with_columns(
        pl.lit(label).alias("model"),
    ).group_by(["model", "level"]).agg(
        pl.col("valid").mean().alias("lint_score"),
        pl.col("bleu_score").mean().alias("bleu_score"),
    )
    if models_comparisons is None:
        models_comparisons = models_comparison
    else:
        models_comparisons = models_comparisons.vstack(models_comparison)

save_graphs(
    data=models_comparisons,
    x="level",
    group="model",
    name="codellama-qwen",
    legend_direction="vertical",
    text=False,
    colors=["#B71C1C", "#F06292", "#0D47A1", "#4FC3F7"]
)