"""Interrupted campaign recovery consumes only previously unreserved requests."""

import copy
import json
from pathlib import Path

import pytest

from scheduling.evaluation.benchmark import tiny_fixtures
from scheduling.evaluation.failure_policy import CONTINUE_TRANSIENT_POLICY
from scheduling.evaluation.qualification import execute_blocks
from scheduling.evaluation.runner import (
    OBSERVE_BACKEND_POLICY, RunConfig, plan_run, read, replay, requests, write_new,
)
from scheduling.evaluation.scoring import digest
from scheduling.providers import ModelConfig
from scheduling.providers.execution import execution_contract
from scheduling.providers.types import Attempt, ModelResponse, ProviderExecution, Usage
from scheduling.solver import SolverLimits
from tests.integration.test_evaluation import canned
from tests.integration.test_model_qualification import load_script


def response(cfg, content, *, error=None):
    model = None if error else cfg.model.model
    attempt = Attempt(
        1, 0.01, None if error else 200, Usage() if error else Usage(2, 3, 5),
        error=error, outcome_uncertain=bool(error), returned_model=model,
        finish_reason=None if error else "stop",
        execution=ProviderExecution(execution_contract(cfg.model), "test-backend"),
    )
    return ModelResponse(content, model, 0.01, (attempt,), error=error,
                         finish_reason=None if error else "stop")


@pytest.fixture
def interrupted(tmp_path, monkeypatch):
    resume = load_script("resume_development_campaign")
    cases = tiny_fixtures()[:2]
    cfg = RunConfig(ModelConfig("qwen3.6:35b", 2048), SolverLimits(), SolverLimits(),
                    4, 8192, evidence="live_development",
                    qualification_policy=OBSERVE_BACKEND_POLICY,
                    provider_failure_policy=CONTINUE_TRANSIENT_POLICY)
    blocks = {"controlled": (cases, cfg, plan_run(cases, cfg))}
    packet = tmp_path / "packet"
    packet.mkdir()
    manifest = {"model": cfg.model.model, "planned_scheduling_completions": 4,
                "total_requests": 7, "requested_output_tokens": 12288}
    write_new(packet / "campaign.json", manifest)
    monkeypatch.setattr(resume, "load_packet", lambda _: (blocks, manifest))
    campaign = tmp_path / "campaign"
    calls = []

    class InitialProvider:
        def __init__(self, *, budget):
            self.budget = budget

        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def list_models(self):
            assert self.budget.reserve(0)
            calls.append("metadata")
            return (cfg.model.model,)

        def complete(self, messages, model):
            assert self.budget.reserve(model.max_tokens)
            calls.append(tuple(messages))
            if len(calls) <= 3:
                return response(cfg, '{"ok":true}')
            return response(cfg, None, error="timeout")

    def stop_between_requests(_):
        raise KeyboardInterrupt("test-only interruption after a durable attempt")

    with monkeypatch.context() as patch:
        patch.setattr("scheduling.evaluation.failure_policy.time.sleep", stop_between_requests)
        with pytest.raises(KeyboardInterrupt):
            execute_blocks(blocks, campaign, allow_live=True,
                           authorization_reference="test-only original allowance",
                           provider_factory=InitialProvider,
                           packet_metadata={"campaign_sha256": digest(manifest)},
                           script_path=Path(resume.__file__).with_name("run_development_campaign.py"))
    assert len(calls) == 4
    assert replay(campaign / "controlled")[1]["completed"] == 1
    assert not (campaign / "summary.json").exists()
    return resume, packet, campaign, cases, cfg


def test_resume_preserves_bytes_skips_all_completed_calls_and_restores_full_budget(interrupted, tmp_path, monkeypatch):
    resume, packet, campaign, cases, cfg = interrupted
    before = {p.relative_to(campaign): p.read_bytes() for p in campaign.rglob("*") if p.is_file()}
    contents = iter(list(canned(cases, cfg).values())[1:])
    completed_keys = {p.stem for p in (campaign / "controlled/attempts").glob("*.json")}
    next_keys = [key for key, *_ in requests(cases, cfg) if key not in completed_keys]
    seen, budgets, cooldowns = [], [], []
    monkeypatch.setattr("scheduling.evaluation.failure_policy.time.sleep", cooldowns.append)

    class RemainingProvider:
        def __init__(self, *, budget):
            assert budget.requests_used == 4
            assert budget.completion_tokens_reserved == 3 * cfg.model.max_tokens
            budgets.append(budget)
            self.budget = budget

        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def list_models(self):
            pytest.fail("Resume must not repeat metadata")

        def complete(self, messages, model):
            assert all(message.content != 'Return exactly {"ok":true} with no other text.'
                       for message in messages)
            assert self.budget.reserve(model.max_tokens)
            seen.append(tuple(messages))
            return response(cfg, next(contents))

    result = resume.resume_campaign(packet, campaign, tmp_path / "receipt",
                                    authorization_reference="test-only resume authorization",
                                    provider_factory=RemainingProvider)
    assert result["state"] == "completed"
    assert result["requests_reserved"] == budgets[0].requests_used == 7
    assert result["requested_output_tokens_reserved"] == budgets[0].completion_tokens_reserved == 12288
    assert len(seen) == len(next_keys) == 3
    prompts = read(campaign / "controlled/manifest.json")["contract"]["request_prompt_sha256"]
    assert [digest(messages) for messages in seen] == [prompts[key] for key in next_keys]
    assert cooldowns == [30]
    assert all((campaign / p).read_bytes() == value for p, value in before.items())
    rows, progress = replay(campaign / "controlled")
    assert progress["completed"] == 4 and not progress["pending_attempt_ids"]
    assert sum(row["category"] == "provider_error" for row in rows) == 1
    assert sum(row["accepted"] for row in rows) == 3


@pytest.mark.parametrize("damage", ["pending", "checksum", "identity", "config", "prefix", "capability"])
def test_invalid_or_fatal_saved_evidence_refused_before_provider(interrupted, tmp_path, damage):
    resume, packet, campaign, _, _ = interrupted
    attempt = next((campaign / "controlled/attempts").glob("*.json"))
    data = read(attempt)
    if damage == "pending":
        data["state"] = "pending_or_interrupted"
    elif damage == "checksum":
        data["sha256"] = "0" * 64
    elif damage == "identity":
        model_response = data["payload"]["pipeline_result"]["model_response"]
        model_response["error"] = None
        model_response["returned_model"] = "unexpected-model"
        model_response["attempts"][0].update(error=None, http_status=200,
                                               returned_model="unexpected-model")
        data["sha256"] = digest(data["payload"])
    elif damage == "config":
        target = campaign / "controlled-runtime-config.json"
        modified = read(target)
        modified["model"]["read_timeout"] += 1
        target.write_text(json.dumps(modified))
    elif damage == "prefix":
        case_ids = list(read(campaign / "controlled/manifest.json")["contract"]["request_prompt_sha256"])
        other_key = next(key for key in case_ids if key != attempt.stem)
        attempt.rename(attempt.with_name(other_key + ".json"))
    else:
        target = campaign / "capability-00.json"
        modified = read(target)
        modified["response"]["attempts"][0]["execution"]["system_fingerprint"] = "changed"
        target.write_text(json.dumps(modified))
    if damage in {"pending", "checksum", "identity"}:
        attempt.write_text(json.dumps(data))
    before = {p.relative_to(campaign): p.read_bytes() for p in campaign.rglob("*") if p.is_file()}
    with pytest.raises(ValueError):
        resume.resume_campaign(packet, campaign, tmp_path / "receipt",
                               authorization_reference="test-only resume authorization",
                               provider_factory=lambda **_: pytest.fail("Must refuse before provider construction"))
    assert all((campaign / p).read_bytes() == value for p, value in before.items())


def test_resume_requires_explicit_authorization(interrupted, tmp_path):
    resume, packet, campaign, _, _ = interrupted
    with pytest.raises(ValueError):
        resume.resume_campaign(packet, campaign, tmp_path / "receipt", authorization_reference="",
                               provider_factory=lambda **_: pytest.fail("No authorized request"))


@pytest.mark.parametrize("difference", ["platform", "unchanged", "source", "config", "dependency", "python"])
def test_platform_transition_accepts_only_one_explicit_runtime_platform_change(difference):
    resume = load_script("resume_development_campaign")
    old = {
        "runtime": {"platform": "macOS-26.5.2-arm64", "python": "3.12.0", "ortools": "9.14"},
        "source_sha256": {"runner.py": "original-source"},
        "config": {"model": {"model": "qwen3.6:35b", "max_tokens": 32768}},
        "request_prompt_sha256": {"one": "unchanged-prompt"},
    }
    new = copy.deepcopy(old)
    if difference != "unchanged":
        new["runtime"]["platform"] = "macOS-27.0.1-arm64"
    if difference == "source":
        new["source_sha256"]["runner.py"] = "changed-source"
    elif difference == "config":
        new["config"]["model"]["max_tokens"] += 1
    elif difference == "dependency":
        new["runtime"]["ortools"] = "9.15"
    elif difference == "python":
        new["runtime"]["python"] = "3.13.0"
    assert resume.platform_only_change(old, new) is (difference == "platform")
    assert old["runtime"]["platform"] == "macOS-26.5.2-arm64"


@pytest.fixture
def derivative(interrupted, tmp_path):
    resume, packet, original, cases, cfg = interrupted
    # The historical fixture represents a completed request on an older OS.
    # Scientific source/configuration and actual current-runtime packet stay fixed.
    for name in ("controlled/manifest.json", "manifest.json"):
        target = original / name
        data = read(target)
        contract = (data["contract"] if name.startswith("controlled/")
                    else data["blocks"]["controlled"]["preflight"]["contract"])
        contract["runtime"]["platform"] = "macOS-historical-test-platform"
        target.write_text(json.dumps(data))
    before = {p.relative_to(original): p.read_bytes() for p in original.rglob("*") if p.is_file()}
    derived = tmp_path / "derived"
    inspected = resume.derive_campaign(original, derived, packet,
                                      authorization_reference="test-only explicit OS transition")
    return resume, packet, original, derived, before, inspected, cases, cfg


def test_derivative_preserves_original_and_copied_evidence_with_explicit_partition(derivative):
    resume, _, original, derived, before, inspected, _, cfg = derivative
    assert all((original / path).read_bytes() == data for path, data in before.items())
    assert all((derived / path).read_bytes() == data for path, data in before.items()
               if str(path) not in {"manifest.json", "controlled/manifest.json"})
    provenance = resume.verify_runtime_transition(derived)
    assert provenance["qualification_and_reference_platform"] == "macOS-historical-test-platform"
    assert [len(s["attempt_ids"]) for s in provenance["segments"]] == [1, 3]
    assert provenance["segments"][0]["platform"] != provenance["segments"][1]["platform"]
    assert inspected["completed"] == 1 and inspected["remaining"] == 3
    assert inspected["budget"].requests_used == 4
    assert inspected["budget"].completion_tokens_reserved == cfg.model.max_tokens * 3


@pytest.mark.parametrize("damage", ["original", "copy", "partition", "binding", "contract"])
def test_derivative_transition_detects_changed_evidence_or_provenance(derivative, damage):
    resume, _, original, derived, _, _, _, _ = derivative
    if damage in {"original", "copy"}:
        root = original if damage == "original" else derived
        target = next((root / "controlled/attempts").glob("*.json"))
        target.write_bytes(target.read_bytes() + b"\n")
    else:
        target = derived / "controlled/manifest.json"
        changed = read(target)
        if damage == "partition":
            segments = changed["runtime_transition"]["segments"]
            segments[1]["attempt_ids"].append(segments[0]["attempt_ids"][0])
        elif damage == "binding":
            changed["runtime_transition"]["authorization_reference"] = "altered authorization"
        else:
            changed["contract"]["runtime"]["python"] = "changed-python"
        target.write_text(json.dumps(changed))
    with pytest.raises(ValueError):
        resume.verify_runtime_transition(derived)


def test_derivative_export_marks_cross_platform_pair_and_both_platforms(derivative, tmp_path, monkeypatch):
    resume, packet, _, derived, _, _, cases, cfg = derivative
    contents = iter(list(canned(cases, cfg).values())[1:])
    monkeypatch.setattr("scheduling.evaluation.failure_policy.time.sleep", lambda _: None)

    class Provider:
        def __init__(self, *, budget):
            self.budget = budget

        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def complete(self, _, model):
            assert self.budget.reserve(model.max_tokens)
            return response(cfg, next(contents))

    assert resume.resume_campaign(packet, derived, tmp_path / "derivative-receipt",
                                  authorization_reference="test-only continuation",
                                  provider_factory=Provider)["state"] == "completed"
    # Numerical scoring/export has its own tests; isolate the new provenance
    # transformation and cross-platform pair identification here.
    def numerical_export(blocks, directory, **_):
        directory.mkdir(parents=True)
        return {"settings": {"runtime": read(derived / "controlled/manifest.json")["contract"]["runtime"]},
                "rows": replay(derived / "controlled")[0]}

    monkeypatch.setattr("scheduling.evaluation.study.export_study", numerical_export)
    result = resume.export_transition_analysis(derived, tmp_path / "export", project_root=tmp_path)
    assert len(result["runtime_assignment"]) == 4
    assert [r["runtime_segment"] for r in result["runtime_assignment"]].count(0) == 1
    assert [r["runtime_segment"] for r in result["runtime_assignment"]].count(1) == 3
    assert len(result["cross_platform_pair_keys"]) == 1
    assert sum(row["runtime_segment"] == 0 for row in result["rows"]) == 1
    assert sum(row["runtime_segment"] == 1 for row in result["rows"]) == 3
    assert sum(row["cross_platform_pair"] for row in result["rows"]) == 2
    for row in result["rows"]:
        assert row["execution_platform"] == result["runtime_transition"]["segments"][row["runtime_segment"]]["platform"]
    assert "Mixed OS" in result["settings"]["runtime_scope"]
