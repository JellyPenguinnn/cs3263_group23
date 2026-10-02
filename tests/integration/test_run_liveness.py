"""OS-owned liveness and crash recovery checks; no network or model calls."""

import os
import select
import subprocess
import sys

import pytest

from scheduling.dashboard.service import Dashboard
from scheduling.evaluation.liveness import RunLock, probe_run_liveness
from scheduling.evaluation.runner import read


CHILD_RUN = r'''
import json
from pathlib import Path
import signal
import sys
from scheduling.evaluation.benchmark import tiny_fixtures
from scheduling.evaluation.runner import RunConfig, run_batch
from scheduling.providers import ModelConfig, ModelResponse
from scheduling.solver import SolverLimits
cases = tiny_fixtures()[:1]
cfg = RunConfig(ModelConfig("synthetic", 512), SolverLimits(), SolverLimits(),
                2, 1024, evidence="live_development")
calls = 0
def provider(*_):
    global calls
    calls += 1
    if calls == 2:
        print("READY", flush=True)
        signal.pause()
    content = json.dumps({"status": cases[0].expected_label,
                         "schedule": cases[0].witness.to_list()})
    return ModelResponse(content, "synthetic", 0, (), finish_reason="stop")
run_batch(cases, Path(sys.argv[1]), cfg, provider_complete=provider)
'''


def test_killed_runner_releases_liveness_invalidates_cache_and_keeps_reservations(tmp_path):
    path = tmp_path / "run"
    process = subprocess.Popen([sys.executable, "-c", CHILD_RUN, str(path)],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        ready, _, _ = select.select([process.stdout], [], [], 20)
        assert ready and process.stdout.readline().strip() == "READY", "Child runner did not reach pending call"
        assert probe_run_liveness(path) == "active"
        with pytest.raises(FileExistsError):
            RunLock(path / ".lock")
        app = Dashboard(tmp_path, run_dir=path)
        key = app.bootstrap()["selected"]
        active = app.overview(key)
        assert active["active"] and active["liveness"] == "active"
        assert active["progress"]["completed"] == 1
        assert len(active["progress"]["pending_attempt_ids"]) == 1
        assert sum(s["attempt_count"] for s in active["summary"]["subsets"]) == 1
        original = {p: p.read_bytes() for p in path.rglob("*") if p.is_file()}
        lock_stat = (path / ".lock").stat()
        process.kill()
        process.wait(timeout=10)
        assert probe_run_liveness(path) == "inactive"
        stopped = app.overview(key)
        assert not stopped["active"] and stopped["liveness"] == "inactive"
        assert stopped["revision"] != active["revision"]
        assert stopped["progress"] == active["progress"]
        assert sum(s["attempt_count"] for s in stopped["summary"]["subsets"]) == 2
        assert (path / ".lock").stat().st_mtime_ns == lock_stat.st_mtime_ns
        assert all(p.read_bytes() == value for p, value in original.items())
        assert (path / ".lock").exists()
        # OS release alone must never authorize reissue of the abandoned run.
        with pytest.raises(FileExistsError):
            RunLock(path / ".lock")
        records = [read(p) for p in (path / "attempts").glob("*.json")]
        assert sorted(r["state"] for r in records) == ["completed", "pending_or_interrupted"]
    finally:
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=10)


def test_legacy_lock_is_unknown_not_active_and_probe_does_not_modify_it(tmp_path):
    path = tmp_path / ".lock"
    path.touch()
    before = path.stat()
    assert probe_run_liveness(tmp_path) == "unknown_legacy"
    assert path.read_bytes() == b"" and path.stat().st_mtime_ns == before.st_mtime_ns
    with pytest.raises(FileExistsError):
        RunLock(path)


def test_normal_lock_release_and_exception_cleanup(tmp_path):
    path = tmp_path / ".lock"
    assert probe_run_liveness(tmp_path) == "inactive"
    with pytest.raises(RuntimeError, match="synthetic"):
        with RunLock(path):
            assert probe_run_liveness(tmp_path) == "active"
            raise RuntimeError("synthetic")
    assert not path.exists() and probe_run_liveness(tmp_path) == "inactive"
    with RunLock(path):
        assert probe_run_liveness(tmp_path) == "active"


@pytest.mark.parametrize("replacement", ["file", "symlink", "absent"])
def test_release_does_not_delete_replaced_lock_or_its_target(tmp_path, replacement):
    path = tmp_path / ".lock"
    outside = tmp_path / "preserved"
    outside.write_text("untouched")
    lock = RunLock(path)
    descriptor = lock.fd
    path.unlink()
    if replacement == "file":
        path.write_text("replacement")
    elif replacement == "symlink":
        path.symlink_to(outside)
    with pytest.raises(ValueError, match="replaced or removed"):
        lock.release()
    with pytest.raises(OSError):
        os.fstat(descriptor)
    assert outside.read_text() == "untouched"
    if replacement == "file":
        assert path.read_text() == "replacement"
    elif replacement == "symlink":
        assert path.is_symlink()
    lock.release()  # Idempotent close even after a replaced path.


def test_lock_probe_and_acquisition_reject_symlinks_without_touching_targets(tmp_path):
    outside = tmp_path / "preserved"
    outside.write_text("untouched")
    path = tmp_path / ".lock"
    path.symlink_to(outside)
    with pytest.raises(ValueError, match="symlink"):
        probe_run_liveness(tmp_path)
    with pytest.raises(FileExistsError):
        RunLock(path)
    assert outside.read_text() == "untouched" and path.is_symlink()


@pytest.mark.parametrize("kind", ["hardlink", "fifo"])
def test_lock_probe_rejects_nonexclusive_regular_file_without_blocking(tmp_path, kind):
    path = tmp_path / ".lock"
    if kind == "hardlink":
        outside = tmp_path / "preserved"
        outside.write_text("untouched")
        os.link(outside, path)
    else:
        os.mkfifo(path)
    with pytest.raises(ValueError, match="regular"):
        probe_run_liveness(tmp_path)



def test_failed_lock_initialization_closes_descriptor_but_preserves_tombstone(tmp_path, monkeypatch):
    import scheduling.evaluation.liveness as liveness
    descriptors = []
    def fail_lock(descriptor, flags):
        descriptors.append(descriptor)
        raise OSError("synthetic advisory lock failure")
    monkeypatch.setattr(liveness.fcntl, "flock", fail_lock)
    with pytest.raises(OSError, match="synthetic"):
        RunLock(tmp_path / ".lock")
    with pytest.raises(OSError):
        os.fstat(descriptors[0])
    assert (tmp_path / ".lock").exists()
    assert probe_run_liveness(tmp_path) == "unknown_legacy"
    with pytest.raises(FileExistsError):
        RunLock(tmp_path / ".lock")
