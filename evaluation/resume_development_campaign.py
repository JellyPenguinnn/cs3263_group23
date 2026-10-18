"""Explicit, no-repeat continuation of an interrupted single-block campaign.

Run with the ORIGINAL installed scheduling package and orchestration source on
sys.path. This operational adapter never modifies scientific source or repeats
metadata/capability calls. Uncertain reservations require separate reconciliation.
"""
from collections import Counter
from copy import deepcopy
import shutil
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import time

from evaluation.run_development_campaign import load_packet
from scheduling.evaluation.cases import case_bundle, load_cases
from scheduling.evaluation.cli import load_config
from scheduling.evaluation.failure_policy import FailureState
from scheduling.evaluation.liveness import probe_run_liveness
from scheduling.evaluation.metrics import token_usage_summary
from scheduling.evaluation.runner import (
    OBSERVE_BACKEND_POLICY, _contract, _stop_reason, baseline_fingerprints,
    read, replay, requests, run_batch, write_new,
)
from scheduling.evaluation.scoring import digest
from scheduling.providers import RequestBudget, SoCLaaSProvider
from scheduling.providers.execution import execution_contract, expected_response_model
from scheduling.schema import load_json, to_data


def file_hashes(directory):
    result = {}
    for path in sorted(Path(directory).rglob('*')):
        if path.is_symlink():
            raise ValueError('Recovery evidence must not follow symlinks')
        if path.is_file():
            result[str(path.relative_to(directory))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def inspect_resume(packet, campaign, *, allow_finalized=False, allow_nonprefix=False, reconciled_http_429_attempt_ids=()):
    """Validate all saved accounting and the exact original contract, offline."""
    campaign = Path(campaign)
    blocks, packet_manifest = load_packet(Path(packet))
    if set(blocks) != {'controlled'}:
        raise ValueError('Recovery supports one controlled block only')
    cases, prepared, preflight = blocks['controlled']
    run = campaign / 'controlled'
    if (campaign / 'summary.json').exists() and not allow_finalized:
        raise ValueError('Campaign already finalized; preserve its existing summary')
    if probe_run_liveness(run) != 'inactive' or (run / '.lock').exists():
        raise ValueError('Run is active or has an unreconciled lock')
    verify_runtime_transition(campaign)
    saved_manifest = read(campaign / 'manifest.json')
    expected_block = {'case_bundle_sha256': digest(case_bundle(cases)),
                      'config': to_data(prepared), 'preflight': preflight}
    if (saved_manifest.get('packet') != {'campaign_sha256': digest(packet_manifest)}
            or saved_manifest.get('blocks') != {'controlled': expected_block}
            or saved_manifest.get('block_order') != ['controlled']
            or saved_manifest.get('max_requests') != prepared.max_requests + 3
            or saved_manifest.get('max_requested_output_tokens') != prepared.max_requested_output_tokens + 2 * prepared.model.max_tokens
            or saved_manifest.get('request_allocation') != {'metadata': 1, 'capability': 2, 'scheduling': prepared.max_requests}
            or read(campaign / 'blocks.json') != {'controlled': 'controlled'}):
        raise ValueError('Campaign/packet identity or budget changed')
    if read(campaign / 'metadata-reservation.json') != {'requests': 1, 'output_tokens': 0}:
        raise ValueError('Metadata reservation changed')
    metadata = read(campaign / 'metadata.json')
    if metadata.get('requested_model') != prepared.model.model or metadata.get('available') is not True:
        raise ValueError('Original model qualification did not succeed')
    caps, fingerprints = [], set()
    for index in range(2):
        if read(campaign / f'capability-{index:02}-reservation.json') != {'requests': 1, 'output_tokens': prepared.model.max_tokens}:
            raise ValueError('Capability reservation changed')
        cap = read(campaign / f'capability-{index:02}.json')
        response = cap.get('response') or {}
        attempts = response.get('attempts', [])
        if (cap.get('index') != index or cap.get('issue') is not None
                or response.get('error') is not None or response.get('finish_reason') != 'stop'
                or response.get('returned_model') != expected_response_model(prepared.model.model)
                or len(attempts) != 1 or load_json(response.get('content')) != {'ok': True}
                or (attempts[0].get('execution') or {}).get('contract') != execution_contract(prepared.model)):
            raise ValueError('Capability evidence is incomplete or changed')
        fingerprints.add((attempts[0].get('execution') or {}).get('system_fingerprint'))
        caps.append(cap)
    baseline = {'capability_sha256': [digest(c) for c in caps]}
    if prepared.qualification_policy == OBSERVE_BACKEND_POLICY:
        baseline['system_fingerprints'] = sorted(fingerprints, key=str)
    else:
        if len(fingerprints) != 1:
            raise ValueError('Original backend qualification inconsistent')
        baseline['system_fingerprint'] = next(iter(fingerprints))
    config = load_config(campaign / 'controlled-runtime-config.json')
    if config != replace(prepared, qualification_baseline=baseline):
        raise ValueError('Saved runtime configuration/baseline changed')
    if read(run / 'manifest.json')['contract'] != to_data(_contract(cases, config)):
        raise ValueError('Original scientific source/runtime/inputs changed')
    expected = list(requests(cases, config))
    saved = {p.stem: read(p) for p in (run / 'attempts').glob('*.json')}
    if (not set(saved) <= {key for key, *_ in expected}
            or (not allow_nonprefix and set(saved) != {key for key, *_ in expected[:len(saved)]})):
        raise ValueError('Saved attempts are not a contiguous planned prefix')
    failures = FailureState(config.provider_failure_policy)
    fingerprints = baseline_fingerprints(config)
    for key, identity, _, _ in expected:
        if key not in saved:
            continue
        record = saved[key]
        if record.get('state') != 'completed':
            raise ValueError('Uncertain reservation: no automatic replay or reconciliation')
        payload = record.get('payload') or {}
        if (record.get('identity') != identity or payload.get('identity') != identity
                or record.get('requested_output_tokens') != config.model.max_tokens
                or record.get('sha256') != digest(payload)):
            raise ValueError('Completed record changed')
        response = payload.get('pipeline_result', {}).get('model_response') or {}
        reason = _stop_reason(response, config.model.model, fingerprints,
            allow_backend_variation=config.qualification_policy == OBSERVE_BACKEND_POLICY)
        if key in reconciled_http_429_attempt_ids and reason == 'http_429':
            reason = None
        reason = failures.observe(reason)
        if reason:
            raise ValueError('Saved fatal failure forbids further model calls: ' + reason)
    rows, progress = replay(run)
    if progress['completed'] != len(saved) or progress['pending_attempt_ids']:
        raise ValueError('Replay and reservation accounting disagree')
    budget = RequestBudget(saved_manifest['max_requests'], saved_manifest['max_requested_output_tokens'])
    if not budget.reserve(0):
        raise ValueError('Cannot restore metadata accounting')
    for _ in range(2 + len(saved)):
        if not budget.reserve(config.model.max_tokens):
            raise ValueError('Saved reservations exceed authorized cap')
    return {'cases': cases, 'config': config, 'budget': budget,
            'completed': len(saved), 'remaining': len(expected) - len(saved),
            'preserved_sha256': file_hashes(campaign), 'campaign_manifest': saved_manifest}


def resume_campaign(packet, campaign, receipt_directory, *, authorization_reference, provider_factory=None):
    if not isinstance(authorization_reference, str) or not authorization_reference.strip():
        raise ValueError('Explicit continuation authorization required')
    campaign, receipt_directory = Path(campaign), Path(receipt_directory)
    if receipt_directory.exists():
        raise FileExistsError('Use a new recovery receipt directory')
    checked = inspect_resume(packet, campaign)
    receipt_directory.mkdir(parents=True, mode=0o700, exist_ok=False)
    budget = checked['budget']
    write_new(receipt_directory / 'start.json', {
        'authorization_reference': authorization_reference,
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'completed_attempts_preserved': checked['completed'], 'remaining_scheduling_calls': checked['remaining'],
        'requests_previously_reserved': budget.requests_used,
        'output_tokens_previously_reserved': budget.completion_tokens_reserved,
        'preserved_sha256': checked['preserved_sha256'],
        'qualification_requests_repeated': 0, 'automatic_retries': 0,
    })
    started = time.monotonic()
    factory = provider_factory or SoCLaaSProvider.from_environment
    with factory(budget=budget) as provider:
        result = run_batch(checked['cases'], campaign / 'controlled', checked['config'],
                           provider_complete=provider.complete)
    for name, expected in checked['preserved_sha256'].items():
        if hashlib.sha256((campaign / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Previously saved evidence changed during continuation')
    attempts = [a for p in sorted(campaign.glob('capability-[0-9][0-9].json'))
                for a in read(p)['response']['attempts']]
    for path in (campaign / 'controlled/attempts').glob('*.json'):
        record = read(path)
        attempts.extend((record['payload']['pipeline_result'].get('model_response') or {}).get('attempts', []))
    now = datetime.now(timezone.utc)
    original_start = datetime.fromisoformat(checked['campaign_manifest']['created_utc'])
    observed = Counter((a.get('execution') or {}).get('system_fingerprint')
                       for a in attempts if a.get('http_status') == 200 and not a.get('error'))
    summary = {
        'state': 'completed' if result['state'] == 'completed' else 'stopped_campaign',
        'stop_reason': result.get('stop_reason'), 'blocks': {'controlled': result},
        'requests_reserved': budget.requests_used,
        'requested_output_tokens_reserved': budget.completion_tokens_reserved,
        'total_wall_seconds': (now - original_start).total_seconds(),
        'total_wall_scope': 'Original campaign creation through continuation finish, including downtime; not pure inference time',
        'continuation_active_wall_seconds': time.monotonic() - started,
        'tokens': token_usage_summary(a['usage'] for a in attempts),
        'provider_failure_counts': dict(Counter(a['error'] for a in attempts if a.get('error'))),
        'usage_scope': 'Original qualification plus all saved scheduling provider attempts; missing usage remains unknown',
        'backend_policy': checked['config'].qualification_policy,
        'backend_observations': [{'system_fingerprint': fp, 'successful_provider_attempts': n}
                                 for fp, n in sorted(observed.items(), key=lambda item: str(item[0]))],
        'continuation': {'preserved_attempts': checked['completed'], 'qualification_requests_repeated': 0},
    }
    write_new(campaign / 'summary.json', summary)
    write_new(receipt_directory / 'exit.json', summary)
    return summary


def platform_only_change(old_contract, new_contract):
    """An explicit OS transition cannot authorize any other scientific change."""
    old, new = deepcopy(old_contract), deepcopy(new_contract)
    old_platform = old.get('runtime', {}).pop('platform', None)
    new_platform = new.get('runtime', {}).pop('platform', None)
    return bool(old_platform and new_platform and old_platform != new_platform and old == new)


def verify_runtime_transition(campaign):
    """Bind mixed-runtime provenance to original immutable bytes and request IDs."""
    campaign = Path(campaign)
    manifest = read(campaign / 'controlled/manifest.json')
    provenance = manifest.get('runtime_transition')
    if provenance is None:
        return None
    original = Path(provenance['original_campaign'])
    if not provenance.get('authorization_reference'):
        raise ValueError('Runtime transition lacks explicit authorization')
    hashes = provenance['original_sha256']
    if file_hashes(original) != hashes:
        raise ValueError('Original campaign changed after derivative preparation')
    old_manifest = read(original / 'controlled/manifest.json')
    if (old_manifest != provenance['original_run_manifest']
            or read(original / 'manifest.json') != provenance['original_campaign_manifest']
            or not platform_only_change(old_manifest['contract'], manifest['contract'])):
        raise ValueError('Transition must preserve every contract field except platform')
    for name, expected in hashes.items():
        if name in ('manifest.json', 'controlled/manifest.json'):
            continue
        if hashlib.sha256((campaign / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Copied original evidence changed')
    cfg = load_config(campaign / 'controlled-runtime-config.json')
    cases = load_cases(campaign / 'controlled/cases.json')
    planned = [key for key, *_ in requests(cases, cfg)]
    prior = {p.stem for p in (original / 'controlled/attempts').glob('*.json')}
    if (prior != set(planned[:len(prior)])
            or provenance['segments'] != [
                {'platform': old_manifest['contract']['runtime']['platform'], 'attempt_ids': planned[:len(prior)]},
                {'platform': manifest['contract']['runtime']['platform'], 'attempt_ids': planned[len(prior):]},
            ]
            or provenance['qualification_and_reference_platform'] != old_manifest['contract']['runtime']['platform']):
        raise ValueError('Runtime segment partition or qualification provenance changed')
    if read(campaign / 'manifest.json').get('runtime_transition_sha256') != digest(provenance):
        raise ValueError('Campaign runtime provenance binding changed')
    return provenance


def derive_campaign(old_campaign, new_campaign, new_packet, *, authorization_reference):
    """Copy completed evidence into an explicitly authorized OS-only continuation.

    The original run is never modified. The new manifest embeds the full original
    contracts and byte hashes so the frozen exporter includes the provenance.
    """
    if not isinstance(authorization_reference, str) or not authorization_reference.strip():
        raise ValueError('Explicit OS-transition authorization required')
    old_campaign, new_campaign = Path(old_campaign), Path(new_campaign)
    if new_campaign.exists():
        raise FileExistsError('Derivative requires a fresh directory')
    if (old_campaign / 'summary.json').exists() or (old_campaign / 'controlled/.lock').exists():
        raise ValueError('Original campaign finalized or locked')
    if probe_run_liveness(old_campaign / 'controlled') != 'inactive':
        raise ValueError('Original worker is active')
    blocks, packet_manifest = load_packet(new_packet)
    if set(blocks) != {'controlled'}:
        raise ValueError('Only single controlled-block transitions are supported')
    cases, prepared, preflight = blocks['controlled']
    cfg = load_config(old_campaign / 'controlled-runtime-config.json')
    old = read(old_campaign / 'controlled/manifest.json')
    current = to_data(_contract(cases, cfg))
    if not platform_only_change(old['contract'], current):
        raise ValueError('Only an actual OS-only transition is authorized')
    old_campaign_manifest = read(old_campaign / 'manifest.json')
    expected_block = {'case_bundle_sha256': digest(case_bundle(cases)),
                      'config': to_data(prepared), 'preflight': preflight}
    previous_block = deepcopy(old_campaign_manifest['blocks']['controlled'])
    if not platform_only_change(previous_block['preflight']['contract'], preflight['contract']):
        raise ValueError('Prepared contract has changes beyond OS')
    # plan_run refreshes measured reference timings; all scientific preflight
    # fields outside reference results and the OS contract must stay unchanged.
    if previous_block['config'] != expected_block['config'] or previous_block['case_bundle_sha256'] != expected_block['case_bundle_sha256']:
        raise ValueError('Prepared inputs changed')
    _, progress = replay(old_campaign / 'controlled')
    if progress['pending_attempt_ids']:
        raise ValueError('Uncertain original reservations cannot be repeated')
    hashes = file_hashes(old_campaign)
    planned = [key for key, *_ in requests(cases, cfg)]
    count = progress['completed']
    provenance = {
        'schema': 'explicit-os-continuation-v1',
        'authorization_reference': authorization_reference,
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'original_campaign': str(old_campaign.resolve()), 'original_sha256': hashes,
        'original_run_manifest': old,
        'original_campaign_manifest': old_campaign_manifest,
        'segments': [
            {'platform': old['contract']['runtime']['platform'], 'attempt_ids': planned[:count]},
            {'platform': current['runtime']['platform'], 'attempt_ids': planned[count:]},
        ],
        'qualification_and_reference_platform': old['contract']['runtime']['platform'],
        'limitations': ['Mixed operating-system evidence; timings are observational.',
                        'The method pair spanning the transition is retained and must be flagged.',
                        'Original qualification and solver references are reused without model calls.'],
    }
    shutil.copytree(old_campaign, new_campaign)
    new_run = {**old, 'contract': current, 'runtime_transition': provenance}
    new_manifest = {**old_campaign_manifest, 'blocks': {'controlled': expected_block},
                    'packet': {'campaign_sha256': digest(packet_manifest)},
                    'runtime_transition_sha256': digest(provenance),
                    'derivative_created_utc': provenance['created_utc']}
    # These two NEW derivative manifests change; original manifests stay intact.
    for name, value in (('controlled/manifest.json', new_run), ('manifest.json', new_manifest)):
        (new_campaign / name).unlink()
        write_new(new_campaign / name, value)
    return inspect_resume(new_packet, new_campaign)


def export_transition_analysis(campaign, directory, *, project_root):
    """Keep frozen numerical exports, with an explicit runtime supplement."""
    from scheduling.evaluation.study import export_study
    import tarfile
    campaign, directory = Path(campaign), Path(directory)
    provenance = verify_runtime_transition(campaign)
    if provenance is None:
        raise ValueError('Expected mixed-runtime evidence')
    result = export_study({'controlled': campaign / 'controlled'}, directory / 'numerical-export',
                          project_root=project_root, figures=True, development=True)
    rows, progress = replay(campaign / 'controlled')
    segment_for = {key: (i, seg['platform']) for i, seg in enumerate(provenance['segments'])
                   for key in seg['attempt_ids']}
    records, pair_platforms = [], {}
    for path in sorted((campaign / 'controlled/attempts').glob('*.json')):
        record = read(path)
        segment, platform = segment_for[path.stem]
        identity = record['identity']
        pair = {k: v for k, v in identity.items() if k != 'approach'}
        pair_key = digest(pair)
        pair_platforms.setdefault(pair_key, set()).add(platform)
        records.append({'attempt_id': path.stem, 'identity': identity, 'runtime_segment': segment,
                        'execution_platform': platform, 'pair_key': pair_key})
    cross = sorted(k for k, platforms in pair_platforms.items() if len(platforms) > 1)
    annotated = deepcopy(result)
    annotated['runtime_transition'] = provenance
    annotated['runtime_assignment'] = records
    row_assignment = {tuple(r['identity'][k] for k in ('case_id', 'variant_id', 'repeat', 'approach')): r for r in records}
    for row in annotated['rows']:
        assignment = row_assignment[tuple(row[k] for k in ('case_id', 'variant_id', 'repeat', 'approach'))]
        row.update(execution_platform=assignment['execution_platform'], runtime_segment=assignment['runtime_segment'],
                   cross_platform_pair=assignment['pair_key'] in cross)
    annotated['cross_platform_pair_keys'] = cross
    annotated['settings']['runtime_scope'] = 'Mixed OS: see runtime_transition and per-attempt runtime_assignment; runtime.platform is continuation environment only.'
    write_new(directory / 'analysis-with-runtime-provenance.json', annotated)
    (directory / 'README.md').write_text(
        '# Mixed-OS continuation evidence\n\n'
        'Read analysis-with-runtime-provenance.json as the canonical annotated analysis. '
        'The numerical-export folder preserves frozen scoring outputs; its single platform field describes '
        'the continuation environment, not every attempt. The full original contract and original-file hashes '
        'are embedded in the run manifest inside its reproduction archive.\n\n'
        'No original attempt or qualification request was repeated. Original failures remain in denominators. '
        'Timing comparisons are observational; retain and flag cross-platform method pairs.\n\n'
        'The annotated snapshot is self-contained. Regenerating its operational provenance checks requires '
        'the original campaign path; frozen numerical replay remains available in the inner reproduction archive.\n')
    with tarfile.open(directory / 'mixed-os-evidence.tar.gz', 'x:gz') as archive:
        for path in sorted(directory.rglob('*')):
            if path.is_file() and path.name != 'mixed-os-evidence.tar.gz':
                archive.add(path, arcname=str(path.relative_to(directory)), recursive=False)
        archive.add(Path(__file__), arcname='operational-resume-adapter.py', recursive=False)
    write_new(directory / 'mixed-os-evidence-sha256.json', {
        'sha256': hashlib.sha256((directory / 'mixed-os-evidence.tar.gz').read_bytes()).hexdigest(),
        'model_calls': 0, 'completed': progress['completed'], 'cross_platform_pairs': len(cross)})
    return annotated
