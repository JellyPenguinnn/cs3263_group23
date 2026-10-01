"""Offline HTTP fixtures for the six-call F2 diagnostic; never network calls."""

import importlib.util
import json
from pathlib import Path
import httpx
import pytest
from scheduling.providers import SoCLaaSProvider, RequestBudget

spec = importlib.util.spec_from_file_location(
    "diagnose_provider",
    Path(__file__).resolve().parents[2] / "scripts/diagnose_provider.py",
)
diagnostic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diagnostic)


def run(tmp_path, handler):
    budget = RequestBudget(6, 1536)
    with SoCLaaSProvider(
        api_key="test-only", budget=budget, transport=httpx.MockTransport(handler)
    ) as provider:
        result = diagnostic.diagnose(
            tmp_path / "run",
            complete=provider.complete,
            authorization_reference="synthetic test only",
        )
    return result, budget


def body(request, **kw):
    return {
        "model": json.loads(request.content)["model"],
        "system_fingerprint": "fp_one",
        "choices": [{"message": {"content": '{"ok":true}'}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 3, "completion_tokens": 4, "total_tokens": 7},
        **kw,
    }


def test_identical_serial_requests_caps_metadata_and_variation_preserved(tmp_path):
    calls = []

    def handler(request):
        index = len(calls)
        calls.append(json.loads(request.content))
        assert (tmp_path / "run" / f"reservation-{index:02}.json").exists()
        assert request.extensions["timeout"]["connect"] == 30
        assert request.extensions["timeout"]["read"] == 120
        return httpx.Response(
            200,
            json=body(request, system_fingerprint="fp_two" if index >= 2 else "fp_one"),
        )

    result, budget = run(tmp_path, handler)
    assert (
        len(calls) == budget.requests_used == 6
        and budget.completion_tokens_reserved == 1536
    )
    assert len({json.dumps(c["messages"]) for c in calls}) == 1
    assert all(c["max_tokens"] == 256 and c["stream"] is False for c in calls)
    assert [c["model"] for c in calls] == list(diagnostic.MODELS) * 3
    assert result["stop_reason"] is None
    assert all(
        m["observed_variation"] and m["reported_tokens"] == 21 for m in result["models"]
    )
    with pytest.raises(FileExistsError):
        diagnostic.diagnose(
            tmp_path / "run",
            complete=lambda *a: pytest.fail("No reissue"),
            authorization_reference="test",
        )


@pytest.mark.parametrize(
    "failure",
    [
        "auth",
        "rate",
        "connect",
        "timeout",
        "model",
        "truncated",
        "json",
        "duplicate",
        "wrong_type",
        "envelope",
    ],
)
def test_first_failure_stops_without_retry(tmp_path, failure):
    calls = []

    def handler(request):
        calls.append(1)
        if failure in ("auth", "rate"):
            return httpx.Response(
                401 if failure == "auth" else 429, json={"error": "untrusted"}
            )
        if failure in ("connect", "timeout"):
            raise (
                httpx.ConnectError("test-only-secret", request=request)
                if failure == "connect"
                else httpx.ReadTimeout("test-only-secret", request=request)
            )
        data = body(request)
        if failure == "model":
            data["model"] = "unexpected"
        elif failure == "envelope":
            data["choices"] = []
        elif failure == "truncated":
            data["choices"][0]["finish_reason"] = "length"
        else:
            data["choices"][0]["message"]["content"] = {
                "json": "{",
                "duplicate": '{"ok":true,"ok":true}',
                "wrong_type": '{"ok":1}',
            }[failure]
        return httpx.Response(200, json=data)

    result, budget = run(tmp_path, handler)
    assert len(calls) == budget.requests_used == 1
    assert result["stop_reason"] and result["requests_reserved"] == 1
    assert all(m["identity_observation"] == "incomplete" for m in result["models"])
    assert "test-only-secret" not in (tmp_path / "run/response-00.json").read_text()


def test_interruption_leaves_reservation_and_forbids_reissue(tmp_path):
    def interrupted(*args):
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        diagnostic.diagnose(
            tmp_path / "run", complete=interrupted, authorization_reference="test"
        )
    assert (tmp_path / "run/reservation-00.json").exists()
    assert not (tmp_path / "run/response-00.json").exists()
    with pytest.raises(FileExistsError):
        diagnostic.diagnose(
            tmp_path / "run",
            complete=lambda *a: pytest.fail("No reissue"),
            authorization_reference="test",
        )


def test_unavailable_usage_and_fingerprint_do_not_claim_zero_or_stability(tmp_path):
    result, _ = run(
        tmp_path,
        lambda req: httpx.Response(
            200, json=body(req, usage=None, system_fingerprint=None)
        ),
    )
    assert all(
        m["reported_tokens"] is None
        and m["usage_reported_attempts"] == 0
        and m["identity_observation"] == "unavailable"
        for m in result["models"]
    )


def test_cli_requires_explicit_live_flag_without_opening_provider(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(
        diagnostic.SoCLaaSProvider,
        "from_environment",
        lambda **kw: pytest.fail("Must not open provider"),
    )
    with pytest.raises(SystemExit):
        diagnostic.main([str(tmp_path / "run"), "--authorization-reference", "test"])
    assert not (tmp_path / "run").exists()


def test_reported_zero_usage_is_distinct_from_unavailable(tmp_path):
    result, _ = run(
        tmp_path,
        lambda req: httpx.Response(200, json=body(req, usage={"total_tokens": 0})),
    )
    assert all(
        m["reported_tokens"] == 0 and m["usage_reported_attempts"] == 3
        for m in result["models"]
    )


def test_copied_installation_without_git_retains_source_hashes(tmp_path, monkeypatch):
    def no_git(*args, **kwargs):
        raise FileNotFoundError("git")

    monkeypatch.setattr(diagnostic.subprocess, "run", no_git)
    result, _ = run(tmp_path, lambda req: httpx.Response(200, json=body(req)))
    manifest = json.loads((tmp_path / "run/manifest.json").read_text())
    assert manifest["code_commit"] is None
    assert manifest["source_sha256"]["diagnose_provider.py"]
    assert result["completed_responses"] == 6
