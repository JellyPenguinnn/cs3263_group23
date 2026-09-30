"""Exhaustive independent checks of the v3 binary-domain challenge matrix."""

from collections import Counter
from dataclasses import replace
from itertools import product

import pytest

from scheduling.evaluation.benchmark import (
    V3_MECHANISMS,
    generate_development_v3,
    render,
)
from scheduling.evaluation.cases import case_bundle, load_cases
from scheduling.evaluation.manifests import (
    benchmark_manifest_v3,
    structural_audit,
    structural_fingerprint,
)
from scheduling.schema import Precedence, Schedule
from scheduling.solver import SolverLimits
from scheduling.validation import validate_schedule
from tests.formal_support import assignment_objective


@pytest.fixture(scope="module")
def generated():
    return generate_development_v3(3265)


def assignments(spec):
    # Enumerate every full-window-contained start in the entire horizon, without
    # calling compiler/domain helpers. Other rules are checked by the oracle.
    domains = [
        [
            s
            for s in range(spec.horizon_slots)
            if any(
                w.start <= s and s + a.duration_slots <= w.end for w in a.availability
            )
        ]
        for a in spec.activities
    ]
    for values in product(*domains):
        yield dict(zip((a.id for a in spec.activities), values))


def answers(spec, old=None):
    return [
        (objective, starts)
        for starts in assignments(spec)
        if (objective := assignment_objective(spec, starts, old)) is not None
    ]


def test_complete_balanced_challenges_and_conservative_families(generated):
    cases, records, selection = generated
    assert len(cases) == 108 and selection["quota_complete"]
    assert not selection["exclusions"]
    assert {c.split for c in cases} == {"development"}
    assert Counter((c.problem.task_type, c.expected_label) for c in cases) == {
        (task, label): 27
        for task in ("generation", "repair")
        for label in ("SAT", "UNSAT")
    }
    assert selection["repair_event_counts"] == dict.fromkeys(
        ("blocked", "deadline", "fixed_start"), 18
    )
    assert selection["sat_repair_movement_counts"] == {"1": 9, "3": 6, "4": 6, "5": 6}
    assert len(records) == 108
    audit = structural_audit(cases)
    assert not audit["cross_split_families"]
    assert all(k == v for k, v in audit["family_for_group"].items())
    assert len({c.group_id for c in cases}) == selection["source_families"] == 9


def test_every_reference_and_validator_match_exhaustive_independent_arithmetic(
    generated,
):
    for case in generated[0]:
        old = case.original_schedule.starts() if case.context else None
        feasible = answers(case.problem, old)
        assert bool(feasible) == (case.expected_label == "SAT"), case.case_id
        if feasible:
            optimum = min(value for value, _ in feasible)
            assert optimum == case.expected_objective
            assert (
                assignment_objective(case.problem, case.witness.starts(), old)
                == optimum
            )
            assert optimum[-1] > 0  # Conflicting preferences cannot all be met.
        for starts in assignments(case.problem):
            schedule = Schedule.from_list(
                [{"activity_id": k, "start_slot": v} for k, v in starts.items()]
            )
            checked = validate_schedule(case.problem, schedule, case.context)
            independent = assignment_objective(case.problem, starts, old)
            assert checked.hard_feasible == (independent is not None), case.case_id
            if independent is not None:
                assert checked.objectives.as_tuple() == independent
        if old is not None:
            original = answers(case.original_problem)
            best = min(v for v, _ in original)
            assert [s for v, s in original if v == best] == [old]
            assert assignment_objective(case.problem, old, old) is None


def test_sat_repairs_propagate_and_each_unsat_mechanism_has_a_relaxation_witness(
    generated,
):
    for c in generated[0]:
        if not c.context:
            continue
        n, d = len(c.problem.activities), c.problem.activities[0].duration_slots
        if c.expected_label == "SAT":
            movement, shift, _ = c.expected_objective
            assert movement == (1 if c.sweep == "unary_boundary" else n)
            assert shift == (
                2 * (n - 1) * d if c.sweep == "resource_chain" else movement * d
            )
            continue
        if c.sweep == "resource_chain":
            # No unary wipeout: all of the circular capacity interaction matters.
            for a in c.problem.activities:
                assert answers(
                    replace(
                        c.problem,
                        activities=(a,),
                        constraints=tuple(
                            r
                            for r in c.problem.constraints
                            if getattr(r, "activity_id", a.id) == a.id
                        ),
                    )
                )
            relaxed = replace(
                c.problem,
                activities=tuple(
                    replace(a, resource_ids=()) for a in c.problem.activities
                ),
            )
            assert answers(relaxed)
        elif c.sweep == "precedence_chain":
            edges = [r for r in c.problem.constraints if isinstance(r, Precedence)]
            assert len(edges) == n - 1
            for edge in edges:
                relaxed = replace(
                    c.problem,
                    constraints=tuple(
                        r for r in c.problem.constraints if r.id != edge.id
                    ),
                )
                assert answers(relaxed), (c.case_id, edge.id)
        else:
            relaxed = replace(
                c.problem,
                constraints=tuple(r for r in c.problem.constraints if r.id != "event"),
            )
            assert answers(relaxed)


def test_determinism_and_seed_structure_variation(generated):
    cases, records, selection = generated
    again, again_records, again_selection = generate_development_v3(3265)
    assert case_bundle(cases) == case_bundle(again)
    assert records == again_records and selection == again_selection
    other, _, _ = generate_development_v3(3266)
    assert {structural_fingerprint(c.problem) for c in cases} != {
        structural_fingerprint(c.problem) for c in other
    }


def test_v3_manifest_and_all_renderings_preserve_evidence_boundaries(generated):
    cases, records, selection = generated
    manifest = benchmark_manifest_v3(
        cases,
        generation_seed=3265,
        rendering_seed=3263,
        selection=selection,
        records=records,
        code_revision="test-only",
    )
    assert manifest["format_version"] == "2.0"
    assert manifest["dataset_version"] == "challenge-v3-development"
    assert manifest["generator_version"] == "3.0"
    assert (
        manifest["human_fixture_review"]
        == manifest["human_language_review"]
        == "pending"
    )
    assert len(manifest["cases"]) == 108
    for c in cases:
        for variant in ("canonical", "paraphrase", "reordered"):
            view = render(c, variant, 3263)
            assert "expected_label" not in view.text and "challenge" not in view.text
            assert not any(
                tag in view.instance_id for tag in ("sat", "unsat", *V3_MECHANISMS)
            )
            assert "independent" not in view.text and "Human review" not in view.text
            assert all(a.id in view.text for a in c.problem.activities)
            assert view.original_schedule == c.original_schedule


def test_zero_budget_keeps_exclusions_and_incomplete_quota():
    cases, records, selection = generate_development_v3(
        reference_limits=SolverLimits(0)
    )
    assert not cases and not records and not selection["quota_complete"]
    assert selection["excluded_candidates"] == len(selection["exclusions"]) == 54
    assert {r["reason"] for r in selection["exclusions"]} == {
        "original_reference_unresolved"
    }


@pytest.mark.parametrize(
    "kwargs", [{"seed": True}, {"seed": -1}, {"repetitions": 0}, {"repetitions": 11}]
)
def test_invalid_generation_settings_rejected(kwargs):
    with pytest.raises(ValueError):
        generate_development_v3(**kwargs)


@pytest.mark.parametrize("git_available", [True, False])
def test_cli_generates_versioned_bundle_without_overwriting(
    tmp_path, monkeypatch, git_available
):
    if not git_available:
        import subprocess

        original_run = subprocess.run

        def missing_git(command, **kwargs):
            if command[0] == "git":
                raise FileNotFoundError("git is not installed")
            return original_run(command, **kwargs)

        monkeypatch.setattr(subprocess, "run", missing_git)
    from scheduling.cli import main

    path = tmp_path / "v3.json"
    args = [
        "benchmark-generate",
        "--version",
        "3",
        "--seed",
        "3265",
        "--output",
        str(path),
    ]
    assert main(args) == 0
    assert len(load_cases(path)) == 108
    if not git_available:
        import json

        assert (
            json.loads(path.with_suffix(".manifest.json").read_text())["code_revision"]
            == "unavailable"
        )
    before = path.read_bytes()
    assert main(args) != 0
    assert path.read_bytes() == before
