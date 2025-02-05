import sys
sys.path.append("../")

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import json
import env
import yaml
import argparse

def visualize_model_performance(data, ax, title, alternative=False):
    x_values = []
    for model_name, levels in data.items():
        x_values = []
        y_values = []

        # Extract level numbers and calculate scores
        for level, metrics in levels.items():
            level_num = int(level.replace('level', ''))
            score = metrics['score']
            count = metrics['count'] if not alternative else metrics['valid_count']

            # Calculate score per count, handling division by zero
            if count > 0:
                y_value = score / count
            else:
                y_value = 0

            x_values.append(level_num)
            y_values.append(y_value)

        # Plot the line
        # ax.plot(x_values, y_values, marker='o', linewidth=2, label=model_name)
        ax.plot(x_values, y_values, marker='o', linewidth=2, label=(model_name[:20] + "..." if len(model_name) > 20 else model_name))

        # Add value annotations
        for x, y in zip(x_values, y_values):
            ax.annotate(f'{y:.2f}',
                       (x, y),
                       textcoords="offset points",
                       xytext=(0,10),
                       ha='center')

    # Customize the plot
    ax.set_xlabel('Level')
    ax.set_ylabel('Average score')
    # ax.set_ylim([0, 1])
    ax.set_title(title)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend(loc="upper left", )

    # Set x-axis to show only integer values
    ax.set_xticks(x_values)

dfs_bleu = {}
dfs_deepdiff = {}
dfs_actionlint = {}

parser = argparse.ArgumentParser()
parser.add_argument("--config", type=str)
args = parser.parse_args()

if args.config is None:
    print("Select a config with --config")
    exit()

configs = yaml.safe_load(open(env.results_folder + "/presentation_configs.yaml"))

# iterate through folders only
for (model, label) in configs[args.config].items():
    print(f"Processing {model} with label {label}")
    dfs_bleu[str(label)] = json.load(open(env.results_folder + "/" + model + "/bleu_score.json"))
    dfs_deepdiff[str(label)] = json.load(open(env.results_folder + "/" + model + "/deepdiff.json"))
    dfs_actionlint[str(label)] = json.load(open(env.results_folder + "/" + model + "/actionlint.json"))

fig, (ax1, ax3) = plt.subplots(1, 2, figsize=(15, 9))

fig = visualize_model_performance(dfs_bleu, ax1, "BLEU Score")
# fig = visualize_model_performance(dfs_deepdiff, ax2, "DeepDiff Score", True)
fig = visualize_model_performance(dfs_actionlint, ax3, "Syntax validity")
plt.tight_layout()
plt.savefig(f"../results/{args.config}.png")
plt.show()
