#!/usr/bin/env python3
"""Export supplementary report figures from preserved summaries, without inference.

Uses the existing acceptance renderer and matplotlib already used by report tooling.
Outputs PNG, SVG, captions and a receipt binding exact plotted data to source hashes.
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

from render_benchmark_results import (
    APPROACHES, COLORS, INK, MODELS, ROOT, plot_data, render_block,
)

NAMES = {"qwen36": "Qwen3.6", "qwen38": "Qwen3.8"}
METHODS = {"direct": "Direct", "solver_augmented": "LLM + CP-SAT"}


def style(ax, *, percent=False):
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_axisbelow(True)
    ax.grid(axis="y", color="#E1E7ED", linewidth=0.7)
    if percent:
        ax.set_ylim(0, 120)
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.yaxis.set_major_formatter(PercentFormatter(100, decimals=0))


def legend(fig):
    fig.legend(handles=[Patch(color=COLORS[a], label=METHODS[a]) for a in APPROACHES],
               loc="upper center", bbox_to_anchor=(0.5, 0.91), ncol=2, frameon=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/figures/visual-aids")
    args = parser.parse_args()
    sources = [ROOT / "results/summary" / name for name in (
        "two-model-development-20261002.json", "two-model-report-tables-20261002.json")]
    summary, tables = [json.loads(p.read_bytes()) for p in sources]
    args.output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "text.color": INK, "axes.labelcolor": INK,
                         "svg.fonttype": "none", "figure.facecolor": "white"})
    records, captions, outputs = {}, {}, {}

    def save(name, fig, data, caption):
        records[name], captions[name] = data, caption
        for extension in ("png", "svg"):
            path = args.output / f"{name}.{extension}"
            fig.savefig(path, dpi=300, metadata={"Date": None} if extension == "svg" else None)
            outputs[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        plt.close(fig)

    acceptance = plot_data(summary)
    for block, data in acceptance.items():
        qualifier = {"controlled": "240 canonical cases per method, from 120 source families",
                     "realistic": "12 AI-assisted fictional scenarios per method; human prose/gold review pending",
                     "language": "48 additional wording conditions per method, reusing 24 controlled bases"}[block]
        save(f"{block}-accepted", render_block(block, data, report=True), data,
             f"Accepted-answer rates: {qualifier}. Accepted means a gold-valid schedule or correct UNSAT, "
             "not necessarily an optimum. All failures remain in denominators. Qwen3.8 rejections are provider "
             "failures, not demonstrated reasoning or wording errors. Exploratory development data.")

    fig, axes = plt.subplots(1, 2, figsize=(6.2, 3.7))
    fig.subplots_adjust(left=0.13, right=0.98, bottom=0.17, top=0.71, wspace=0.35)
    fig.suptitle("Reference-optimum matching", fontsize=13, weight="bold", y=0.98)
    legend(fig)
    data = {}
    for ax, model in zip(axes, MODELS):
        rows = summary["models"][model]["controlled_by_task"]
        data[model] = rows
        for j, approach in enumerate(APPROACHES):
            selected = [next(r for r in rows if r["approach"] == approach and r["task"] == task)
                        for task in ("generation", "repair")]
            assert all(0 < r["gold_sat_valid"] <= r["gold_sat"] and
                       0 <= r["reference_objective_matched"] <= r["gold_sat_valid"] for r in selected)
            bars = ax.bar([x + (j - 0.5) * 0.36 for x in range(2)],
                          [100 * r["reference_objective_matched"] / r["gold_sat_valid"] for r in selected],
                          width=0.33, color=COLORS[approach])
            ax.bar_label(bars, labels=[f'{r["reference_objective_matched"]}/{r["gold_sat_valid"]}'
                                      for r in selected], padding=4 + 16 * j, fontsize=11)
        ax.set_title(NAMES[model], fontsize=11)
        ax.set_xticks([0, 1], ["Generate", "Repair"])
        style(ax, percent=True)
        ax.set_ylim(0, 135)
    axes[0].set_ylabel("Among valid SAT schedules")
    save("optimality", fig, data, "Controlled reference-optimum matching, conditional on gold-valid SAT "
         "schedules with proven reference objectives. Labels show matches/valid schedules. Successful subsets "
         "differ across methods; compare with failure-inclusive acceptance. Qwen3.8 Direct repair matches "
         "59/60, despite all 60 schedules being valid.")

    fig, axes = plt.subplots(2, 1, figsize=(6.2, 5.3))
    fig.subplots_adjust(left=0.35, right=0.81, bottom=0.12, top=0.85, hspace=0.6)
    fig.suptitle("Controlled model-call overhead", fontsize=13, weight="bold", y=0.98)
    resource_rows = []
    for model in MODELS:
        for approach in APPROACHES:
            row = next(r for r in summary["models"][model]["resources"]
                       if r["study_block"] == "controlled" and r["approach"] == approach)
            resource_rows.append({"model": model, **row})
    for ax, metric, label in zip(axes, ("model_seconds", "total_tokens"),
                                  ("Mean call time (seconds)", "Mean total tokens per call")):
        values = [r["distributions"][metric]["mean"] for r in resource_rows]
        assert all(v is not None and v >= 0 for v in values)
        bars = ax.barh(range(4), values, color=[COLORS[r["approach"]] for r in resource_rows])
        ax.set_yticks(range(4), [f'{NAMES[r["model"]]} · {METHODS[r["approach"]]}' for r in resource_rows])
        ax.invert_yaxis()
        ax.set_xlim(0, max(values) * 1.13)
        ax.bar_label(bars, labels=[f"{v:,.2f}" if metric == "model_seconds" else f"{v:,.1f}" for v in values], padding=4)
        ax.set_xlabel(label)
        ax.spines[["top", "right"]].set_visible(False)
    save("resources", fig, resource_rows, "Controlled mean model-call time and provider-reported total "
         "tokens. Time covers all 240 attempts per row, including failures, and excludes subsequent local "
         "solving. Token coverage: Qwen3.8 Direct 239/240; all other rows 240/240. Missing usage is unknown. "
         "Shared hosted backends/defaults were uncontrolled; these are not monetary costs or causal speed comparisons.")

    fig, ax = plt.subplots(figsize=(6.2, 4.4))
    fig.subplots_adjust(left=0.35, right=0.97, bottom=0.21, top=0.64)
    fig.suptitle("Controlled outcome breakdown", fontsize=13, weight="bold", y=0.98)
    categories = [("accepted", "Accepted", "#39846A"),
                  ("gold_invalid_schedule", "Invalid schedule", "#B45B1F"),
                  ("false_unsat", "False UNSAT", "#8962A8"),
                  ("invalid_output", "Invalid output", "#718295"),
                  ("provider_error", "Provider error", "#C54148")]
    rows = [{"model": model, "approach": approach,
             **summary["models"][model]["accepted_by_block"]["controlled"][approach]}
            for model in MODELS for approach in APPROACHES]
    left = [0] * 4
    for category, label, color in categories:
        values = [r["categories"].get(category, 0) for r in rows]
        bars = ax.barh(range(4), values, left=left, color=color, label=label)
        for bar, count in zip(bars, values):
            if count >= 10:
                ax.text(bar.get_x() + count / 2, bar.get_y() + bar.get_height() / 2,
                        str(count), ha="center", va="center", color="white", fontsize=11)
        left = [a + b for a, b in zip(left, values)]
    assert left == [240] * 4
    ax.set_yticks(range(4), [f'{NAMES[r["model"]]} · {METHODS[r["approach"]]}' for r in rows])
    ax.invert_yaxis()
    ax.set_xlim(0, 240)
    ax.set_xticks([0, 60, 120, 180, 240])
    ax.set_xlabel("Attempts (240 per row)")
    ax.spines[["top", "right"]].set_visible(False)
    fig.legend(handles=[Patch(color=c, label=l) for _, l, c in categories], loc="upper left",
               bbox_to_anchor=(0.03, 0.9), ncol=2, frameon=False, fontsize=11)
    fig.text(0.03, 0.04, "Small segments: Qwen3.6 CP-SAT has 1 invalid schedule;\nQwen3.8 Direct has 1 provider error.", fontsize=11)
    save("outcomes", fig, rows, "Controlled outcome counts, retaining all 240 attempts in each row. "
         "Invalid output denotes parser/schema-invalid output; invalid schedule denotes a gold-constraint "
         "violation. Small segments are explicitly noted. Acceptance includes correct UNSAT and does not "
         "guarantee optimality. Qwen3.8's controlled rejection is operational, not a demonstrated reasoning failure.")

    fig, axes = plt.subplots(1, 2, figsize=(6.2, 3.7))
    fig.subplots_adjust(left=0.13, right=0.98, bottom=0.2, top=0.71, wspace=0.35)
    fig.suptitle("Activity count and schedule validity", fontsize=13, weight="bold", y=0.98)
    legend(fig)
    data = {}
    for ax, model in zip(axes, MODELS):
        data[model] = {}
        for approach in APPROACHES:
            rows = sorted([r for r in tables["models"][model]["difficulty"]
                           if r["sweep"] == "activity_count" and r["task"] == "generation"
                           and r["gold_label"] == "SAT" and r["approach"] == approach], key=lambda r: int(r["level"]))
            assert len(rows) == 3 and all(r["attempts"] == 5 and len(r["activity_counts"]) == 1 for r in rows)
            data[model][approach] = rows
            xs = [r["activity_counts"][0] for r in rows]
            ys = [100 * r["accepted"] / r["attempts"] for r in rows]
            ax.plot(xs, ys, marker="o" if approach == "direct" else "s", color=COLORS[approach],
                    linestyle="-" if approach == "direct" else "--", linewidth=2)
            for x, y, r in zip(xs, ys, rows):
                # Offset overlapping perfect-series labels in opposite directions.
                offset = -18 if approach == "direct" else 8
                ax.annotate(f'{r["accepted"]}/{r["attempts"]}', (x, y), xytext=(0, offset),
                            textcoords="offset points", ha="center", fontsize=11)
        ax.set_title(NAMES[model], fontsize=11)
        ax.set_xticks([4, 8, 12])
        ax.set_xlim(3, 13)
        ax.set_xlabel("Activities")
        style(ax, percent=True)
    axes[0].set_ylabel("Gold-valid schedules")
    save("activity-count", fig, data, "Controlled SAT generation activity-count sweep: five cases per "
         "level and method. Labels show valid/attempted. Qwen3.6 Direct declines across these levels. "
         "Qwen3.8 Direct's 4/5 at 12 activities includes one provider failure, not a demonstrated "
         "reasoning error. This selected sweep is descriptive, not a causal threshold or a claim "
         "that all difficulty dimensions have monotonic effects. Lines connect tested levels only.")

    receipt = {"scope": summary["evidence_scope"], "new_model_calls": 0,
               "source_sha256": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
               "renderer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "acceptance_renderer_sha256": hashlib.sha256((ROOT / "scripts/render_benchmark_results.py").read_bytes()).hexdigest(),
               "matplotlib_version": matplotlib.__version__, "output_sha256": outputs, "plotted_data": records}
    (args.output / "figure-data.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    guide = ["# Statistical visual aids", "", "Generated offline from saved development summaries. No model calls.", "",
             "PNG: 300 dpi. SVG: vector, editable text. Place at 6.2 inches wide to preserve 11-point labels.", "",
             "Choose figures that support the narrative; the report body is limited to ten pages. "
             "Inserting figures requires a fresh report render, page-count check and visual review.", "",
             "Regenerate with the report plotting environment: `python scripts/render_report_visual_aids.py`.", ""]
    for name, caption in captions.items():
        guide += [f"## {name}", "", f"[PNG]({name}.png) · [SVG]({name}.svg)", "", caption, ""]
    (args.output / "README.md").write_text("\n".join(guide), encoding="utf-8")
    print(f"Created {len(outputs)} image exports, captions and figure-data.json in {args.output}")


if __name__ == "__main__":
    main()
