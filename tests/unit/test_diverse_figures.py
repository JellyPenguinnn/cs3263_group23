"""New mechanism classes must not silently disappear from diagnostic figures."""
import matplotlib
matplotlib.use("Agg")
from matplotlib.figure import Figure
from scheduling.evaluation.figures import _export_mechanism_sweeps


def test_all_new_mechanisms_and_observed_rates_are_plotted(tmp_path, monkeypatch):
    rows, intervals = [], {}
    for i in range(10):
        for arm in ("direct", "solver_augmented"):
            row = {"task_type": "generation", "sweep": f"mechanism_{i}",
                   "level": "hard", "approach": arm,
                   "sat_validity": {"rate": i / 10, "denominator": 10}}
            rows.append(row)
            intervals[("generation", f"mechanism_{i}", "hard", arm)] = {"cluster_bootstrap_95": None}
    observed = []
    original = Figure.savefig
    def inspect(fig, *args, **kwargs):
        observed.append([(ax.get_title(), [list(line.get_ydata()) for line in ax.lines]) for ax in fig.axes])
        return original(fig, *args, **kwargs)
    monkeypatch.setattr(Figure, "savefig", inspect)
    paths = _export_mechanism_sweeps(rows, intervals, tmp_path, phase="Offline qualification",
                                    evidence="offline_canned", tiers=("easy", "moderate", "hard", "very_hard", "extreme"))
    assert len(paths) == 2
    assert len(observed[0]) == 10
    for i, (title, lines) in enumerate(observed[0]):
        assert title == f"generation / mechanism {i}"
        assert lines == [[i / 10], [i / 10]]
