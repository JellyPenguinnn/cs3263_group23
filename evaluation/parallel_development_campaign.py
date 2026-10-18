"""Explicit parallel execution adapter around frozen scheduling pipelines.

No prompt, parser, solver, validator or model configuration is changed. This is a
separate execution protocol: bounded concurrency, one coordinator, durable claims,
no retries, drain-on-stop, and separately attributed timing segments.
"""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from datetime import datetime, timezone
from pathlib import Path
import threading
import math
import time

from scheduling.evaluation.cases import case_bundle, check_case_set
from scheduling.evaluation.failure_policy import TRANSIENT_FAILURES, CONTINUE_TRANSIENT_POLICY
from scheduling.evaluation.liveness import RunLock
from scheduling.evaluation.runner import (
    _contract, _stop_reason, baseline_fingerprints, read, write_new, replace_pending,
    requests, OBSERVE_BACKEND_POLICY,
)
from scheduling.evaluation.scoring import digest, evaluate, reference, check_reference
from scheduling.pipelines.direct import run_direct
from scheduling.pipelines.solver_augmented import run_solver_augmented
from scheduling.providers import RequestBudget
from scheduling.schema import to_data


def utc():
    return datetime.now(timezone.utc).isoformat()


class ThreadSafeBudget(RequestBudget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mutex = threading.Lock()

    def reserve(self, tokens):
        with self._mutex:
            return super().reserve(tokens)


def protocol(planned, saved, concurrency, prior_segments=None):
    return {
        'version': 'parallel-development-v2' if prior_segments is not None else 'parallel-development-v1', 'concurrency': concurrency,
        'max_attempts_per_request': 1, 'dispatch_order': 'original planned request order',
        'transient_policy': 'Global 30-second dispatch cooldown; in-flight calls drain; no retry',
        'fatal_policy': 'Stop new dispatch and drain all already-submitted calls',
        'segments': ([{**segment, 'attempt_ids': [key for key in segment['attempt_ids'] if key in saved]} for segment in prior_segments] if prior_segments is not None else [
            {'name': 'serial_before_parallel', 'concurrency': 1, 'attempt_ids': [k for k in planned if k in saved]},
        ]) + [{'name': f'parallel{concurrency}', 'concurrency': concurrency, 'attempt_ids': [k for k in planned if k not in saved]}],
        'timing_note': 'Request elapsed times overlap in the parallel segment; their sum is not campaign wall time. Report by OS and concurrency; matched-model timing uses common parallel cases only.',
    }


def run_parallel(cases, directory, config, *, provider_complete, concurrency=16,
                 stop_event=None, progress=None, cooldown_seconds=30):
    if type(concurrency) is not int or not 1 <= concurrency <= 16 or config.model.max_attempts != 1:
        raise ValueError('Bounded 1..16 concurrency and exactly one provider attempt required')
    if config.evidence != 'live_development' or config.qualification_policy != OBSERVE_BACKEND_POLICY:
        raise ValueError('Parallel adapter is explicitly qualified development evidence only')
    if config.provider_failure_policy != CONTINUE_TRANSIENT_POLICY:
        raise ValueError('Explicit continue-transient policy required')
    if type(cooldown_seconds) not in (int, float) or not math.isfinite(cooldown_seconds) or cooldown_seconds < 0:
        raise ValueError('Cooldown must be finite and nonnegative')
    stop_event = stop_event if stop_event is not None else threading.Event()
    cases = check_case_set(tuple(cases))
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    started = time.monotonic()
    with RunLock(directory / '.lock'):
        contract = to_data(_contract(cases, config))
        planned = list(requests(cases, config))
        keys = [r[0] for r in planned]
        records = directory / 'attempts'; refs = directory / 'references'
        if (directory / 'manifest.json').exists():
            manifest = read(directory / 'manifest.json')
            if manifest['contract'] != contract or digest(read(directory / 'cases.json')) != contract['case_bundle_sha256']:
                raise ValueError('Scientific contract or cases changed')
            declared = manifest.get('execution_protocol')
            if not declared or declared.get('concurrency') != concurrency:
                raise ValueError('An explicit new parallel derivative is required')
        else:
            if any(p.name != '.lock' for p in directory.iterdir()):
                raise ValueError('New run must be empty')
            declared = protocol(keys, set(), concurrency)
            write_new(directory / 'manifest.json', {'contract': contract, 'created_utc': utc(), 'execution_protocol': declared})
            write_new(directory / 'cases.json', case_bundle(cases))
        refs.mkdir(exist_ok=True); records.mkdir(exist_ok=True)
        saved = {p.stem: read(p) for p in records.glob('*.json')}
        prior_segments = declared['segments'][:-1] if declared.get('version') == 'parallel-development-v2' else None
        initial_ids = {key for segment in declared['segments'][:-1] for key in segment['attempt_ids']}
        if declared != protocol(keys, initial_ids, concurrency, prior_segments) or not initial_ids <= set(saved):
            raise ValueError('Execution segment membership changed')
        if set(saved) - set(keys) or len(saved) > config.max_requests or len(saved) * config.model.max_tokens > config.max_requested_output_tokens:
            raise ValueError('Unexpected or over-budget reservations')
        gold = {}
        for case in cases:
            path = refs / (digest(case.case_id) + '.json')
            if not path.exists():
                value = reference(case, config.reference_solver)
                write_new(path, {'reference': value, 'sha256': digest(value)})
            value = read(path)
            if digest(value['reference']) != value['sha256']:
                raise ValueError('Reference checksum mismatch')
            check_reference(case, value['reference'])
            gold[case.case_id] = value['reference']
        reconciled = set()
        if declared.get('version') == 'parallel-development-v2':
            verify_parallel_copy(directory.parent)
            reconciled = set(manifest['execution_transition']['reconciled_http_429_attempt_ids'])
        fingerprints = baseline_fingerprints(config)
        cooldown_until = 0.0
        for key, identity, case, _ in planned:
            if key not in saved:
                continue
            record = saved[key]
            if (record.get('state') != 'completed' or record.get('identity') != identity
                    or record.get('requested_output_tokens') != config.model.max_tokens
                    or record.get('sha256') != digest(record.get('payload'))):
                raise ValueError('Pending, corrupted or changed attempt; never reissue')
            payload = record['payload']
            if payload['identity'] != identity or digest(evaluate(case, payload['pipeline_result'], gold[case.case_id], repeat=identity['repeat'])) != digest(payload['evaluation']):
                raise ValueError('Saved evaluation differs from replay')
            reason = _stop_reason(payload['pipeline_result'].get('model_response') or {}, config.model.model, fingerprints, allow_backend_variation=True)
            if reason and reason not in TRANSIENT_FAILURES and not (reason == 'http_429' and key in reconciled):
                raise ValueError('Saved fatal provider error forbids dispatch: ' + reason)
        # On a later recovery, a success saved after a transient failure must
        # not erase that failure's cooldown. Conservatively wait once if any
        # retained transient exists; this never reissues the failed request.
        if any((d['payload']['pipeline_result'].get('model_response') or {}).get('error')
               in TRANSIENT_FAILURES for d in saved.values()):
            cooldown_until = time.monotonic() + cooldown_seconds
        todo = [item for item in planned if item[0] not in saved]
        cursor = 0; reserved = len(saved); completed = len(saved); fatal = None
        in_flight = {}; max_in_flight = 0

        def execute(item, pending):
            key, identity, _, view = item
            worker_started = utc()
            timing = {'protocol': 'parallel-development-v1', 'configured_concurrency': concurrency,
                      'dispatch_utc': pending['started_utc'], 'worker_started_utc': worker_started}
            result = (run_direct(view, config.model, provider_complete=provider_complete)
                      if identity['approach'] == 'direct' else
                      run_solver_augmented(view, config.model, config.solver, provider_complete=provider_complete))
            timing['worker_finished_utc'] = utc()
            # Preserve a received response before coordinator scoring, so an
            # interrupted evaluation cannot cause the model call to be repeated.
            replace_pending(records / (key + '.json'), {**pending, 'pipeline_result': to_data(result), 'execution_timing': timing})
            return result, timing

        with ThreadPoolExecutor(max_workers=concurrency, thread_name_prefix='schedule') as pool:
            while cursor < len(todo) or in_flight:
                if stop_event.is_set() and fatal is None:
                    fatal = 'operator_stop'
                # Consume every already-finished future before scheduling more.
                done = {f for f in in_flight if f.done()}
                for future in done:
                    item, pending = in_flight.pop(future)
                    key, identity, case, _ = item
                    try:
                        result, timing = future.result()
                        scored = evaluate(case, result, gold[case.case_id], repeat=identity['repeat'])
                        payload = {'identity': identity, 'public_view': to_data(item[3]),
                                   'pipeline_result': to_data(result), 'evaluation': to_data(scored)}
                        replace_pending(records / (key + '.json'), {**pending, 'state': 'completed',
                            'payload': payload, 'sha256': digest(payload), 'execution_timing': timing})
                        completed += 1
                        reason = _stop_reason(result.model_response, config.model.model, fingerprints, allow_backend_variation=True)
                        if reason:
                            if reason in TRANSIENT_FAILURES and config.provider_failure_policy == CONTINUE_TRANSIENT_POLICY:
                                cooldown_until = max(cooldown_until, time.monotonic() + cooldown_seconds)
                            elif fatal is None:
                                fatal = reason
                        if progress:
                            progress({'completed': completed, 'reserved': reserved, 'in_flight': len(in_flight), 'stop_reason': fatal})
                    except Exception as error:
                        if fatal is None:
                            fatal = 'worker_or_scoring_error:' + type(error).__name__
                        # Leave its reservation and any raw response untouched.
                if fatal and not in_flight:
                    break
                if not fatal and time.monotonic() >= cooldown_until:
                    while len(in_flight) < concurrency and cursor < len(todo) and not stop_event.is_set():
                        # A fatal future may have finished while another record
                        # was scored; return to processing before refilling.
                        if any(f.done() for f in in_flight):
                            break
                        if reserved >= config.max_requests or (reserved + 1) * config.model.max_tokens > config.max_requested_output_tokens:
                            fatal = 'budget_exhausted'; break
                        item = todo[cursor]; key = item[0]
                        pending = {'state': 'pending_or_interrupted', 'identity': item[1],
                                   'requested_output_tokens': config.model.max_tokens, 'started_utc': utc()}
                        write_new(records / (key + '.json'), pending)
                        reserved += 1; cursor += 1
                        future = pool.submit(execute, item, pending)
                        in_flight[future] = (item, pending)
                        max_in_flight = max(max_in_flight, len(in_flight))
                if in_flight:
                    wait(in_flight, timeout=.1, return_when=FIRST_COMPLETED)
                elif cursor < len(todo) and not fatal:
                    stop_event.wait(min(.1, max(.001, cooldown_until-time.monotonic())))
        return {'state': 'completed' if fatal is None and completed == len(planned) else
                        'stopped_interrupted' if fatal == 'operator_stop' else 'stopped_provider',
                'stop_reason': fatal, 'completed': completed, 'reserved_requests': reserved,
                'reserved_output_tokens': reserved * config.model.max_tokens,
                'elapsed_seconds': time.monotonic() - started, 'max_in_flight': max_in_flight,
                'concurrency': concurrency, 'previous_completed': len(saved)}


def _resume_adapter():
    import importlib.util
    spec = importlib.util.spec_from_file_location('serial_resume_adapter', Path(__file__).with_name('resume_development_campaign.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prepare_parallel_copy(original, destination, packet, *, authorization_reference):
    """Prepare a new derivative; preserve original campaign and old record bytes."""
    import shutil
    if not authorization_reference:
        raise ValueError('Explicit concurrency-change authorization required')
    adapter = _resume_adapter()
    checked = adapter.inspect_resume(packet, original)
    original, destination = Path(original), Path(destination)
    hashes = adapter.file_hashes(original)
    if destination.exists():
        raise FileExistsError('Use a new parallel campaign directory')
    shutil.copytree(original, destination)
    manifest = read(destination / 'controlled/manifest.json')
    keys = [key for key, *_ in requests(checked['cases'], checked['config'])]
    saved = {p.stem for p in (destination / 'controlled/attempts').glob('*.json')}
    transition = {'authorization_reference': authorization_reference, 'created_utc': utc(),
                  'original_campaign': str(original.resolve()), 'original_sha256': hashes,
                  'original_run_manifest': manifest, 'original_campaign_manifest': read(original / 'manifest.json'),
                  'completed_attempts_reused': len(saved), 'qualification_requests_repeated': 0}
    manifest = {**manifest, 'execution_transition': transition,
                'execution_protocol': protocol(keys, saved, 16)}
    top = {**read(destination / 'manifest.json'), 'execution_transition_sha256': digest(transition)}
    for name, data in (('controlled/manifest.json', manifest), ('manifest.json', top)):
        (destination / name).unlink()
        write_new(destination / name, data)
    verify_parallel_copy(destination)
    return {'completed': len(saved), 'remaining': len(keys)-len(saved),
            'requests_already_reserved': checked['budget'].requests_used}


def verify_parallel_copy(campaign):
    import hashlib
    campaign = Path(campaign)
    m = read(campaign / 'controlled/manifest.json')
    t = m.get('execution_transition')
    if t is None:
        return
    adapter = _resume_adapter(); original = Path(t['original_campaign'])
    if not t.get('authorization_reference') or adapter.file_hashes(original) != t['original_sha256']:
        raise ValueError('Original serial evidence changed')
    if (m['contract'] != t['original_run_manifest']['contract']
            or read(original / 'controlled/manifest.json') != t['original_run_manifest']
            or read(original / 'manifest.json') != t['original_campaign_manifest']
            or read(campaign / 'manifest.json').get('execution_transition_sha256') != digest(t)):
        raise ValueError('Execution transition binding changed')
    if t.get('kind') == 'parallel_continuation':
        verify_parallel_copy(original)
        _validate_continuation(m, original)
    for name, h in t['original_sha256'].items():
        if name not in ('manifest.json', 'controlled/manifest.json'):
            target = t.get('relocated_files', {}).get(name, name)
            if hashlib.sha256((campaign / target).read_bytes()).hexdigest() != h:
                raise ValueError('Copied serial evidence changed')


def _historical_429(original):
    summary = read(original / 'summary.json')
    saved = {p.stem: read(p) for p in (original / 'controlled/attempts').glob('*.json')}
    if (summary.get('state') != 'stopped_campaign' or summary.get('stop_reason') != 'http_429'
            or summary.get('requests_reserved') != len(saved) + 3
            or any(d.get('state') != 'completed' for d in saved.values())):
        raise ValueError('Expected a fully drained, accounted HTTP 429 stop')
    ids = []
    for key, d in saved.items():
        response = d['payload']['pipeline_result']['model_response']
        if len(response['attempts']) != 1:
            raise ValueError('One provider call per retained attempt required')
        if response.get('error') == 'http_429':
            a = response['attempts'][0]
            if a.get('http_status') != 429 or a.get('outcome_uncertain') is not False:
                raise ValueError('Historical HTTP 429 must be an explicitly rejected request')
            ids.append(key)
    if not ids:
        raise ValueError('No recorded HTTP 429 to reconcile')
    return sorted(ids), saved


def _validate_continuation(manifest, original):
    t = manifest['execution_transition']; previous = t['original_run_manifest']['execution_protocol']
    current = manifest['execution_protocol']; ids, saved = _historical_429(original)
    prior = [{**s, 'attempt_ids': [k for k in s['attempt_ids'] if k in saved]}
             for s in previous['segments']]
    from scheduling.evaluation.cases import load_cases
    from scheduling.evaluation.cli import load_config
    planned = [k for k, *_ in requests(load_cases(original / 'controlled/cases.json'), load_config(original / 'controlled-runtime-config.json'))]
    if (type(current['concurrency']) is not int or not 1 <= current['concurrency'] < previous['concurrency']
            or t.get('reconciled_http_429_attempt_ids') != ids
            or current != protocol(planned, set(saved), current['concurrency'], prior)
            or t.get('relocated_files') != {'summary.json': 'prior-phase/summary.json',
                                           'parallel-start.json': 'prior-phase/parallel-start.json'}):
        raise ValueError('Continuation changed historical segments or reconciliation')


def inspect_parallel_resume(packet, campaign):
    campaign = Path(campaign)
    verify_parallel_copy(campaign)
    t = read(campaign / 'controlled/manifest.json')['execution_transition']
    if t.get('kind') != 'parallel_continuation':
        raise ValueError('Explicit continuation provenance required')
    return _resume_adapter().inspect_resume(packet, campaign, allow_nonprefix=True,
        reconciled_http_429_attempt_ids=t['reconciled_http_429_attempt_ids'])


def prepare_parallel_continuation(original, destination, packet, *, authorization_reference, concurrency=8):
    """Reconcile a drained 429 stop without replaying any previous call."""
    import shutil
    original, destination = Path(original), Path(destination)
    if not isinstance(authorization_reference, str) or not authorization_reference.strip():
        raise ValueError('Explicit continuation authorization required')
    if destination.exists():
        raise FileExistsError('Use a fresh continuation directory')
    verify_parallel_copy(original)
    manifest = read(original / 'controlled/manifest.json')
    previous = manifest['execution_protocol']
    if type(concurrency) is not int or not 1 <= concurrency < previous['concurrency']:
        raise ValueError('HTTP 429 continuation requires lower concurrency')
    ids, saved = _historical_429(original)
    adapter = _resume_adapter()
    checked = adapter.inspect_resume(packet, original, allow_finalized=True, allow_nonprefix=True,
                                      reconciled_http_429_attempt_ids=ids)
    keys = [key for key, *_ in requests(checked['cases'], checked['config'])]
    if [k for s in previous['segments'] for k in s['attempt_ids']] != keys:
        # Segments may be noncontiguous after an interrupted parallel wave.
        if sorted(k for s in previous['segments'] for k in s['attempt_ids']) != sorted(keys):
            raise ValueError('Previous protocol does not cover the exact planned requests')
    prior = [{**s, 'attempt_ids': [k for k in s['attempt_ids'] if k in saved]} for s in previous['segments']]
    hashes = adapter.file_hashes(original)
    t = {'kind': 'parallel_continuation', 'authorization_reference': authorization_reference,
         'created_utc': utc(), 'original_campaign': str(original.resolve()),
         'original_sha256': hashes, 'original_run_manifest': manifest,
         'original_campaign_manifest': read(original / 'manifest.json'),
         'completed_attempts_reused': len(saved), 'qualification_requests_repeated': 0,
         'reconciled_http_429_attempt_ids': ids,
         'relocated_files': {'summary.json': 'prior-phase/summary.json',
                             'parallel-start.json': 'prior-phase/parallel-start.json'}}
    updated = {**manifest, 'execution_transition': t,
               'execution_protocol': protocol(keys, set(saved), concurrency, prior)}
    _validate_continuation(updated, original)
    shutil.copytree(original, destination)
    (destination / 'prior-phase').mkdir(exist_ok=False)
    for name, relocated in t['relocated_files'].items():
        (destination / name).rename(destination / relocated)
    for name, value in [('controlled/manifest.json', updated),
                        ('manifest.json', {**read(original / 'manifest.json'), 'execution_transition_sha256': digest(t)})]:
        (destination / name).unlink(); write_new(destination / name, value)
    verify_parallel_copy(destination)
    return {'completed': len(saved), 'remaining': len(keys)-len(saved),
            'requests_already_reserved': checked['budget'].requests_used,
            'reconciled_http_429_attempt_ids': ids, 'concurrency': concurrency}


def execute_parallel_campaign(packet, campaign, *, authorization_reference, stop_event=None,
                              provider_factory=None, resume=False, progress=None, concurrency=16):
    """One single-model campaign, original caps and qualification, new execution."""
    from dataclasses import replace
    from evaluation.run_development_campaign import load_packet
    from scheduling.evaluation.qualification import MESSAGES, capability_issue
    from scheduling.evaluation.metrics import token_usage_summary
    from scheduling.providers import SoCLaaSProvider
    import hashlib
    if not authorization_reference:
        raise ValueError('Explicit live authorization required')
    if type(concurrency) is not int or not 1 <= concurrency <= 16:
        raise ValueError('Concurrency must be an integer in 1..16')
    campaign = Path(campaign)
    blocks, packet_manifest = load_packet(packet)
    if set(blocks) != {'controlled'}:
        raise ValueError('One controlled block required')
    cases, prepared, preflight = blocks['controlled']
    adapter = _resume_adapter()
    if resume:
        verify_parallel_copy(campaign)
        checked = (inspect_parallel_resume(packet, campaign)
                   if read(campaign / 'controlled/manifest.json').get('execution_transition', {}).get('kind') == 'parallel_continuation'
                   else adapter.inspect_resume(packet, campaign))
        cfg = checked['config']
        budget = ThreadSafeBudget(checked['budget'].max_requests, checked['budget'].max_completion_tokens)
        if not budget.reserve(0):
            raise ValueError('Cannot restore metadata budget')
        for _ in range(checked['completed'] + 2):
            if not budget.reserve(cfg.model.max_tokens):
                raise ValueError('Cannot restore previous request budget')
    else:
        campaign.mkdir(parents=True, exist_ok=False, mode=0o700)
        cfg = prepared
        budget = ThreadSafeBudget(prepared.max_requests+3, prepared.max_requested_output_tokens+2*prepared.model.max_tokens)
        write_new(campaign / 'manifest.json', {
            'format_version': '1.0', 'evidence': f'live_development_parallel{concurrency}',
            'authorization_reference': authorization_reference, 'created_utc': utc(),
            'packet': {'campaign_sha256': digest(packet_manifest)},
            'blocks': {'controlled': {'case_bundle_sha256': digest(case_bundle(cases)), 'config': to_data(prepared), 'preflight': preflight}},
            'block_order': ['controlled'], 'max_requests': budget.max_requests,
            'max_requested_output_tokens': budget.max_completion_tokens,
            'request_allocation': {'metadata': 1, 'capability': 2, 'scheduling': prepared.max_requests},
            'capability_messages': to_data(MESSAGES), 'execution_concurrency': concurrency,
            'operational_adapter_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        })
        write_new(campaign / 'blocks.json', {'controlled': 'controlled'})
    start = time.monotonic()
    write_new(campaign / 'parallel-start.json', {'created_utc': utc(), 'concurrency': concurrency,
        'previous_requests_reserved': budget.requests_used, 'previous_output_tokens_reserved': budget.completion_tokens_reserved,
        'authorization_reference': authorization_reference, 'automatic_retries': 0,
        'operational_adapter_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    factory = provider_factory or SoCLaaSProvider.from_environment
    result = None; failure = None
    with factory(budget=budget) as provider:
        if not resume and stop_event is not None and stop_event.is_set():
            failure = 'operator_stop'
        if not resume and not failure:
            write_new(campaign / 'metadata-reservation.json', {'requests': 1, 'output_tokens': 0})
            try:
                models = provider.list_models()
            except ValueError:
                models = (); failure = 'model_listing_failed'
            available = prepared.model.model in models
            write_new(campaign / 'metadata.json', {'requested_model': prepared.model.model, 'available': available, 'catalogue_sha256': digest(models)})
            if not available:
                failure = failure or 'requested_model_unavailable'
            fingerprints = set(); caps = []
            if not failure:
                for index in range(2):
                    if stop_event is not None and stop_event.is_set():
                        failure = 'operator_stop'; break
                    write_new(campaign / f'capability-{index:02}-reservation.json', {'requests': 1, 'output_tokens': prepared.model.max_tokens})
                    response = provider.complete(MESSAGES, prepared.model)
                    issue = capability_issue(response, prepared, fingerprints)
                    record = {'index': index, 'response': to_data(response), 'issue': issue}
                    write_new(campaign / f'capability-{index:02}.json', record); caps.append(digest(record))
                    if issue:
                        failure = issue; break
            if not failure:
                cfg = replace(prepared, qualification_baseline={'capability_sha256': caps, 'system_fingerprints': sorted(fingerprints, key=str)})
                write_new(campaign / 'controlled-runtime-config.json', cfg)
        if not failure:
            result = run_parallel(cases, campaign / 'controlled', cfg, provider_complete=provider.complete,
                                  concurrency=concurrency, stop_event=stop_event, progress=progress)
            failure = result.get('stop_reason')
    verify_parallel_copy(campaign) if (campaign / 'controlled/manifest.json').exists() else None
    attempts = [a for p in sorted(campaign.glob('capability-[0-9][0-9].json')) for a in read(p)['response']['attempts']]
    for path in (campaign / 'controlled/attempts').glob('*.json'):
        d = read(path); z = d.get('payload', {}).get('pipeline_result') or d.get('pipeline_result') or {}
        attempts.extend((z.get('model_response') or {}).get('attempts', []))
    summary = {'state': 'completed' if result and result['state']=='completed' else 'stopped_campaign',
               'stop_reason': failure, 'blocks': {'controlled': result},
               'requests_reserved': budget.requests_used, 'requested_output_tokens_reserved': budget.completion_tokens_reserved,
               'parallel_phase_wall_seconds': time.monotonic()-start,
               'wall_scope': 'This execution phase only, including qualification for a fresh model; excludes all earlier execution phases',
               'tokens': token_usage_summary(a['usage'] for a in attempts),
               'usage_scope': 'All saved qualification and scheduling attempts, including all preserved earlier attempts; missing usage remains unknown',
               'provider_failure_counts': dict(Counter(a['error'] for a in attempts if a.get('error'))),
               'concurrency': concurrency, 'automatic_retries': 0}
    write_new(campaign / 'summary.json', summary)
    return summary


def export_parallel_study(campaign, directory, *, project_root):
    """Frozen numeric replay plus mandatory per-request concurrency/OS attribution."""
    import hashlib
    import tarfile
    from copy import deepcopy
    from scheduling.evaluation.study import export_study, resource_statistics
    campaign, directory = Path(campaign), Path(directory)
    verify_parallel_copy(campaign)
    manifest = read(campaign / 'controlled/manifest.json')
    execution = manifest['execution_protocol']
    numerical = export_study({'controlled': campaign / 'controlled'}, directory / 'numerical-export',
                             project_root=project_root, figures=True, development=True)
    result = deepcopy(numerical)
    assignments = {key: (segment['name'], segment['concurrency'])
                   for segment in execution['segments'] for key in segment['attempt_ids']}
    os_segments = manifest.get('runtime_transition', {}).get('segments', [])
    platforms = {key: seg['platform'] for seg in os_segments for key in seg['attempt_ids']}
    lookup = {}; pair_segments = {}
    for path in (campaign / 'controlled/attempts').glob('*.json'):
        d = read(path); identity = d['identity']; segment, concurrency = assignments[path.stem]
        row_key = tuple(identity[k] for k in ('case_id','variant_id','repeat','approach'))
        platform = platforms.get(path.stem, manifest['contract']['runtime']['platform'])
        lookup[row_key] = {'attempt_id': path.stem, 'execution_segment': segment,
                           'execution_concurrency': concurrency, 'execution_platform': platform,
                           'execution_timing': d.get('execution_timing')}
        pair_segments.setdefault(row_key[:3], set()).add((segment,platform))
    for row in result['rows']:
        key = tuple(row[k] for k in ('case_id','variant_id','repeat','approach'))
        row.update(lookup[key]); row['cross_execution_pair'] = len(pair_segments[key[:3]]) > 1
    result['execution_protocol'] = execution
    result['runtime_transition'] = manifest.get('runtime_transition')
    result['execution_transition'] = manifest.get('execution_transition')
    result['settings']['execution_scope'] = 'Mixed OS/concurrency where annotated; never treat aggregate timings as a uniform serial or parallel condition'
    result['timing_by_execution_segment'] = resource_statistics(result['rows'], group_by=('execution_segment','execution_concurrency','execution_platform','approach'))
    write_new(directory / 'analysis-with-execution-provenance.json', result)
    write_new(directory / 'timing-by-execution-segment.json', result['timing_by_execution_segment'])
    (directory / 'README.md').write_text(
        f"# Explicit concurrency-{execution['concurrency']} development evidence\n\n"
        'Use analysis-with-execution-provenance.json and timing-by-execution-segment.json. '
        'All serial observations remain in primary outcome denominators. Each row records OS and execution concurrency. '
        'Cross-execution method pairs are flagged. Compare Qwen/GLM timing only on common cases where both methods '
        'ran in the same parallel protocol; do not pool serial and parallel latency as controlled evidence. '
        'Sum of request times is not parallel elapsed wall time. Queueing and shared-service backend variation remain possible.\n\n'
        'numerical-export preserves unchanged scoring/replay and charts; its unstratified timing tables are not the '
        'recommended timing comparison. The inner reproduction archive includes the provenance-bearing run manifest. '
        'Operational provenance revalidation requires original campaign paths; frozen numerical replay is portable.\n')
    with tarfile.open(directory / 'parallel-evidence.tar.gz', 'x:gz') as archive:
        for path in sorted(directory.rglob('*')):
            if path.is_file() and path.name != 'parallel-evidence.tar.gz':
                archive.add(path, arcname=str(path.relative_to(directory)), recursive=False)
        for path in sorted([*campaign.glob('*.json'), *(campaign / 'prior-phase').rglob('*.json')]):
            archive.add(path, arcname='campaign/'+str(path.relative_to(campaign)), recursive=False)
        for name in ('parallel_development_campaign.py','resume_development_campaign.py'):
            archive.add(Path(__file__).with_name(name), arcname='operations/'+name, recursive=False)
    write_new(directory / 'archive-sha256.json', {'sha256': hashlib.sha256((directory/'parallel-evidence.tar.gz').read_bytes()).hexdigest(), 'model_calls':0})
    return result
