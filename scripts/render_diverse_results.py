#!/usr/bin/env python3
"""Render report-sized PNG charts from the verified diverse comparison.

Figures keep all failures in primary denominators and never pool timing phases.
"""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import PercentFormatter
from render_benchmark_results import COLORS, INK, LABELS, MUTED, ROOT
from render_difficulty_results import style_axis

MODELS = ("qwen36", "glm53flash")
NAMES = {"qwen36": "Qwen3.6", "glm53flash": "GLM5.3 Flash"}
ARMS = ("direct", "solver_augmented")
CATEGORIES = ("gold_invalid_schedule", "false_unsat", "invalid_output", "provider_error")
CATEGORY_LABELS = ("Constraint\nviolation", "False\nUNSAT", "Output\nformat", "Infrastructure")


def plot_data(summary):
    data = {}
    for model in MODELS:
        data[model] = {}
        for arm in ARMS:
            row = summary["models"][model]["overall_by_method"][arm]
            n, accepted = row["attempts"], row["accepted"]
            if (n != 1000 or not isinstance(accepted, int) or not 0 <= accepted <= n or
                sum(row["categories"].values()) != n or row["categories"].get("accepted", 0) != accepted or
                set(row["categories"]) - {"accepted", *CATEGORIES}):
                raise ValueError("Unexpected or inconsistent diverse category counts")
            data[model][arm] = {"accepted": accepted, "attempts": n, "percent": 100 * accepted / n,
                "failures": {c: row["categories"].get(c, 0) for c in CATEGORIES},
                "by_size": {s: {"accepted": v[arm]["accepted"], "attempts": v[arm]["attempts"]}
                            for s, v in summary["models"][model]["by_size"].items()}}
    return data


def legend(fig, y):
    fig.legend(handles=[Patch(color=COLORS[a], label=LABELS[a]) for a in ARMS],
               loc="upper left", bbox_to_anchor=(.13, y), ncol=2, frameon=False, fontsize=11)


def acceptance(data, compact=False):
    fig, ax = plt.subplots(figsize=(6.2, 2.6 if compact else 3.45))
    fig.subplots_adjust(left=.15, right=.98, bottom=.20 if compact else .17,
                        top=.78 if compact else .72)
    if not compact:
        fig.text(.15, .95, "Diverse schedule generation", fontsize=13, weight="bold")
    legend(fig, 1.0 if compact else .91)
    for j, arm in enumerate(ARMS):
        rows = [data[m][arm] for m in MODELS]
        bars = ax.bar([i + (j - .5) * .36 for i in range(2)],
                      [r["percent"] for r in rows], width=.33, color=COLORS[arm])
        ax.bar_label(bars, labels=[f'{r["percent"]:.1f}%' for r in rows], padding=4, fontsize=11)
        for bar, row in zip(bars, rows):
            ax.text(bar.get_x() + bar.get_width() / 2, row["percent"] / 2,
                    f'{row["accepted"]:,}\nof {row["attempts"]:,}', ha="center", va="center",
                    color="white", fontsize=11, weight="bold")
    ax.set_xticks(range(2), [NAMES[m] for m in MODELS], fontsize=11)
    ax.set_ylabel("Accepted answers", fontsize=11)
    ax.set_ylim(0, 119)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.yaxis.set_major_formatter(PercentFormatter(100, decimals=0))
    style_axis(ax)
    return fig


def failures(data, compact=False):
    fig, axes = plt.subplots(2, 1, figsize=(6.2, 3.9 if compact else 4.9))
    fig.subplots_adjust(left=.15, right=.98, bottom=.14 if compact else .11,
                        top=.82 if compact else .79, hspace=1.0 if compact else .83)
    if not compact:
        fig.text(.15, .96, "Failures by observed category", fontsize=13, weight="bold")
    legend(fig, 1.0 if compact else .93)
    for ax, model in zip(axes, MODELS):
        ax.set_title(NAMES[model], loc="left", fontsize=11, pad=6)
        maximum = max(v for arm in ARMS for v in data[model][arm]["failures"].values())
        for j, arm in enumerate(ARMS):
            values = [data[model][arm]["failures"][c] for c in CATEGORIES]
            bars = ax.bar([i + (j - .5) * .36 for i in range(4)], values,
                          width=.33, color=COLORS[arm])
            ax.bar_label(bars, labels=[str(v) for v in values], padding=3, fontsize=11)
        ax.set_xticks(range(4), CATEGORY_LABELS, fontsize=11)
        ax.set_ylabel("Failed attempts", fontsize=11)
        ax.set_ylim(0, maximum * 1.3)
        style_axis(ax)
    return fig


def sizes(data):
    fig, axes = plt.subplots(2, 1, figsize=(6.2, 4.8), sharey=True)
    fig.subplots_adjust(left=.15, right=.98, bottom=.12, top=.78, hspace=.65)
    fig.text(.15, .96, "Acceptance by activity count", fontsize=13, weight="bold")
    legend(fig, .93)
    counts = (8, 12, 16, 24, 32)
    for ax, model in zip(axes, MODELS):
        ax.set_title(NAMES[model], loc="left", fontsize=11, pad=6)
        for j, arm in enumerate(ARMS):
            rows = [data[model][arm]["by_size"][str(n)] for n in counts]
            values = [100 * r["accepted"] / r["attempts"] for r in rows]
            bars = ax.bar([i + (j - .5) * .36 for i in range(5)], values, width=.33, color=COLORS[arm])
            ax.bar_label(bars, labels=[str(r['accepted']) for r in rows], padding=3, fontsize=11)
        ax.set_xticks(range(5), [str(n) for n in counts], fontsize=11)
        ax.set_ylabel("Accepted", fontsize=11)
        ax.set_ylim(0, 125)
        ax.set_yticks([0, 50, 100])
        ax.yaxis.set_major_formatter(PercentFormatter(100, decimals=0))
        style_axis(ax)
    axes[-1].set_xlabel("Activities per case (labels: accepted out of 200)", fontsize=11)
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "results/summary/diverse-comparison-20261018.json")
    parser.add_argument("--output", type=Path, default=ROOT / "docs/figures/diverse-comparison-20261018")
    parser.add_argument("--compact", action="store_true", help="Reduce whitespace while retaining 11-point labels")
    args = parser.parse_args()
    raw = args.source.read_bytes()
    data = plot_data(json.loads(raw))
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "text.color": INK,
                        "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                        "figure.facecolor": "white"})
    args.output.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for name, fig in {"diverse-acceptance": acceptance(data, args.compact), "diverse-failures": failures(data, args.compact),
                      "diverse-size": sizes(data)}.items():
        target = args.output / f"{name}.png"
        fig.savefig(target, dpi=180, metadata={"Software": "CS3263 diverse comparison"})
        outputs[target.name] = hashlib.sha256(target.read_bytes()).hexdigest()
        plt.close(fig)
    receipt = {"source_sha256": hashlib.sha256(raw).hexdigest(), "new_model_calls": 0,
        "renderer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "shared_renderer_sha256": {p: hashlib.sha256((ROOT / "scripts" / p).read_bytes()).hexdigest()
                                   for p in ("render_benchmark_results.py", "render_difficulty_results.py")},
        "compact": args.compact, "matplotlib_version": matplotlib.__version__, "width_inches": 6.2, "minimum_text_points": 11,
        "plotted_data": data, "output_sha256": outputs,
        "notes": ["All failures retained; 1,000 attempts per main bar and 200 per size bar.",
                  "Failure categories are mutually exclusive; accepted suboptimal answers are not counted as failures here.",
                  "Failure chart panels have different vertical ranges; compare counts.",
                  "Size annotations are exact accepted counts out of 200; vertical axis shows percentages.",
                  "Render at native width or larger to preserve 11-point text."]}
    (args.output / "figure-data.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print("Rendered three PNG figures and checksum receipt; zero model calls.")


if __name__ == "__main__":
    main()
