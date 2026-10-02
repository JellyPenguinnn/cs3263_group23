#!/usr/bin/env python3
"""Verify committed run archives and optionally extract them into a NEW directory.

Uses only Python's standard library. No credentials, network or inference.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile
import unicodedata

ROOT = Path(__file__).resolve().parents[1]


def verify_archive(path: Path, expected: dict) -> dict:
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected['sha256']:
        raise ValueError(f'Archive checksum mismatch: {path.name}')
    with tarfile.open(path, 'r:gz') as archive:
        members = archive.getmembers()
        names = [m.name for m in members]
        if len(set(names)) != len(names):
            raise ValueError('Duplicate archive members')
        destinations = set()
        for member in members:
            name = PurePosixPath(member.name)
            if (not member.isfile() or name.is_absolute() or '..' in name.parts
                    or not name.parts or str(name) != member.name):
                raise ValueError('Unsafe archive member')
            destination = unicodedata.normalize('NFC', member.name).casefold()
            if destination in destinations:
                raise ValueError('Colliding archive destinations')
            destinations.add(destination)
        for destination in destinations:
            if any(str(parent) in destinations for parent in PurePosixPath(destination).parents):
                raise ValueError('Archive file conflicts with a parent directory')
        stream = archive.extractfile('CHECKSUMS.json')
        if stream is None:
            raise ValueError('Missing checksum manifest')
        checksums = json.load(stream)
        if len(checksums) != expected['checksummed_members']:
            raise ValueError('Unexpected checksum member count')
        if set(names) != set(checksums) | {'CHECKSUMS.json'}:
            raise ValueError('Archive membership differs from checksum manifest')
        for name, expected_sha in checksums.items():
            stream = archive.extractfile(name)
            if stream is None or hashlib.sha256(stream.read()).hexdigest() != expected_sha:
                raise ValueError(f'Member checksum mismatch: {name}')
    return {'archive': path.name, 'sha256': expected['sha256'], 'verified_files': len(checksums)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--extract-to', type=Path, help='New directory; creates qwen36/ and qwen38/ inside it')
    args = parser.parse_args()
    manifest = json.loads((ROOT/'results/evidence-manifest.json').read_text())
    verified = []
    for entry in manifest['archives']:
        verified.append(verify_archive(ROOT/entry['path'], entry))
    if args.extract_to:
        args.extract_to.mkdir(parents=True, exist_ok=False)
        for entry in manifest['archives']:
            target = args.extract_to/entry['id']
            target.mkdir()
            with tarfile.open(ROOT/entry['path'], 'r:gz') as archive:
                archive.extractall(target, filter='data')
    print(json.dumps({'verified': verified, 'extracted': str(args.extract_to) if args.extract_to else None}, indent=2))


if __name__ == '__main__':
    main()
