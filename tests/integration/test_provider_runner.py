"""Real adapter plus runner; HTTPX transport is synthetic and sends no network calls."""

from dataclasses import replace
import json
import ssl

import httpx
import pytest

from scheduling.evaluation.runner import run_batch, replay, read
from scheduling.providers import RequestBudget, SoCLaaSProvider
from tests.integration.test_evaluation import canned
from tests.integration.test_frozen_evaluation import frozen_setup


def setup(mode):
    cases, cfg = frozen_setup("live_frozen")
    if mode == "live_development":
        cases = tuple(replace(c, split="development") for c in cases)
        cfg = replace(cfg, evidence=mode, freeze=None)
    return cases, cfg


@pytest.mark.parametrize("mode", ["live_development", "live_frozen"])
@pytest.mark.parametrize(
    "failure,reason",
    [
        ("auth", "http_401"),
        ("rate", "http_429"),
        ("tls", "tls_verification_error"),
        ("timeout", "timeout"),
        ("bad_body", "invalid_provider_response"),
        ("deep_body", "invalid_provider_response"),
    ],
)
def test_provider_failure_saved_and_stops_all_later_calls_and_resume(
    tmp_path, mode, failure, reason
):
    cases, cfg = setup(mode)
    calls = []

    def handler(request):
        calls.append(request)
        if failure == "tls":
            raise httpx.ConnectError(
                "synthetic-private-detail", request=request
            ) from ssl.SSLCertVerificationError("untrusted")
        if failure == "timeout":
            raise httpx.ReadTimeout("synthetic-private-detail", request=request)
        if failure in ("auth", "rate"):
            return httpx.Response(
                401 if failure == "auth" else 429, text="synthetic-private-detail"
            )
        return httpx.Response(
            200,
            content=(
                b"[" * 1200 + b"]" * 1200
                if failure == "deep_body"
                else b"synthetic-private-detail"
            ),
        )

    budget = RequestBudget(4, 8192)
    with SoCLaaSProvider(
        api_key="test-only", budget=budget, transport=httpx.MockTransport(handler)
    ) as provider:
        for _ in range(2):
            result = run_batch(
                cases, tmp_path, cfg, provider_complete=provider.complete
            )
            assert (
                result["state"] == "stopped_provider"
                and result["stop_reason"] == reason
            )
            assert result["reserved_requests"] == 1
    assert len(calls) == budget.requests_used == 1
    rows, progress = replay(tmp_path)
    assert len(rows) == 1 and rows[0]["pipeline_status"] == "ERROR"
    assert progress["completed"] == 1 and progress["not_started"] == 3
    record = read(next((tmp_path / "attempts").glob("*.json")))
    response = record["payload"]["pipeline_result"]["model_response"]
    assert response["attempts"][0]["outcome_uncertain"] == (failure == "timeout")
    assert response["attempts"][0]["usage"]["total_tokens"] is None
    assert "synthetic-private-detail" not in json.dumps(record)


@pytest.mark.parametrize("mode", ["live_development", "live_frozen"])
def test_model_format_failure_is_observation_not_provider_stop(tmp_path, mode):
    cases, cfg = setup(mode)
    outputs = list(canned(cases, cfg).values())
    outputs[0] = 'Explanation before {"status":"UNSAT","schedule":null}'
    calls = []

    def handler(request):
        index = len(calls)
        calls.append(request)
        return httpx.Response(
            200,
            json={
                "model": cfg.model.model,
                "choices": [
                    {"message": {"content": outputs[index]}, "finish_reason": "stop"}
                ],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                    "total_tokens": 15,
                },
            },
        )

    budget = RequestBudget(4, 8192)
    with SoCLaaSProvider(
        api_key="test-only", budget=budget, transport=httpx.MockTransport(handler)
    ) as provider:
        for _ in range(2):
            assert (
                run_batch(cases, tmp_path, cfg, provider_complete=provider.complete)[
                    "state"
                ]
                == "completed"
            )
    assert len(calls) == budget.requests_used == 4
    rows, progress = replay(tmp_path)
    assert progress["completed"] == 4
    assert sum(r["pipeline_status"] == "INVALID_OUTPUT" for r in rows) == 1
    assert sum(r["accepted"] is True for r in rows) == 3
    assert sum(u["total_tokens"] for r in rows for u in r["usage"]) == 60
