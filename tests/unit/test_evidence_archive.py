"""Evidence verification rejects archives that cannot preserve every member."""

import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tarfile

import pytest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("verify_evidence", ROOT / "scripts/verify_evidence.py")
verifier = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verifier)


def sha256(content):
    return hashlib.sha256(content).hexdigest()


def make_archive(tmp_path, members, *, checksums=None, symlink=None):
    """Write a real tar so tests cover archive names rather than mocked members."""
    path = tmp_path / "evidence.tar.gz"
    if checksums is None:
        checksums = {name: sha256(content) for name, content in members}
    with tarfile.open(path, "w:gz") as archive:
        for name, content in members:
            item = tarfile.TarInfo(name)
            if name == symlink:
                item.type = tarfile.SYMTYPE
                item.linkname = content.decode()
                archive.addfile(item)
            else:
                item.size = len(content)
                archive.addfile(item, io.BytesIO(content))
        content = json.dumps(checksums).encode()
        item = tarfile.TarInfo("CHECKSUMS.json")
        item.size = len(content)
        archive.addfile(item, io.BytesIO(content))
    return path, {"sha256": sha256(path.read_bytes()), "checksummed_members": len(checksums)}


def test_valid_nested_package_verifies_without_modifying_evidence(tmp_path):
    path, expected = make_archive(tmp_path, [("run/attempt.json", b'{"accepted":true}'),
                                             ("source/model.py", b"pass\n")])
    original = path.read_bytes()
    assert verifier.verify_archive(path, expected) == {
        "archive": path.name, "sha256": expected["sha256"], "verified_files": 2,
    }
    assert path.read_bytes() == original
    assert not (tmp_path / "run").exists()


def test_archive_digest_mismatch_rejects_before_contents_are_trusted(tmp_path):
    path, expected = make_archive(tmp_path, [("payload.txt", b"evidence")])
    expected["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="Archive checksum mismatch"):
        verifier.verify_archive(path, expected)


@pytest.mark.parametrize("members,checksums", [
    ([], {"missing.txt": sha256(b"missing")}),
    ([("extra.txt", b"extra")], {}),
])
def test_checksum_manifest_must_describe_exact_membership(tmp_path, members, checksums):
    path, expected = make_archive(tmp_path, members, checksums=checksums)
    with pytest.raises(ValueError, match="membership differs"):
        verifier.verify_archive(path, expected)


def test_inner_digest_mismatch_rejects_even_with_valid_archive_digest(tmp_path):
    path, expected = make_archive(tmp_path, [("payload.txt", b"changed")],
                                  checksums={"payload.txt": sha256(b"original")})
    with pytest.raises(ValueError, match="Member checksum mismatch"):
        verifier.verify_archive(path, expected)


@pytest.mark.parametrize("name", [
    "../escape.txt", "/absolute.txt", "sub/../escape.txt",
    "./payload.txt", "sub//payload.txt", "sub/./payload.txt",
])
def test_unsafe_or_noncanonical_member_paths_are_rejected(tmp_path, name):
    path, expected = make_archive(tmp_path, [(name, b"evidence")])
    with pytest.raises(ValueError, match="Unsafe archive member"):
        verifier.verify_archive(path, expected)


def test_symlink_member_is_rejected(tmp_path):
    path, expected = make_archive(tmp_path, [("link", b"../outside")], symlink="link")
    with pytest.raises(ValueError, match="Unsafe archive member"):
        verifier.verify_archive(path, expected)


def test_duplicate_member_cannot_overwrite_verified_content(tmp_path):
    path, expected = make_archive(tmp_path, [("payload.txt", b"original"),
                                             ("payload.txt", b"replacement")])
    with pytest.raises(ValueError, match="Duplicate archive members"):
        verifier.verify_archive(path, expected)


@pytest.mark.parametrize("names", [
    ("payload.txt", "PAYLOAD.txt"),
    ("caf\u00e9.txt", "cafe\u0301.txt"),
    ("run/answer.json", "RUN/ANSWER.json"),
])
def test_casefold_and_unicode_destination_aliases_are_rejected(tmp_path, names):
    path, expected = make_archive(tmp_path, [(names[0], b"original"),
                                             (names[1], b"replacement")])
    with pytest.raises(ValueError, match="Colliding archive destinations"):
        verifier.verify_archive(path, expected)


@pytest.mark.parametrize("names", [("run", "run/attempt.json"),
                                   ("RUN", "run/attempt.json")])
def test_file_cannot_also_be_another_members_parent(tmp_path, names):
    path, expected = make_archive(tmp_path, [(names[0], b"file"), (names[1], b"child")])
    with pytest.raises(ValueError, match="conflicts with a parent directory"):
        verifier.verify_archive(path, expected)


def test_command_extracts_valid_package_and_refuses_existing_destination(tmp_path, monkeypatch):
    path, expected = make_archive(tmp_path, [("run/attempt.json", b'{"accepted":true}')])
    manifest = {"archives": [{"id": "qwen36", "path": path.name, **expected}]}
    (tmp_path / "results").mkdir()
    (tmp_path / "results/evidence-manifest.json").write_text(json.dumps(manifest))
    monkeypatch.setattr(verifier, "ROOT", tmp_path)
    destination = tmp_path / "extracted"
    monkeypatch.setattr(sys, "argv", ["verify_evidence.py", "--extract-to", str(destination)])
    verifier.main()
    evidence = destination / "qwen36/run/attempt.json"
    assert evidence.read_bytes() == b'{"accepted":true}'
    with pytest.raises(FileExistsError):
        verifier.main()
    assert evidence.read_bytes() == b'{"accepted":true}'
