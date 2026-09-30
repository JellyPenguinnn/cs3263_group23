"""Versioned known-source exclusion registries retain exact source provenance."""

from copy import deepcopy
from dataclasses import replace
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile

import pytest
from scheduling.evaluation.benchmark import tiny_fixtures
from scheduling.evaluation.cases import case_bundle
from scheduling.evaluation.manifests import (
    FINGERPRINT_VERSION, development_registry, check_development_registry,
    structural_fingerprint,
)
from scheduling.evaluation.scoring import digest


def test_registry_includes_original_and_updated_with_exact_source_provenance():
    cases = tiny_fixtures()
    registry = development_registry({"known.json": cases})
    fingerprints = check_development_registry(registry)
    assert registry["fingerprint_version"] == FINGERPRINT_VERSION
    assert registry["sources"] == [{"reference": "known.json", "case_count": len(cases),
                                    "bundle_sha256": digest(case_bundle(cases))}]
    for case in cases:
        for spec in (case.problem, case.original_problem):
            if spec is not None:
                assert structural_fingerprint(spec) in fingerprints
    changed = replace(cases[0], problem=replace(cases[0].problem, horizon_start="2026-10-06T09:00:00+08:00"))
    original = development_registry({"source": (cases[0],)})
    dated = development_registry({"source": (changed,)})
    assert original["fingerprints"] == dated["fingerprints"]
    assert original["sources"] != dated["sources"]


@pytest.mark.parametrize("field,value", [
    ("fingerprint_version", "legacy"), ("format_version", "1.0"),
    ("fingerprints", ["a" * 64]), ("fingerprints", [None]),
    ("sources", []), ("coverage", ""),
])
def test_registry_rejects_stale_or_malformed_metadata(field, value):
    registry = deepcopy(development_registry({"source": tiny_fixtures()}))
    registry[field] = value
    with pytest.raises(ValueError):
        check_development_registry(registry)


def test_registry_cli_reads_explicit_archive_member_without_mutating_inputs(tmp_path):
    bundle = case_bundle(tiny_fixtures())
    content = json.dumps(bundle).encode()
    path = tmp_path / "source.json"
    path.write_bytes(content)
    archive = tmp_path / "source.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        info = tarfile.TarInfo("saved/cases.json")
        info.size = len(content)
        tar.addfile(info, io.BytesIO(content))
    before = archive.read_bytes()
    output = tmp_path / "registry.json"
    command = [sys.executable, "evaluation/development_registry.py", "--bundle", str(path),
               "--archive-bundle", str(archive), "saved/cases.json", "--output", str(output)]
    subprocess.run(command, check=True, cwd=Path(__file__).resolve().parents[2], capture_output=True)
    registry = json.loads(output.read_text())
    assert len(registry["sources"]) == 2
    assert check_development_registry(registry) == check_development_registry(development_registry({"source": tiny_fixtures()}))
    assert path.read_bytes() == content and archive.read_bytes() == before
    assert subprocess.run(command, capture_output=True).returncode != 0
