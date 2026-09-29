from dataclasses import replace
from itertools import product
import ast
from pathlib import Path
import pytest
from scheduling.schema import (
    Activity,
    BlockedInterval,
    Deadline,
    Entity,
    FixedStart,
    Precedence,
    PreferredStart,
    ReleaseTime,
    RepairContext,
    Schedule,
    Window,
)
from scheduling.validation import validate_schedule, participant_disruption
from scheduling.evaluation.benchmark import (
    tiny_fixtures,
    generate_development,
    render,
    difficulty,
)
from scheduling.evaluation.cases import case_bundle, load_cases, check_case_set
from scheduling.solver import SolverLimits, solve
from tests.formal_support import enumerate_answers, tiny


def rows(a=0, b=1):
    return [
        {"activity_id": "A", "start_slot": a},
        {"activity_id": "B", "start_slot": b},
    ]


@pytest.mark.parametrize(
    "mutated,category",
    [
        ([], "missing_activity"),
        (rows() + [{"activity_id": "A", "start_slot": 2}], "duplicate_activity"),
        (rows() + [{"activity_id": "X", "start_slot": 2}], "extra_activity"),
        ([{"activity_id": "A", "start_slot": True}], "malformed_entry"),
        (None, "malformed_schedule"),
        (rows(0, 0), "participant_overlap"),
        (rows(0, 0), "resource_overlap"),
        (rows(0, 4), "horizon"),
    ],
)
def test_deliberate_structural_and_overlap_mutations(mutated, category):
    result = validate_schedule(tiny(), mutated)
    assert not result.hard_feasible and category in {
        v.category for v in result.violations
    }


@pytest.mark.parametrize(
    "rule,category",
    [
        (ReleaseTime("r", "A", 1), "release"),
        (Deadline("d", "B", 1), "deadline"),
        (FixedStart("f", "A", 2), "fixed_start"),
        (Precedence("p", "B", "A"), "precedence"),
        (BlockedInterval("b", "participant", "P", 0, 1), "blocked"),
        (BlockedInterval("b", "resource", "R", 0, 1), "blocked"),
    ],
)
def test_each_hard_rule_has_diagnostic_id(rule, category):
    result = validate_schedule(tiny(constraints=(rule,)), rows())
    assert any(
        v.category == category and v.constraint_id == rule.id for v in result.violations
    )


def test_boundaries_preferences_and_independent_repair_arithmetic():
    spec = tiny(task_type="repair", constraints=(PreferredStart("p", "A", 0, 1, 7),))
    old = RepairContext(Schedule.from_list(rows(0, 2)))
    result = validate_schedule(spec, rows(1, 2), old)
    assert result.hard_feasible and result.objectives.as_tuple() == (1, 1, 7)
    assert participant_disruption(spec, Schedule.from_list(rows(1, 2)), old) == {
        "P": {"moved_count": 1, "total_shift_slots": 1}
    }
    assert validate_schedule(spec, rows(0, 2), old).objectives.as_tuple() == (0, 0, 0)


def test_availability_entire_interval_and_all_participants():
    spec = tiny()
    a = replace(spec.activities[0], duration_slots=2, participant_ids=("P", "Q"))
    spec = replace(
        spec,
        activities=(a,),
        participants=(
            Entity("P", (Window(0, 1), Window(1, 4))),
            Entity("Q", (Window(2, 4),)),
        ),
    )
    result = validate_schedule(spec, [{"activity_id": "A", "start_slot": 0}])
    assert not result.hard_feasible
    assert validate_schedule(
        spec, [{"activity_id": "A", "start_slot": 2}]
    ).hard_feasible
    assert not validate_schedule(
        replace(spec, resources=(Entity("R", ()),)),
        [{"activity_id": "A", "start_slot": 2}],
    ).hard_feasible


def test_validator_has_no_solver_or_objective_imports():
    import scheduling.validation as module

    tree = ast.parse(Path(module.__file__).read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            assert node.module in ("collections", "itertools", "scheduling.schema")
        if isinstance(node, ast.Import):
            assert all(
                "solver" not in n.name
                and "ortools" not in n.name
                and "objectives" not in n.name
                for n in node.names
            )


@pytest.mark.parametrize(
    "rules",
    [
        (),
        (Precedence("p", "A", "B"),),
        (Deadline("d", "B", 1),),
        (ReleaseTime("r", "A", 3),),
        (FixedStart("f", "A", 0),),
        (BlockedInterval("b", "participant", "P", 1, 3),),
        (PreferredStart("p", "A", 0, 1, 9),),
    ],
)
def test_full_cartesian_assignments_agree_with_separate_enumerator(rules):
    spec = tiny(constraints=rules)
    expected = dict(
        (tuple(sorted(starts.items())), obj) for obj, starts in enumerate_answers(spec)
    )
    for a, b in product(range(4), repeat=2):
        got = validate_schedule(spec, rows(a, b))
        key = (("A", a), ("B", b))
        assert got.hard_feasible == (key in expected)
        if got.hard_feasible:
            assert got.objectives.as_tuple() == expected[key]


@pytest.mark.parametrize("case", tiny_fixtures(), ids=lambda c: c.case_id)
def test_six_fixtures_hand_expectations_solver_and_validator(case):
    result = solve(case.problem, SolverLimits(), case.context)
    if case.expected_label == "UNSAT":
        assert result.status == "INFEASIBLE"
    else:
        assert (
            result.status == "OPTIMAL"
            and result.objectives.as_tuple() == case.expected_objective
        )
        assert validate_schedule(
            case.problem, result.schedule, case.context
        ).hard_feasible
        assert (
            validate_schedule(
                case.problem, case.witness, case.context
            ).objectives.as_tuple()
            == case.expected_objective
        )


def test_fixture_roundtrip_and_split_boundary(tmp_path):
    import json

    cases = tiny_fixtures()
    p = tmp_path / "cases.json"
    p.write_text(json.dumps(case_bundle(cases)))
    assert load_cases(p) == cases
    with pytest.raises(ValueError):
        check_case_set(
            (cases[0], replace(cases[1], group_id=cases[0].group_id, split="test"))
        )
    with pytest.raises(ValueError):
        replace(cases[-1], original_schedule=Schedule.from_list(rows(2, 0)))


def test_development_generator_renderings_and_covariates():
    cases = generate_development(19)
    assert len(cases) == 24 and case_bundle(cases) == case_bundle(
        generate_development(19)
    )
    assert {c.event for c in cases if c.context} == {
        "new blocked interval",
        "tightened deadline",
        "changed fixed appointment",
    }
    for case in cases:
        result = solve(case.problem, SolverLimits(), case.context)
        assert result.status in ("OPTIMAL", "INFEASIBLE")
        if result.schedule:
            assert validate_schedule(
                case.problem, result.schedule, case.context
            ).hard_feasible
        views = [render(case, v, 3) for v in ("canonical", "paraphrase", "reordered")]
        assert len({v.text for v in views}) == 3
        assert set(views[0].text.splitlines()[1:-1]) == set(
            views[2].text.splitlines()[1:-1]
        )
        for v in views:
            assert (
                "expected_label" not in v.text
                and "witness" not in v.text
                and v.original_schedule == case.original_schedule
            )
        assert difficulty(case.problem)["activity_count"] == len(
            case.problem.activities
        )


def test_split_allocation_is_grouped_deterministic_and_rejects_tuning_leakage():
    from scheduling.evaluation.manifests import (
        allocate_fresh_groups,
        benchmark_manifest,
    )

    groups = [f"fresh-{i}" for i in range(10)]
    registry = allocate_fresh_groups(groups, development_count=3, seed=2)
    assert list(registry.values()).count("development") == 3
    assert registry == allocate_fresh_groups(
        reversed(groups), development_count=3, seed=2
    )
    with pytest.raises(ValueError, match="development"):
        allocate_fresh_groups(
            groups, development_count=3, seed=2, used_development_groups=["fresh-0"]
        )
    manifest = benchmark_manifest(
        tiny_fixtures(), generation_seed=None, rendering_seed=3263
    )
    assert (
        manifest["case_count"] == 6
        and manifest["status"] == "development_draft_not_frozen"
    )
