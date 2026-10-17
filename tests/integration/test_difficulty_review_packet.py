"""Fresh mathematical checks support, but never replace, human meaning review."""

import csv
import json
from pathlib import Path
import shutil

import pytest

from evaluation.prepare_case_review import prepare_review
from scheduling.evaluation.benchmark import render
from scheduling.evaluation.cases import load_cases
from scheduling.evaluation.runner import read
from scheduling.evaluation.scoring import digest


DATASET = Path(__file__).resolve().parents[2] / "benchmarks/fixtures/difficulty-v1"


def test_difficulty_review_rechecks_math_keeps_gold_and_text_pending(tmp_path, monkeypatch):
    from scheduling.evaluation import scoring

    before = {path.name: path.read_bytes() for path in DATASET.iterdir()}
    calls = []
    original_reference = scoring.reference

    def fresh_reference(case, limits):
        calls.append(case.case_id)
        return original_reference(case, limits)

    monkeypatch.setattr(scoring, "reference", fresh_reference)
    output = tmp_path / "review"
    receipt = prepare_review(DATASET, output, source_mode="difficulty-v1")
    cases = load_cases(DATASET / "controlled.json") + load_cases(DATASET / "realistic.json")
    assert len(calls) == len(set(calls)) == receipt["fresh_reference_solves"] == 80
    assert receipt["new_model_calls"] == 0
    assert receipt["human_review"] == "pending"
    assert receipt["source_mode"] == "difficulty-suite-v1"
    assert receipt["counts"]["scheduling_attempts_per_model"] == 200
    for case in cases:
        record = read(output / (digest(case.case_id) + ".json"))
        assert record["case_sha256"] == digest(case)
        assert record["gold_review_status"] == record["text_review_status"] == "pending"
        assert set(record["gold_review_checks"].values()) == {"pending"}
        assert record["offline_verification"]["independent_certificate_checked"] is True
        assert record["offline_verification"]["reference_recomputed"] is True
        assert record["reference"]["problem_sha256"] == digest(case.problem)
        for variant, checks in record["rendered_fact_checks"].items():
            assert set(checks.values()) == {"pending"}
            assert "equivalence_to_gold" in checks
            assert record["public_views"][variant]["text"] == render(case, variant, 3263).text
            assert record["rendering_sha256"][variant] == digest(record["public_views"][variant])
        if case.context:
            assert record["case"]["original_problem"]
            assert record["case"]["original_schedule"]
    with (output / "review-index.csv").open(newline="") as stream:
        index = list(csv.DictReader(stream))
    assert len(index) == 80
    assert sum(row["wording_block_selected"] == "True" for row in index) == 10
    assert sum(row["kind"] == "realistic" for row in index) == 20
    assert all(not row["gold_reviewer"] and not row["text_reviewer"] for row in index)
    assert before == {path.name: path.read_bytes() for path in DATASET.iterdir()}
    calls.clear()
    with pytest.raises(FileExistsError):
        prepare_review(DATASET, output, source_mode="difficulty-v1")
    assert calls == []


@pytest.mark.parametrize("change", ["bundle_hash", "counts", "language", "proof_problem",
                                    "certificate", "proof_status", "generator"])
def test_difficulty_review_rejects_changed_manifest_before_output(tmp_path, change):
    source = tmp_path / "source"
    shutil.copytree(DATASET, source)
    manifest = read(source / "manifest.json")
    first = load_cases(source / "controlled.json")[0]
    if change == "bundle_hash":
        manifest["case_bundle_sha256"]["controlled"] = "wrong"
    elif change == "counts":
        manifest["counts"]["unique_cases"] = 81
    elif change == "language":
        manifest["language_case_ids"] = manifest["language_case_ids"][:-1]
    elif change == "proof_problem":
        manifest["proofs"][first.case_id]["problem_sha256"] = "wrong"
    elif change == "certificate":
        # A claimed checked flag must not cause a false certificate to be trusted.
        first_unsat = next(c for c in load_cases(source / "controlled.json")
                           if c.expected_label == "UNSAT")
        cert = manifest["proofs"][first_unsat.case_id]["certificate"]
        cert["deadline"] = 48
    elif change == "proof_status":
        manifest["proofs"][first.case_id]["reference_status"] = "UNKNOWN"
    elif change == "generator":
        manifest["generator_sha256"] = "wrong"
    (source / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        prepare_review(source, tmp_path / "review", source_mode="difficulty-v1")
    assert not (tmp_path / "review").exists()


def test_difficulty_review_fresh_solver_rejects_forged_optimum(tmp_path):
    source = tmp_path / "source"
    shutil.copytree(DATASET, source)
    bundle = read(source / "controlled.json")
    case = next(c for c in bundle["cases"] if c["expected_label"] == "SAT")
    case["expected_objective"][0] += 1
    manifest = read(source / "manifest.json")
    manifest["case_bundle_sha256"]["controlled"] = digest(bundle)
    manifest["proofs"][case["case_id"]]["expected_objective"] = case["expected_objective"]
    (source / "controlled.json").write_text(json.dumps(bundle))
    (source / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="hand-checked objective"):
        prepare_review(source, tmp_path / "review", source_mode="difficulty-v1")
    assert not (tmp_path / "review").exists()


def test_unknown_review_mode_rejected(tmp_path):
    with pytest.raises(ValueError, match="Unsupported review source mode"):
        prepare_review(DATASET, tmp_path / "review", source_mode="unknown")
