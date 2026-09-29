"""Reproducible diagnostic figure export from independently scored records."""

from collections import Counter, defaultdict
from pathlib import Path


def export_figures(rows, directory: Path, *, evidence):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from scheduling.evaluation.metrics import difficulty_rates, robustness

    figures = []
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), layout="constrained")
    fig.suptitle(
        f"Scheduling development diagnostics — {evidence}\nDescriptive evidence; not a frozen benchmark comparison",
        fontsize=13,
    )
    difficulty = difficulty_rates(rows)
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
            repairs[row["approach"]].append(row["objective_values"])
    labels = []
    moved = []
    shift = []
    for approach, values in sorted(repairs.items()):
        labels.append(f"{approach}\nvalid n={len(values)}")
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
    sweeps = ("activity_count", "slack", "interaction_density", "resource_contention")
    if any(row["sweep"] in sweeps for row in difficulty):
        fig, axes = plt.subplots(
            2, 4, figsize=(13, 6), layout="constrained", sharey=True
        )
        fig.suptitle(
            f"Provisional development difficulty sweeps — {evidence}\nPoints show gold-SAT denominators; tiny cells are descriptive only",
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
                        key=lambda r: r["level"],
                    )
                    values = [
                        r for r in values if r["sat_validity"]["rate"] is not None
                    ]
                    xs = [int(r["level"]) for r in values]
                    ys = [r["sat_validity"]["rate"] for r in values]
                    ax.plot(
                        xs,
                        ys,
                        style,
                        label="A" if approach == "direct" else "B",
                        alpha=0.8,
                    )
                    for x, y, r in zip(xs, ys, values):
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
                    xticks=[0, 1, 2],
                    xlabel="Recorded level",
                )
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
