"""Rebuild versioned exclusions from explicit case bundles, never legacy hashes.

Usage: python evaluation/development_registry.py --bundle CASES_JSON ...
       [--archive-bundle ARCHIVE MEMBER] --output NEW_REGISTRY_JSON
The output is a known-source registry, not approval or proof of complete coverage.
"""

import argparse
import json
from pathlib import Path
import tarfile
from tempfile import TemporaryDirectory

from scheduling.evaluation.cases import load_cases
from scheduling.evaluation.manifests import development_registry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", action="append", default=[], type=Path)
    parser.add_argument("--archive-bundle", action="append", nargs=2, default=[],
                        metavar=("ARCHIVE", "MEMBER"))
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    bundles = {}
    for path in args.bundle:
        bundles[path.as_posix()] = load_cases(path)
    for archive, member in args.archive_bundle:
        # Read only the explicitly named regular-file member; never extract paths.
        with tarfile.open(archive, "r:*") as tar:
            info = tar.getmember(member)
            if not info.isfile():
                raise ValueError("Archive bundle must be a regular file")
            with tar.extractfile(info) as stream, TemporaryDirectory() as folder:
                path = Path(folder) / "cases.json"
                path.write_bytes(stream.read())
                bundles[f"{archive}!{member}"] = load_cases(path)
    if not bundles:
        parser.error("Provide at least one source case bundle")
    registry = development_registry(bundles)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(registry, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(f"{len(registry['fingerprints'])} known structures from {len(bundles)} bundles; coverage requires review")


if __name__ == "__main__":
    main()
