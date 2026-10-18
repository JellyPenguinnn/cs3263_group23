"""Authorized concurrency reduction preserves completed calls and failure evidence."""

from dataclasses import replace
import importlib
import json
import threading
import time

import pytest

from scheduling.evaluation.runner import plan_run, read, replay, requests, write_new
from scheduling.evaluation.scoring import digest
from tests.integration.test_campaign_resume import response
from tests.integration.test_model_qualification import load_script
from tests.integration.test_parallel_campaign import setup


@pytest.fixture
def stopped_parallel(setup, tmp_path, monkeypatch):
    parallel, cases, cfg, answers = setup
    resume = load_script("resume_development_campaign")
    blocks = {"controlled": (cases, cfg, plan_run(cases, cfg))}
    packet_manifest = {"model": cfg.model.model, "planned_scheduling_completions": 40,
                       "total_requests": 43, "requested_output_tokens": 42 * cfg.model.max_tokens}
    packet = tmp_path / "packet"
    packet.mkdir()
    write_new(packet / "campaign.json", packet_manifest)
    load = lambda _: (blocks, packet_manifest)
    monkeypatch.setattr(importlib.import_module("evaluation.run_development_campaign"), "load_packet", load)
    monkeypatch.setattr(resume, "load_packet", load)
    monkeypatch.setattr(parallel, "_resume_adapter", lambda: resume)
    barrier, lock = threading.Event(), threading.Lock()
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
            with lock:
                index = len(calls)
                calls.append(digest(messages))
                if len(calls) == 19:
                    barrier.set()
            if index < 3:
                return response(cfg, '{"ok":true}')
            assert barrier.wait(5), "Initial sixteen scheduling requests were not dispatched"
            if index < 7:
                result = response(cfg, None, error="http_429")
                return replace(result, attempts=(replace(result.attempts[0], http_status=429, outcome_uncertain=False),))
            time.sleep(0.1)
            return response(cfg, answers[digest(messages)])

    original = tmp_path / "parallel16"
    summary = parallel.execute_parallel_campaign(packet, original, authorization_reference="test-only initial16",
                                                  provider_factory=InitialProvider)
    assert summary["state"] == "stopped_campaign" and summary["stop_reason"] == "http_429"
    assert summary["requests_reserved"] == len(calls) == 19
    assert replay(original / "controlled")[1]["completed"] == 16
    assert not replay(original / "controlled")[1]["pending_attempt_ids"]
    return parallel, packet, original, cases, cfg, answers


def test_protocol_preserves_serial_and_sixteen_way_segments():
    parallel = load_script("parallel_development_campaign")
    planned = [f"attempt-{i}" for i in range(40)]
    old = parallel.protocol(planned, set(planned[:3]), 16)
    revised = parallel.protocol(planned, set(planned[:19]), 8, prior_segments=old["segments"])
    assert revised["concurrency"] == 8
    assigned = {key: segment["concurrency"] for segment in revised["segments"] for key in segment["attempt_ids"]}
    assert len(assigned) == 40
    assert [assigned[key] for key in planned] == [1] * 3 + [16] * 16 + [8] * 21
    assert sum(len(segment["attempt_ids"]) for segment in revised["segments"]) == 40


def test_reduced_concurrency_preserves_all_calls_and_historical_429(stopped_parallel, tmp_path, monkeypatch):
    parallel, packet, original, cases, cfg, answers = stopped_parallel
    old_bytes = {p.relative_to(original): p.read_bytes() for p in original.rglob("*") if p.is_file()}
    saved_ids = {p.stem for p in (original / "controlled/attempts").glob("*.json")}
    derived = tmp_path / "parallel8"
    prepared = parallel.prepare_parallel_continuation(original, derived, packet,
        authorization_reference="User authorized eight parallel requests without repeating calls", concurrency=8)
    assert prepared["completed"] == 16 and prepared["remaining"] == 24
    actual = parallel.run_parallel
    monkeypatch.setattr(parallel, "run_parallel", lambda *a, **kw: actual(*a, **kw, cooldown_seconds=0.001))
    full, lock = threading.Event(), threading.Lock()
    active = peak = 0
    seen = []
    old_prompts = read(original / "controlled/manifest.json")["contract"]["request_prompt_sha256"]
    already_used = {old_prompts[key] for key in saved_ids}

    class RemainingProvider:
        def __init__(self, *, budget):
            assert budget.requests_used == 19
            assert budget.completion_tokens_reserved == 18 * cfg.model.max_tokens
            self.budget = budget

        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def list_models(self):
            pytest.fail("Metadata qualification was repeated")

        def complete(self, messages, model):
            nonlocal active, peak
            prompt = digest(messages)
            assert prompt not in already_used and prompt in answers
            assert self.budget.reserve(model.max_tokens)
            with lock:
                assert prompt not in seen
                seen.append(prompt)
                active += 1
                peak = max(peak, active)
                if active == 8:
                    full.set()
            assert full.wait(5), "Eight concurrent requests were not dispatched"
            time.sleep(0.005)
            with lock:
                active -= 1
            return response(cfg, answers[prompt])

    result = parallel.execute_parallel_campaign(packet, derived, authorization_reference="test-only continuation",
        concurrency=8, resume=True, provider_factory=RemainingProvider)
    assert result["state"] == "completed"
    assert result["requests_reserved"] == 43 and result["requested_output_tokens_reserved"] == 42 * cfg.model.max_tokens
    assert peak == 8 and len(seen) == 24
    assert all((original / name).read_bytes() == data for name, data in old_bytes.items())
    for name, data in old_bytes.items():
        if str(name).startswith("controlled/attempts/") or str(name).startswith("capability-"):
            assert (derived / name).read_bytes() == data
    for name in ("summary.json", "parallel-start.json"):
        assert (derived / "prior-phase" / name).read_bytes() == (original / name).read_bytes()
    rows, progress = replay(derived / "controlled")
    assert progress["completed"] == 40 and not progress["pending_attempt_ids"]
    assert sum(row["category"] == "provider_error" for row in rows) == 4
    protocol = read(derived / "controlled/manifest.json")["execution_protocol"]
    assignments = {key: segment["concurrency"] for segment in protocol["segments"] for key in segment["attempt_ids"]}
    assert all(assignments[key] == 16 for key in saved_ids)
    assert sum(value == 8 for value in assignments.values()) == 24
    assert all(read(derived / "controlled/attempts" / f"{key}.json")["execution_timing"]["configured_concurrency"] == 8
               for key in assignments if key not in saved_ids)


@pytest.mark.parametrize("corruption", ["pending", "payload", "source-after-copy", "different-fatal"])
def test_unsafe_historical_evidence_rejected_without_calls(stopped_parallel, tmp_path, corruption):
    parallel, packet, original, cases, cfg, _ = stopped_parallel
    derived = tmp_path / "parallel8"
    if corruption == "source-after-copy":
        parallel.prepare_parallel_continuation(original, derived, packet,
            authorization_reference="test-only reduction", concurrency=8)
        (original / "metadata.json").write_text("{}")
        with pytest.raises(ValueError):
            parallel.execute_parallel_campaign(packet, derived, authorization_reference="test-only resume",
                concurrency=8, resume=True, provider_factory=lambda **_: pytest.fail("Modified source issued calls"))
        return
    path = next((original / "controlled/attempts").glob("*.json"))
    record = read(path)
    if corruption == "pending":
        record["state"] = "pending_or_interrupted"
    elif corruption == "payload":
        record["payload"]["evaluation"]["accepted"] = "tampered"
    else:
        # A different fatal response must not be pardoned by authorization to
        # resume a historical HTTP 429 batch, even with a new payload checksum.
        record["payload"]["pipeline_result"]["model_response"]["error"] = "http_401"
        record["sha256"] = digest(record["payload"])
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError):
        parallel.prepare_parallel_continuation(original, derived, packet,
            authorization_reference="test-only reduction", concurrency=8)


def test_new_429_still_stops_and_drains_eight(stopped_parallel, tmp_path):
    parallel, packet, original, _, cfg, answers = stopped_parallel
    derived = tmp_path / "parallel8"
    parallel.prepare_parallel_continuation(original, derived, packet,
        authorization_reference="test-only reduction", concurrency=8)
    full, lock = threading.Event(), threading.Lock()
    calls = []

    class Provider:
        def __init__(self, *, budget):
            self.budget = budget

        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def list_models(self):
            pytest.fail("Metadata repeated")

        def complete(self, messages, model):
            assert self.budget.reserve(model.max_tokens)
            with lock:
                index = len(calls)
                calls.append(digest(messages))
                if len(calls) == 8:
                    full.set()
            assert full.wait(5)
            if index == 0:
                return response(cfg, None, error="http_429")
            time.sleep(0.1)
            return response(cfg, answers[digest(messages)])

    result = parallel.execute_parallel_campaign(packet, derived, authorization_reference="test-only continuation",
        concurrency=8, resume=True, provider_factory=Provider)
    assert result["state"] == "stopped_campaign" and result["stop_reason"] == "http_429"
    assert len(calls) == 8 and result["requests_reserved"] == 27
    _, progress = replay(derived / "controlled")
    assert progress["completed"] == 24 and not progress["pending_attempt_ids"]


def test_fresh_glm_uses_eight_requests_and_exact_canonical_model(setup, tmp_path, monkeypatch):
    parallel, cases, cfg, answers = setup
    cfg = replace(cfg, model=replace(cfg.model, model="x-test-1"))
    blocks = {"controlled": (cases, cfg, plan_run(cases, cfg))}
    monkeypatch.setattr(importlib.import_module("evaluation.run_development_campaign"), "load_packet",
                        lambda _: (blocks, {"model": "x-test-1"}))
    full, lock = threading.Event(), threading.Lock()
    active = peak = 0
    calls = []

    class Provider:
        def __init__(self, *, budget):
            self.budget = budget

        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def list_models(self):
            assert self.budget.reserve(0)
            calls.append("metadata")
            return ("x-test-1",)

        def complete(self, messages, model):
            nonlocal active, peak
            assert model.model == "x-test-1" and self.budget.reserve(model.max_tokens)
            prompt = digest(messages)
            with lock:
                index = len(calls)
                calls.append(prompt)
                if index >= 3:
                    active += 1
                    peak = max(peak, active)
                    if active == 8:
                        full.set()
            if index >= 3:
                assert full.wait(5)
                time.sleep(0.005)
                with lock:
                    active -= 1
            value = response(cfg, '{"ok":true}' if index < 3 else answers[prompt])
            return replace(value, returned_model="glm-5.3-flash",
                           attempts=(replace(value.attempts[0], returned_model="glm-5.3-flash"),))

    result = parallel.execute_parallel_campaign(tmp_path / "packet", tmp_path / "glm",
        authorization_reference="test-only fresh GLM", concurrency=8, provider_factory=Provider)
    assert result["state"] == "completed" and result["concurrency"] == 8
    assert peak == 8 and len(calls) == result["requests_reserved"] == 43
    rows, progress = replay(tmp_path / "glm/controlled")
    assert progress["completed"] == 40 and all(row["accepted"] for row in rows)
    assert all(read(path)["payload"]["pipeline_result"]["model_response"]["returned_model"] == "glm-5.3-flash"
               for path in (tmp_path / "glm/controlled/attempts").glob("*.json"))


def test_second_concurrency_reduction_preserves_every_phase(stopped_parallel, tmp_path):
    parallel, packet, original, _, cfg, answers = stopped_parallel
    intermediate = tmp_path / "parallel8"
    parallel.prepare_parallel_continuation(original, intermediate, packet,
        authorization_reference="test-only first reduction", concurrency=8)
    full, lock = threading.Event(), threading.Lock()
    seen = set()

    class Provider:
        fail = True

        def __init__(self, *, budget):
            self.budget = budget

        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def list_models(self):
            pytest.fail("Metadata qualification repeated")

        def complete(self, messages, model):
            assert self.budget.reserve(model.max_tokens)
            prompt = digest(messages)
            with lock:
                assert prompt not in seen
                index = len(seen)
                seen.add(prompt)
                if len(seen) == 8:
                    full.set()
            if self.fail:
                assert full.wait(5)
                if index == 0:
                    failed = response(cfg, None, error="http_429")
                    return replace(failed, attempts=(replace(failed.attempts[0],
                        http_status=429, outcome_uncertain=False),))
                time.sleep(0.1)
            return response(cfg, answers[prompt])

    stopped = parallel.execute_parallel_campaign(packet, intermediate,
        authorization_reference="test-only eight", concurrency=8, resume=True, provider_factory=Provider)
    assert stopped["stop_reason"] == "http_429" and len(seen) == 8
    originals = {directory: {p.relative_to(directory): p.read_bytes()
                            for p in directory.rglob("*") if p.is_file()}
                 for directory in (original, intermediate)}
    completed = {p.stem for p in (intermediate / "controlled/attempts").glob("*.json")}
    prompts = read(intermediate / "controlled/manifest.json")["contract"]["request_prompt_sha256"]
    seen.update(prompts[key] for key in completed)
    final = tmp_path / "parallel4"
    prepared = parallel.prepare_parallel_continuation(intermediate, final, packet,
        authorization_reference="test-only second reduction", concurrency=4)
    assert prepared["completed"] == 24 and prepared["remaining"] == 16
    Provider.fail = False
    result = parallel.execute_parallel_campaign(packet, final,
        authorization_reference="test-only four", concurrency=4, resume=True, provider_factory=Provider)
    assert result["state"] == "completed" and result["requests_reserved"] == 43
    assert len(seen) == 40
    parallel.verify_parallel_copy(final)
    assert all((directory / name).read_bytes() == data
               for directory, files in originals.items() for name, data in files.items())
    for name in ("summary.json", "parallel-start.json"):
        assert (final / "prior-phase" / name).read_bytes() == (original / name).read_bytes()
        assert (final / "prior-phase/concurrency-8" / name).read_bytes() == (intermediate / name).read_bytes()
    for key in completed:
        assert (final / "controlled/attempts" / f"{key}.json").read_bytes() == (
            intermediate / "controlled/attempts" / f"{key}.json").read_bytes()
    rows, progress = replay(final / "controlled")
    assert progress["completed"] == 40 and not progress["pending_attempt_ids"]
    assert sum(row["category"] == "provider_error" for row in rows) == 5
