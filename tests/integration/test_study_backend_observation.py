"""Synthetic shared-service replay tests; no network or measured model performance."""

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import tarfile

import pytest

from scheduling.evaluation.benchmark import tiny_fixtures
from scheduling.evaluation.failure_policy import CONTINUE_TRANSIENT_POLICY
from scheduling.evaluation.runner import (
    OBSERVE_BACKEND_POLICY, STRICT_QUALIFICATION_POLICY, RunConfig, read, run_batch,
)
from scheduling.evaluation.study import analyze_blocks, export_study
from scheduling.providers.execution import execution_contract
from scheduling.providers.types import Attempt, ModelConfig, ModelResponse, ProviderExecution, Usage
from scheduling.solver import SolverLimits
from tests.integration.test_evaluation import canned


def make_block(path, cases, fingerprints, *, variants=("canonical",),
               policy=OBSERVE_BACKEND_POLICY, failures=None, returned_models=None,
               baseline=None):
    count = len(cases) * len(variants) * 2
    if baseline is None:
        baseline = {"capability_sha256": ["a" * 64, "b" * 64],
                    **({"system_fingerprints": ["backend-one", "backend-two"]}
                       if policy == OBSERVE_BACKEND_POLICY else
                       {"system_fingerprint": "backend-one"})}
    cfg = RunConfig(
        ModelConfig("synthetic-study-model", 2048), SolverLimits(), SolverLimits(),
        count, count * 2048, evidence="live_development", variants=variants,
        qualification_policy=policy, qualification_baseline=baseline,
        provider_failure_policy=CONTINUE_TRANSIENT_POLICY,
    )
    outputs = iter(canned(cases, cfg).values())
    fingerprints = iter(fingerprints)
    failures = iter(failures or [None] * count)
    models = iter(returned_models or [cfg.model.model] * count)

    def callback(*_):
        content, fp, failure, model = next(outputs), next(fingerprints), next(failures), next(models)
        if failure == "timeout":
            return ModelResponse(
                None, None, 0.1,
                (Attempt(1, 0.1, None, Usage(), error="timeout", outcome_uncertain=True,
                         execution=ProviderExecution(execution_contract(cfg.model))),),
                error="timeout",
            )
        return ModelResponse(
            "{invalid" if failure == "invalid_output" else content, model, 0.1,
            (Attempt(1, 0.1, 200, Usage(2, 3, 5), returned_model=model,
                     execution=ProviderExecution(execution_contract(cfg.model), fp)),),
        )

    return run_batch(cases, path, cfg, provider_complete=callback)


def shared_blocks(tmp_path):
    controlled = (tiny_fixtures()[0],)
    realistic = (replace(tiny_fixtures()[1], kind="realistic"),)
    blocks = {name: tmp_path / name for name in ("controlled", "realistic", "language")}
    make_block(blocks["controlled"], controlled, ["backend-one", "backend-two"])
    make_block(blocks["realistic"], realistic, [None, None],
               failures=["invalid_output", "timeout"])
    make_block(blocks["language"], controlled, ["backend-one", "backend-two", None, "backend-two"],
               variants=("paraphrase", "reordered"))
    return blocks


def test_shared_service_replay_retains_all_failures_pairing_and_metadata(tmp_path, monkeypatch):
    blocks = shared_blocks(tmp_path)
    before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
              for path in blocks.values() for p in path.rglob("*.json")}
    monkeypatch.setattr("scheduling.solver.solve", lambda *a, **k: pytest.fail("No solver in replay"))
    result = analyze_blocks(blocks, development=True)
    assert result["evidence"] == "live_development"
    assert result["evidence_scope"] == "shared_service_development"
    assert "not a fixed-backend study" in result["backend_note"]
    assert result["backend_fingerprints"] == [None, "backend-one", "backend-two"]
    assert result["counts"] == dict(primary_attempts=2, realistic_attempts=2,
                                    additional_language_attempts=4, unique_attempts=8)
    assert sum(r["accepted"] for r in result["rows"]) == 6
    diagnostic = result["backend_diagnostics"]
    assert diagnostic["coverage"] == dict(
        pipeline_attempts=8, provider_attempts=8, reported_fingerprints=5,
        missing_fingerprints=3, successful_provider_responses=7,
        successful_responses_with_fingerprint=5,
    )
    assert sum(r["pipeline_attempts"] for r in diagnostic["outcomes"]) == 8
    assert sum(r["failed"] for r in diagnostic["outcomes"]) == 2
    assert {r["backend_observation"] for r in diagnostic["outcomes"]} == {
        "reported", "missing", "provider_failure",
    }
    pairs = diagnostic["pair_fingerprint_combinations"]
    assert sum(r["pairs"] for r in pairs) == 4
    assert sum(r["both_accepted"] for r in pairs) == 3
    assert sum(r["neither_accepted"] for r in pairs) == 1
    assert any(r["direct_system_fingerprint"] == "backend-one"
               and r["solver_system_fingerprint"] == "backend-two" for r in pairs)
    assert diagnostic["missing_method_pairs"] == 0
    assert before == {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in before}


def test_shared_service_requires_explicit_development_opt_in(tmp_path):
    make_block(tmp_path / "controlled", (tiny_fixtures()[0],), ["backend-one", "backend-two"])
    with pytest.raises(ValueError, match="development needs explicit opt-in"):
        analyze_blocks({"controlled": tmp_path / "controlled"})


@pytest.mark.parametrize("model", [None, "other-model"])
def test_observed_backends_never_relax_exact_model_identity(tmp_path, model):
    path = tmp_path / "controlled"
    progress = make_block(path, (tiny_fixtures()[0],), ["backend-one", "backend-two"],
                          returned_models=["synthetic-study-model", model])
    assert progress["completed"] == 2
    assert progress["stop_reason"] == "returned_model_mismatch"
    with pytest.raises(ValueError, match="Returned model differs"):
        analyze_blocks({"controlled": path}, development=True)


def test_strict_policy_still_rejects_a_complete_block_with_backend_variation(tmp_path):
    path = tmp_path / "controlled"
    progress = make_block(path, (tiny_fixtures()[0],), ["backend-one", "backend-two"],
                          policy=STRICT_QUALIFICATION_POLICY)
    assert progress["completed"] == 2
    assert progress["stop_reason"] == "backend_fingerprint_changed"
    with pytest.raises(ValueError, match="Backend fingerprint changed"):
        analyze_blocks({"controlled": path}, development=True)


@pytest.mark.parametrize("change", ["strict_policy", "capability_baseline"])
def test_incompatible_backend_policies_or_baselines_cannot_be_pooled(tmp_path, change):
    controlled, realistic = tmp_path / "controlled", tmp_path / "realistic"
    make_block(controlled, (tiny_fixtures()[0],), ["backend-one", "backend-two"])
    kwargs = ({"policy": STRICT_QUALIFICATION_POLICY} if change == "strict_policy" else
              {"baseline": {"system_fingerprints": ["backend-one"],
                            "capability_sha256": ["a" * 64, "b" * 64]}})
    make_block(realistic, (replace(tiny_fixtures()[1], kind="realistic"),),
               ["backend-one", "backend-one"], **kwargs)
    with pytest.raises(ValueError, match="Incompatible"):
        analyze_blocks({"controlled": controlled, "realistic": realistic}, development=True)


def test_mixed_backend_export_archive_and_offline_round_trip(tmp_path):
    blocks = shared_blocks(tmp_path)
    output = tmp_path / "analysis"
    expected = export_study(blocks, output, project_root=Path(__file__).resolve().parents[2],
                            development=True)
    restored = tmp_path / "restored"
    with tarfile.open(output / "reproduction.tar.gz") as archive:
        checksums = json.load(archive.extractfile("CHECKSUMS.json"))
        assert "tables/backend_outcomes.csv" in checksums
        assert "tables/backend_pair_fingerprint_combinations.csv" in checksums
        for name, checksum in checksums.items():
            assert hashlib.sha256(archive.extractfile(name).read()).hexdigest() == checksum
        archive.extractall(restored, filter="data")
    actual = analyze_blocks({role: restored / path for role, path in read(restored / "blocks.json").items()},
                             development=True)
    assert actual == expected
    assert "--development" in (restored / "REPRODUCE.txt").read_text()
