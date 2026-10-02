#!/usr/bin/env python3
"""Check report text preservation, page geometry and font size (pdfplumber 0.11.9).

Visual inspection of every page is still required. This records checks, not approval.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re

import pdfplumber

ROOT = Path(__file__).resolve().parents[1]


def visible(text):
    text = re.sub(r'!?\[([^\]]+)\]\([^)]+\)', r'\1', text)
    return re.sub(r'[^a-z0-9]', '', text.lower())


def source_chunks(source):
    chunks, paragraph, fence = [], [], None
    def flush():
        if paragraph:
            chunks.append(' '.join(paragraph))
            paragraph.clear()
    for line in source.splitlines():
        if line.startswith('```'):
            flush()
            fence = None if fence else line[3:]
        elif fence == 'mermaid':
            chunks.extend(re.findall(r'\[([^\]]+)\]', line))
        elif fence:
            chunks.append(line)
        elif line.startswith('|'):
            flush()
            cells = [x.strip() for x in line.strip('|').split('|')]
            if not all(re.fullmatch(r':?-+:?', x) for x in cells):
                chunks.extend(cells)
        elif line.startswith('#'):
            flush()
            chunks.append(line.lstrip('# '))
        elif line.startswith('!['):
            flush()
            chunks.append(re.fullmatch(r'!\[([^\]]+)\]\([^)]+\)', line)[1])
        elif not line.strip():
            flush()
        else:
            paragraph.append(line)
    flush()
    return [c for c in chunks if visible(c)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT/'docs/submission-report.md')
    parser.add_argument('--pdf', type=Path, default=ROOT/'docs/submission-report.pdf')
    parser.add_argument('--receipt', type=Path, default=ROOT/'results/summary/submission-report-format.json')
    args = parser.parse_args()
    with pdfplumber.open(args.pdf) as doc:
        # Exclude running headers/page numbers and retain drawing order for wrapped
        # table cells and diagram labels. Geometric line order interleaves columns.
        texts = [p.crop((72, 100, p.width-72, p.height-100)).extract_text(use_text_flow=True) or ''
                 for p in doc.pages]
        abstract = [i for i, t in enumerate(texts) if re.search(r'^Abstract$', t, re.M)]
        references = [i for i, t in enumerate(texts) if re.search(r'^References$', t, re.M)]
        if len(abstract) != 1 or len(references) != 1:
            raise ValueError('Unable to identify unique body/reference boundaries')
        body_pages = references[0] - abstract[0]
        if not 0 < body_pages <= 10:
            raise ValueError(f'Body page limit: {body_pages}')
        min_font = min(c['size'] for p in doc.pages for c in p.chars)
        if min_font < 10.99:
            raise ValueError(f'Text below 11 pt: {min_font}')
        for p in doc.pages:
            for item in [*p.chars, *p.images]:
                if (item['x0'] < 71.9 or item['x1'] > p.width-71.9
                        or item['top'] < 71.9 or item['bottom'] > p.height-71.9):
                    raise ValueError(f'Content outside one-inch margin on page {p.page_number}')
        combined = visible('\n'.join(texts))
        chunks = source_chunks(args.source.read_text())
        missing = [c for c in chunks if visible(c) not in combined]
        if missing:
            raise ValueError(f'Visible source text missing from PDF: {missing[:3]}')
        receipt = {'source_sha256': hashlib.sha256(args.source.read_bytes()).hexdigest(),
                   'pdf_sha256': hashlib.sha256(args.pdf.read_bytes()).hexdigest(),
                   'total_pages': len(doc.pages), 'body_pages': body_pages,
                   'title_pages': abstract[0], 'reference_pages': len(doc.pages)-references[0],
                   'minimum_text_font_pt': min_font, 'margin_inches': 1,
                   'visible_text_chunks_verified': len(chunks), 'figure_images': sum(len(p.images) for p in doc.pages),
                   'automated_checks_passed': True,
                   'visual_review': 'Separately recorded in docs/publication-verification.md; not implied by this script'}
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
