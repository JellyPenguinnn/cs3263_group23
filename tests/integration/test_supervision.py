"""One-shot lifecycle guarantees using child processes without network access."""

import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import pytest

from scheduling.evaluation.supervision import supervise
from tests.integration.test_model_qualification import load_script

entry = load_script("supervise_development_campaign")


@pytest.mark.parametrize("code", [0, 7])
def test_child_exit_is_recorded_once_and_cannot_be_reissued(tmp_path, code):
    root = tmp_path / "supervisor"
    assert supervise([sys.executable, "-c", f"raise SystemExit({code})"], root, interval=0.02) == code
    result = json.loads((root / "exit.json").read_text())
    assert result["state"] == ("completed" if code == 0 else "failed")
    assert result["returncode"] == code and result["automatic_restarts"] == 0
    assert result["worker_pid"] != os.getpid()
    assert result["elapsed_wall_seconds"] >= 0
    with pytest.raises(FileExistsError):
        supervise([sys.executable, "-c", "raise AssertionError('Must not start')"], root)


def test_worker_signal_exit_is_durable_and_not_retried(tmp_path):
    root = tmp_path / "supervisor"
    code = "import os, signal; os.kill(os.getpid(), signal.SIGTERM)"
    assert supervise([sys.executable, "-c", code], root, interval=0.02) == -signal.SIGTERM
    record = json.loads((root / "exit.json").read_text())
    assert record["state"] == "interrupted" and record["automatic_restarts"] == 0


def test_supervisor_publishes_heartbeat_and_forwards_stop(tmp_path):
    root = tmp_path / "supervisor"
    script = (
        "import sys; from pathlib import Path; from scheduling.evaluation.supervision import supervise; "
        "supervise([sys.executable,'-c','import time; time.sleep(60)'],Path(sys.argv[1]),interval=0.05)"
    )
    with subprocess.Popen([sys.executable, "-c", script, str(root)]) as parent:
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            if (root / "status.json").exists():
                record = json.loads((root / "status.json").read_text())
                if record["state"] == "running":
                    break
            time.sleep(0.02)
        else:
            parent.kill()
            pytest.fail("No supervisor heartbeat")
        first = record["heartbeat_utc"]
        while time.monotonic() < deadline:
            record = json.loads((root / "status.json").read_text())
            if record["heartbeat_utc"] != first:
                break
            time.sleep(0.02)
        assert record["heartbeat_utc"] != first
        parent.send_signal(signal.SIGTERM)
        parent.wait(timeout=8)
    result = json.loads((root / "exit.json").read_text())
    assert result["state"] == "interrupted" and result["stop_signal"] == signal.SIGTERM
    with pytest.raises(ProcessLookupError):
        os.kill(record["worker_pid"], 0)


def test_spawn_failure_records_failure_without_leaving_running_status(tmp_path):
    root = tmp_path / "supervisor"
    with pytest.raises(FileNotFoundError):
        supervise([str(tmp_path / "missing")], root)
    assert json.loads((root / "exit.json").read_text())["state"] == "supervisor_failed"


def test_env_file_is_data_not_shell_code_and_is_never_logged(tmp_path, capsys):
    secret = tmp_path / ".env"
    secret.write_text("export SOCLAAS_API_KEY='test-only-$(no-shell)'\nSOCLAAS_MODEL=ignored\n")
    secret.chmod(0o600)
    values = entry.load_credentials(secret)
    assert values == {"SOCLAAS_API_KEY": "test-only-$(no-shell)"}
    assert capsys.readouterr().out == ""
    secret.chmod(0o644)
    with pytest.raises(ValueError, match="private"):
        entry.load_credentials(secret)


def test_worker_failure_writes_sanitized_nonzero_receipt(tmp_path, monkeypatch):
    from types import SimpleNamespace
    def fail(_):
        raise ValueError("test-only private value must not be logged")
    monkeypatch.setattr(entry, "load_packet", fail)
    args = SimpleNamespace(packet=tmp_path / "missing", directory=tmp_path)
    assert entry.worker(args) == 2
    text = (tmp_path / "worker-exit.json").read_text()
    assert "private value" not in text
    assert json.loads(text)["phase"] == "preflight"


def test_service_has_no_automatic_restart_or_embedded_credentials(tmp_path):
    import plistlib
    launcher = load_script("launch_macos_campaign")
    command = [sys.executable, "/snapshot/supervise.py", "--env-file", "/private/.env"]
    config = launcher.service_definition(command, tmp_path / "campaign",
                                         working_directory=tmp_path, label="test.campaign")
    assert config["RunAtLoad"] is True and config["KeepAlive"] is False
    assert config["ProgramArguments"] == ["/usr/bin/caffeinate", "-is", *command]
    assert set(config["EnvironmentVariables"]) == {"PYTHONDONTWRITEBYTECODE", "PYTHONUNBUFFERED"}
    assert "SOCLAAS_API_KEY" not in plistlib.dumps(config).decode()
