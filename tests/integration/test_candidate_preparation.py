"""F3 candidate-policy tests use development cases and synthetic decision fixtures."""

from dataclasses import replace
from pathlib import Path
import pytest

from scheduling.evaluation.preparation import (
    CandidatePolicy,
    prepare,
    generator_hash,
    _source,
)
from scheduling.evaluation.manifests import development_registry, structural_fingerprint
from scheduling.evaluation.cases import BenchmarkCase, case_bundle, load_cases
from scheduling.evaluation.scoring import digest
from scheduling.evaluation.runner import read
from scheduling.schema import Schedule
from scheduling.validation import validate_schedule


@pytest.fixture(scope="module")
def pilot(tmp_path_factory):
    directory = tmp_path_factory.mktemp("candidate-parent") / "pilot"
    policy = CandidatePolicy(wall_seconds=180)
    manifest = prepare(directory, policy, 716, development_registry({}))
    return directory, policy, manifest


def test_deterministic_whole_family_quotas_witnesses_and_exclusions(pilot, tmp_path):
    directory, policy, manifest = pilot
    cases = load_cases(directory / "cases.json")
    assert manifest["quota_complete"] and len(cases) == 48
    assert manifest["family_count"] == 24
    assert set(manifest["counts"].values()) == {1}
    assert manifest["repair_events"] == {"blocked": 8, "deadline": 8, "fixed_start": 8}
    assert manifest["coupled_sat_repairs"] > 0
    assert manifest["positive_preference_cases"] == 24
    assert (
        manifest["human_fixture_review"]
        == manifest["human_language_review"]
        == "pending"
    )
    again = prepare(tmp_path / "again", policy, 716, development_registry({}))
    assert digest(case_bundle(load_cases(tmp_path / "again/cases.json"))) == digest(
        case_bundle(cases)
    )
    assert again["cases"] == manifest["cases"]
    registry = read(directory / "development-registry.json")
    inspected = load_cases(directory / "inspected.json")
    assert len(inspected) >= 48
    assert {structural_fingerprint(c.problem) for c in inspected} <= set(
        registry["fingerprints"]
    )
    assert {c.group_id for c in cases} == set(
        manifest["structural_audit"]["family_for_group"]
    )
    for c in cases:
        assert c.split == "development"
        pair = [other for other in cases if other.group_id == c.group_id]
        assert {other.problem.task_type for other in pair} == {"generation", "repair"}
        assert len({other.expected_label for other in pair}) == 1
        if c.context:
            assert validate_schedule(
                c.original_problem, c.original_schedule
            ).hard_feasible
        if c.witness:
            assert validate_schedule(c.problem, c.witness, c.context).hard_feasible
            broken = Schedule.from_list(
                [
                    {"activity_id": e.activity_id, "start_slot": 48}
                    for e in c.witness.entries
                ]
            )
            assert not validate_schedule(c.problem, broken, c.context).hard_feasible
    with pytest.raises(FileExistsError):
        prepare(directory, policy, 716, development_registry({}))


def test_original_overlap_and_rejected_candidates_remain_registered(pilot, tmp_path):
    directory, policy, _ = pilot
    original = next(
        c.original_problem for c in load_cases(directory / "cases.json") if c.context
    )
    # Calendar/instance metadata cannot hide original-only overlap.
    renamed = replace(
        original,
        instance_id="known-original",
        horizon_start="2026-10-06T00:00:00+08:00",
    )
    source = BenchmarkCase(
        "known-original", "known", "development", "controlled", "test", "0", renamed
    )
    registry = development_registry({"known-source": (source,)})
    prepare(tmp_path / "draw", replace(policy, proposals_per_family=1), 716, registry)
    ledger = read(tmp_path / "draw/ledger.json")
    assert any(r["reason"] == "development_overlap" for r in ledger)
    cumulative = read(tmp_path / "draw/development-registry.json")
    assert set(registry["fingerprints"]) <= set(cumulative["fingerprints"])
    assert all(
        structural_fingerprint(c.problem) in cumulative["fingerprints"]
        for c in load_cases(tmp_path / "draw/inspected.json")
    )


@pytest.mark.parametrize("change", [{"reference_seconds": 0}, {"wall_seconds": 0}])
def test_exhausted_work_is_incomplete_not_fabricated_labels(tmp_path, change):
    manifest = prepare(
        tmp_path / "draw",
        replace(CandidatePolicy(), **change),
        11,
        development_registry({}),
    )
    assert not manifest["quota_complete"] and manifest["case_count"] == 0
    ledger = read(tmp_path / "draw/ledger.json")
    assert all(r["reason"] == "original_reference_unresolved" for r in ledger)
    assert all(r["original_reference"]["result"]["status"] == "UNKNOWN" for r in ledger)


@pytest.mark.parametrize("bad", [None, {}, {"format_version": "1.0"}])
def test_final_draw_requires_prior_matching_policy_decisions(tmp_path, bad):
    with pytest.raises(ValueError, match="frozen-policy"):
        prepare(
            tmp_path / "no",
            CandidatePolicy(families_per_cell=4),
            1,
            development_registry({}),
            mode="final",
            freeze=bad,
        )
    assert not (tmp_path / "no").exists()


def test_final_decision_mismatch_rejected_and_review_never_invented(tmp_path):
    policy = CandidatePolicy(families_per_cell=4, wall_seconds=0)
    registry = development_registry({})
    frozen = {
        "format_version": "1.0",
        "policy_sha256": digest(policy),
        "generator_sha256": generator_hash(),
        "registry_sha256": digest(registry),
        "draw_seed": 7,
        "policy_review_reference": "SYNTHETIC TEST ONLY",
        "model_decision_reference": "SYNTHETIC TEST ONLY",
    }
    with pytest.raises(ValueError, match="mismatch"):
        prepare(tmp_path / "bad", policy, 8, registry, mode="final", freeze=frozen)
    result = prepare(
        tmp_path / "final", policy, 7, registry, mode="final", freeze=frozen
    )
    assert result["status"] == "pending_human_review" and not result["quota_complete"]
    assert result["human_fixture_review"] == "pending"
    assert not (tmp_path / "final/development-registry.json").exists()


def test_source_grid_stays_in_day_at_largest_size():
    for seed in range(100):
        _, spec, *_ = _source(seed, ("activity_count", 2), 0, 0, CandidatePolicy())
        assert len(spec.activities) == 12 and all(
            a.availability[0].end <= 48 for a in spec.activities
        )
