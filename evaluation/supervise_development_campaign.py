"""Run one authorized campaign under an OS service, with durable exit evidence.

Use a one-shot service with automatic restart disabled. This entry point is
portable; on macOS launchd can own it independently of an agent terminal.
"""

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import shlex
import signal
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evaluation.run_development_campaign import load_packet, run_campaign
from scheduling.evaluation.runner import write_new
from scheduling.evaluation.study import export_study
from scheduling.evaluation.supervision import supervise
from scheduling.providers.execution import BASE_URL


def load_credentials(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_mode & 0o077:
        raise ValueError("Use a private regular credential file")
    values = {}
    for line in path.read_text().splitlines():
        fields = shlex.split(line, comments=True)
        if fields and fields[0] == "export":
            fields = fields[1:]
        if len(fields) == 1:
            name, separator, value = fields[0].partition("=")
            if separator and name in {"SOCLAAS_API_KEY", "SOCLAAS_BASE_URL"}:
                values[name] = value
    if not values.get("SOCLAAS_API_KEY", "").strip():
        raise ValueError("Configure an authorized provider key locally")
    if values.get("SOCLAAS_BASE_URL", BASE_URL).rstrip("/") != BASE_URL:
        raise ValueError("Unexpected provider endpoint")
    return values


class WorkerInterrupted(BaseException):
    def __init__(self, signum):
        self.signum = signum


def worker(args):
    phase = "preflight"
    old_handlers = {}

    def stop(signum, _frame):
        raise WorkerInterrupted(signum)

    try:
        for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
            old_handlers[sig] = signal.signal(sig, stop)
        load_packet(args.packet)
        values = load_credentials(args.env_file)
        os.environ.update(values)
        phase = "campaign"
        result = run_campaign(args.packet, args.directory / "run", allow_live=True,
                              authorization_reference=args.authorization_reference)
        for name in values:
            os.environ.pop(name, None)
        if result["state"] != "completed":
            write_new(args.directory / "worker-exit.json", {
                "state": "campaign_stopped", "stop_reason": result["stop_reason"],
                "finished_utc": datetime.now(timezone.utc).isoformat(),
            })
            return 2
        phase = "offline_analysis"
        analysis = export_study(
            {role: args.directory / "run" / role for role in ("controlled", "realistic", "language")},
            args.directory / "analysis", project_root=Path(__file__).resolve().parents[1],
            figures=True, development=True,
        )
        write_new(args.directory / "worker-exit.json", {
            "state": "analysis_exported", "counts": analysis["counts"],
            "finished_utc": datetime.now(timezone.utc).isoformat(),
            "evidence": "development_only", "analysis_model_calls": 0,
        })
        return 0
    except WorkerInterrupted as error:
        write_new(args.directory / "worker-exit.json", {
            "state": "interrupted", "signal": error.signum, "phase": phase,
            "finished_utc": datetime.now(timezone.utc).isoformat(),
            "pending_requests": "Retain as uncertain; no automatic reissue",
        })
        return 128 + error.signum
    except Exception as error:
        # Exception messages can contain provider credentials. Keep a sanitized
        # failure receipt and a nonzero exit, never a fallback or hidden rerun.
        write_new(args.directory / "worker-exit.json", {
            "state": "failed", "error_type": type(error).__name__, "phase": phase,
            "finished_utc": datetime.now(timezone.utc).isoformat(),
        })
        return 2
    finally:
        os.environ.pop("SOCLAAS_API_KEY", None)
        for sig, handler in old_handlers.items():
            signal.signal(sig, handler)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("directory", type=Path, help="New supervisor/run/analysis output root")
    parser.add_argument("--env-file", required=True, type=Path)
    parser.add_argument("--authorization-reference", required=True)
    parser.add_argument("--allow-live", action="store_true")
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    args.packet, args.directory = args.packet.resolve(), args.directory.resolve()
    args.env_file = args.env_file.absolute()
    if not args.allow_live or not args.authorization_reference.strip():
        parser.error("Explicit live selection and authorization reference required")
    if args.worker:
        return worker(args)
    load_packet(args.packet)
    load_credentials(args.env_file)  # Validate only; the parent never installs the secret.
    if args.directory.exists():
        raise FileExistsError("Use a new output root; supervisor never retries a campaign")
    if args.preflight_only:
        print("Preflight passed; no model calls or output reservations made", flush=True)
        return 0
    args.directory.mkdir(mode=0o700, parents=True, exist_ok=False)
    command = [
        sys.executable, str(Path(__file__).resolve()), str(args.packet), str(args.directory),
        "--env-file", str(args.env_file), "--authorization-reference", args.authorization_reference,
        "--allow-live", "--worker",
    ]
    returncode = supervise(command, args.directory / "supervisor")
    return returncode if returncode >= 0 else 128 - returncode


if __name__ == "__main__":
    raise SystemExit(main())
