#!/usr/bin/env python3
"""Build explicitly redacted, portable derivatives of completed diverse-study evidence.

Offline only. Original archives and raw attempt/case/reference/source bytes are
never changed. Historical hashes remain hashes of the original evidence.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile

from verify_evidence import verify_archive

ROOT = Path(__file__).resolve().parents[1]
RUNS = {
    "qwen36": "parallel8-20261017-01/qwen36",
    "glm53flash": "parallel4-glm-20261017-01/glm53flash",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encoded(value) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode()


def portable_paths(value, evidence_root: Path, changes: list, pointer=""):
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            child = pointer + "/" + key.replace("~", "~0").replace("/", "~1")
            if key == "original_campaign" and isinstance(item, str):
                original = Path(item)
                if not original.is_absolute():
                    raise ValueError("Expected original campaign path to be absolute")
                relative = original.relative_to(evidence_root)
                replacement = "campaign-history/" + relative.as_posix()
                changes.append({"json_pointer": child, "original_value_sha256": digest(item.encode()),
                                "replacement": replacement})
                result[key] = replacement
            else:
                result[key] = portable_paths(item, evidence_root, changes, child)
        return result
    if isinstance(value, list):
        return [portable_paths(item, evidence_root, changes, f"{pointer}/{i}") for i, item in enumerate(value)]
    if isinstance(value, str) and ("/Users/" in value or "/private/" in value):
        raise ValueError(f"Unexpected private path at {pointer}; review rather than silently redact")
    return value


def write_new_or_identical(path: Path, data: bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f"Refusing to replace differing evidence: {path}")
        return
    with path.open("xb") as handle:
        handle.write(data)


def package(evidence_root: Path):
    archives = []
    for model, relative in RUNS.items():
        base = evidence_root / relative / "analysis"
        source = base / "numerical-export/reproduction.tar.gz"
        original_receipt = json.loads((source.parent / "archive-sha256.json").read_text())
        verify_archive(source, {"sha256": original_receipt["sha256"],
                                "checksummed_members": original_receipt["files"]})
        with tarfile.open(source) as archive:
            entries = {m.name: archive.extractfile(m).read() for m in archive.getmembers()}
        original_entries = dict(entries)
        modifications = []
        manifest_name = "runs/controlled/controlled/manifest.json"
        changes = []
        manifest = portable_paths(json.loads(entries[manifest_name]), evidence_root, changes)
        entries[manifest_name] = encoded(manifest)
        modifications.append({"member": manifest_name, "original_sha256": digest(original_entries[manifest_name]),
                              "changes": changes})
        analysis = json.loads(entries["analysis.json"])
        analysis["block_checksums"]["controlled"]["manifest.json"] = digest(entries[manifest_name])
        entries["analysis.json"] = encoded(analysis)
        modifications.append({"member": "analysis.json", "original_sha256": digest(original_entries["analysis.json"]),
                              "changes": [{"json_pointer": "/block_checksums/controlled/manifest.json",
                                           "replacement": digest(entries[manifest_name])}]})
        changes = []
        annotated = portable_paths(json.loads((base / "analysis-with-execution-provenance.json").read_text()),
                                   evidence_root, changes)
        annotated["block_checksums"]["controlled"]["manifest.json"] = digest(entries[manifest_name])
        entries["analysis-with-execution-provenance.json"] = encoded(annotated)
        entries["timing-by-execution-segment.json"] = (base / "timing-by-execution-segment.json").read_bytes()
        entries["timing-comparability.json"] = (evidence_root / "parallel4-glm-20261017-01/timing-comparability.json").read_bytes()
        outer_receipt = json.loads((base / "archive-sha256.json").read_text())
        if digest((base / "parallel-evidence.tar.gz").read_bytes()) != outer_receipt["sha256"]:
            raise ValueError("Original operational archive checksum mismatch")
        preserved = [name for name in original_entries if name.startswith((
            "runs/controlled/controlled/attempts/", "runs/controlled/controlled/references/", "source/"))
                     or name == "runs/controlled/controlled/cases.json"]
        if any(entries[name] != original_entries[name] for name in preserved):
            raise ValueError("Raw scientific evidence changed")
        receipt = {
            "format_version": "1.0", "evidence_class": "portable_redacted_derivative",
            "original_reproduction_archive_sha256": original_receipt["sha256"],
            "original_operational_archive_sha256": outer_receipt["sha256"],
            "original_archives_modified": False, "new_model_calls": 0,
            "unchanged_scientific_members": len(preserved),
            "modifications": modifications,
            "added_execution_provenance_path_redactions": changes,
            "historical_hash_fields": "Preserved unchanged; they identify originals, not redacted derivatives.",
            "campaign_history_paths": "Relative provenance labels only; original campaign trees remain private.",
        }
        entries["PORTABLE-DERIVATIVE.json"] = encoded(receipt)
        entries["CHECKSUMS.json"] = encoded({name: digest(data) for name, data in entries.items() if name != "CHECKSUMS.json"})
        tar_buffer = io.BytesIO()
        with tarfile.open(fileobj=tar_buffer, mode="w", format=tarfile.PAX_FORMAT) as archive:
            for name, data in sorted(entries.items()):
                info = tarfile.TarInfo(name); info.size = len(data); info.mode = 0o644
                archive.addfile(info, io.BytesIO(data))
        compressed = gzip.compress(tar_buffer.getvalue(), compresslevel=9, mtime=0)
        destination = ROOT / f"results/archives/diverse-2000-{model}-20261018-portable.tar.gz"
        write_new_or_identical(destination, compressed)
        entry = {"id": model, "run_id": f"diverse-2000-{model}-20261018", "path": str(destination.relative_to(ROOT)),
                 "sha256": digest(compressed), "bytes": len(compressed), "checksummed_members": len(entries)-1,
                 "scheduling_attempts": 2000, "required_returned_model": "qwen3.6:35b" if model == "qwen36" else "glm-5.3-flash",
                 "evidence_scope": "Shared-service synthetic/AI-assisted development; not held out",
                 "original_reproduction_archive_sha256": original_receipt["sha256"],
                 "original_operational_archive_sha256": outer_receipt["sha256"],
                 "redacted_manifest_paths": len(modifications[0]["changes"]),
                 "unchanged_scientific_members": len(preserved)}
        verify_archive(destination, entry)
        archives.append(entry)
    result = {"format_version": "1.0", "archives": archives, "policy": {
        "original_bytes": False, "portable_redacted_derivative": True, "overwrite_originals": False,
        "raw_attempt_case_reference_source_bytes_unchanged": True, "new_model_calls": 0,
        "dataset": "diverse-generation-v1", "earlier_studies": "Separate immutable archives and scores; no pooling",
        "limitations": "Ten conservative construction families; actual human review pending; differing OS/concurrency phases.",
        "redactions": "Only absolute original_campaign provenance paths; corresponding manifest/checksum digests updated. Exact transformation receipts are inside each archive."}}
    write_new_or_identical(ROOT / "results/diverse-evidence-manifest.json", encoded(result))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(package(args.evidence_root.resolve()), indent=2))
