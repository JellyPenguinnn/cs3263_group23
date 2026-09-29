"""Regression checks for the real batch CLI's operational boundaries."""

from dataclasses import replace
import json
import ssl

import httpx
import pytest

from scheduling.cli import main
from scheduling.evaluation.benchmark import tiny_fixtures, generate_development
from scheduling.evaluation.cases import case_bundle, load_cases
from scheduling.evaluation.cli import load_config
from scheduling.evaluation.runner import plan_run, run_batch, replay
from scheduling.providers import Message, ModelConfig, RequestBudget, SoCLaaSProvider
from scheduling.providers.types import Attempt, ModelResponse, Usage
from scheduling.schema import to_data
from tests.integration.test_evaluation import config, canned


def test_full_development_preflight_checks_references_without_model_access():
    cfg = replace(
        config(evidence="live_development"),
        model=ModelConfig("qwen3.6:35b", 8192),
        max_requests=60,
        max_requested_output_tokens=491520,
    )
    plan = plan_run(tiny_fixtures() + generate_development(), cfg)
    assert plan["state"] == "ready" and plan["within_cap"]
    assert plan["planned_requests"] == 60 and plan["requested_output_tokens"] == 491520
    assert sum(plan["reference_labels"].values()) == 30
    assert plan["reference_labels"]["SAT"] > 0 and plan["reference_labels"]["UNSAT"] > 0
    assert plan["prompt_characters"]["max"] > plan["prompt_characters"]["min"]
    assert plan["contract"]["runtime"]["truststore"]


@pytest.mark.parametrize("raw", [[], {}, {"model": []}, {"model": {}, "unexpected": 1}])
def test_config_boundary_rejects_bad_objects(tmp_path, raw):
    path = tmp_path / "config.json"
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError):
        load_config(path)


@pytest.mark.parametrize("variants", ["canonical", [None], [[]]])
def test_config_boundary_rejects_bad_variants(tmp_path, variants):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({**to_data(config()), "variants": variants}))
    with pytest.raises(ValueError):
        load_config(path)


@pytest.mark.parametrize("cases", [None, {}, [None], [{}]])
def test_case_boundary_rejects_malformed_rows(tmp_path, cases):
    path = tmp_path / "cases.json"
    path.write_text(json.dumps({"format_version": "1.0", "cases": cases}))
    with pytest.raises(ValueError):
        load_cases(path)


def test_tls_verification_failure_is_sanitized_and_never_retried():
    calls = []

    def handler(request):
        calls.append(1)
        try:
            raise ssl.SSLCertVerificationError("private diagnostic must not escape")
        except ssl.SSLCertVerificationError as cause:
            raise httpx.ConnectError("private diagnostic", request=request) from cause

    with SoCLaaSProvider(
        api_key="test-only",
        budget=RequestBudget(3, 300),
        transport=httpx.MockTransport(handler),
    ) as provider:
        result = provider.complete(
            [Message("user", "test")], ModelConfig("test", 100, max_attempts=3)
        )
    assert result.error == "tls_verification_error" and len(calls) == 1
    assert not result.attempts[0].outcome_uncertain
    assert "private diagnostic" not in repr(result)


@pytest.mark.parametrize(
    "error", ["tls_verification_error", "transport_error", "timeout", "http_500"]
)
def test_provider_failure_stops_durable_run_and_resume(tmp_path, error):
    calls, events = [], []

    def failure(*_):
        calls.append(1)
        return ModelResponse(
            None, None, 0, (Attempt(1, 0, None, Usage(), error=error),), error
        )

    cfg = config(evidence="live_development")
    first = run_batch(
        tiny_fixtures(),
        tmp_path,
        cfg,
        provider_complete=failure,
        progress=events.append,
    )
    again = run_batch(tiny_fixtures(), tmp_path, cfg, provider_complete=failure)
    assert first == again and first["stop_reason"] == error
    assert first["state"] == "stopped_provider" and len(calls) == 1
    assert len(events) == 1 and events[0]["category"] == "provider_error"
    rows, state = replay(tmp_path)
    assert state["reserved"] == 1 and rows[0]["accepted"] is False


def test_cli_plan_has_no_credential_requirement_and_budget_stop_is_nonzero(
    tmp_path, capsys, monkeypatch
):
    monkeypatch.delenv("SOCLAAS_API_KEY", raising=False)
    cases, conf, responses = (
        tmp_path / name for name in ("cases.json", "config.json", "responses.json")
    )
    cfg = replace(config(), max_requests=1)
    cases.write_text(json.dumps(case_bundle(tiny_fixtures())))
    conf.write_text(json.dumps(to_data(cfg)))
    responses.write_text(json.dumps(canned(tiny_fixtures(), cfg)))
    assert main(["evaluate-plan", "--cases", str(cases), "--config", str(conf)]) == 2
    plan = json.loads(capsys.readouterr().out)
    assert plan["within_cap"] is False
    assert (
        main(
            [
                "evaluate-batch",
                "--cases",
                str(cases),
                "--config",
                str(conf),
                "--canned",
                str(responses),
                "--run-dir",
                str(tmp_path / "run"),
            ]
        )
        == 2
    )
    output = capsys.readouterr()
    assert json.loads(output.out)["state"] == "budget_exhausted"
    assert json.loads(output.err)["event"] == "attempt_completed"


def test_installed_preflight_does_not_require_git(monkeypatch):
    import scheduling.evaluation.runner as runner

    def absent(*args, **kwargs):
        raise FileNotFoundError("git is not installed")

    monkeypatch.setattr(runner.subprocess, "run", absent)
    plan = plan_run(tiny_fixtures(), config())
    assert plan["contract"]["code_commit"] is None
    assert plan["contract"]["source_sha256"]
