#!/usr/bin/env python3
"""Render grouped acceptance charts from the audited two-model summary, offline.

Produces one PNG and vector PDF per evaluation block (matplotlib 3.10.8).
Reads no raw responses and makes no model calls.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import PercentFormatter

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "results/summary/two-model-development-20261002.json"
DEFAULT_OUTPUT = ROOT / "results/figures/two-model-development-20261002"
MODELS = ("qwen36", "qwen38")
APPROACHES = ("direct", "solver_augmented")
LABELS = {"direct": "A · Direct LLM", "solver_augmented": "B · LLM + CP-SAT"}
COLORS = {"direct": "#326DA8", "solver_augmented": "#B45B1F"}
INK, MUTED = "#182A3E", "#4F6072"
BLOCKS = {
    "controlled": ("Controlled scheduling", "240 canonical cases per approach · generation and repair",
                   "Synthetic development cases from 120 source families. Qwen3.8's one rejection is a provider failure."),
    "realistic": ("Realistic scenarios", "12 scenarios per approach · generation and repair",
                  "Small AI-assisted fictional set; human review pending. Both Qwen3.8 rejections are provider failures."),
    "language": ("Additional wording", "48 wording conditions per approach · paraphrased and reordered requests",
                 "Variants reuse 24 controlled bases. All six Qwen3.8 rejections are provider failures, not wording errors."),
}


def plot_data(summary: dict, *, models=MODELS, blocks=BLOCKS) -> dict:
    """Keep exact denominators and fail if categories no longer explain the totals."""
    data = {}
    for block in blocks:
        data[block] = {}
        for key in models:
            model = summary["models"][key]
            rows = model["accepted_by_block"][block]
            data[block][key] = {"model": model["model"], "approaches": {}}
            for approach in APPROACHES:
                row = rows[approach]
                accepted, total = row["accepted"], row["attempts"]
                if (not isinstance(accepted, int) or not isinstance(total, int)
                        or not 0 <= accepted <= total or total <= 0
                        or sum(row["categories"].values()) != total
                        or row["categories"].get("accepted", 0) != accepted):
                    raise ValueError(f"Inconsistent counts: {key}/{block}/{approach}")
                data[block][key]["approaches"][approach] = {
                    "accepted": accepted, "attempts": total,
                    "percent": 100 * accepted / total, "categories": row["categories"],
                }
    return data


def render_block(block: str, data: dict, *, report: bool = False, models=MODELS, blocks=BLOCKS):
    title, subtitle, note = blocks[block]
    if report:
        # At 6.2 inches this fits the report body without shrinking 11-point labels.
        fig, ax = plt.subplots(figsize=(6.2, 3.2))
        fig.subplots_adjust(left=0.14, right=0.98, bottom=0.14, top=0.75)
        fig.text(0.14, 0.94, title, fontsize=13, weight="bold", color=INK)
        fig.legend(handles=[Patch(color=COLORS[a], label=LABELS[a]) for a in APPROACHES],
                   loc="upper left", bbox_to_anchor=(0.125, 0.91), ncol=2, frameon=False,
                   fontsize=11, handlelength=1.4, columnspacing=1.2)
    else:
        fig, ax = plt.subplots(figsize=(10, 6.5))
        fig.subplots_adjust(left=0.105, right=0.96, bottom=0.245, top=0.72)
        fig.text(0.075, 0.943, title, fontsize=22, weight="bold", color=INK)
        fig.text(0.075, 0.894, subtitle, fontsize=11, color=MUTED)
        fig.legend(handles=[Patch(color=COLORS[a], label=LABELS[a]) for a in APPROACHES],
                   loc="upper left", bbox_to_anchor=(0.067, 0.859), ncol=2, frameon=False)
    for j, approach in enumerate(APPROACHES):
        rows = [data[key]["approaches"][approach] for key in models]
        bars = ax.bar([x + (j - 0.5) * 0.32 for x in range(2)],
                      [r["percent"] for r in rows], width=0.29, color=COLORS[approach])
        labels = [f'{r["percent"]:.1f}%' +
                  (f'\n{r["accepted"]}/{r["attempts"]}' if r["percent"] < 12 else "")
                  for r in rows]
        ax.bar_label(bars, labels=labels,
                     padding=5, fontsize=11, fontweight="bold")
        for bar, row in zip(bars, rows):
            # Short bars cannot contain an 11-point label; show that count above.
            if row["percent"] < 12:
                continue
            x = bar.get_x()+bar.get_width()/2
            ax.text(x, row["percent"]/2, f'{row["accepted"]}/{row["attempts"]}',
                    ha="center", va="center", color="white", fontsize=11)
    ax.set_xticks(range(2), [data[key]["model"] for key in models], fontsize=12)
    ax.set_xlim(-0.55, 1.55)
    ax.set_ylim(0, 118)
    ax.set_yticks(range(0, 101, 20))
    ax.yaxis.set_major_formatter(PercentFormatter(100, decimals=0))
    ax.set_ylabel("Accepted answers", fontsize=11)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#C7D0D9")
    ax.grid(axis="y", color="#E1E7ED", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0, pad=8)
    if report:
        return fig
    fig.text(0.075, 0.145, "Accepted = gold-valid feasible schedule or correct UNSAT; optimality is a separate measure.",
             fontsize=9.5, color=MUTED)
    fig.text(0.075, 0.104, "Rates above bars; accepted/total inside (above short bars). All errors remain in the denominators.",
             fontsize=9.5, color=MUTED)
    fig.text(0.075, 0.057, note, fontsize=9, color=MUTED)
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", action="store_true", help="Compact layout with labels at least 11 pt; explain limits in report captions")
    args = parser.parse_args()
    source_bytes = args.source.read_bytes()
    data = plot_data(json.loads(source_bytes))
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "text.color": INK, "axes.labelcolor": INK, "xtick.color": MUTED,
                         "ytick.color": MUTED, "pdf.fonttype": 42, "figure.facecolor": "white"})
    args.output.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for block in BLOCKS:
        fig = render_block(block, data[block], report=args.report)
        for extension in ("png", "pdf"):
            destination = args.output / f"{block}-accepted.{extension}"
            metadata = {"Creator": "CS3263 offline benchmark figures", "CreationDate": None,
                        "ModDate": None} if extension == "pdf" else {"Software": "CS3263 offline benchmark figures"}
            fig.savefig(destination, dpi=180, metadata=metadata)
            outputs[destination.name] = hashlib.sha256(destination.read_bytes()).hexdigest()
        plt.close(fig)
    receipt = {"source": args.source.name, "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
               "renderer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "matplotlib_version": matplotlib.__version__, "new_model_calls": 0,
               "layout": "report" if args.report else "standalone",
               "evidence_scope": "Exploratory development results; not held-out evidence",
               "plotted_data": data, "output_sha256": outputs}
    (args.output / "figure-data.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(f"Rendered {len(outputs)} figures and figure-data.json in {args.output}")


if __name__ == "__main__":
    main()
