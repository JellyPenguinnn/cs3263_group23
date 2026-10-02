"""Task failures remain observations, without retries or lost reservations."""

from dataclasses import replace

import pytest

from scheduling.evaluation.failure_policy import CONTINUE_TRANSIENT_POLICY
from scheduling.evaluation.frozen import settings_digest
from scheduling.evaluation.runner import read, replay, run_batch
from scheduling.evaluation.study import _settings
from tests.integration.test_evaluation import canned
from tests.integration.test_strict_qualification import response, strict_setup


def recovery_setup():
    cases, cfg = strict_setup()
    return cases, replace(cfg, provider_failure_policy=CONTINUE_TRANSIENT_POLICY)


@pytest.fixture
def pauses(monkeypatch):
    values = []
    monkeypatch.setattr("scheduling.evaluation.failure_policy.time.sleep", values.append)
    return values


@pytest.mark.parametrize("error", ["timeout", "transport_error", "http_408", "http_500",
                                 "http_502", "http_503", "http_504"])
def test_transient_failures_continue_without_retry_even_when_consecutive(tmp_path, pauses, error):
    cases, cfg = recovery_setup()
    outputs = list(canned(cases, cfg).values())
    calls = []

    def callback(*_):
        index = len(calls)
        calls.append(index)
        if index < 3:
            return response(cfg, None, model=None, fingerprint=None, error=error,
                            status=int(error[5:]) if error.startswith("http_") else None)
        return response(cfg, outputs[index], model=cfg.model.model, fingerprint="stable")

    result = run_batch(cases, tmp_path, cfg, provider_complete=callback)
    assert result["state"] == "completed"
    assert result["completed"] == result["reserved_requests"] == 4
    assert result["reserved_output_tokens"] == 4 * cfg.model.max_tokens
    assert calls == [0, 1, 2, 3] and pauses == [30, 30, 30]
    rows, progress = replay(tmp_path)
    assert progress["not_started"] == 0 and len(rows) == 4
    assert sum(r["category"] == "provider_error" for r in rows) == 3
    assert sum(r["accepted"] for r in rows) == 1
    for file in (tmp_path / "attempts").glob("*.json"):
        saved = read(file)["payload"]["pipeline_result"]["model_response"]
        assert len(saved["attempts"]) == 1
        if saved["error"]:
            assert saved["attempts"][0]["usage"]["total_tokens"] is None
    again = run_batch(cases, tmp_path, cfg, provider_complete=lambda *_: pytest.fail("No retries"))
    assert again == result and pauses == [30, 30, 30]


@pytest.mark.parametrize("error", ["http_401", "http_403", "http_429", "http_400",
                                 "tls_verification_error", "invalid_provider_response",
                                 "request_budget_exhausted"])
def test_fatal_failure_still_stops_and_resume_remains_stopped(tmp_path, pauses, error):
    cases, cfg = recovery_setup()
    calls = []

    def callback(*_):
        calls.append(1)
        return response(cfg, None, model=None, fingerprint=None, error=error,
                        status=int(error[5:]) if error.startswith("http_") else None)

    for _ in range(2):
        result = run_batch(cases, tmp_path, cfg, provider_complete=callback)
        assert result["state"] == "stopped_provider" and result["stop_reason"] == error
    assert len(calls) == 1 and not pauses


def test_resume_after_timeout_skips_failed_task_and_preserves_later_attempts(tmp_path, pauses):
    cases, cfg = recovery_setup()
    outputs = list(canned(cases, cfg).values())

    def interrupt_before_next_request(_):
        raise KeyboardInterrupt

    callback = lambda *_: response(cfg, None, model=None, fingerprint=None, error="timeout", status=None)
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("scheduling.evaluation.failure_policy.time.sleep", interrupt_before_next_request)
        with pytest.raises(KeyboardInterrupt):
            run_batch(cases, tmp_path, cfg, provider_complete=callback)
    saved_before = {p.name: p.read_bytes() for p in (tmp_path / "attempts").glob("*.json")}
    assert len(saved_before) == 1
    remaining = iter(outputs[1:])
    callback = lambda *_: response(cfg, next(remaining), model=cfg.model.model, fingerprint="stable")
    result = run_batch(cases, tmp_path, cfg, provider_complete=callback)
    assert result["state"] == "completed" and result["completed"] == 4
    assert pauses == [30]
    assert all((tmp_path / "attempts" / name).read_bytes() == content for name, content in saved_before.items())


def test_policy_and_timeout_bound_to_resume_freeze_and_study_compatibility(tmp_path, pauses):
    cases, cfg = recovery_setup()
    outputs = iter(canned(cases, cfg).values())
    run_batch(cases, tmp_path, cfg, provider_complete=lambda *_: response(
        cfg, next(outputs), model=cfg.model.model, fingerprint="stable"))
    contract = read(tmp_path / "manifest.json")["contract"]
    legacy = replace(cfg, provider_failure_policy=None)
    assert settings_digest(cfg) != settings_digest(legacy)
    assert _settings(contract)["provider_failure_policy"] == CONTINUE_TRANSIENT_POLICY
    for changed in (legacy, replace(cfg, model=replace(cfg.model, read_timeout=1800))):
        with pytest.raises(ValueError, match="configuration/source/input changed"):
            run_batch(cases, tmp_path, changed, provider_complete=lambda *_: pytest.fail("Changed run"))


@pytest.mark.parametrize("policy", ["", "continue_transient_v0", False, {}])
def test_unknown_failure_policy_is_rejected(policy):
    _, cfg = recovery_setup()
    with pytest.raises(ValueError, match="provider failure policy"):
        replace(cfg, provider_failure_policy=policy)
