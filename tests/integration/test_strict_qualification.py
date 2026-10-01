"""Strict development qualification uses the shared runner; no network access."""

from dataclasses import replace
import json

import pytest

from scheduling.evaluation.cli import load_config
from scheduling.evaluation.frozen import settings_digest
from scheduling.evaluation.runner import (
    STRICT_QUALIFICATION_POLICY, _contract, read, replay, run_batch,
)
from scheduling.evaluation.scoring import digest
from scheduling.providers import ModelResponse
from scheduling.providers.execution import execution_contract
from scheduling.providers.types import Attempt, ProviderExecution, Usage
from scheduling.schema import to_data
from tests.integration.test_evaluation import canned
from tests.integration.test_provider_runner import setup


def strict_setup():
    cases, cfg = setup("live_development")
    return cases, replace(cfg, qualification_policy=STRICT_QUALIFICATION_POLICY)


def response(cfg, content, *, model, fingerprint, error=None, status=200):
    return ModelResponse(
        content, model, 0.1,
        (Attempt(
            1, 0.1, status, Usage(), error=error,
            outcome_uncertain=error == "timeout", returned_model=model,
            finish_reason="stop" if error is None else None,
            execution=ProviderExecution(execution_contract(cfg.model), fingerprint),
        ),),
        error=error, finish_reason="stop" if error is None else None,
    )


@pytest.mark.parametrize("change,reason", [
    ("missing_model", "returned_model_mismatch"),
    ("wrong_model", "returned_model_mismatch"),
    ("fingerprint_drift", "backend_fingerprint_changed"),
    ("fingerprint_appears", "backend_fingerprint_changed"),
    ("fingerprint_disappears", "backend_fingerprint_changed"),
    ("timeout", "timeout"),
    ("http", "http_503"),
    ("invalid_envelope", "invalid_provider_response"),
])
def test_qualification_stops_before_next_call_and_stays_stopped_on_resume(tmp_path, change, reason):
    cases, cfg = strict_setup()
    outputs = list(canned(cases, cfg).values())
    calls = []

    def callback(*_):
        index = len(calls)
        calls.append(index)
        model, fingerprint, error, status = cfg.model.model, "stable", None, 200
        if index == 0 and change == "fingerprint_appears":
            fingerprint = None
        if index == 1:
            if change == "missing_model":
                model = None
            elif change == "wrong_model":
                model = "wrong-model"
            elif change == "fingerprint_drift":
                fingerprint = "different"
            elif change == "fingerprint_disappears":
                fingerprint = None
            elif change in ("timeout", "http", "invalid_envelope"):
                model = fingerprint = None
                error = {"timeout": "timeout", "http": "http_503",
                         "invalid_envelope": "invalid_provider_response"}[change]
                status = None if change == "timeout" else 503 if change == "http" else 200
        return response(cfg, None if error else outputs[index], model=model,
                        fingerprint=fingerprint, error=error, status=status)

    for _ in range(2):
        result = run_batch(cases, tmp_path, cfg, provider_complete=callback)
        assert result["state"] == "stopped_provider"
        assert result["stop_reason"] == reason
        assert result["reserved_requests"] == 2
    assert calls == [0, 1]
    rows, progress = replay(tmp_path)
    assert progress["evidence"] == "live_development"
    assert progress["completed"] == 2 and progress["not_started"] == 2
    if change in ("timeout", "http", "invalid_envelope"):
        assert sum(row["category"] == "provider_error" for row in rows) == 1
        assert sum(row["accepted"] for row in rows) == 1


def test_completed_strict_run_resumes_without_calls_and_policy_cannot_change(tmp_path):
    cases, cfg = strict_setup()
    outputs = iter(canned(cases, cfg).values())
    callback = lambda *_: response(cfg, next(outputs), model=cfg.model.model, fingerprint="stable")
    assert run_batch(cases, tmp_path, cfg, provider_complete=callback)["completed"] == 4
    no_call = lambda *_: pytest.fail("Completed or changed-policy resume must not call")
    assert run_batch(cases, tmp_path, cfg, provider_complete=no_call)["completed"] == 4
    contract = read(tmp_path / "manifest.json")["contract"]
    assert contract["config"]["qualification_policy"] == STRICT_QUALIFICATION_POLICY
    assert contract["config"]["evidence"] == "live_development"
    with pytest.raises(ValueError, match="configuration/source/input changed"):
        run_batch(cases, tmp_path, replace(cfg, qualification_policy=None), provider_complete=no_call)


def test_legacy_configuration_loads_with_unchanged_default_contract_shape(tmp_path):
    cases, cfg = setup("live_development")
    legacy = to_data(cfg)
    legacy.pop("qualification_policy")
    legacy.pop("qualification_baseline")
    path = tmp_path / "legacy.json"
    path.write_text(json.dumps(legacy))
    loaded = load_config(path)
    assert loaded.qualification_policy is None
    assert _contract(cases, loaded)["config"] == legacy


def test_legacy_frozen_settings_digest_retains_absent_policy_shape():
    _, cfg = setup("live_frozen")
    legacy = to_data(cfg)
    legacy.pop("freeze")
    legacy.pop("qualification_policy")
    legacy.pop("qualification_baseline")
    legacy["provider_execution"] = execution_contract(cfg.model)
    assert settings_digest(cfg) == digest(legacy)


def test_qualification_profile_can_seed_a_non_runnable_frozen_draft():
    from scheduling.evaluation.frozen import draft_frozen_config
    from scheduling.evaluation.manifests import development_registry

    cases, cfg = strict_setup()
    draft = draft_frozen_config(cases, cfg, {}, development_registry({}), mode="live_frozen")
    assert draft.qualification_policy is None
    assert draft.evidence == "live_frozen"
    assert draft.freeze["approval_reference"] == ""


@pytest.mark.parametrize("policy", ["strict_model_backend_v0", "", False, {}])
def test_unknown_policy_rejected(policy):
    _, cfg = setup("live_development")
    with pytest.raises(ValueError, match="Qualification policy"):
        replace(cfg, qualification_policy=policy)


@pytest.mark.parametrize("mode", ["offline_canned", "offline_frozen", "live_frozen"])
def test_development_policy_does_not_change_other_evidence_modes(mode):
    _, cfg = setup("live_frozen")
    with pytest.raises(ValueError, match="Qualification policy"):
        replace(cfg, evidence=mode, freeze=None if mode == "offline_canned" else {},
                qualification_policy=STRICT_QUALIFICATION_POLICY)
