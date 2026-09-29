"""Development construction, meaning-changing edges and conservative family audits."""

from collections import Counter
from dataclasses import replace
from itertools import product
import json
import pytest

from scheduling.evaluation.benchmark import (
    _v2_candidate,
    generate_development_v2,
    difficulty,
    tiny_fixtures,
    render,
)
from scheduling.evaluation.manifests import (
    structural_fingerprint,
    structural_audit,
    benchmark_manifest_v2,
)
from scheduling.schema import Precedence, PreferredStart, ProblemSpec, Schedule, to_data
from scheduling.solver import SolverLimits
from scheduling.validation import validate_schedule


@pytest.fixture(scope="module")
def generated():
    return generate_development_v2(3264)


def test_balanced_proven_matrix_and_nonempty_unsat_domains(generated):
    cases, records, selection = generated
    assert len(cases) == 144 and selection["quota_complete"]
    assert selection["exclusions"] == []
    assert Counter((c.problem.task_type, c.expected_label) for c in cases) == {
        ("generation", "SAT"): 36,
        ("generation", "UNSAT"): 36,
        ("repair", "SAT"): 36,
        ("repair", "UNSAT"): 36,
    }
    cells = Counter(
        (c.sweep, c.level, c.expected_label, c.event) for c in cases if c.context
    )
    assert len(cells) == 72 and set(cells.values()) == {1}
    for c in cases:
        if c.witness:
            assert validate_schedule(c.problem, c.witness, c.context).hard_feasible
        else:
            assert all(difficulty(c.problem)["unary_start_counts"])
            assert records[c.case_id]["gold_status"] == "INFEASIBLE"
    audit = structural_audit(cases)
    assert not audit["cross_split_families"]
    assert len(set(audit["family_for_group"].values())) == 72


def test_determinism_and_seed_changes_hard_structure(generated):
    cases, records, selection = generated
    again, again_records, again_selection = generate_development_v2(3264)
    assert to_data(cases) == to_data(again)
    assert records == again_records and selection == again_selection
    for seed in (5, 71, 3265):
        one = _v2_candidate(seed, "activity_count", 2, "blocked", "SAT", 0)[1]
        other = _v2_candidate(seed + 1, "activity_count", 2, "blocked", "SAT", 0)[1]
        assert structural_fingerprint(one) != structural_fingerprint(other)


def test_each_precedence_edge_changes_feasible_set():
    for level in range(3):
        _, spec, _, _, witness = _v2_candidate(
            3264, "interaction_density", level, "blocked", "SAT", 0
        )
        edges = [c for c in spec.constraints if isinstance(c, Precedence)]
        assert len(edges) == (0, 1, 3)[level]
        for rule in edges:
            starts = witness.starts()
            acts = {a.id: a for a in spec.activities}
            left, right = rule.before, rule.after
            gap = starts[right] - starts[left] - acts[left].duration_slots
            starts[right], starts[left] = (
                starts[left],
                starts[left] + acts[right].duration_slots + gap,
            )
            flipped = Schedule.from_list(
                [{"activity_id": k, "start_slot": v} for k, v in starts.items()]
            )
            assert not validate_schedule(spec, flipped).hard_feasible
            relaxed = replace(
                spec, constraints=tuple(c for c in spec.constraints if c.id != rule.id)
            )
            assert validate_schedule(relaxed, flipped).hard_feasible


def test_unsat_anchor_pair_independently_exhausted_for_every_event():
    for event in ("blocked", "deadline", "fixed_start"):
        _, _, spec, _, witness = _v2_candidate(
            17, "activity_count", 0, event, "UNSAT", 0
        )
        # Enumerate only the contradictory pair; all other activities keep their
        # valid constructed starts. Pair infeasibility is due to Rpair occupancy.
        for a, b in product(range(12), repeat=2):
            starts = witness.starts()
            starts.update(A0=a, A1=b)
            candidate = Schedule.from_list(
                [{"activity_id": k, "start_slot": v} for k, v in starts.items()]
            )
            assert not validate_schedule(spec, candidate).hard_feasible


def renamed(spec):
    data = spec.to_dict()
    mapping = {
        row["id"]: f"renamed-{i}-{key}"
        for key in ("activities", "participants", "resources")
        for i, row in enumerate(data[key])
    }

    def walk(v):
        if isinstance(v, str):
            return mapping.get(v, v)
        if isinstance(v, list):
            return [walk(x) for x in reversed(v)]
        if isinstance(v, dict):
            return {k: walk(x) for k, x in v.items()}
        return v

    return ProblemSpec.from_dict(walk(data))


def test_fingerprint_ignores_ids_order_and_redundant_precedence():
    spec = _v2_candidate(7, "slack", 1, "blocked", "SAT", 0)[1]
    assert structural_fingerprint(spec) == structural_fingerprint(renamed(spec))
    changed = replace(
        spec,
        constraints=tuple(
            replace(c, weight=c.weight + 1) if isinstance(c, PreferredStart) else c
            for c in spec.constraints
        ),
    )
    assert structural_fingerprint(spec) == structural_fingerprint(changed)
    assert structural_fingerprint(
        spec, include_objective=True
    ) != structural_fingerprint(changed, include_objective=True)
    chain = replace(
        spec, constraints=(Precedence("a", "A2", "A3"), Precedence("b", "A3", "A4"))
    )
    redundant = replace(
        chain, constraints=chain.constraints + (Precedence("c", "A2", "A4"),)
    )
    assert structural_fingerprint(chain) == structural_fingerprint(redundant)


def test_duplicate_hard_structure_cannot_hide_behind_new_group_or_id():
    base = tiny_fixtures()[0]
    renamed_spec = replace(renamed(base.problem), instance_id="different")
    second = replace(
        base,
        case_id="different",
        group_id="different",
        split="test",
        problem=renamed_spec,
        witness=None,
    )
    report = structural_audit((base, second))
    assert len(report["cross_split_families"]) == 1
    assert report["hard_duplicate_sets"] == [["simple-sat", "different"]]


def test_v2_manifest_has_provenance_realized_counts_and_review_status(generated):
    cases, records, selection = generated
    m = benchmark_manifest_v2(
        cases,
        generation_seed=3264,
        rendering_seed=17,
        selection=selection,
        records=records,
        code_revision="test-only",
    )
    assert m["format_version"] == "2.0" and m["human_language_review"] == "pending"
    assert m["cases"][0]["creation_method"] == "procedural"
    assert set(m["cases"][0]["renderings"]) == {"canonical", "paraphrase", "reordered"}
    for c in cases[:4]:
        for variant in ("canonical", "paraphrase", "reordered"):
            text = render(c, variant, 17).text
            assert all(a.id in text for a in c.problem.activities)
            assert "expected_label" not in text and "Human review" not in text


def test_unresolved_candidates_remain_excluded_with_explicit_unfilled_quotas():
    cases, _, selection = generate_development_v2(reference_limits=SolverLimits(0))
    assert not cases and not selection["quota_complete"]
    assert selection["excluded_candidates"] == 720
    assert (
        sum(
            r["reason"] == "quota_unfilled_after_10_candidates"
            for r in selection["exclusions"]
        )
        == 72
    )
