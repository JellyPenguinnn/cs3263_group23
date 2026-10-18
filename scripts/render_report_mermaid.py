#!/usr/bin/env python3
"""Rebuild the report's Mermaid vector asset using an installed mmdc CLI.

The normal report build uses this committed asset and does not launch a browser.
Only diagram changes require Mermaid CLI 11.12.0 and a compatible Chrome runtime.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'docs/figures/report-compact-20261018'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mmdc', default='mmdc')
    parser.add_argument('--puppeteer-config', type=Path)
    args = parser.parse_args()
    version = subprocess.check_output([args.mmdc, '--version'], text=True).strip()
    if version != '11.12.0':
        raise ValueError(f'Expected Mermaid CLI 11.12.0, received {version}')
    command = [args.mmdc, '-i', str(DIRECTORY/'architecture.mmd'),
               '-o', str(DIRECTORY/'architecture.pdf'),
               '-c', str(DIRECTORY/'mermaid-config.json'),
               '-C', str(DIRECTORY/'mermaid.css'), '-f']
    if args.puppeteer_config:
        command += ['-p', str(args.puppeteer_config)]
    subprocess.run(command, check=True)
    digest = lambda name: hashlib.sha256((DIRECTORY/name).read_bytes()).hexdigest()
    receipt = {'renderer': 'Mermaid CLI', 'renderer_version': version,
               'mermaid_source_sha256': digest('architecture.mmd'),
               'config_sha256': digest('mermaid-config.json'),
               'css_sha256': digest('mermaid.css'),
               'pdf_sha256': digest('architecture.pdf'),
               'report_width_pt': 340, 'layout': 'Mermaid automatic flowchart layout'}
    (DIRECTORY/'architecture-receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')


if __name__ == '__main__':
    main()
