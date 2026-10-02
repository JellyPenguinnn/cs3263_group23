"""Full development campaign integration, using only recorded synthetic HTTP."""

from collections import Counter
import json
import shutil

import httpx
import pytest

from scheduling.evaluation.benchmark import generate_development_v2, generate_development_v3
from scheduling.evaluation.cases import case_bundle, load_cases
from scheduling.evaluation.cli import load_config
from scheduling.evaluation.runner import OBSERVE_BACKEND_POLICY, read, replay, write_new
from scheduling.providers import SoCLaaSProvider
from tests.integration.test_evaluation import canned
from tests.integration.test_model_qualification import ROOT, load_script

prepare = load_script("prepare_development_campaign")
execute = load_script("run_development_campaign")


@pytest.fixture(scope="module", params=("qwen3.8:27b", "qwen3.6:35b"))
def campaign_packet(tmp_path_factory, request):
    directory = tmp_path_factory.mktemp("campaign-packet")
    # Reuse existing inspected development generators; no fresh held-out families.
    v2, _, _ = generate_development_v2(3264)
    v3, _, _ = generate_development_v3(3265)
    cases = tuple(c for task in ("generation", "repair") for label in ("SAT", "UNSAT")
                  for c in [c for c in v2 + v3 if (c.problem.task_type, c.expected_label) == (task, label)][:60])
    source = directory / "source.json"
    write_new(source, case_bundle(cases))
    packet = directory / "prepared"
    prepare.prepare(source, ROOT / "benchmarks/fixtures/realistic-drafts-v1.json", packet,
                    model=request.param)
    return packet


def mock_factory(packet, change=None):
    model = read(packet / "campaign.json")["model"]
    outputs = iter(content for role in execute.ROLES for content in canned(
        load_cases(packet / f"{role}-cases.json"), load_config(packet / f"{role}-config.json")
    ).values())
    calls, budgets = [], []

    def handler(request):
        calls.append(request)
        if request.method == "GET":
            return httpx.Response(200, json={"data": [{"id": model}]})
        index = len(calls) - 2  # Completion index: capabilities 0, 1; controlled starts 2.
        body = json.loads(request.content)
        assert body["model"] == model and body["max_tokens"] == 32768
        assert body["stream"] is False
        content = '{"ok":true}' if index < 2 else next(outputs)
        if change == "transient" and index in (2, 3, 4, 481, 505):
            raise httpx.ReadTimeout("test-only timeout; never log exception text", request=request)
        if change == "transient" and index == 482:
            return httpx.Response(503)
        fp = "different" if change == "realistic_drift" and index == 482 else "stable"
        if change == "mixed_backends":
            fp = ("backend-a", "backend-b", None)[index % 3]
        return httpx.Response(200, json={
            "model": model, "system_fingerprint": fp,
            "choices": [{"message": {"content": content}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 2, "completion_tokens": 3, "total_tokens": 5},
        })

    def factory(*, budget):
        budgets.append(budget)
        if change == "exhausted":
            assert budget.reserve(budget.max_completion_tokens)
        return SoCLaaSProvider(api_key="test-only", budget=budget,
                               transport=httpx.MockTransport(handler))
    return factory, calls, budgets


def invoke(packet, directory, factory):
    return execute.run_campaign(packet, directory, allow_live=True,
                                authorization_reference="TEST ONLY mocked campaign", provider_factory=factory)


def test_language_selection_balances_strata_and_retains_exact_partners(campaign_packet):
    blocks, manifest = execute.load_packet(campaign_packet)
    controlled, language = blocks["controlled"][0], blocks["language"][0]
    assert len(language) == len({c.group_id for c in language}) == 24
    assert Counter((c.problem.task_type, c.expected_label) for c in language) == {
        (task, label): 6 for task in ("generation", "repair") for label in ("SAT", "UNSAT")
    }
    assert language == prepare.select_language(tuple(reversed(controlled)))
    assert all(c in controlled for c in language)
    assert manifest["planned_scheduling_completions"] == 600
    assert manifest["total_requests"] == 603
    assert manifest["requested_output_tokens"] == 19726336
    assert manifest["policy_version"] == "development-campaign-2"
    assert all(cfg.model.read_timeout == 1800 and cfg.model.connect_timeout == 30
               and cfg.provider_failure_policy == "continue_transient_v1"
               for _, cfg, _ in blocks.values())


def test_full_600_attempt_campaign_preserves_blocks_and_shared_budget(campaign_packet, tmp_path):
    factory, calls, budgets = mock_factory(campaign_packet)
    directory = tmp_path / "campaign"
    result = invoke(campaign_packet, directory, factory)
    assert result["state"] == "completed"
    assert result["requests_reserved"] == len(calls) == 603
    assert result["requested_output_tokens_reserved"] == 19726336
    assert len(budgets) == 1 and budgets[0].max_requests == 603
    assert result["tokens"]["total_tokens"] == {
        "reported_sum": 3010, "reported_attempts": 602, "all_provider_attempts": 602,
    }
    assert result["total_wall_seconds"] > 0
    assert read(directory / "blocks.json") == {role: role for role in execute.ROLES}
    baseline = None
    for role, count in execute.EXPECTED_CALLS.items():
        assert result["blocks"][role]["completed"] == count
        cfg = load_config(directory / f"{role}-runtime-config.json")
        assert cfg.evidence == "live_development" and cfg.max_requests == count
        baseline = baseline or cfg.qualification_baseline
        assert cfg.qualification_baseline == baseline
        rows, progress = replay(directory / role)
        assert progress["completed"] == len(rows) == count
        assert {r["variant_id"] for r in rows} == (
            {"paraphrase", "reordered"} if role == "language" else {"canonical"}
        )
        assert Counter(r["approach"] for r in rows) == {"direct": count // 2, "solver_augmented": count // 2}
    with pytest.raises(FileExistsError):
        invoke(campaign_packet, directory, factory)
    assert len(calls) == 603 and len(budgets) == 1


def test_crossblock_backend_drift_stops_campaign_before_language(campaign_packet, tmp_path):
    factory, calls, _ = mock_factory(campaign_packet, "realistic_drift")
    directory = tmp_path / "campaign"
    result = invoke(campaign_packet, directory, factory)
    assert result["state"] == "stopped_campaign"
    assert result["stop_reason"] == "backend_fingerprint_changed"
    assert result["blocks"]["controlled"]["completed"] == 480
    assert result["blocks"]["realistic"]["completed"] == 1
    assert len(calls) == 484 and not (directory / "language").exists()


def test_full_campaign_continues_timeouts_across_blocks_and_analysis_keeps_failures(
    campaign_packet, tmp_path, monkeypatch,
):
    from scheduling.evaluation.study import analyze_blocks

    pauses = []
    monkeypatch.setattr("scheduling.evaluation.failure_policy.time.sleep", pauses.append)
    factory, calls, budgets = mock_factory(campaign_packet, "transient")
    directory = tmp_path / "campaign"
    result = invoke(campaign_packet, directory, factory)
    assert result["state"] == "completed" and result["stop_reason"] is None
    assert result["requests_reserved"] == len(calls) == budgets[0].requests_used == 603
    assert result["provider_failure_counts"] == {"timeout": 5, "http_503": 1}
    assert pauses == [30] * 6
    assert result["tokens"]["total_tokens"]["reported_attempts"] == 596
    assert result["tokens"]["total_tokens"]["all_provider_attempts"] == 602
    assert all(request.extensions["timeout"] == {
        "connect": 30, "read": 1800, "write": 1800, "pool": 1800,
    } for request in calls if request.method == "POST")
    rows = [r for role in execute.ROLES for r in replay(directory / role)[0]]
    assert len(rows) == 600 and sum(r["category"] == "provider_error" for r in rows) == 6
    analyzed = analyze_blocks({role: directory / role for role in execute.ROLES}, development=True)
    assert analyzed["counts"]["unique_attempts"] == 600
    assert sum(r["category"] == "provider_error" for r in analyzed["rows"]) == 6
    assert sum(r["accepted"] for r in analyzed["rows"]) == 594
    assert analyzed["settings"]["provider_failure_policy"] == "continue_transient_v1"


def test_exhausted_shared_budget_stops_before_scheduling(campaign_packet, tmp_path):
    factory, calls, _ = mock_factory(campaign_packet, "exhausted")
    directory = tmp_path / "campaign"
    result = invoke(campaign_packet, directory, factory)
    assert result["stop_reason"] == "request_budget_exhausted"
    assert len(calls) == 1 and not (directory / "controlled").exists()


def test_explicit_observation_campaign_completes_all_blocks_and_records_variation(campaign_packet, tmp_path):
    model = read(campaign_packet / "campaign.json")["model"]
    packet = tmp_path / "observed-packet"
    prepare.prepare(campaign_packet / "controlled-cases.json",
                    campaign_packet / "realistic-cases.json", packet, model=model,
                    qualification_policy=OBSERVE_BACKEND_POLICY)
    factory, calls, _ = mock_factory(packet, "mixed_backends")
    directory = tmp_path / "campaign"
    result = invoke(packet, directory, factory)
    assert result["state"] == "completed" and result["requests_reserved"] == len(calls) == 603
    assert result["backend_policy"] == OBSERVE_BACKEND_POLICY
    assert {r["system_fingerprint"] for r in result["backend_observations"]} == {"backend-a", "backend-b", None}
    assert sum(r["successful_provider_attempts"] for r in result["backend_observations"]) == 602
    for role, expected in execute.EXPECTED_CALLS.items():
        cfg = load_config(directory / f"{role}-runtime-config.json")
        assert cfg.qualification_baseline["system_fingerprints"] == ["backend-a", "backend-b"]
        assert replay(directory / role)[1]["completed"] == expected


@pytest.mark.parametrize("change", ["config", "cases", "preflight", "model", "retries"])
def test_campaign_tamper_rejected_before_provider(campaign_packet, tmp_path, change):
    packet = tmp_path / "packet"
    shutil.copytree(campaign_packet, packet)
    path = packet / {"config": "controlled-config.json", "cases": "language-cases.json",
                     "preflight": "realistic-preflight.json", "model": "campaign.json",
                     "retries": "controlled-config.json"}[change]
    data = read(path)
    if change == "config":
        data["model"]["max_tokens"] = 1024
    elif change == "cases":
        data["cases"].reverse()
    elif change == "model":
        data["model"] = "different-model"
    elif change == "retries":
        data["model"]["max_attempts"] = 2
        manifest_path = packet / "campaign.json"
        manifest = read(manifest_path)
        manifest["configs"]["controlled"] = data
        manifest_path.write_text(json.dumps(manifest))
    else:
        data["contract"]["source_sha256"] = {}
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        invoke(packet, tmp_path / "campaign", lambda **_: pytest.fail("No provider before preflight"))
    assert not (tmp_path / "campaign").exists()


@pytest.mark.parametrize("model", ["default", "", "qwen3.6:35b ", None])
def test_prepare_rejects_implicit_model_before_reading_inputs(tmp_path, model):
    with pytest.raises(ValueError, match="explicit"):
        prepare.prepare(tmp_path / "unused", tmp_path / "unused", tmp_path / "packet", model=model)
    assert not (tmp_path / "packet").exists()


@pytest.mark.parametrize("kwargs", [{}, {"allow_live": True}, {"authorization_reference": "reference"}])
def test_campaign_requires_new_explicit_authorization(tmp_path, kwargs):
    with pytest.raises(ValueError, match="authorization"):
        execute.run_campaign(tmp_path / "missing-packet", tmp_path / "campaign",
                             provider_factory=lambda **_: pytest.fail("No unauthorized provider"), **kwargs)
    assert not (tmp_path / "campaign").exists()
