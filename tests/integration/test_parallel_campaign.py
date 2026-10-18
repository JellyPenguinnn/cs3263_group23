"""Concurrent operations preserve scientific attempts, accounting and failure evidence."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime, timedelta
import json
import importlib
import shutil
import threading
import time

import pytest

from scheduling.evaluation.benchmark import tiny_fixtures
from scheduling.evaluation.failure_policy import CONTINUE_TRANSIENT_POLICY
from scheduling.evaluation.runner import (
    OBSERVE_BACKEND_POLICY, RunConfig, build_extraction_messages, build_messages,
    plan_run, read, replay, requests, run_batch,
)
from scheduling.evaluation.scoring import digest
from scheduling.providers import ModelConfig
from scheduling.solver import SolverLimits
from tests.integration.test_campaign_resume import interrupted, response
from tests.integration.test_evaluation import canned
from tests.integration.test_model_qualification import load_script


@pytest.fixture
def setup():
    parallel = load_script("parallel_development_campaign")
    base = tiny_fixtures()[0]
    cases = tuple(replace(base, case_id=f"parallel-test-{i}",
                          problem=replace(base.problem, instance_id=f"parallel-test-{i}",
                                          horizon_start=(datetime.fromisoformat(base.problem.horizon_start)
                                                         + timedelta(days=i)).isoformat())) for i in range(20))
    cfg = RunConfig(ModelConfig("qwen3.6:35b", 2048), SolverLimits(), SolverLimits(),
                    40, 81920, evidence="live_development",
                    qualification_policy=OBSERVE_BACKEND_POLICY,
                    provider_failure_policy=CONTINUE_TRANSIENT_POLICY)
    answers = canned(cases, cfg)
    by_prompt = {}
    for key, identity, _, view in requests(cases, cfg):
        messages = (build_extraction_messages(view) if identity["approach"] == "solver_augmented"
                    else build_messages(view.text, task_type=view.task_type,
                                        required_activity_ids=view.activity_ids, original_schedule=None))
        by_prompt[digest(messages)] = answers[key]
    return parallel, cases, cfg, by_prompt


def test_thread_safe_budget_enforces_joint_request_and_token_cap(setup):
    parallel, _, _, _ = setup
    budget = parallel.ThreadSafeBudget(17, 51)
    with ThreadPoolExecutor(max_workers=32) as workers:
        reserved = list(workers.map(lambda _: budget.reserve(3), range(2000)))
    assert sum(reserved) == budget.requests_used == 17
    assert budget.completion_tokens_reserved == 51


def test_parallel_peak_16_preserves_previous_timeout_and_never_reissues_completed(setup, tmp_path, monkeypatch):
    parallel, cases, cfg, by_prompt = setup
    budget = parallel.ThreadSafeBudget(cfg.max_requests, cfg.max_requested_output_tokens)

    def first_call(*_):
        assert budget.reserve(cfg.model.max_tokens)
        return response(cfg, None, error="timeout")

    def interrupt(_):
        raise KeyboardInterrupt

    with monkeypatch.context() as patch:
        patch.setattr("scheduling.evaluation.failure_policy.time.sleep", interrupt)
        with pytest.raises(KeyboardInterrupt):
            run_batch(cases, tmp_path / "original", cfg, provider_complete=first_call)
    shutil.copytree(tmp_path / "original", tmp_path / "run")
    prior = {p.name: p.read_bytes() for p in (tmp_path / "run/attempts").glob("*.json")}
    assert len(prior) == 1
    manifest = read(tmp_path / "run/manifest.json")
    manifest["execution_protocol"] = parallel.protocol(
        [key for key, *_ in requests(cases, cfg)], {name[:-5] for name in prior}, 16)
    (tmp_path / "run/manifest.json").write_text(json.dumps(manifest))
    lock, full = threading.Lock(), threading.Event()
    active = peak = calls = 0

    def callback(messages, model):
        nonlocal active, peak, calls
        assert budget.reserve(model.max_tokens)
        with lock:
            active += 1
            calls += 1
            peak = max(peak, active)
            if active == 16:
                full.set()
        assert full.wait(5), "Coordinator failed to dispatch sixteen concurrent requests"
        try:
            return response(cfg, by_prompt[digest(messages)])
        finally:
            with lock:
                active -= 1

    result = parallel.run_parallel(cases, tmp_path / "run", cfg, provider_complete=callback,
                                   concurrency=16, cooldown_seconds=0.001)
    assert result["state"] == "completed"
    assert result["completed"] == result["reserved_requests"] == 40
    assert peak == 16 and calls == 39
    assert budget.requests_used == 40 and budget.completion_tokens_reserved == 81920
    assert all((tmp_path / "run/attempts" / name).read_bytes() == data for name, data in prior.items())
    assert all((tmp_path / "original/attempts" / name).read_bytes() == data for name, data in prior.items())
    rows, progress = replay(tmp_path / "run")
    assert progress["completed"] == 40 and not progress["pending_attempt_ids"]
    assert sum(r["category"] == "provider_error" for r in rows) == 1
    assert sum(r["accepted"] for r in rows) == 39
    again = parallel.run_parallel(cases, tmp_path / "run", cfg, concurrency=16,
                                  provider_complete=lambda *_: pytest.fail("Completed request repeated"))
    assert again["state"] == "completed"


def test_fatal_model_identity_stops_dispatch_but_drains_initial_sixteen(setup, tmp_path):
    parallel, cases, cfg, by_prompt = setup
    lock, full = threading.Lock(), threading.Event()
    calls = 0

    def callback(messages, _):
        nonlocal calls
        with lock:
            index = calls
            calls += 1
            if calls == 16:
                full.set()
        assert full.wait(5)
        if index == 0:
            return replace(response(cfg, by_prompt[digest(messages)]), returned_model="wrong-model")
        time.sleep(0.1)
        return response(cfg, by_prompt[digest(messages)])

    result = parallel.run_parallel(cases, tmp_path / "run", cfg, provider_complete=callback, concurrency=16)
    assert result["state"] == "stopped_provider"
    assert result["stop_reason"] == "returned_model_mismatch"
    assert calls == result["completed"] == 16
    assert not replay(tmp_path / "run")[1]["pending_attempt_ids"]
    with pytest.raises(ValueError):
        parallel.run_parallel(cases, tmp_path / "run", cfg, concurrency=16,
                              provider_complete=lambda *_: pytest.fail("Fatal saved result allowed new calls"))


def test_requested_stop_drains_all_reserved_futures_without_dispatching_more(setup, tmp_path):
    parallel, cases, cfg, by_prompt = setup
    lock, full, stop = threading.Lock(), threading.Event(), threading.Event()
    calls = 0

    def callback(messages, _):
        nonlocal calls
        with lock:
            calls += 1
            if calls == 16:
                stop.set()
                full.set()
        assert full.wait(5)
        return response(cfg, by_prompt[digest(messages)])

    result = parallel.run_parallel(cases, tmp_path / "run", cfg, provider_complete=callback,
                                   concurrency=16, stop_event=stop)
    assert result["state"] == "stopped_interrupted"
    assert calls == result["completed"] == 16
    assert not replay(tmp_path / "run")[1]["pending_attempt_ids"]


def test_pending_reservation_is_never_reissued(setup, tmp_path):
    parallel, cases, cfg, _ = setup

    def crash(*_):
        raise RuntimeError("test-only interruption after reservation")

    with pytest.raises(RuntimeError):
        run_batch(cases, tmp_path / "run", cfg, provider_complete=crash)
    before = {p.name: p.read_bytes() for p in (tmp_path / "run/attempts").glob("*.json")}
    manifest = read(tmp_path / "run/manifest.json")
    manifest["execution_protocol"] = parallel.protocol(
        [key for key, *_ in requests(cases, cfg)], set(), 16)
    (tmp_path / "run/manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        parallel.run_parallel(cases, tmp_path / "run", cfg, concurrency=16,
                              provider_complete=lambda *_: pytest.fail("Uncertain request repeated"))
    assert all((tmp_path / "run/attempts" / name).read_bytes() == data for name, data in before.items())


def test_transient_failure_dispatch_cooldown_survives_other_successes(setup, tmp_path):
    parallel, cases, cfg, by_prompt = setup
    lock, full = threading.Lock(), threading.Event()
    starts = []
    failure_at = []

    def callback(messages, _):
        with lock:
            index = len(starts)
            starts.append(time.monotonic())
            if len(starts) == 16:
                full.set()
        assert full.wait(5)
        if index == 0:
            failure_at.append(time.monotonic())
            return response(cfg, None, error="http_502")
        if index < 16:
            time.sleep(0.05)
        return response(cfg, by_prompt[digest(messages)])

    result = parallel.run_parallel(cases, tmp_path / "run", cfg, provider_complete=callback,
                                   concurrency=16, cooldown_seconds=0.2)
    assert result["state"] == "completed"
    assert len(starts) == 40
    assert min(starts[16:]) - failure_at[0] >= 0.18
    rows, progress = replay(tmp_path / "run")
    assert progress["completed"] == 40
    assert sum(row["category"] == "provider_error" for row in rows) == 1


@pytest.mark.parametrize("concurrency", [0, 17, True, 1.5])
def test_unsupported_concurrency_is_rejected_without_calls(setup, tmp_path, concurrency):
    parallel, cases, cfg, _ = setup
    with pytest.raises(ValueError):
        parallel.run_parallel(cases, tmp_path / "run", cfg, concurrency=concurrency,
                              provider_complete=lambda *_: pytest.fail("Invalid concurrency dispatched a call"))


@pytest.mark.parametrize("failure", ["worker", "scoring"])
def test_unexpected_exception_preserves_uncertain_evidence_drains_and_blocks_resume(setup, tmp_path, monkeypatch, failure):
    parallel, cases, cfg, by_prompt = setup
    lock, full = threading.Lock(), threading.Event()
    calls = 0
    original_evaluate = parallel.evaluate

    def checked_evaluate(case, result, reference, **kwargs):
        if failure == "scoring" and case.case_id == cases[0].case_id and result.approach == "direct":
            raise ValueError("test-only scoring interruption")
        return original_evaluate(case, result, reference, **kwargs)

    monkeypatch.setattr(parallel, "evaluate", checked_evaluate)

    def callback(messages, _):
        nonlocal calls
        with lock:
            index = calls
            calls += 1
            if calls == 16:
                full.set()
        assert full.wait(5)
        first_request = digest(messages) == next(iter(by_prompt))
        if failure == "worker" and first_request:
            raise RuntimeError("test-only transport worker interruption")
        if not first_request:
            time.sleep(0.1)
        return response(cfg, by_prompt[digest(messages)])

    result = parallel.run_parallel(cases, tmp_path / "run", cfg, provider_complete=callback, concurrency=16)
    assert result["state"] == "stopped_provider"
    assert result["stop_reason"].startswith("worker_or_scoring_error:")
    assert calls == result["reserved_requests"] == 16
    assert result["completed"] == 15
    pending = [read(p) for p in (tmp_path / "run/attempts").glob("*.json") if read(p)["state"] != "completed"]
    assert len(pending) == 1
    assert ("pipeline_result" in pending[0]) is (failure == "scoring")
    with pytest.raises(ValueError):
        parallel.run_parallel(cases, tmp_path / "run", cfg, concurrency=16,
                              provider_complete=lambda *_: pytest.fail("Interrupted call reissued"))


@pytest.mark.parametrize("seconds", [-1, float("nan"), float("inf"), True])
def test_invalid_cooldown_is_rejected_before_provider(setup, tmp_path, seconds):
    parallel, cases, cfg, _ = setup
    with pytest.raises(ValueError):
        parallel.run_parallel(cases, tmp_path / "run", cfg, cooldown_seconds=seconds,
                              provider_complete=lambda *_: pytest.fail("Invalid cooldown dispatched a call"))


@pytest.mark.parametrize("model", ["qwen3.6:35b", "x-test-1"])
@pytest.mark.parametrize("mismatch", [False, True])
def test_fresh_campaign_qualifies_exact_model_and_counts_every_request(setup, tmp_path, monkeypatch, model, mismatch):
    parallel, cases, cfg, by_prompt = setup
    cfg = replace(cfg, model=replace(cfg.model, model=model))
    blocks = {"controlled": (cases, cfg, plan_run(cases, cfg))}
    execute = importlib.import_module("evaluation.run_development_campaign")
    monkeypatch.setattr(execute, "load_packet", lambda _: (blocks, {"model": model}))
    lock = threading.Lock()
    calls, budgets = [], []

    class Provider:
        def __init__(self, *, budget):
            budgets.append(budget)
            self.budget = budget

        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def list_models(self):
            assert self.budget.reserve(0)
            calls.append("metadata")
            return (model,)

        def complete(self, messages, config):
            assert self.budget.reserve(config.max_tokens)
            with lock:
                index = len(calls)
                calls.append(digest(messages))
            capability = index in (1, 2)
            content = '{"ok":true}' if capability else by_prompt[digest(messages)]
            answer = response(cfg, content)
            returned = "glm-5.3-flash" if model == "x-test-1" else model
            if mismatch:
                returned = "unexpected-model"
            return replace(answer, returned_model=returned,
                           attempts=(replace(answer.attempts[0], returned_model=returned),))

    result = parallel.execute_parallel_campaign(tmp_path / "packet", tmp_path / "campaign",
                                               authorization_reference="test-only parallel campaign",
                                               provider_factory=Provider)
    if mismatch:
        assert result["state"] == "stopped_campaign"
        assert result["stop_reason"] == "returned_model_mismatch"
        assert len(calls) == budgets[0].requests_used == 2
        assert not (tmp_path / "campaign/controlled").exists()
    else:
        assert result["state"] == "completed"
        assert len(calls) == budgets[0].requests_used == result["requests_reserved"] == 43
        assert result["requested_output_tokens_reserved"] == 42 * cfg.model.max_tokens
        assert replay(tmp_path / "campaign/controlled")[1]["completed"] == 40


def test_parallel_derivative_wrapper_preserves_calls_and_exports_segment_timings(interrupted, tmp_path, monkeypatch):
    resume, packet, original, cases, cfg = interrupted
    parallel = load_script("parallel_development_campaign")
    monkeypatch.setattr(parallel, "_resume_adapter", lambda: resume)
    execute = importlib.import_module("evaluation.run_development_campaign")
    monkeypatch.setattr(execute, "load_packet", resume.load_packet)
    derived = tmp_path / "parallel-derivative"
    before = {p.relative_to(original): p.read_bytes() for p in original.rglob("*") if p.is_file()}
    prepared = parallel.prepare_parallel_copy(original, derived, packet,
                                              authorization_reference="test-only concurrency transition")
    assert prepared["completed"] == 1 and prepared["remaining"] == 3
    actual_parallel = parallel.run_parallel
    monkeypatch.setattr(parallel, "run_parallel", lambda *a, **kw: actual_parallel(*a, **kw, cooldown_seconds=0.001))
    answers = canned(cases, cfg)
    by_prompt = {}
    for key, identity, _, view in requests(cases, cfg):
        messages = (build_extraction_messages(view) if identity["approach"] == "solver_augmented"
                    else build_messages(view.text, task_type=view.task_type,
                                        required_activity_ids=view.activity_ids, original_schedule=None))
        by_prompt[digest(messages)] = answers[key]
    lock = threading.Lock()
    calls = []

    class Provider:
        def __init__(self, *, budget):
            assert budget.requests_used == 4
            assert budget.completion_tokens_reserved == cfg.model.max_tokens * 3
            self.budget = budget

        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def list_models(self):
            pytest.fail("Derivative must reuse existing metadata qualification")

        def complete(self, messages, model):
            assert all(m.content != 'Return exactly {"ok":true} with no other text.' for m in messages)
            assert self.budget.reserve(model.max_tokens)
            with lock:
                calls.append(digest(messages))
            return response(cfg, by_prompt[digest(messages)])

    result = parallel.execute_parallel_campaign(packet, derived,
                                               authorization_reference="test-only resume", resume=True,
                                               provider_factory=Provider)
    assert result["state"] == "completed" and len(calls) == 3
    assert result["requests_reserved"] == 7
    assert sum(row["accepted"] for row in replay(derived / "controlled")[0]) == 3
    assert all((original / name).read_bytes() == data for name, data in before.items())
    assert all((derived / name).read_bytes() == data for name, data in before.items()
               if str(name) not in {"manifest.json", "controlled/manifest.json"})

    def numerical_export(blocks, directory, **_):
        directory.mkdir(parents=True)
        return {"settings": {"runtime": read(derived / "controlled/manifest.json")["contract"]["runtime"]},
                "rows": replay(derived / "controlled")[0]}

    monkeypatch.setattr("scheduling.evaluation.study.export_study", numerical_export)
    annotated = parallel.export_parallel_study(derived, tmp_path / "export", project_root=tmp_path)
    assert sum(row["execution_concurrency"] == 1 for row in annotated["rows"]) == 1
    assert sum(row["execution_concurrency"] == 16 for row in annotated["rows"]) == 3
    assert sum(row["cross_execution_pair"] for row in annotated["rows"]) == 2
    assert {item["execution_concurrency"] for item in annotated["timing_by_execution_segment"]} == {1, 16}
    assert sum(item["pipeline_attempts"] for item in annotated["timing_by_execution_segment"]) == 4


def test_preset_stop_prevents_even_fresh_metadata_qualification(setup, tmp_path, monkeypatch):
    parallel, cases, cfg, _ = setup
    execute = importlib.import_module("evaluation.run_development_campaign")
    blocks = {"controlled": (cases, cfg, plan_run(cases, cfg))}
    monkeypatch.setattr(execute, "load_packet", lambda _: (blocks, {"model": cfg.model.model}))
    stop = threading.Event()
    stop.set()

    class Provider:
        def __init__(self, *, budget):
            assert budget.requests_used == 0

        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def list_models(self):
            pytest.fail("A preset stop must prevent metadata requests")

        def complete(self, *_):
            pytest.fail("A preset stop must prevent capability and scheduling requests")

    result = parallel.execute_parallel_campaign(tmp_path / "packet", tmp_path / "campaign",
                                               authorization_reference="test-only stopped execution",
                                               provider_factory=Provider, stop_event=stop)
    assert result["state"] == "stopped_campaign"
    assert result["stop_reason"] == "operator_stop"
    assert result["requests_reserved"] == result["requested_output_tokens_reserved"] == 0
    assert not (tmp_path / "campaign/metadata-reservation.json").exists()
    assert not (tmp_path / "campaign/controlled").exists()
