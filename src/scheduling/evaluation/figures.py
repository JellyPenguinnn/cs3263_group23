"""Reproducible diagnostic figure export from independently scored records."""

from collections import Counter, defaultdict
from pathlib import Path


def export_figures(rows, directory: Path, *, evidence):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from scheduling.evaluation.metrics import (
        difficulty_rates,
        difficulty_intervals,
        robustness,
    )

    figures = []
    phase = (
        "Frozen evaluation"
        if evidence == "live_frozen"
        else (
            "Offline qualification"
            if evidence in ("offline_canned", "offline_frozen")
            else "Development"
        )
    )
    qualifier = (
        "Recorded results; scientific interpretation requires review"
        if evidence == "live_frozen"
        else "Descriptive evidence; not a frozen benchmark comparison"
    )
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), layout="constrained")
    fig.suptitle(
        f"{phase} scheduling diagnostics — {evidence}\n{qualifier}",
        fontsize=13,
    )
    difficulty = difficulty_rates(rows)
    uncertainty = {
        (r["task_type"], r["sweep"], r["level"], r["approach"]): r
        for r in difficulty_intervals(rows)
    }
    ax = axes[0, 0]
    canonical = defaultdict(list)
    for row in rows:
        if (
            row["kind"] == "controlled"
            and row["variant_id"] == "canonical"
            and row["repeat"] == 0
            and row["gold_label"] == "SAT"
        ):
            canonical[(row["task_type"], row["approach"])].append(row)
    labels = []
    values = []
    for (task, approach), items in sorted(canonical.items()):
        labels.append(f"{task}\n{'A' if approach=='direct' else 'B'}: n={len(items)}")
        values.append(sum(r["gold_valid"] for r in items) / len(items))
    ax.bar(
        labels,
        values,
        color=["#4c78a8" if "A:" in label else "#f58518" for label in labels],
    )
    ax.set(
        title="Canonical gold-SAT validity",
        ylabel="Valid / all gold-SAT attempts",
        ylim=(0, 1.12),
    )
    for i, value in enumerate(values):
        ax.text(i, value + 0.025, f"{value:.0%}", ha="center", fontsize=9)
    ax = axes[0, 1]
    categories = Counter(row["category"] for row in rows)
    ax.barh(list(categories), list(categories.values()), color="#4c78a8")
    ax.set(title="Outcome categories (all reserved attempts)", xlabel="Count")
    ax = axes[1, 0]
    repairs = defaultdict(list)
    for row in rows:
        if (
            row["task_type"] == "repair"
            and row["gold_valid"]
            and row["variant_id"] == "canonical"
            and row["repeat"] == 0
        ):
            repairs[(row["kind"], row["approach"])].append(row["objective_values"])
    labels = []
    moved = []
    shift = []
    for (kind, approach), values in sorted(repairs.items()):
        labels.append(f"{kind} / {approach}\nvalid n={len(values)}")
        moved.append(sum(v[0] for v in values) / len(values))
        shift.append(sum(v[1] for v in values) / len(values))
    xs = list(range(len(labels)))
    ax.bar([x - 0.18 for x in xs], moved, width=0.36, label="Moved activities")
    ax.bar([x + 0.18 for x in xs], shift, width=0.36, label="Shift slots")
    ax.set_xticks(xs, labels)
    ax.set(title="Valid canonical repairs only", ylabel="Mean component value")
    if labels:
        ax.legend(fontsize=8)
    ax = axes[1, 1]
    transitions = Counter()
    for row in robustness(rows):
        if (
            row["canonical_accepted"] is not None
            and row["variant_accepted"] is not None
        ):
            transitions[
                f"{int(row['canonical_accepted'])} → {int(row['variant_accepted'])}"
            ] += 1
    ax.bar(list(transitions), list(transitions.values()), color="#59a14f")
    ax.set(title="Canonical → variant acceptance", ylabel="Matched pairs")
    if not transitions:
        ax.text(
            0.5,
            0.5,
            "No matched language variants",
            ha="center",
            va="center",
            transform=ax.transAxes,
        )
    for suffix in ("png", "pdf"):
        path = directory / f"diagnostics.{suffix}"
        if path.exists():
            raise FileExistsError(path)
        fig.savefig(path, dpi=160)
        figures.append(str(path))
    plt.close(fig)
    from scheduling.evaluation.difficulty_suite import MECHANISMS, TIERS

    tiered = any(row["level"] in TIERS for row in difficulty)
    observed_sweeps = sorted({row["sweep"] for row in difficulty})
    if tiered and set(observed_sweeps) - set(MECHANISMS):
        return figures + _export_mechanism_sweeps(
            difficulty, uncertainty, directory, phase=phase, evidence=evidence, tiers=TIERS
        )
    sweeps = MECHANISMS if tiered else ("activity_count", "slack", "interaction_density", "resource_contention")
    if any(row["sweep"] in sweeps for row in difficulty):
        fig, axes = plt.subplots(
            2, len(sweeps), figsize=(13, 6), layout="constrained", sharey=True
        )
        fig.suptitle(
            f"{phase} difficulty sweeps — {evidence}\n95% family bootstrap when ≥10 groups; smaller cells descriptive (n shown)",
            fontsize=12,
        )
        for row_index, task in enumerate(("generation", "repair")):
            for col, sweep in enumerate(sweeps):
                ax = axes[row_index, col]
                for approach, style in (("direct", "o-"), ("solver_augmented", "s--")):
                    values = sorted(
                        (
                            r
                            for r in difficulty
                            if r["task_type"] == task
                            and r["sweep"] == sweep
                            and r["approach"] == approach
                        ),
                        key=lambda r: TIERS.index(r["level"]) if tiered else int(r["level"]),
                    )
                    values = [
                        r for r in values if r["sat_validity"]["rate"] is not None
                    ]
                    xs = [TIERS.index(r["level"]) if tiered else int(r["level"]) for r in values]
                    ys = [r["sat_validity"]["rate"] for r in values]
                    ax.plot(
                        xs,
                        ys,
                        style,
                        label="A" if approach == "direct" else "B",
                        alpha=0.8,
                    )
                    for x, y, r in zip(xs, ys, values):
                        interval = uncertainty[(task, sweep, r["level"], approach)][
                            "cluster_bootstrap_95"
                        ]
                        if interval is not None:
                            ax.vlines(
                                x,
                                *interval,
                                color="C0" if approach == "direct" else "C1",
                                alpha=0.7,
                            )
                        ax.annotate(
                            f"n={r['sat_validity']['denominator']}",
                            (x, y),
                            xytext=(0, 8 if approach == "direct" else -14),
                            textcoords="offset points",
                            ha="center",
                            fontsize=7,
                        )
                ax.set(
                    title=task + " / " + sweep.replace("_", " "),
                    ylim=(-0.15, 1.2),
                    xticks=list(range(5)) if tiered else [0, 1, 2],
                    xlabel="Construction tier" if tiered else "Recorded level",
                )
                if tiered:
                    ax.set_xticklabels([t.replace("_", " ") for t in TIERS], rotation=25, ha="right")
                ax.legend(fontsize=7)
                if col == 0:
                    ax.set_ylabel("Gold-SAT validity")
        for suffix in ("png", "pdf"):
            path = directory / f"difficulty.{suffix}"
            if path.exists():
                raise FileExistsError(path)
            fig.savefig(path, dpi=160)
            figures.append(str(path))
        plt.close(fig)
    return figures


def _export_mechanism_sweeps(difficulty, uncertainty, directory, *, phase, evidence, tiers):
    """Include every observed mechanism without squeezing ten columns into one row."""
    import matplotlib.pyplot as plt

    panels = sorted({(row["task_type"], row["sweep"]) for row in difficulty})
    fig, axes = plt.subplots(
        (len(panels) + 1) // 2, 2, figsize=(12, 3.3 * ((len(panels) + 1) // 2)),
        squeeze=False, layout="constrained", sharey=True,
    )
    fig.suptitle(
        f"{phase} mechanism coverage — {evidence}\n"
        "Construction strata, not measured hardness; related cases remain grouped",
        fontsize=12,
    )
    for ax, (task, sweep) in zip(axes.flat, panels):
        for approach, style in (("direct", "o-"), ("solver_augmented", "s--")):
            values = sorted(
                (row for row in difficulty if row["task_type"] == task
                 and row["sweep"] == sweep and row["approach"] == approach
                 and row["level"] in tiers and row["sat_validity"]["rate"] is not None),
                key=lambda row: tiers.index(row["level"]),
            )
            xs = [tiers.index(row["level"]) for row in values]
            ys = [row["sat_validity"]["rate"] for row in values]
            ax.plot(xs, ys, style, label="A · Direct" if approach == "direct" else "B · CP-SAT")
            for x, y, row in zip(xs, ys, values):
                interval = uncertainty[(task, sweep, row["level"], approach)]["cluster_bootstrap_95"]
                if interval is not None:
                    ax.vlines(x, *interval, color="C0" if approach == "direct" else "C1", alpha=.6)
                ax.annotate(f"n={row['sat_validity']['denominator']}", (x, y),
                            xytext=(0, 8 if approach == "direct" else -14),
                            textcoords="offset points", ha="center", fontsize=8)
        ax.set(title=task + " / " + sweep.replace("_", " "),
               ylim=(-.15, 1.2), ylabel="Gold-SAT validity", xlabel="Construction stratum")
        ax.set_xticks(range(len(tiers)), [tier.replace("_", " ") for tier in tiers],
                      rotation=20, ha="right")
        ax.legend(fontsize=8)
    for ax in list(axes.flat)[len(panels):]:
        ax.set_visible(False)
    paths = []
    try:
        for suffix in ("png", "pdf"):
            path = directory / f"difficulty.{suffix}"
            if path.exists():
                raise FileExistsError(path)
            fig.savefig(path, dpi=160)
            paths.append(str(path))
    finally:
        plt.close(fig)
    return paths


def export_tier_figures(rows, resources, directory: Path, *, evidence):
    """Paired-method bars for the five-tier study; missing time stays unavailable."""
    from scheduling.evaluation.difficulty_suite import TIERS

    if not rows or not all(r["level"] in TIERS for r in rows):
        return []
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter

    blocks = [b for b in ("controlled", "realistic", "language") if any(r["study_block"] == b for r in rows)]
    fig, axes = plt.subplots(2, len(blocks), figsize=(5 * len(blocks), 8), squeeze=False, layout="constrained")
    fig.suptitle(f"Difficulty study — {evidence}\nDescriptive tier aggregates; methods receive matched conditions; related cases are not independent", fontsize=12)
    lookup = {(r["study_block"], r["level"], r["approach"]): r for r in resources}
    for col, block in enumerate(blocks):
        for approach, offset, color, label in (("direct", -.19, "#326da8", "A · Direct LLM"),
                                               ("solver_augmented", .19, "#c66a22", "B · LLM + CP-SAT")):
            for i, tier in enumerate(TIERS):
                items = [r for r in rows if (r["study_block"], r["level"], r["approach"]) == (block, tier, approach)]
                n = len(items)
                accepted = sum(r["accepted"] is True for r in items)
                valid_rate = n > 0 and all(r["accepted"] is not None for r in items)
                rate = accepted / n if valid_rate else float("nan")
                axes[0, col].bar(i + offset, rate, .36, color=color, label=label if i == 0 else None)
                axes[0, col].text(i + offset, rate + .025 if valid_rate else .02,
                                  f"{rate:.0%}\n{accepted}/{n}" if valid_rate else "n/a", ha="center", fontsize=7)
                stats = lookup.get((block, tier, approach), {}).get("distributions", {}).get("total_seconds", {})
                mean = stats.get("mean")
                axes[1, col].bar(i + offset, mean if mean is not None else float("nan"), .36, color=color)
                axes[1, col].annotate(f"{stats.get('reported', 0)}/{n}" if mean is not None else "n/a",
                                     (i + offset, mean or 0), xytext=(0, 4), textcoords="offset points", ha="center", fontsize=7)
        axes[0, col].set(title=block.title(), ylim=(0, 1.24), ylabel="Accepted / all attempts")
        axes[0, col].yaxis.set_major_formatter(PercentFormatter(1))
        axes[0, col].set_yticks([0, .25, .5, .75, 1])
        axes[1, col].set(ylabel="Mean full-pipeline seconds", title="Recorded time; n = reported / attempts")
        axes[1, col].margins(y=.22)
        for ax in axes[:, col]:
            ax.set_xticks(range(5), [t.replace("_", " ") for t in TIERS], rotation=25, ha="right")
            # Empty tiers have no finite bars to contribute to autoscaling.
            ax.set_xlim(-.6, len(TIERS) - .4)
            ax.grid(axis="y", alpha=.2)
            ax.set_axisbelow(True)
    fig.legend(*axes[0, 0].get_legend_handles_labels(), loc="outside lower center", ncol=2, fontsize=10)
    paths = []
    for suffix in ("png", "pdf"):
        path = directory / f"tier-comparison.{suffix}"
        if path.exists():
            plt.close(fig)
            raise FileExistsError(path)
        fig.savefig(path, dpi=160)
        paths.append(str(path))
    plt.close(fig)
    return paths
