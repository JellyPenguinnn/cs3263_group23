"""Installed CLI evidence reads are deterministic and make no inference calls."""

import json

import pytest

from scheduling.cli import main
from scheduling.schema import to_data
from scheduling.solver import SolverLimits, solve
from tests.formal_support import tiny
from tests.integration.test_dashboard import saved


def test_standalone_saved_result_and_invalid_input(tmp_path, capsys, monkeypatch):
    spec = tiny()
    result = solve(spec, SolverLimits())
    spec_path, result_path = tmp_path / "spec.json", tmp_path / "result.json"
    spec_path.write_text(spec.to_json())
    result_path.write_text(json.dumps({"result": to_data(result)}))
    monkeypatch.setattr(
        "scheduling.solver.solve", lambda *_: pytest.fail("Explanation must not solve")
    )
    args = [
        "explain",
        "--spec",
        str(spec_path),
        "--result",
        str(result_path),
        "--format",
        "json",
    ]
    assert main(args) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["solver"]["optimality_proven"]
    assert output["evidence"] == "saved_solver_result_not_gold_evaluation"
    result_path.write_text("{}")
    assert main(args) == 2
    assert "invalid_input" in capsys.readouterr().out


def test_saved_run_is_revalidated_without_mutation_or_inference(
    saved, capsys, monkeypatch
):
    path, *_ = saved
    before = {p: p.read_bytes() for p in path.rglob("*") if p.is_file()}
    monkeypatch.setattr(
        "scheduling.solver.solve", lambda *_: pytest.fail("Must not solve")
    )
    monkeypatch.setattr(
        "scheduling.providers.SoCLaaSProvider.from_environment",
        lambda **_: pytest.fail("No credentials"),
    )
    for approach in ("direct", "solver_augmented"):
        args = [
            "explain",
            "--run-dir",
            str(path),
            "--case-id",
            "repair",
            "--approach",
            approach,
            "--format",
            "json",
        ]
        assert main(args) == 0
        output = capsys.readouterr().out
        assert json.loads(output)["evaluation"]["accepted"]
        assert main(args) == 0
        assert capsys.readouterr().out == output
    assert before == {p: p.read_bytes() for p in path.rglob("*") if p.is_file()}
    assert (
        main(
            [
                "explain",
                "--run-dir",
                str(path),
                "--case-id",
                "repair",
                "--approach",
                "direct",
                "--variant",
                "absent",
            ]
        )
        == 2
    )
    capsys.readouterr()
    attempt = next((path / "attempts").glob("*.json"))
    content = json.loads(attempt.read_text())
    content["payload"]["pipeline_result"]["status"] = "UNKNOWN"
    attempt.write_text(json.dumps(content))
    assert main(args) == 2


def test_rejected_large_model_slot_survives_replay_and_explanation(tmp_path, capsys):
    from scheduling.evaluation.benchmark import tiny_fixtures
    from scheduling.evaluation.runner import requests, run_batch, replay
    from tests.integration.test_evaluation import config, canned

    cases = tiny_fixtures()[:1]
    cfg = config()
    responses = canned(cases, cfg)
    key = next(k for k, identity, _, _ in requests(cases, cfg)
               if identity["approach"] == "direct")
    responses[key] = json.dumps({"status": "SAT", "schedule": [
        {"activity_id": "A", "start_slot": 10**30},
        {"activity_id": "B", "start_slot": 2},
    ]})
    run_batch(cases, tmp_path, cfg, canned=responses)
    rows, progress = replay(tmp_path)
    direct = next(r for r in rows if r["approach"] == "direct")
    assert progress["completed"] == 2
    assert direct["accepted"] is False
    assert direct["category"] == "gold_invalid_schedule"
    before = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    assert main(["explain", "--run-dir", str(tmp_path), "--case-id",
                 cases[0].case_id, "--approach", "direct", "--format", "json"]) == 0
    text = capsys.readouterr().out
    assert json.loads(text)["evaluation"]["accepted"] is False
    assert f"slot {10**30} (outside horizon)" in text
    assert before == {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
