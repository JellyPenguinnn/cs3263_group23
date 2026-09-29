"""Synthetic fixture qualification only: no real held-out study or human approval."""

from copy import deepcopy
from dataclasses import replace
import pytest
from scheduling.evaluation.benchmark import tiny_fixtures, render
from scheduling.evaluation.frozen import settings_digest, ANALYSIS_SETTINGS
from scheduling.evaluation.manifests import structural_audit, structural_fingerprint
from scheduling.evaluation.runner import (
    RunConfig,
    _contract,
    run_batch,
    plan_run,
    replay,
    read,
)
from scheduling.evaluation.scoring import digest
from scheduling.providers import ModelConfig
from scheduling.solver import SolverLimits
from tests.integration.test_evaluation import canned


def frozen_setup(mode="offline_frozen"):
    # These known fixture copies are test inputs for the guard, NOT fresh study data.
    cases = tuple(
        replace(c, split="test") for c in (tiny_fixtures()[0], tiny_fixtures()[-1])
    )
    audit = structural_audit(cases)
    # Original repair structure coincides with another fixture only if its extra
    # precedence is removed; this pair has separate family IDs.
    cfg = RunConfig(
        ModelConfig("offline-fixture", 2048),
        SolverLimits(),
        SolverLimits(),
        4,
        8192,
        evidence=mode,
        freeze={},
    )
    contract = _contract(cases, cfg)
    manifest = {
        "format_version": "2.0",
        "status": "reviewed_frozen",
        "human_fixture_review": "approved",
        "human_language_review": "approved",
        "review_references": {"gold": "TEST ONLY", "language": "TEST ONLY"},
        "cases": [
            {
                "case_id": c.case_id,
                "group_id": c.group_id,
                "source_family_id": audit["family_for_group"][c.group_id],
                "split": c.split,
                "sha256": digest(c),
                "creation_method": "fixed_fixture",
                "fixture_review": "approved",
                "language_review": "approved",
                "renderings": {
                    v: digest(render(c, v, cfg.rendering_seed)) for v in cfg.variants
                },
            }
            for c in cases
        ],
    }
    freeze = {
        k: contract[k]
        for k in ("source_sha256", "case_bundle_sha256", "request_prompt_sha256")
    }
    freeze.update(
        format_version="1.0",
        protocol_id="test-only",
        model_id=cfg.model.model,
        eligibility_reference="TEST ONLY",
        approval_reference="TEST ONLY",
        authorization_reference="TEST ONLY",
        development_registry_reference="TEST ONLY",
        development_hard_fingerprints=[],
        benchmark_manifest=manifest,
        settings_sha256=settings_digest(cfg),
        analysis_settings=ANALYSIS_SETTINGS,
    )
    return cases, replace(cfg, freeze=freeze)


def test_complete_offline_frozen_resume_replay_without_inference(tmp_path, monkeypatch):
    cases, cfg = frozen_setup()
    assert plan_run(cases, cfg)["within_cap"]
    responses = canned(cases, cfg)
    assert run_batch(cases, tmp_path, cfg, canned=responses)["completed"] == 4
    assert read(tmp_path / "manifest.json")["contract"]["format_version"] == "2.0"
    monkeypatch.setattr(
        "scheduling.evaluation.runner.run_direct",
        lambda *_a, **_k: pytest.fail("No call on resume"),
    )
    monkeypatch.setattr(
        "scheduling.evaluation.runner.run_solver_augmented",
        lambda *_a, **_k: pytest.fail("No call on resume"),
    )
    assert run_batch(cases, tmp_path, cfg, canned=responses)["reserved_requests"] == 4
    rows, progress = replay(tmp_path)
    assert progress["evidence"] == "offline_frozen" and all(r["accepted"] for r in rows)


@pytest.mark.parametrize(
    "mutation",
    [
        "missing",
        "model",
        "prompt",
        "source",
        "input",
        "settings",
        "review",
        "membership",
        "family",
        "rendering",
        "development",
        "cap",
        "eligibility",
    ],
)
def test_changed_or_unreviewed_freeze_rejected_before_any_provider_call(
    tmp_path, mutation
):
    cases, cfg = frozen_setup("live_frozen")
    f = deepcopy(cfg.freeze)
    if mutation == "missing":
        f.pop("approval_reference")
    elif mutation == "model":
        f["model_id"] = "other"
    elif mutation == "prompt":
        f["request_prompt_sha256"] = {}
    elif mutation == "source":
        f["source_sha256"] = {}
    elif mutation == "input":
        f["case_bundle_sha256"] = "wrong"
    elif mutation == "settings":
        cfg = replace(cfg, rendering_seed=9)
    elif mutation == "review":
        f["benchmark_manifest"]["human_fixture_review"] = "pending"
    elif mutation == "membership":
        f["benchmark_manifest"]["cases"].pop()
    elif mutation == "family":
        f["benchmark_manifest"]["cases"][0]["source_family_id"] = "other"
    elif mutation == "rendering":
        f["benchmark_manifest"]["cases"][0]["renderings"] = {}
    elif mutation == "development":
        f["development_hard_fingerprints"] = [structural_fingerprint(cases[0].problem)]
    elif mutation == "cap":
        cfg = replace(cfg, max_requests=1)
        f["settings_sha256"] = settings_digest(cfg)
    else:
        f["eligibility_reference"] = ""
    cfg = replace(cfg, freeze=f)
    with pytest.raises(ValueError):
        run_batch(
            cases,
            tmp_path / "run",
            cfg,
            provider_complete=lambda *_: pytest.fail("Preflight must stop calls"),
        )
    assert not (tmp_path / "run").exists()


def test_reference_failure_cannot_call_provider(tmp_path):
    cases, cfg = frozen_setup("live_frozen")
    cfg = replace(cfg, reference_solver=SolverLimits(0))
    f = deepcopy(cfg.freeze)
    f["settings_sha256"] = settings_digest(cfg)
    cfg = replace(cfg, freeze=f)
    with pytest.raises(ValueError, match="resolved label"):
        run_batch(
            cases,
            tmp_path,
            cfg,
            provider_complete=lambda *_: pytest.fail("No calls before references"),
        )
    assert not list((tmp_path / "attempts").glob("*.json"))


def test_changed_freeze_cannot_resume_completed_records(tmp_path):
    cases, cfg = frozen_setup()
    responses = canned(cases, cfg)
    run_batch(cases, tmp_path, cfg, canned=responses)
    f = deepcopy(cfg.freeze)
    f["authorization_reference"] = "different"
    with pytest.raises(ValueError, match="configuration"):
        run_batch(cases, tmp_path, replace(cfg, freeze=f), canned=responses)


def test_development_split_guard_and_provider_modes_stay_separate(tmp_path):
    cases, cfg = frozen_setup()
    with pytest.raises(ValueError, match="development"):
        run_batch(
            cases,
            tmp_path,
            replace(cfg, evidence="offline_canned", freeze=None),
            canned={},
        )
    with pytest.raises(ValueError, match="Offline runs"):
        run_batch(cases, tmp_path, cfg, provider_complete=lambda *_: None)
    with pytest.raises(ValueError, match="Live runs"):
        run_batch(
            *frozen_setup("live_frozen")[:1],
            tmp_path,
            frozen_setup("live_frozen")[1],
            canned={},
        )


def test_live_frozen_stops_on_returned_model_drift_and_never_reissues(tmp_path):
    from scheduling.providers import ModelResponse
    import json

    cases, cfg = frozen_setup("live_frozen")
    calls = []

    def callback(*_):
        calls.append(1)
        return ModelResponse(
            json.dumps({"status": "SAT", "schedule": cases[0].witness.to_list()}),
            "different-backend",
            0,
            (),
        )

    for _ in range(2):
        result = run_batch(cases, tmp_path, cfg, provider_complete=callback)
        assert result["stop_reason"] == "returned_model_mismatch"
    assert len(calls) == 1 and replay(tmp_path)[1]["not_started"] == 3


def test_draft_cli_cannot_manufacture_approval_or_run(tmp_path):
    import json
    from scheduling.cli import main
    from scheduling.schema import to_data
    from scheduling.evaluation.cases import case_bundle
    from scheduling.evaluation.cli import load_config

    cases, cfg = frozen_setup()
    plain = replace(cfg, evidence="offline_canned", freeze=None)
    for name, data in [
        ("cases", case_bundle(cases)),
        ("config", to_data(plain)),
        ("manifest", cfg.freeze["benchmark_manifest"]),
        ("registry", []),
    ]:
        (tmp_path / (name + ".json")).write_text(json.dumps(data))
    output = tmp_path / "draft.json"
    assert (
        main(
            [
                "freeze-draft",
                "--cases",
                str(tmp_path / "cases.json"),
                "--config",
                str(tmp_path / "config.json"),
                "--manifest",
                str(tmp_path / "manifest.json"),
                "--development-registry",
                str(tmp_path / "registry.json"),
                "--output",
                str(output),
            ]
        )
        == 0
    )
    draft = load_config(output)
    assert draft.freeze["approval_reference"] == ""
    with pytest.raises(ValueError, match="decision references"):
        plan_run(cases, draft)


@pytest.mark.parametrize("bad", ["case_id", "renderings", "registry"])
def test_malformed_frozen_metadata_has_explicit_validation_error(bad):
    cases, cfg = frozen_setup()
    f = deepcopy(cfg.freeze)
    if bad == "case_id":
        f["benchmark_manifest"]["cases"][0]["case_id"] = []
    elif bad == "renderings":
        f["benchmark_manifest"]["cases"][0]["renderings"] = []
    else:
        f["development_hard_fingerprints"] = ["z" * 64]
    with pytest.raises(ValueError):
        plan_run(cases, replace(cfg, freeze=f))
