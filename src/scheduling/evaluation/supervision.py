"""One-shot process supervision; lifecycle records never authorize a retry."""

from datetime import datetime, timezone
from pathlib import Path
import os
import signal
import subprocess
import time

from scheduling.evaluation.runner import replace_pending, write_new


def supervise(command, directory, *, cwd=None, interval=5, stop_grace=20):
    """Run one child, preserve its exit/signal, and publish a durable heartbeat.

    The supervisor itself must be started by an independent process manager.
    It neither restarts a child nor reconciles interrupted provider reservations.
    """
    if interval <= 0 or stop_grace <= 0:
        raise ValueError("Supervisor intervals must be positive")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False, mode=0o700)
    started = datetime.now(timezone.utc)
    status = {
        "format_version": "1.0", "supervisor_pid": os.getpid(),
        "started_utc": started.isoformat(), "worker_pid": None,
        "state": "starting", "returncode": None, "stop_signal": None,
        "automatic_restarts": 0,
    }
    write_new(directory / "start.json", status)
    child = None
    stop_at = None

    def publish():
        now = datetime.now(timezone.utc)
        status["heartbeat_utc"] = now.isoformat()
        status["elapsed_wall_seconds"] = (now - started).total_seconds()
        replace_pending(directory / "status.json", status)

    def stop(signum, _frame):
        nonlocal stop_at
        if status["stop_signal"] is None:
            status["stop_signal"] = signum
            stop_at = time.monotonic()
            if child is not None and child.poll() is None:
                child.send_signal(signum)

    signals = (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)
    previous = {sig: signal.signal(sig, stop) for sig in signals}
    publish()
    try:
        with (directory / "worker.log").open("xb") as log:
            if status["stop_signal"] is not None:
                status.update(state="interrupted", returncode=-status["stop_signal"])
                return status["returncode"]
            child = subprocess.Popen(command, cwd=cwd, stdin=subprocess.DEVNULL,
                                     stdout=log, stderr=subprocess.STDOUT)
            status.update(worker_pid=child.pid, state="running")
            # Cover a signal delivered between the pre-spawn guard and Popen.
            if status["stop_signal"] is not None:
                child.send_signal(status["stop_signal"])
            publish()
            while child.poll() is None:
                if stop_at is not None and time.monotonic() - stop_at >= stop_grace:
                    child.kill()
                try:
                    child.wait(timeout=interval)
                except subprocess.TimeoutExpired:
                    pass
                publish()
            status["returncode"] = child.returncode
            status["state"] = (
                "interrupted" if status["stop_signal"] is not None or child.returncode < 0
                else "completed" if child.returncode == 0 else "failed"
            )
            return child.returncode
    except Exception as error:
        status.update(state="supervisor_failed", error_type=type(error).__name__)
        # Never leave an unobserved child dispatching new requests after the
        # supervisor can no longer persist its own lifecycle records.
        if child is not None and child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=stop_grace)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
        raise
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)
        status["finished_utc"] = datetime.now(timezone.utc).isoformat()
        publish()
        write_new(directory / "exit.json", status)
