#!/usr/bin/env python3
"""Build a descriptive comparison from checksum-verified difficulty archives.

Standard library only; no inference, solver calls or changes to original evidence.
Archive replay is a separate validation step recorded in the audit companion.
"""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from statistics import mean, median
import tarfile

from verify_evidence import ROOT, verify_archive

MODELS = {'qwen36': 'qwen3.6:35b', 'glm53flash': 'glm-5.3-flash'}
ARMS = ('direct', 'solver_augmented')
BLOCKS = ('controlled', 'realistic', 'language')
TIERS = ('easy', 'moderate', 'hard', 'very_hard', 'extreme')


def unit(row):
    return tuple(row[k] for k in ('study_block', 'case_id', 'variant_id', 'repeat', 'approach'))


def distribution(values):
    observed = [v for v in values if v is not None]
    return {'mean': mean(observed) if observed else None,
            'median': median(observed) if observed else None,
            'reported': len(observed), 'attempts': len(values),
            'missing': len(values) - len(observed)}


def resources(rows):
    return {'model_seconds': distribution([r['model_seconds'] for r in rows]),
            'total_tokens': distribution([
                sum(u['total_tokens'] for u in r['usage'])
                if r['usage'] and all(u['total_tokens'] is not None for u in r['usage']) else None
                for r in rows]),
            'solver_seconds': distribution([dict(r['timings']).get('solver_seconds') for r in rows])}


def normalized_settings(settings):
    result = deepcopy(settings)
    result['model'].pop('model')
    result['provider_execution']['configured_body'].pop('model')
    result['provider_execution'].pop('model_identity', None)
    # Capability hashes and observed backend fingerprints are outcomes, not controls.
    result.pop('qualification_baseline')
    return result


def aggregate(rows, diagnostics):
    statuses = Counter(diagnostics[unit(r)]['objective_status'] for r in rows)
    categories = dict(sorted(Counter(r['category'] for r in rows).items()))
    sat = [r for r in rows if r['gold_label'] == 'SAT']
    unsat = [r for r in rows if r['gold_label'] == 'UNSAT']
    return {'attempts': len(rows), 'accepted': sum(r['accepted'] for r in rows),
            'categories': categories,
            'sat_valid': sum(r['gold_valid'] for r in sat), 'sat_attempts': len(sat),
            'correct_unsat': sum(r['accepted'] for r in unsat), 'unsat_attempts': len(unsat),
            'objective_matches': statuses['reference_match'],
            'objective_comparable': statuses['reference_match'] + statuses['proven_suboptimal'],
            'objective_suboptimal': statuses['proven_suboptimal'],
            'objective_partially_proven': statuses['partially_proven']}


def build(manifest):
    result = {'format_version': '1.0', 'new_model_calls': 0,
              'scope': 'Descriptive, shared-service development comparison; not held out',
              'models': {}, 'comparison_checks': {},
              'limitations': ['Failures remain in every primary denominator.',
                  'Wording conditions reuse controlled cases; do not pool blocks as independent samples.',
                  'Objective matching is conditional on valid gold-SAT schedules and proven references.',
                  'Structural extraction differences alone do not demonstrate semantic error.',
                  'Hosted defaults, backend selection and sequential runs prevent causal model-speed claims.']}
    shared_settings = shared_inputs = None
    if {e['id'] for e in manifest['archives']} != set(MODELS):
        raise ValueError('This comparison requires exactly the two difficulty-study models')
    for entry in manifest['archives']:
        key = entry['id']
        archive_path = ROOT / entry['path']
        verify_archive(archive_path, entry)
        with tarfile.open(archive_path) as archive:
            analysis_bytes = archive.extractfile('analysis.json').read()
            analysis = json.loads(analysis_bytes)
            rows = analysis['rows']
            if len(rows) != 200 or len({unit(r) for r in rows}) != 200:
                raise ValueError('Expected 200 unique scheduling observations')
            inputs = {}
            for block in BLOCKS:
                base = f'runs/{block}/{block}'
                contract = json.load(archive.extractfile(base + '/manifest.json'))['contract']
                inputs[block] = {'cases': contract['case_bundle_sha256'], 'requests': {}}
                members = [m for m in archive.getnames() if m.startswith(base + '/attempts/')]
                if len(members) != {'controlled': 120, 'realistic': 40, 'language': 40}[block]:
                    raise ValueError('Incorrect block size')
                for member in members:
                    record = json.load(archive.extractfile(member))
                    if record['state'] != 'completed':
                        raise ValueError('Pending response cannot enter completed comparison')
                    payload = record['payload']
                    response = payload['pipeline_result']['model_response']
                    if response['returned_model'] not in (None, MODELS[key]):
                        raise ValueError('Returned model mismatch')
                    if response['returned_model'] is None and not response['error']:
                        raise ValueError('Successful response without model identity')
                    if len(response['attempts']) != 1:
                        raise ValueError('Unexpected retry or missing provider attempt')
                    if any(a['returned_model'] not in (None, MODELS[key]) for a in response['attempts']):
                        raise ValueError('Attempt-level identity mismatch')
                    identity = payload['identity']
                    request_key = '|'.join(str(identity[k]) for k in ('case_id', 'variant_id', 'repeat', 'approach'))
                    inputs[block]['requests'][request_key] = {
                        'prompt': payload['pipeline_result']['prompt_sha256'],
                        'public_view': payload['public_view'],
                    }
            settings = normalized_settings(analysis['settings'])
            if shared_settings is None:
                shared_settings, shared_inputs = settings, inputs
            elif settings != shared_settings or inputs != shared_inputs:
                raise ValueError('Model-independent settings or public inputs differ')
        diagnostics = {tuple(d['unit']): d for d in analysis['interpretation']['attempt_diagnostics']}
        if set(diagnostics) != {unit(r) for r in rows}:
            raise ValueError('Incomplete interpretation records')
        model = {'model': MODELS[key], 'requested_model': analysis['settings']['model']['model'],
                 'archive': entry['path'], 'archive_sha256': entry['sha256'],
                 'analysis_sha256': hashlib.sha256(analysis_bytes).hexdigest(),
                 'accepted_by_block': {}, 'controlled_tiers': {}, 'controlled_task_labels': [],
                 'overall_by_method': {}, 'resources': {}, 'failure_catalogue': [],
                 'controlled_paired': analysis['primary_controlled']['paired'],
                 'backend_fingerprints': analysis['backend_fingerprints'],
                 'unique_cases': len({r['case_id'] for r in rows}),
                 'normalized_source_families': len({r['group_id'] for r in rows}),
                 'conditions': len({unit(r)[:-1] for r in rows})}
        for block in BLOCKS:
            model['accepted_by_block'][block] = {arm: aggregate(
                [r for r in rows if r['study_block'] == block and r['approach'] == arm], diagnostics)
                for arm in ARMS}
        for tier in TIERS:
            model['controlled_tiers'][tier] = {arm: aggregate(
                [r for r in rows if r['study_block'] == 'controlled' and r['level'] == tier
                 and r['approach'] == arm], diagnostics) for arm in ARMS}
        for arm in ARMS:
            subset = [r for r in rows if r['approach'] == arm]
            model['overall_by_method'][arm] = aggregate(subset, diagnostics)
            model['resources'][arm] = resources(subset)
            for task in ('generation', 'repair'):
                model['controlled_task_labels'].append({'task': task, 'approach': arm, **aggregate(
                    [r for r in subset if r['study_block'] == 'controlled' and r['task_type'] == task], diagnostics)})
        for row in rows:
            diagnostic = diagnostics[unit(row)]
            if not row['accepted'] or diagnostic['objective_status'] == 'proven_suboptimal':
                model['failure_catalogue'].append({**diagnostic, 'gold_label': row['gold_label'],
                    'declared_status': row['declared_status'], 'level': row['level'],
                    'objective_values': row['objective_values'], 'objective_gaps': row['objective_gaps'],
                    'violations': (row.get('validation') or {}).get('violations', []),
                    'provider_errors': [p['error'] for p in row['provider_attempts'] if p['error']]})
        result['models'][key] = model
    result['comparison_checks'] = {'source_runtime_and_non_model_settings_match': True,
        'all_200_paired_prompt_hashes_and_public_views_match': True,
        'all_three_case_bundles_match': True, 'all_returned_identities_match': True,
        'no_pending_requests_or_retries': True,
        'allowed_differences': ['requested/required model identity', 'observed capability and backend metadata'],
        'shared_settings': shared_settings}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=ROOT/'results/difficulty-evidence-manifest.json')
    parser.add_argument('--output', type=Path, default=ROOT/'results/summary/difficulty-comparison-20261014.json')
    args = parser.parse_args()
    result = build(json.loads(args.manifest.read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print('Verified and summarized 400 scheduling attempts; no model calls.')


if __name__ == '__main__':
    main()
