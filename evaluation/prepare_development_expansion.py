"""Prepare a deterministic 100-case / 200-call development comparison, offline.

Selection is fixed before model outputs: 64 v2 + 36 v3 cases, paired generation
and repair, with 25 cases in each task/feasibility stratum. This samples known
synthetic development generators; it does not create a held-out test set.
"""

import argparse
from collections import Counter
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import random

from scheduling.evaluation.benchmark import (
    V2_SWEEPS, V2_EVENTS, V3_MECHANISMS,
    generate_development_v2, generate_development_v3,
)
from scheduling.evaluation.cases import case_bundle
from scheduling.evaluation.cli import load_config
from scheduling.evaluation.manifests import (
    structural_audit, structural_fingerprint, check_development_registry,
    benchmark_manifest_v2, benchmark_manifest_v3, development_registry,
)
from scheduling.evaluation.runner import plan_run, write_new
from scheduling.evaluation.scoring import digest


def select_cases(v2, v3, provenance):
    selected = []
    for sweep_index, sweep in enumerate(V2_SWEEPS):
        for label_index, label in enumerate(('SAT', 'UNSAT')):
            # One event at each level, plus one distinct event at a rotated level.
            cells = [(level, (sweep_index + level + label_index) % 3)
                     for level in range(3)]
            extra = sweep_index % 3
            cells.append((extra, (sweep_index + extra + label_index + 1) % 3))
            for level, event_index in cells:
                pair = [c for c in v2 if c.sweep == sweep and c.level == str(level)
                        and c.expected_label == label
                        and provenance[c.case_id]['construction_event'] == V2_EVENTS[event_index]]
                if len(pair) != 2 or {c.problem.task_type for c in pair} != {'generation', 'repair'}:
                    raise ValueError('V2 selection cell lacks its complete generation/repair pair')
                selected.extend(pair)
    for mechanism_index, mechanism in enumerate(V3_MECHANISMS):
        for size_index, size in enumerate((3, 4, 5)):
            for label_index, label in enumerate(('SAT', 'UNSAT')):
                event = V2_EVENTS[(mechanism_index + size_index + label_index) % 3]
                pair = [c for c in v3 if c.sweep == mechanism and c.level == str(size)
                        and c.expected_label == label
                        and provenance[c.case_id]['construction_event'] == event]
                if len(pair) != 2 or {c.problem.task_type for c in pair} != {'generation', 'repair'}:
                    raise ValueError('V3 selection cell lacks its complete generation/repair pair')
                selected.extend(pair)
    if len(selected) != 100 or len({c.case_id for c in selected}) != 100:
        raise ValueError('Selection must contain exactly 100 distinct cases')
    if set(Counter((c.problem.task_type, c.expected_label) for c in selected).values()) != {25}:
        raise ValueError('Selection must balance task and feasibility strata')
    audit = structural_audit(selected)
    selected = [replace(c, group_id=audit['family_for_group'][c.group_id]) for c in selected]
    random.Random(326630).shuffle(selected)
    return tuple(selected)


def prepare(directory, config_path, registry_path):
    directory.mkdir(parents=True, exist_ok=False)
    pools = []
    records = {}
    for version, seed, generate, manifest in (
        ('2', 3264, generate_development_v2, benchmark_manifest_v2),
        ('3', 3265, generate_development_v3, benchmark_manifest_v3),
    ):
        cases, provenance, selection = generate(seed)
        if not selection['quota_complete']:
            write_new(directory / f'incomplete-v{version}.json', selection)
            raise ValueError('Source matrix incomplete; do not substitute cases silently')
        write_new(directory / f'pool-v{version}.json', case_bundle(cases))
        write_new(directory / f'pool-v{version}.manifest.json', manifest(
            cases, generation_seed=seed, rendering_seed=3263, selection=selection,
            records=provenance, code_revision='use_exact_source_hashes_in_preflight'))
        pools.append(cases)
        records.update(provenance)
    cases = select_cases(*pools, records)
    config = load_config(config_path)
    if config.evidence != 'live_development' or config.max_requests != 200 or config.variants != ('canonical',) or config.repeats != 1:
        raise ValueError('Expansion requires the explicit 200-call canonical development configuration')
    known = check_development_registry(json.loads(registry_path.read_text()))
    inspected = development_registry({f'pool-v{i}.json': p for i, p in zip((2, 3), pools)})
    write_new(directory / 'inspected-pool-registry.json', inspected)
    write_new(directory / 'cases.json', case_bundle(cases))
    write_new(directory / 'config.json', json.loads(config_path.read_text()))
    audit = structural_audit(cases)
    prior_live = set()
    repo = Path(__file__).resolve().parents[1]
    for name in ('main-baseline-20260929-01', 'yongqing-v2-pilot-20260929-01',
                 'lihao-boundary-pilot-20260930-01', 'yaoxiang-availability-pilot-20260930-01'):
        path = repo / 'runs' / name / 'cases.json'
        if path.exists():
            prior_live.update(c['case_id'] for c in json.loads(path.read_text())['cases'])
    manifest = {
        'format_version': '1.0', 'status': 'development_preselected_not_frozen_test',
        'selection': '64 v2 cases: each sweep/label takes one pair per level plus one rotated extra pair; 36 v3 cases: one event pair per mechanism/size/label. Events rotate deterministically. See preparation source.',
        'selection_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'case_bundle_sha256': digest(case_bundle(cases)),
        'ordering_seed': 326630, 'source_seeds': {'v2': 3264, 'v3': 3265},
        'case_count': len(cases), 'source_family_count': len(set(audit['family_for_group'].values())),
        'counts': dict(Counter(f'{c.problem.task_type}/{c.expected_label}' for c in cases)),
        'dataset_counts': dict(Counter('v2' if c.sweep in V2_SWEEPS else 'v3' for c in cases)),
        'repair_events': dict(Counter(c.event for c in cases if c.context)),
        'factors': dict(Counter(f'{c.sweep}/{c.level}' for c in cases)),
        'known_development_case_count': sum(any(structural_fingerprint(s) in known for s in (c.problem, c.original_problem) if s is not None) for c in cases),
        'previously_live_case_ids': sorted(c.case_id for c in cases if c.case_id in prior_live),
        'previously_live_scope': 'IDs from locally available named historical case bundles; not a claim of unseen data',
        'new_inspected_structures': sorted(set(inspected['fingerprints']) - known),
        'structural_audit': audit,
        'human_fixture_review': 'pending', 'human_language_review': 'pending',
        'provenance': {c.case_id: records[c.case_id] for c in cases},
        'limitations': ['Known synthetic development data; not held-out or human-authored.',
                       'Related event/task/label cases share families; do not count all100 as independent.',
                       'Canonical text only: no language-robustness claim.',
                       'Larger per-call/solver limits differ from the small pilot; no causal comparison to old scores.'],
    }
    write_new(directory / 'selection.json', manifest)
    preflight = plan_run(cases, config)
    write_new(directory / 'preflight.json', preflight)
    if preflight['state'] != 'ready' or not preflight['within_cap']:
        raise ValueError('Reference/budget preflight failed; no live execution')
    print(json.dumps({k: manifest[k] for k in ('case_count', 'source_family_count', 'counts', 'dataset_counts', 'repair_events', 'known_development_case_count')}, sort_keys=True))
    print(json.dumps({k: preflight[k] for k in ('state', 'planned_requests', 'requested_output_tokens', 'reference_labels', 'prompt_characters')}, sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--config', type=Path, default=Path('configs/development/expanded-development-100.json'))
    parser.add_argument('--registry', type=Path, default=Path('benchmarks/manifests/development-hard-fingerprints-v2-20260930.json'))
    args = parser.parse_args()
    prepare(args.output, args.config, args.registry)
