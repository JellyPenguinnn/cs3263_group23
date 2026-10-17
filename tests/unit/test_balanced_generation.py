"""Counterbalancing, independently justified labels and immutable preparation."""

from collections import Counter
from copy import deepcopy
from dataclasses import replace
import json

import pytest

from evaluation.prepare_balanced_generation import prepare
from scheduling.evaluation.balanced_generation import (
    DEFAULT_SEED, MECHANISMS, PROFILES, VERSION, build_suite, check_design,
    profile, validate_manifest, verify_certificate, verify_suite,
)
from scheduling.evaluation.benchmark import difficulty, render
from scheduling.evaluation.cases import case_bundle, load_cases
from scheduling.evaluation.scoring import digest
from scheduling.schema import Precedence
from scheduling.solver import SolverLimits, solve
from scheduling.validation import validate_schedule


@pytest.fixture(scope="module")
def suite():
    return build_suite()


def test_presence_cannot_predict_label_and_pairs_match(suite):
    cases, proofs = suite
    coverage = verify_suite(cases, proofs)
    assert coverage["unique_cases"] == 48
    assert coverage["construction_families"] == 3
    assert coverage["independently_checked_certificates"] == 48
    assert coverage["operative_deadline_examples"] == coverage["operative_fixed_start_examples"] == 12
    assert {c.problem.task_type for c in cases} == {"generation"}
    assert set(Counter(c.group_id for c in cases).values()) == {16}
    for p in PROFILES:
        assert Counter(c.expected_label for c in cases if profile(c.problem) == p) == {"SAT": 6, "UNSAT": 6}
    for mechanism in MECHANISMS:
        for layout in ("loose", "tight"):
            for p in PROFILES:
                pair = [c for c in cases if (c.sweep, c.level, profile(c.problem)) == (mechanism, layout, p)]
                assert len(pair) == 2
                assert pair[0].problem.constraints == pair[1].problem.constraints
                assert [(a.id, a.duration_slots, a.participant_ids, a.resource_ids) for a in pair[0].problem.activities] == [
                    (a.id, a.duration_slots, a.participant_ids, a.resource_ids) for a in pair[1].problem.activities]
                assert pair[0].group_id == pair[1].group_id
                for case in pair:
                    assert all(difficulty(case.problem)["unary_start_counts"])


def test_deadlines_and_fixed_appointments_are_operative_in_every_sat_profile(suite):
    cases, proofs = suite
    checked_counts = Counter()
    for case in cases:
        if case.expected_label != "SAT":
            continue
        assert validate_schedule(case.problem, case.witness).hard_feasible
        for kind, evidence in proofs[case.case_id]["operative_constraints"].items():
            counterexample = evidence["counterexample_schedule"]
            rule_id = evidence["constraint_id"]
            full = validate_schedule(case.problem, counterexample)
            assert not full.hard_feasible
            assert [(v.category, v.constraint_id) for v in full.violations] == [(kind, rule_id)]
            without = replace(case.problem, constraints=tuple(c for c in case.problem.constraints if c.id != rule_id))
            assert validate_schedule(without, counterexample).hard_feasible
            checked_counts[kind] += 1
    assert checked_counts == {"deadline": 12, "fixed_start": 12}


def test_unsat_certificates_reject_feasible_matched_inputs_and_weakened_proofs(suite):
    cases, proofs = suite
    for unsat in (c for c in cases if c.expected_label == "UNSAT"):
        cert = proofs[unsat.case_id]["certificate"]
        sat = next(c for c in cases if c.expected_label == "SAT" and
                   (c.sweep, c.level, profile(c.problem)) == (unsat.sweep, unsat.level, profile(unsat.problem)))
        assert verify_certificate(unsat.problem, cert)
        assert not verify_certificate(sat.problem, cert)
        assert not verify_certificate(unsat.problem, {**cert, "trusted_label": "UNSAT"})
        assert not verify_certificate(unsat.problem, {**cert, "activity_ids": [cert["activity_ids"][0]]})
        if unsat.sweep == "precedence_interaction":
            without = replace(unsat.problem, constraints=tuple(c for c in unsat.problem.constraints if not isinstance(c, Precedence)))
            assert not verify_certificate(without, cert)
            result = solve(without, SolverLimits(5))
            assert result.schedule is not None and validate_schedule(without, result.schedule).hard_feasible


@pytest.mark.parametrize("certificate", (None, [], {}, {"kind": []}, {"kind": "sat_witness"},
    {"kind": "capacity", "activity_ids": [["A1"]], "target_kind": "resource", "target_id": "R1"},
    {"kind": "precedence_window", "activity_ids": ["unknown"]}))
def test_malformed_or_unbound_certificates_fail_closed(suite, certificate):
    case = suite[0][0]
    assert not verify_certificate(case.problem, certificate)


def test_saved_suite_verification_never_uses_solver(suite, monkeypatch):
    import scheduling.solver

    def forbidden(*args, **kwargs):
        raise AssertionError("Certificate verification must not invoke CP-SAT")

    monkeypatch.setattr(scheduling.solver, "solve", forbidden)
    assert verify_suite(*suite)["independently_checked_certificates"] == 48


def test_all_public_renderings_are_complete_dated_and_metadata_free(suite):
    cases, _ = suite
    for case in cases:
        assert case.gold_review_reference is None
        for variant in ("canonical", "reordered"):
            text = render(case, variant).text
            assert "2026-10-26T09:00:00+08:00" in text
            assert "16 slots of 30 minutes" in text
            assert all(a.id in text for a in case.problem.activities)
            assert all(token not in text for token in (case.case_id, case.group_id, "SAT", "UNSAT", VERSION,
                                                       "certificate", "review", "gold", "expected_label"))
        assert {r.review_status for r in case.authored_renderings} == {"pending"}
        assert {r.creation_method for r in case.authored_renderings} == {"llm_assisted"}


@pytest.mark.parametrize("mutation", ("missing", "extra", "hash", "label", "kind", "certificate_fields",
                                    "operative", "objective", "reference"))
def test_proof_mutations_are_rejected(suite, mutation):
    cases, original = suite
    proofs = deepcopy(original)
    case = next(c for c in cases if c.expected_label == "SAT" and profile(c.problem) == "both")
    proof = proofs[case.case_id]
    if mutation == "missing":
        del proofs[case.case_id]
    elif mutation == "extra":
        proofs["unknown"] = proof
    elif mutation == "hash":
        proof["problem_sha256"] = "0" * 64
    elif mutation == "label":
        i = next(i for i, c in enumerate(cases) if c.expected_label == "UNSAT")
        cases = (*cases[:i], replace(cases[i], expected_label="SAT"), *cases[i + 1:])
    elif mutation == "kind":
        proof["certificate"] = {"kind": "capacity"}
    elif mutation == "certificate_fields":
        proof["certificate"]["asserted"] = True
    elif mutation == "operative":
        proof["operative_constraints"]["deadline"]["counterexample_schedule"] = proof["construction_witness"]
    elif mutation == "objective":
        proof["expected_objective"] = None
    else:
        proof["reference_status"] = "FEASIBLE"
    with pytest.raises(ValueError):
        verify_suite(cases, proofs)


def test_design_rejects_incomplete_scope_family_splitting_and_text_mutation(suite):
    cases, _ = suite
    with pytest.raises(ValueError, match="48 unique"):
        check_design(cases[:-1])
    changed = replace(cases[0], group_id="extra-independent-family")
    with pytest.raises(ValueError, match="conservative construction"):
        check_design((changed, *cases[1:]))
    rendering = replace(cases[0].authored_renderings[0], text=cases[0].authored_renderings[0].text.replace("2026-10-26", "2026-10-27"))
    changed = replace(cases[0], authored_renderings=(rendering, cases[0].authored_renderings[1]))
    with pytest.raises(ValueError, match="complete dated template"):
        check_design((changed, *cases[1:]))


def test_seeded_construction_and_exclusive_preparation(suite, tmp_path):
    cases, proofs = suite
    repeated, repeated_proofs = build_suite(seed=DEFAULT_SEED)
    assert case_bundle(repeated) == case_bundle(cases)
    assert repeated_proofs == proofs
    output = tmp_path / "new-dataset"
    manifest = prepare(output)
    loaded = load_cases(output / "cases.json")
    loaded_proofs = json.loads((output / "proofs.json").read_text())
    assert manifest["case_bundle_sha256"] == digest(case_bundle(loaded))
    assert manifest["proofs_sha256"] == digest(loaded_proofs)
    assert verify_suite(loaded, loaded_proofs) == manifest["coverage"]
    assert validate_manifest(loaded, loaded_proofs, manifest) == manifest["coverage"]
    for field in ("case_bundle_sha256", "proofs_sha256", "generator_sha256", "coverage", "counts",
                  "models", "expected_response_models", "budget_per_model", "structural_audit"):
        changed = deepcopy(manifest)
        changed[field] = "altered"
        with pytest.raises(ValueError, match="manifest"):
            validate_manifest(loaded, loaded_proofs, changed)
    assert manifest["new_model_calls"] == 0
    assert manifest["counts"]["scheduling_attempts_per_model"] == 96
    assert manifest["budget_per_model"]["total_http_requests"] == 99
    assert manifest["models"] == ["qwen3.6:35b", "x-test-1"]
    review = json.loads((output / "review.json").read_text())
    assert len(review["cases"]) == 48 and review["human_review_status"] == "pending"
    before = {p.name: p.read_bytes() for p in output.iterdir()}
    with pytest.raises(FileExistsError):
        prepare(output)
    assert before == {p.name: p.read_bytes() for p in output.iterdir()}
