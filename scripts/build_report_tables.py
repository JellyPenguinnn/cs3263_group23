#!/usr/bin/env python3
"""Derive supplemental task/label and difficulty tables from verified run archives."""
from collections import Counter
import json
from pathlib import Path
import tarfile

from verify_evidence import ROOT, verify_archive


def main():
    manifest = json.loads((ROOT/'results/evidence-manifest.json').read_text())
    output = {'format_version': '1.0', 'new_model_calls': 0,
              'scope': 'Exploratory development; descriptive difficulty cells, not independent causal effects',
              'models': {}}
    for entry in manifest['archives']:
        verify_archive(ROOT/entry['path'], entry)
        with tarfile.open(ROOT/entry['path']) as archive:
            analysis = json.load(archive.extractfile('analysis.json'))
        rows = [r for r in analysis['rows'] if r['study_block'] == 'controlled']
        tasks, difficulty = [], []
        for task in ('generation', 'repair'):
            for approach in ('direct', 'solver_augmented'):
                for label in ('SAT', 'UNSAT'):
                    subset = [r for r in rows if r['task_type'] == task and r['approach'] == approach and r['gold_label'] == label]
                    tasks.append({'task': task, 'approach': approach, 'gold_label': label,
                                  'attempts': len(subset), 'accepted': sum(r['accepted'] for r in subset)})
                    for sweep in sorted({r['sweep'] for r in subset}):
                        for level in sorted({r['level'] for r in subset if r['sweep'] == sweep}):
                            cell = [r for r in subset if r['sweep'] == sweep and r['level'] == level]
                            sizes = [r['difficulty']['start_domain_product'] for r in cell]
                            difficulty.append({'task': task, 'approach': approach, 'gold_label': label,
                                               'sweep': sweep, 'level': level, 'attempts': len(cell),
                                               'accepted': sum(r['accepted'] for r in cell),
                                               'categories': dict(Counter(r['category'] for r in cell)),
                                               'activity_counts': sorted({r['difficulty']['activity_count'] for r in cell}),
                                               'domain_product_min': min(sizes), 'domain_product_max': max(sizes),
                                               'case_ids': sorted(r['case_id'] for r in cell)})
        output['models'][entry['id']] = {'model': analysis['settings']['model']['model'],
                                       'archive_sha256': entry['sha256'], 'task_label': tasks,
                                       'difficulty': difficulty}
    destination = ROOT/'results/summary/two-model-report-tables-20261002.json'
    destination.write_text(json.dumps(output, indent=2, sort_keys=True)+'\n')
    print(f'Wrote {destination.relative_to(ROOT)} from both verified archives')


if __name__ == '__main__':
    main()
