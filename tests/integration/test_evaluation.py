from dataclasses import replace
import json
from pathlib import Path
import pytest
from scheduling.evaluation.benchmark import tiny_fixtures
from scheduling.evaluation.cases import case_bundle
from scheduling.evaluation.runner import RunConfig, requests, run_batch, replay, read
from scheduling.evaluation.scoring import reference, evaluate, digest
from scheduling.evaluation.metrics import summarize, paired, wilson
from scheduling.providers.types import ModelConfig, ModelResponse, Attempt, Usage
from scheduling.schema import PipelineResult, Schedule, to_data
from scheduling.pipelines.solver_augmented import PUBLIC_REQUEST_ID
from scheduling.solver import SolverLimits


def config(**kwargs):
    return RunConfig(
        ModelConfig("offline", 2048),
        SolverLimits(),
        SolverLimits(),
        100,
        204800,
        **kwargs,
    )


def canned(cases, cfg):
    result = {}
    for key, identity, case, view in requests(cases, cfg):
        if identity["approach"] == "solver_augmented":
            content = replace(case.problem, instance_id=PUBLIC_REQUEST_ID).to_json()
        else:
            content = json.dumps(
                {
                    "status": case.expected_label,
                    "schedule": case.witness.to_list() if case.witness else None,
                }
            )
        result[key] = content
    return result


def test_complete_batch_and_offline_replay_resume_without_provider(
    tmp_path, monkeypatch
):
    cases = tiny_fixtures()
    cfg = config()
    responses = canned(cases, cfg)
    assert run_batch(cases, tmp_path, cfg, canned=responses)["completed"] == 12
    for _ in range(2):
        assert (
            run_batch(cases, tmp_path, cfg, canned=responses)["reserved_requests"] == 12
        )
    import scheduling.solver as solver

    monkeypatch.setattr(
        solver, "solve", lambda *_: pytest.fail("Replay must not call solver")
    )
    rows, progress = replay(tmp_path)
    assert progress["completed"] == 12
    assert all(r["accepted"] for r in rows)
    summary = summarize(rows)
    assert all(s["accepted_answer"]["rate"] == 1 for s in summary["subsets"])
    assert all(
        s["tokens"]["total_tokens"]["reported_sum"] is None for s in summary["subsets"]
    )
    assert not list(tmp_path.glob(".lock"))


def test_invalid_wrong_and_unknown_keep_denominators_and_extraction_separate(tmp_path):
    cases = (tiny_fixtures()[3],)
    cfg = config()
    responses = canned(cases, cfg)
    for key, identity, case, _ in requests(cases, cfg):
        if identity["approach"] == "direct":
            responses[key] = "bad JSON"
        else:
            wrong = replace(case.problem, instance_id=PUBLIC_REQUEST_ID).to_dict()
            wrong["constraints"] = []
            # This may happen to return a valid schedule; scoring must independently check.
            responses[key] = json.dumps(wrong)
    run_batch(cases, tmp_path, cfg, canned=responses)
    rows, _ = replay(tmp_path)
    a = next(r for r in rows if r["approach"] == "direct")
    b = next(r for r in rows if r["approach"] == "solver_augmented")
    assert a["accepted"] is False and a["category"] == "invalid_output"
    assert not b["extraction_comparison"]["structurally_equivalent"]
    assert summarize(rows)["paired"][0]["pair_count"] == 1


def test_budget_persists_across_resume_and_mismatch_refused(tmp_path):
    cases = tiny_fixtures()
    cfg = replace(config(), max_requests=1, max_requested_output_tokens=2048)
    responses = canned(cases, cfg)
    assert (
        run_batch(cases, tmp_path, cfg, canned=responses)["state"] == "budget_exhausted"
    )
    assert run_batch(cases, tmp_path, cfg, canned=responses)["reserved_requests"] == 1
    with pytest.raises(ValueError, match="configuration"):
        run_batch(cases, tmp_path, replace(cfg, max_requests=2), canned=responses)


def test_interrupted_request_not_reissued_and_reservation_retained(tmp_path):
    cases = (tiny_fixtures()[0],)
    cfg = config(evidence="live_development")
    calls = []

    def failed(*_):
        calls.append(1)
        raise RuntimeError("simulated interruption")

    with pytest.raises(RuntimeError):
        run_batch(cases, tmp_path, cfg, provider_complete=failed)
    with pytest.raises(ValueError, match="Interrupted"):
        run_batch(cases, tmp_path, cfg, provider_complete=failed)
    assert len(calls) == 1
    assert len(replay(tmp_path)[1]["pending_attempt_ids"]) == 1


def test_auth_failure_stops_run_and_resume(tmp_path):
    cfg = config(evidence="live_development")
    calls = []

    def failed(*_):
        calls.append(1)
        return ModelResponse(
            None, None, 0, (Attempt(1, 0, 401, Usage(), error="http_401"),), "http_401"
        )

    assert (
        run_batch(tiny_fixtures(), tmp_path, cfg, provider_complete=failed)["state"]
        == "stopped_provider"
    )
    assert (
        run_batch(tiny_fixtures(), tmp_path, cfg, provider_complete=failed)["state"]
        == "stopped_provider"
    )
    assert len(calls) == 1


def test_changed_saved_result_rejected(tmp_path):
    cases = (tiny_fixtures()[0],)
    cfg = config()
    run_batch(cases, tmp_path, cfg, canned=canned(cases, cfg))
    p = next((tmp_path / "attempts").glob("*.json"))
    r = read(p)
    r["payload"]["pipeline_result"]["status"] = "UNSAT"
    p.write_text(json.dumps(r))
    with pytest.raises(ValueError, match="checksum"):
        replay(tmp_path)


def test_test_split_refused_and_reference_unknown_not_unsat(tmp_path):
    case = tiny_fixtures()[0]
    cfg = config()
    with pytest.raises(ValueError, match="development"):
        run_batch((replace(case, split="test"),), tmp_path, cfg, canned={})
    ref = reference(case, SolverLimits(0))
    output = PipelineResult(case.case_id, "canonical", "direct", "UNKNOWN")
    row = evaluate(case, output, ref)
    assert row["gold_label"] == "UNRESOLVED" and row["accepted"] is None


def test_reference_contradiction_stops_scoring():
    case = tiny_fixtures()[0]
    ref = reference(case, SolverLimits())
    ref["result"]["status"] = "INFEASIBLE"
    ref["result"]["schedule"] = None
    with pytest.raises(ValueError, match="contradicts"):
        evaluate(
            case,
            PipelineResult(case.case_id, "canonical", "direct", "SAT", case.witness),
            ref,
        )


def test_repair_gaps_condition_on_prior_proven_objectives():
    case = tiny_fixtures()[-1]
    ref = reference(case, SolverLimits())
    schedule = Schedule.from_list(
        [{"activity_id": "A", "start_slot": 2}, {"activity_id": "B", "start_slot": 3}]
    )
    row = evaluate(
        case, PipelineResult(case.case_id, "canonical", "direct", "SAT", schedule), ref
    )
    assert row["objective_values"] == (2, 3, 0) and row["objective_gaps"] == [
        1,
        None,
        None,
    ]


def test_wilson_and_paired_cluster_identity():
    assert wilson(0, 0) is None and wilson(0, 10)[0] == 0
    rows = []
    for i in range(12):
        for approach in ("direct", "solver_augmented"):
            rows.append(
                dict(
                    case_id=str(i),
                    group_id=str(i),
                    variant_id="canonical",
                    repeat=0,
                    approach=approach,
                    gold_label="SAT",
                    accepted=approach == "solver_augmented",
                    returned_model="one",
                )
            )
    result = paired(rows, resamples=100, seed=7)
    assert result["B_minus_A_percentage_points"] == 100 and result[
        "cluster_bootstrap_95"
    ] == [100, 100]
    assert result["counts"]["only_B"] == 12
    with pytest.raises(ValueError):
        paired(rows + [rows[0]])


def test_transport_failure_remains_in_same_model_denominator():
    case = tiny_fixtures()[0]
    ref = reference(case, SolverLimits())
    good = PipelineResult(
        case.case_id,
        "canonical",
        "direct",
        "SAT",
        case.witness,
        model_response=ModelResponse("", "backend", 0, ()),
        config_sha256="one-config",
    )
    bad = PipelineResult(
        case.case_id, "canonical", "direct", "ERROR", config_sha256="one-config"
    )
    a = evaluate(case, good, ref)
    b = evaluate(case, bad, ref)
    b["case_id"] = "second"
    b["group_id"] = "second"
    summaries = summarize([a, b])["subsets"]
    assert len(summaries) == 1 and summaries[0]["sat_validity"] == {
        "numerator": 1,
        "denominator": 2,
        "rate": 0.5,
    }


def test_interrupted_attempt_counts_as_failure_in_replay(tmp_path):
    case = tiny_fixtures()[0]
    cfg = config(evidence="live_development")

    def interrupted(*_):
        raise RuntimeError("interrupt")

    with pytest.raises(RuntimeError):
        run_batch((case,), tmp_path, cfg, provider_complete=interrupted)
    rows, progress = replay(tmp_path)
    assert (
        progress["reserved"] == 1
        and progress["completed"] == 0
        and progress["not_started"] == 1
    )
    assert rows[0]["accepted"] is False
    assert summarize(rows)["subsets"][0]["sat_validity"]["denominator"] == 1


def test_live_boundary_only_receives_public_messages(tmp_path):
    case = tiny_fixtures()[0]
    cfg = config(evidence="live_development")
    payloads = []

    def callback(messages, model):
        payloads.append(messages[1].content)
        if "instance_id" in json.loads(messages[1].content):
            content = replace(case.problem, instance_id=PUBLIC_REQUEST_ID).to_json()
        else:
            content = json.dumps({"status": "SAT", "schedule": case.witness.to_list()})
        return ModelResponse(content, "backend", 0, ())

    run_batch((case,), tmp_path, cfg, provider_complete=callback)
    assert len(payloads) == 2
    assert all(case.case_id not in p for p in payloads)
    assert all("variant_id" not in json.loads(p) for p in payloads)
    assert all(
        "expected_label" not in p and "justification" not in p and "witness" not in p
        for p in payloads
    )


def test_invalid_direct_retains_missing_duplicate_and_extra_diagnostics():
    from scheduling.pipelines.direct import run_direct
    from scheduling.evaluation.benchmark import render

    case = tiny_fixtures()[0]
    malformed = [
        {"activity_id": "A", "start_slot": 0},
        {"activity_id": "A", "start_slot": 0},
        {"activity_id": "X", "start_slot": 1},
    ]
    result = run_direct(
        render(case),
        ModelConfig("canned", 200),
        provider_complete=lambda *_: ModelResponse(
            json.dumps({"status": "SAT", "schedule": malformed}), "canned", 0, ()
        ),
    )
    row = evaluate(case, result, reference(case, SolverLimits()))
    assert not row["accepted"] and {
        v["category"] for v in row["validation"]["violations"]
    } == {"missing_activity", "duplicate_activity", "extra_activity"}


def test_cli_generator_validator_batch_and_replay(tmp_path, capsys):
    from scheduling.cli import main

    cases = tmp_path / "cases.json"
    cfgfile = tmp_path / "config.json"
    responses = tmp_path / "canned.json"
    cfg = config()
    cfgfile.write_text(json.dumps(to_data(cfg)))
    responses.write_text(json.dumps(canned(tiny_fixtures(), cfg)))
    assert main(["benchmark-generate", "--fixtures-only", "--output", str(cases)]) == 0
    assert (
        main(
            [
                "evaluate-batch",
                "--cases",
                str(cases),
                "--config",
                str(cfgfile),
                "--canned",
                str(responses),
                "--run-dir",
                str(tmp_path / "run"),
            ]
        )
        == 0
    )
    assert (
        main(
            [
                "evaluate-replay",
                "--run-dir",
                str(tmp_path / "run"),
                "--export-dir",
                str(tmp_path / "export"),
            ]
        )
        == 0
    )
    assert (tmp_path / "export/attempts.csv").is_file()
    spec = tmp_path / "spec.json"
    schedule = tmp_path / "schedule.json"
    spec.write_text(tiny_fixtures()[0].problem.to_json())
    schedule.write_text("[]")
    assert main(["validate", "--spec", str(spec), "--schedule", str(schedule)]) == 2
    capsys.readouterr()
