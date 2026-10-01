"""Selected-model orchestration uses synthetic HTTP only, never a live endpoint."""

import json
import shutil

import httpx
import pytest

from scheduling.evaluation.cases import case_bundle, load_cases
from scheduling.evaluation.cli import load_config
from scheduling.evaluation.runner import read, run_batch, write_new
from scheduling.evaluation.scoring import digest
from scheduling.providers import SoCLaaSProvider
from tests.integration.test_evaluation import canned
from tests.integration.test_model_qualification import ROOT, load_script, pool

qualification = load_script("run_model_qualification")


@pytest.fixture(scope="module")
def packet(pool, tmp_path_factory):
    root = tmp_path_factory.mktemp("qualification-packet")
    source = root / "source.json"
    write_new(source, case_bundle(pool))
    output = root / "packet"
    load_script("prepare_model_qualification").prepare(
        source, ROOT / "benchmarks/manifests/expanded-development-100-20260930.json", output
    )
    return output


def factory_for(packet, *, change=None):
    cfg = load_config(packet / "qwen3.8-27b.json")
    cases = load_cases(packet / "cases.json")
    outputs = iter(canned(cases, cfg).values())
    calls, budgets = [], []

    def handler(request):
        calls.append(request)
        index = len(calls) - 1
        if request.method == "GET":
            return httpx.Response(200, json={"data": [{"id": cfg.model.model}]})
        body = json.loads(request.content)
        assert body["model"] == cfg.model.model
        assert body["max_tokens"] == 32768 and body["stream"] is False
        if change == "interrupt" and index == 1:
            raise KeyboardInterrupt("synthetic interruption")
        content = '{"ok":true}' if index <= 2 else next(outputs)
        model, fingerprint, finish = cfg.model.model, "stable", "stop"
        if change == "unknown_to_known":
            fingerprint = None if index <= 2 else "stable"
        if index == 2:
            if change == "bad_capability":
                content = '{"ok":false}'
            elif change == "truncated":
                finish = "length"
            elif change == "wrong_model":
                model = "different-model"
            elif change == "capability_drift":
                fingerprint = "different"
        if index == 3 and change == "batch_drift":
            fingerprint = "different"
        usage = {"prompt_tokens": 2, "completion_tokens": 3, "total_tokens": 5}
        if index == 1 and change in ("missing_usage", "zero_usage"):
            usage = None if change == "missing_usage" else {k: 0 for k in usage}
        return httpx.Response(200, json={
            "model": model, "system_fingerprint": fingerprint,
            "choices": [{"message": {"content": content}, "finish_reason": finish}],
            "usage": usage,
        })

    def factory(*, budget):
        budgets.append(budget)
        if change == "exhausted":
            assert budget.reserve(budget.max_completion_tokens)
        return SoCLaaSProvider(api_key="test-only", budget=budget,
                               transport=httpx.MockTransport(handler))

    return factory, calls, budgets


def invoke(packet, directory, factory):
    return qualification.qualify(
        packet, directory, allow_live=True,
        authorization_reference="TEST ONLY mocked qualification", provider_factory=factory,
    )


def test_complete_packet_shares_budget_records_baseline_and_resumes_without_calls(packet, tmp_path):
    factory, calls, budgets = factory_for(packet)
    directory = tmp_path / "qualification"
    result = invoke(packet, directory, factory)
    assert result["state"] == "completed"
    assert result["requests_reserved"] == len(calls) == 51
    assert result["requested_output_tokens_reserved"] == 1638400
    assert len(budgets) == 1 and budgets[0].max_requests == 51
    assert result["batch"]["completed"] == 48
    assert result["total_wall_seconds"] > 0
    assert result["tokens"]["total_tokens"] == {
        "reported_sum": 250, "reported_attempts": 50, "all_provider_attempts": 50,
    }
    cfg = load_config(directory / "runtime-config.json")
    assert cfg.evidence == "live_development"
    assert cfg.qualification_baseline == {
        "system_fingerprint": "stable",
        "capability_sha256": [digest(read(directory / f"capability-{i:02}.json")) for i in range(2)],
    }
    cases = load_cases(packet / "cases.json")
    assert run_batch(cases, directory / "batch", cfg,
                     provider_complete=lambda *_: pytest.fail("No repeated call"))["completed"] == 48
    with pytest.raises(FileExistsError):
        invoke(packet, directory, factory)
    assert len(calls) == 51 and len(budgets) == 1


@pytest.mark.parametrize("change,reported", [("missing_usage", 49), ("zero_usage", 50)])
def test_usage_accounting_distinguishes_missing_and_zero(packet, tmp_path, change, reported):
    factory, _, _ = factory_for(packet, change=change)
    result = invoke(packet, tmp_path / "qualification", factory)
    assert result["state"] == "completed"
    for field, per_call in (("prompt_tokens", 2), ("completion_tokens", 3), ("total_tokens", 5)):
        assert result["tokens"][field] == {
            "reported_sum": 49 * per_call,
            "reported_attempts": reported,
            "all_provider_attempts": 50,
        }


@pytest.mark.parametrize("change,reason,count", [
    ("bad_capability", "invalid_capability_answer", 3),
    ("truncated", "incomplete_completion", 3),
    ("wrong_model", "returned_model_mismatch", 3),
    ("capability_drift", "backend_fingerprint_changed", 3),
    ("batch_drift", "backend_fingerprint_changed", 4),
    ("unknown_to_known", "backend_fingerprint_changed", 4),
    ("exhausted", "request_budget_exhausted", 1),
])
def test_capability_issues_and_first_batch_drift_stop_without_more_requests(packet, tmp_path, change, reason, count):
    factory, calls, _ = factory_for(packet, change=change)
    directory = tmp_path / "qualification"
    result = invoke(packet, directory, factory)
    assert result["state"] == "stopped_qualification" and result["stop_reason"] == reason
    assert len(calls) == count
    if change in ("batch_drift", "unknown_to_known"):
        assert result["batch"]["completed"] == 1
        cfg = load_config(directory / "runtime-config.json")
        cases = load_cases(packet / "cases.json")
        assert run_batch(cases, directory / "batch", cfg,
                         provider_complete=lambda *_: pytest.fail("Stopped resume cannot call"))["stop_reason"] == reason
    else:
        assert not (directory / "batch").exists()


def test_interrupted_capability_keeps_reservation_and_cannot_be_reissued(packet, tmp_path):
    factory, calls, _ = factory_for(packet, change="interrupt")
    directory = tmp_path / "qualification"
    with pytest.raises(KeyboardInterrupt):
        invoke(packet, directory, factory)
    assert (directory / "capability-00-reservation.json").exists()
    assert not (directory / "capability-00.json").exists()
    with pytest.raises(FileExistsError):
        invoke(packet, directory, factory)
    assert len(calls) == 2


@pytest.mark.parametrize("change", ["config", "cases", "preflight"])
def test_changed_packet_rejected_before_provider_creation(packet, tmp_path, change):
    copied = tmp_path / "packet"
    shutil.copytree(packet, copied)
    path = copied / {"config": "qwen3.8-27b.json", "cases": "cases.json",
                     "preflight": "qwen3.8-27b.preflight.json"}[change]
    data = read(path)
    if change == "config":
        data["model"]["max_tokens"] = 1024
    elif change == "cases":
        data["cases"].reverse()
    else:
        data["contract"]["source_sha256"] = {}
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        invoke(copied, tmp_path / "output", lambda **_: pytest.fail("No provider"))
    assert not (tmp_path / "output").exists()


@pytest.mark.parametrize("allow,reference", [(False, "TEST ONLY"), (True, None), (True, " ")])
def test_authorization_and_live_selection_required_before_any_access(tmp_path, allow, reference):
    with pytest.raises(ValueError, match="authorization"):
        qualification.qualify(tmp_path / "missing-packet", tmp_path / "output",
                              allow_live=allow, authorization_reference=reference,
                              provider_factory=lambda **_: pytest.fail("No provider"))
    assert not (tmp_path / "output").exists()
