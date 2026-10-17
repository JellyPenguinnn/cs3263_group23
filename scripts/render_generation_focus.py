#!/usr/bin/env python3
"""Render post-run generation views; preserve all earlier study figures."""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import PercentFormatter

from render_benchmark_results import COLORS, INK, LABELS, MUTED, ROOT, render_block
from render_difficulty_results import style_axis

MODELS = ("qwen36", "glm53flash")
ARMS = ("direct", "solver_augmented")
TIERS = ("easy", "moderate", "hard", "very_hard", "extreme")
BLOCKS = {
    "generation_core": ("Controlled schedule generation", "30 cases per approach · 15 SAT and 15 UNSAT",
                        "Post-run generation view of the unchanged development study; includes all five construction tiers."),
    "generation_small": ("Small-case schedule generation", "12 cases per approach · 4 or 8 activities",
                         "Size-selected descriptive subset, not a new experiment. The complete generation view retains all larger cases."),
}


def tier_figure(summary):
    fig, axes = plt.subplots(2, 1, figsize=(6.2, 5.0))
    fig.subplots_adjust(left=.14, right=.98, bottom=.10, top=.81, hspace=.55)
    fig.text(.14, .97, "Generation by construction tier", fontsize=13, weight="bold")
    fig.legend(handles=[Patch(color=COLORS[a], label=LABELS[a]) for a in ARMS],
               loc="upper left", bbox_to_anchor=(.125, .95), ncol=2, frameon=False, fontsize=11)
    for ax, model in zip(axes, MODELS):
        data = summary["models"][model]
        ax.set_title(data["model"], loc="left", fontsize=11, pad=8)
        for j, arm in enumerate(ARMS):
            rows = [data["generation_tiers"][tier]["approaches"][arm] for tier in TIERS]
            bars = ax.bar([x+(j-.5)*.36 for x in range(5)],
                          [100*r["accepted"]/r["attempts"] for r in rows],
                          width=.33, color=COLORS[arm])
            ax.bar_label(bars, labels=[str(r["accepted"]) for r in rows], fontsize=11, padding=3)
        ax.set_xticks(range(5), ["Easy", "Moderate", "Hard", "Very hard", "Extreme"], fontsize=11)
        ax.set_ylim(0, 125)
        ax.set_yticks([0, 50, 100])
        ax.yaxis.set_major_formatter(PercentFormatter(100, decimals=0))
        ax.set_ylabel("Accepted", fontsize=11)
        style_axis(ax)
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT/"results/summary/generation-focus-20261015.json")
    parser.add_argument("--output", type=Path, default=ROOT/"results/figures/generation-focus-20261015")
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()
    raw = args.source.read_bytes()
    summary = json.loads(raw)
    data = {scope: {model: {"model": summary["models"][model]["model"], "approaches": {
        arm: {**summary["models"][model]["scopes"][scope]["approaches"][arm],
              "percent": 100*summary["models"][model]["scopes"][scope]["approaches"][arm]["accepted"]/
                         summary["models"][model]["scopes"][scope]["approaches"][arm]["attempts"]}
        for arm in ARMS}} for model in MODELS} for scope in BLOCKS}
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "text.color": INK,
        "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
        "pdf.fonttype": 42, "figure.facecolor": "white"})
    figures = {scope.replace("_", "-"): render_block(scope, data[scope], report=args.report,
               models=MODELS, blocks=BLOCKS) for scope in BLOCKS}
    figures["generation-tiers"] = tier_figure(summary)
    args.output.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for name, fig in figures.items():
        for ext in ("png", "pdf"):
            path = args.output/(name+"."+ext)
            metadata = {"Creator": "CS3263 generation view", "CreationDate": None, "ModDate": None} if ext == "pdf" else {"Software": "CS3263 generation view"}
            fig.savefig(path, dpi=180, metadata=metadata)
            outputs[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        plt.close(fig)
    receipt = {"source_sha256": hashlib.sha256(raw).hexdigest(), "new_model_calls": 0,
        "renderer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "shared_renderer_sha256": hashlib.sha256((ROOT/"scripts/render_benchmark_results.py").read_bytes()).hexdigest(),
        "style_renderer_sha256": hashlib.sha256((ROOT/"scripts/render_difficulty_results.py").read_bytes()).hexdigest(),
        "matplotlib_version": matplotlib.__version__, "layout": "report" if args.report else "standalone",
        "plotted_data": data, "generation_tiers": {m: summary["models"][m]["generation_tiers"] for m in MODELS},
        "output_sha256": outputs}
    (args.output/"figure-data.json").write_text(json.dumps(receipt, indent=2, sort_keys=True)+"\n")
    print(f"Rendered {len(outputs)} generation figures; no existing study figures replaced.")


if __name__ == "__main__":
    main()
