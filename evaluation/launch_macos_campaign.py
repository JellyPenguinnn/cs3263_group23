"""Launch one authorized campaign independently of the coding-agent process.

    python evaluation/launch_macos_campaign.py PACKET NEW_OUTPUT \
      --env-file /private/local/.env --authorization-reference REF --allow-live

The service is registered only in the current login session. It is not installed
as a login item and does not automatically restart or replay provider requests.
"""

import argparse
import hashlib
import os
from pathlib import Path
import plistlib
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evaluation.supervise_development_campaign import main as preflight


def service_definition(command, output, *, working_directory, label):
    return {
        "Label": label,
        "ProgramArguments": ["/usr/bin/caffeinate", "-is", *command],
        "WorkingDirectory": str(working_directory),
        "RunAtLoad": True,
        "KeepAlive": False,
        "ProcessType": "Standard",
        "ExitTimeOut": 30,
        "EnvironmentVariables": {"PYTHONDONTWRITEBYTECODE": "1", "PYTHONUNBUFFERED": "1"},
        "StandardOutPath": str(output.parent / (output.name + "-service.stdout.log")),
        "StandardErrorPath": str(output.parent / (output.name + "-service.stderr.log")),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--env-file", required=True, type=Path)
    parser.add_argument("--authorization-reference", required=True)
    parser.add_argument("--allow-live", action="store_true")
    args = parser.parse_args(argv)
    if sys.platform != "darwin":
        parser.error("This launcher is macOS-only; use a one-shot OS service for the portable supervisor")
    if not args.allow_live:
        parser.error("Explicit --allow-live is required")
    output = args.directory.resolve()
    common = [str(args.packet.resolve()), str(output), "--env-file", str(args.env_file.absolute()),
              "--authorization-reference", args.authorization_reference, "--allow-live"]
    preflight([*common, "--preflight-only"])
    output.parent.mkdir(parents=True, exist_ok=True)
    label = "edu.nus.cs3263.campaign." + hashlib.sha256(str(output).encode()).hexdigest()[:16]
    plist_path = output.parent / (output.name + "-launchd.plist")
    command = [sys.executable, str(Path(__file__).with_name("supervise_development_campaign.py").resolve()), *common]
    definition = service_definition(command, output, working_directory=Path(__file__).resolve().parents[1], label=label)
    fd = os.open(plist_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as out:
        plistlib.dump(definition, out)
    subprocess.run(["launchctl", "bootstrap", f"gui/{os.getuid()}", str(plist_path)], check=True)
    print(f"Registered one-shot service: gui/{os.getuid()}/{label}", flush=True)
    print(f"Lifecycle records: {output / 'supervisor'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
