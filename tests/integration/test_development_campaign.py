"""Full development campaign integration, using only recorded synthetic HTTP."""

from collections import Counter
import json
import shutil

import httpx
import pytest

from scheduling.evaluation.benchmark import generate_development_v2, generate_development_v3
from scheduling.evaluation.cases import case_bundle, load_cases
from scheduling.evaluation.cli import load_config
from scheduling.evaluation.runner import read, replay, write_new
from scheduling.providers import SoCLaaSProvider
from tests.integration.test_evaluation import canned
from tests.integration.test_model_qualification import ROOT, load_script

prepare = load_script("prepare_development_campaign")
execute = load_script("run_development_campaign")


@pytest.fixture(scope="module")
def campaign_packet(tmp_path_factory):
    directory = tmp_path_factory.mktemp("campaign-packet")
    # Reuse existing inspected development generators; no fresh held-out families.
    v2, _, _ = generate_development_v2(3264)
    v3, _, _ = generate_development_v3(3265)
    cases = tuple(c for task in ("generation", "repair") for label in ("SAT", "UNSAT")
                  for c in [c for c in v2 + v3 if (c.problem.task_type, c.expected_label) == (task, label)][:60])
    source = directory / "source.json"
    write_new(source, case_bundle(cases))
    packet = directory / "prepared"
    prepare.prepare(source, ROOT / "benchmarks/fixtures/realistic-drafts-v1.json", packet)
    return packet


def mock_factory(packet, change=None):
    outputs = iter(content for role in execute.ROLES for content in canned(
        load_cases(packet / f"{role}-cases.json"), load_config(packet / f"{role}-config.json")
    ).values())
    calls, budgets = [], []

    def handler(request):
        calls.append(request)
        if request.method == "GET":
            return httpx.Response(200, json={"data": [{"id": "qwen3.8:27b"}]})
        index = len(calls) - 2  # Completion index: capabilities 0, 1; controlled starts 2.
        body = json.loads(request.content)
        assert body["model"] == "qwen3.8:27b" and body["max_tokens"] == 32768
        assert body["stream"] is False
        content = '{"ok":true}' if index < 2 else next(outputs)
        fp = "different" if change == "realistic_drift" and index == 482 else "stable"
        return httpx.Response(200, json={
            "model": "qwen3.8:27b", "system_fingerprint": fp,
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


def test_exhausted_shared_budget_stops_before_scheduling(campaign_packet, tmp_path):
    factory, calls, _ = mock_factory(campaign_packet, "exhausted")
    directory = tmp_path / "campaign"
    result = invoke(campaign_packet, directory, factory)
    assert result["stop_reason"] == "request_budget_exhausted"
    assert len(calls) == 1 and not (directory / "controlled").exists()


@pytest.mark.parametrize("change", ["config", "cases", "preflight"])
def test_campaign_tamper_rejected_before_provider(campaign_packet, tmp_path, change):
    packet = tmp_path / "packet"
    shutil.copytree(campaign_packet, packet)
    path = packet / {"config": "controlled-config.json", "cases": "language-cases.json",
                     "preflight": "realistic-preflight.json"}[change]
    data = read(path)
    if change == "config":
        data["model"]["max_tokens"] = 1024
    elif change == "cases":
        data["cases"].reverse()
    else:
        data["contract"]["source_sha256"] = {}
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        invoke(packet, tmp_path / "campaign", lambda **_: pytest.fail("No provider before preflight"))
    assert not (tmp_path / "campaign").exists()


@pytest.mark.parametrize("kwargs", [{}, {"allow_live": True}, {"authorization_reference": "reference"}])
def test_campaign_requires_new_explicit_authorization(tmp_path, kwargs):
    with pytest.raises(ValueError, match="authorization"):
        execute.run_campaign(tmp_path / "missing-packet", tmp_path / "campaign",
                             provider_factory=lambda **_: pytest.fail("No unauthorized provider"), **kwargs)
    assert not (tmp_path / "campaign").exists()
