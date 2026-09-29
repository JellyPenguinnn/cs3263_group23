from copy import deepcopy
from dataclasses import replace
from scheduling.evaluation.benchmark import tiny_fixtures
from scheduling.evaluation.scoring import reference, evaluate
from scheduling.evaluation.metrics import analysis_details
from scheduling.schema import PipelineResult, Schedule
from scheduling.solver import SolverLimits


def test_violations_count_instances_not_multiple_occurrences_and_retains_failures():
    case = tiny_fixtures()[0]
    bad = Schedule.from_list(
        [{"activity_id": "A", "start_slot": 0}, {"activity_id": "B", "start_slot": 0}]
    )
    ref = reference(case, SolverLimits())
    row = evaluate(
        case, PipelineResult(case.case_id, "canonical", "direct", "SAT", bad), ref
    )
    # The same violation listed twice must not count as two affected instances.
    row["validation"]["violations"] *= 2
    out = analysis_details([row])
    f = out["funnels"][0]
    assert f["reserved_attempts"] == 1 and f["parsed_outputs"] == 1
    assert f["gold_valid_schedules"] == 0 and f["accepted_answers"] == 0
    assert f["violation_instance_counts"] == {"participant_overlap": 1}
    assert f["missing_usage_instances"] == 1


def test_canonical_strata_and_objective_changes_keep_variant_weight_separate():
    case = tiny_fixtures()[-1]
    ref = reference(case, SolverLimits())
    a = evaluate(
        case,
        PipelineResult(case.case_id, "canonical", "direct", "SAT", case.witness),
        ref,
    )
    b = deepcopy(a)
    b["approach"] = "solver_augmented"
    v = deepcopy(a)
    v["variant_id"] = "paraphrase"
    v["objective_values"] = [2, 3, 0]
    r = deepcopy(a)
    r["kind"] = "realistic"
    r["case_id"] = "realistic"
    r["group_id"] = "realistic"
    out = analysis_details([a, b, v, r])
    assert len(out["canonical_paired_strata"]) == 2
    control = next(
        s for s in out["canonical_paired_strata"] if s["kind"] == "controlled"
    )
    assert control["pair_count"] == 1 and control["counts"]["both"] == 1
    assert out["language_transitions"][0][
        "objective_change_variant_minus_canonical"
    ] == [1, 2, 0]
    assert control["cluster_bootstrap_95"] is None


def test_difficulty_uncertainty_resamples_families_and_excludes_variants():
    from scheduling.evaluation.metrics import difficulty_intervals

    base = {
        "kind": "controlled",
        "task_type": "generation",
        "sweep": "slack",
        "level": "0",
        "approach": "direct",
        "variant_id": "canonical",
        "repeat": 0,
        "gold_label": "SAT",
        "gold_valid": True,
    }
    rows = [{**base, "group_id": str(i)} for i in range(10)]
    assert difficulty_intervals(rows)[0]["cluster_bootstrap_95"] == [1.0, 1.0]
    rows[0]["gold_valid"] = False
    first = difficulty_intervals(rows)[0]
    assert first == difficulty_intervals(rows)[0]
    assert 0 <= first["cluster_bootstrap_95"][0] < first["cluster_bootstrap_95"][1] <= 1
    variants = [{**r, "variant_id": "paraphrase"} for r in rows]
    assert difficulty_intervals(rows + variants)[0] == first
    # Many observations from too few families must never manufacture an interval.
    assert difficulty_intervals(rows[:5] * 3)[0]["cluster_bootstrap_95"] is None
