"""Dashboard accounting, live monitoring and HTTP boundaries without network calls."""

from datetime import datetime, timedelta
from io import BytesIO
import json
from types import SimpleNamespace

import pytest

from scheduling.dashboard.service import Dashboard, snapshot
from scheduling.dashboard.server import Handler
from scheduling.evaluation.benchmark import tiny_fixtures
from scheduling.evaluation.runner import RunConfig, requests, run_batch, read, replay
from scheduling.evaluation.scoring import digest
from scheduling.providers import ModelConfig
from scheduling.solver import SolverLimits


@pytest.fixture
def saved(tmp_path):
    cases = tiny_fixtures()
    cfg = RunConfig(
        ModelConfig("offline", 512), SolverLimits(), SolverLimits(), 12, 6144
    )
    responses = {
        key: (
            case.problem.to_json()
            if ident["approach"] == "solver_augmented"
            else json.dumps(
                {
                    "status": case.expected_label,
                    "schedule": case.witness.to_list() if case.witness else None,
                }
            )
        )
        for key, ident, case, _ in requests(cases, cfg)
    }
    directory = tmp_path / "run"
    run_batch(cases, directory, cfg, canned=responses)
    return directory, cases, cfg


def test_snapshot_recomputes_scores_and_preserves_missing_usage(saved):
    path, cases, cfg = saved
    record_path = next((path / "attempts").glob("*.json"))
    record = read(record_path)
    record["payload"]["evaluation"]["accepted"] = False
    record["sha256"] = digest(record["payload"])
    record_path.write_text(json.dumps(record))
    app = Dashboard(path.parent, run_dir=path)
    key = app.bootstrap()["selected"]
    result = app.overview(key)
    assert result["progress"]["completed"] == 12
    assert all(s["accepted_answer"]["rate"] == 1 for s in result["summary"]["subsets"])
    assert all(
        s["tokens"]["total_tokens"]["reported_sum"] is None
        for s in result["summary"]["subsets"]
    )
    assert app.case_page(key, task="repair")["total"] == 1
    assert app.case_page(key, outcome="rejected")["total"] == 0
    assert app.case_page(key, offset=20)["items"] == []
    detail = app.case_detail(key, 5)
    assert detail["case"]["original_schedule"]
    assert detail["reference"]["optimality_proven"]
    with pytest.raises(LookupError):
        app.get_run("../../.env")
    with pytest.raises(LookupError):
        app.case_detail(key, -1)


def test_corrupt_and_symlinked_records_are_not_shown(saved, tmp_path):
    path, *_ = saved
    record_path = next((path / "attempts").glob("*.json"))
    content = record_path.read_text()
    record = json.loads(content)
    record["payload"]["pipeline_result"]["status"] = "UNSAT"
    record_path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="checksum"):
        snapshot(path)
    outside = tmp_path / "external.json"
    outside.write_text(content)
    record_path.unlink()
    record_path.symlink_to(outside)
    with pytest.raises(ValueError, match="inside"):
        snapshot(path)


def test_active_pending_is_not_counted_as_model_rejection(saved):
    path, *_ = saved
    record_path = next((path / "attempts").glob("*.json"))
    record = read(record_path)
    record_path.write_text(
        json.dumps({"state": "pending_or_interrupted", "identity": record["identity"]})
    )
    (path / ".lock").touch()
    result = snapshot(path)
    assert result["progress"]["completed"] == 11
    assert len(result["progress"]["pending_attempt_ids"]) == 1
    assert sum(s["attempt_count"] for s in result["summary"]["subsets"]) == 11
    (path / ".lock").unlink()
    assert sum(s["attempt_count"] for s in snapshot(path)["summary"]["subsets"]) == 12


class Connection:
    def __init__(self, data):
        self.input = BytesIO(data)
        self.output = BytesIO()

    def makefile(self, mode, *args):
        return self.input

    def sendall(self, data):
        self.output.write(data)

    def settimeout(self, *args):
        pass


def http(app, method="GET", path="/api/session", headers=None, body=None):
    payload = json.dumps(body).encode() if body is not None else b""
    fields = {"Host": "127.0.0.1:8876", **(headers or {})}
    if body is not None:
        fields |= {
            "Content-Type": "application/json",
            "Content-Length": str(len(payload)),
        }
    raw = (
        f"{method} {path} HTTP/1.0\r\n"
        + "".join(f"{k}: {v}\r\n" for k, v in fields.items())
        + "\r\n"
    )
    connection = Connection(raw.encode() + payload)
    Handler(connection, ("127.0.0.1", 1), SimpleNamespace(app=app, server_port=8876))
    head, content = connection.output.getvalue().split(b"\r\n\r\n", 1)
    return int(head.split()[1]), head, content


def test_http_security_assets_and_read_only_boundary(tmp_path):
    app = Dashboard(tmp_path)
    status, headers, body = http(app)
    assert status == 200 and b"no-store" in headers
    assert set(json.loads(body)) == {"runs", "selected"}
    for headers in (
        {"Host": "attacker.invalid"},
        {"Origin": "https://attacker.invalid"},
        {"Sec-Fetch-Site": "cross-site"},
    ):
        assert http(app, headers=headers)[0] == 403
    for path in (
        "/.env",
        "/../.env",
        "/static/../../.env",
        "/api/case?run=../../.env&id=0",
    ):
        assert http(app, path=path)[0] in (404, 422)
    for path in ("/", "/style.css", "/app.js"):
        status, headers, body = http(app, path=path)
        assert status == 200 and body and b"Content-Security-Policy" in headers
    for path in ("/api/preview", "/api/start", "/api/stop"):
        assert http(app, "POST", path, body={"authorized": True})[0] == 405
    assert not list(tmp_path.iterdir())


def test_cached_monitor_refreshes_external_progress_without_solver_or_provider(
    saved, monkeypatch
):
    path, *_ = saved
    monkeypatch.setattr(
        "scheduling.solver.solve",
        lambda *a, **kw: pytest.fail("Dashboard must not solve"),
    )
    monkeypatch.setattr(
        "scheduling.providers.SoCLaaSProvider.from_environment",
        lambda **kw: pytest.fail("Dashboard must not access credentials"),
    )
    app = Dashboard(path.parent, run_dir=path)
    key = app.bootstrap()["selected"]
    first = app.overview(key)
    assert first["progress"]["completed"] == 12
    record_path = next((path / "attempts").glob("*.json"))
    original = record_path.read_bytes()
    record = json.loads(original)
    latest = max(
        datetime.fromisoformat(read(p)["started_utc"])
        for p in (path / "attempts").glob("*.json")
    )
    record_path.write_text(
        json.dumps(
            {
                "state": "pending_or_interrupted",
                "identity": record["identity"],
                "started_utc": (latest + timedelta(seconds=1)).isoformat(),
            }
        )
    )
    (path / ".lock").touch()
    pending = app.overview(key)
    assert pending["revision"] != first["revision"]
    assert pending["progress"]["completed"] == 11
    assert pending["activity"][0]["state"] == "pending_or_interrupted"
    record_path.write_bytes(original)
    (path / ".lock").unlink()
    complete = app.overview(key)
    assert complete["progress"]["completed"] == 12
    assert complete["progress"]["pending_attempt_ids"] == []
    assert all(row["state"] == "completed" for row in complete["activity"])


def test_catalog_ignores_component_manifests_and_discovers_new_runs(saved, tmp_path):
    path, *_ = saved
    app = Dashboard(tmp_path)
    assert len(app.bootstrap()["runs"]) == 1
    component = tmp_path / "component"
    component.mkdir()
    (component / "manifest.json").write_text("{}")
    assert len(app.bootstrap()["runs"]) == 1
    import shutil

    shutil.copytree(path, tmp_path / "later-run")
    assert len(app.bootstrap()["runs"]) == 2
