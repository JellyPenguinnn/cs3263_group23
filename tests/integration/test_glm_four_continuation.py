"""GLM's eight-to-four continuation retains qualification and rejected calls."""

from dataclasses import replace
import importlib
import threading

import pytest

from scheduling.evaluation.runner import plan_run, read, replay, write_new
from scheduling.evaluation.scoring import digest
from tests.integration.test_campaign_resume import response
from tests.integration.test_model_qualification import load_script
from tests.integration.test_parallel_campaign import setup


def test_glm_eight_to_four_preserves_calls_budgets_identity_and_timing(setup, tmp_path, monkeypatch):
    parallel, cases, cfg, answers = setup
    cfg = replace(cfg, model=replace(cfg.model, model="x-test-1"))
    resume = load_script("resume_development_campaign")
    blocks = {"controlled": (cases, cfg, plan_run(cases, cfg))}
    packet_manifest = {"model": "x-test-1", "planned_scheduling_completions": 40,
                       "total_requests": 43, "requested_output_tokens": 42 * cfg.model.max_tokens}
    packet = tmp_path / "packet"
    packet.mkdir()
    write_new(packet / "campaign.json", packet_manifest)
    load = lambda _: (blocks, packet_manifest)
    monkeypatch.setattr(importlib.import_module("evaluation.run_development_campaign"), "load_packet", load)
    monkeypatch.setattr(resume, "load_packet", load)
    monkeypatch.setattr(parallel, "_resume_adapter", lambda: resume)

    def glm_response(content):
        value = response(cfg, content)
        return replace(value, returned_model="glm-5.3-flash",
                       attempts=(replace(value.attempts[0], returned_model="glm-5.3-flash"),))

    lock = threading.Lock()
    first_wave = threading.Barrier(8, timeout=10)
    fatal_saved = threading.Event()
    initial_calls = []

    class InitialProvider:
        def __init__(self, *, budget):
            self.budget = budget

        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def list_models(self):
            assert self.budget.reserve(0)
            initial_calls.append("metadata")
            return ("x-test-1",)

        def complete(self, messages, model):
            assert model.model == "x-test-1" and self.budget.reserve(model.max_tokens)
            with lock:
                index = len(initial_calls)
                initial_calls.append(digest(messages))
            if index < 3:
                return glm_response('{"ok":true}')
            first_wave.wait()
            if index < 5:
                value = response(cfg, None, error="http_429")
                return replace(value, attempts=(replace(value.attempts[0], http_status=429,
                                                       outcome_uncertain=False),))
            # Keep successful requests in flight until the coordinator has
            # persisted a fatal response, independent of thread timing.
            assert fatal_saved.wait(10), "Coordinator did not persist the fatal outcome"
            return glm_response(answers[digest(messages)])

    original = tmp_path / "glm8"
    stopped = parallel.execute_parallel_campaign(
        packet, original, authorization_reference="offline test: initial GLM eight",
        concurrency=8, provider_factory=InitialProvider,
        progress=lambda state: fatal_saved.set() if state["stop_reason"] == "http_429" else None)
    assert stopped["state"] == "stopped_campaign" and stopped["stop_reason"] == "http_429"
    assert stopped["requests_reserved"] == len(initial_calls) == 11
    old_bytes = {p.relative_to(original): p.read_bytes() for p in original.rglob("*") if p.is_file()}
    saved_ids = {p.stem for p in (original / "controlled/attempts").glob("*.json")}
    assert len(saved_ids) == 8

    derived = tmp_path / "glm4"
    prepared = parallel.prepare_parallel_continuation(
        original, derived, packet,
        authorization_reference="User authorized four requests and preservation without repeat calls",
        concurrency=4)
    assert prepared["completed"] == 8 and prepared["remaining"] == 32
    assert prepared["requests_already_reserved"] == 11
    assert len(prepared["reconciled_http_429_attempt_ids"]) == 2
    prior_prompts = set(initial_calls[3:])
    remaining_calls = []
    wave = threading.Barrier(4, timeout=10)
    active = peak = 0

    class RemainingProvider:
        def __init__(self, *, budget):
            assert budget.requests_used == 11
            assert budget.completion_tokens_reserved == 10 * cfg.model.max_tokens
            self.budget = budget

        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def list_models(self):
            pytest.fail("Metadata qualification must not be repeated")

        def complete(self, messages, model):
            nonlocal active, peak
            assert model.model == "x-test-1" and self.budget.reserve(model.max_tokens)
            prompt = digest(messages)
            assert prompt in answers and prompt not in prior_prompts
            with lock:
                assert prompt not in remaining_calls
                remaining_calls.append(prompt)
                active += 1
                peak = max(peak, active)
            wave.wait()
            with lock:
                active -= 1
            return glm_response(answers[prompt])

    result = parallel.execute_parallel_campaign(
        packet, derived, authorization_reference="offline test: resume GLM four",
        concurrency=4, resume=True, provider_factory=RemainingProvider)
    assert result["state"] == "completed" and result["concurrency"] == 4
    assert peak == 4 and len(remaining_calls) == 32
    assert result["requests_reserved"] == 43
    assert result["requested_output_tokens_reserved"] == 42 * cfg.model.max_tokens
    assert len(set(initial_calls[3:] + remaining_calls)) == 40
    assert all((original / name).read_bytes() == value for name, value in old_bytes.items())
    for name, value in old_bytes.items():
        if str(name).startswith(("controlled/attempts/", "capability-", "metadata")):
            assert (derived / name).read_bytes() == value
    for name in ("summary.json", "parallel-start.json"):
        assert (derived / "prior-phase" / name).read_bytes() == old_bytes[next(p for p in old_bytes if str(p) == name)]
    rows, progress = replay(derived / "controlled")
    assert progress["completed"] == 40 and not progress["pending_attempt_ids"]
    assert sum(row["category"] == "provider_error" for row in rows) == 2
    assert sum(row["accepted"] for row in rows) == 38
    protocol = read(derived / "controlled/manifest.json")["execution_protocol"]
    assigned = {key: segment["concurrency"] for segment in protocol["segments"] for key in segment["attempt_ids"]}
    assert len(assigned) == 40
    for path in (derived / "controlled/attempts").glob("*.json"):
        record = read(path)
        concurrency = 8 if path.stem in saved_ids else 4
        assert assigned[path.stem] == concurrency
        assert record["execution_timing"]["configured_concurrency"] == concurrency
        saved_response = record["payload"]["pipeline_result"]["model_response"]
        assert len(saved_response["attempts"]) == 1
        if not saved_response.get("error"):
            assert saved_response["returned_model"] == "glm-5.3-flash"
