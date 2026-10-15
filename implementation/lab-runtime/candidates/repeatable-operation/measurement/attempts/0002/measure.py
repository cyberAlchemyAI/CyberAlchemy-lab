#!/usr/bin/env python3
"""Bounded measured current-code baseline, isolated from all real operator stores."""
from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import signal
import statistics
import sys
from tempfile import TemporaryDirectory
import time
from unittest.mock import patch
import uuid

ACTIVE_RESULTS = []
ACTIVE_PHASE = {'name': 'initialization', 'transaction_count': None}
STARTED = None
ATTEMPT = None
PROTOCOL = None


def persist_event(value):
    with (ATTEMPT / 'events.jsonl').open('a') as handle:
        handle.write(json.dumps(value, sort_keys=True) + '\n')
        handle.flush()
        import os
        os.fsync(handle.fileno())


def phase(name, count=None):
    ACTIVE_PHASE.update(name=name, transaction_count=count)
    persist_event({'kind': 'phase-entry', 'phase': dict(ACTIVE_PHASE), 'elapsed_seconds': time.monotonic() - STARTED})


def timeout(signum, frame):
    raise TimeoutError('wall budget expired in ' + ACTIVE_PHASE['name'])

PACKAGE = Path(__file__).resolve().parents[1]
REPO = PACKAGE.parents[3]
sys.path.insert(0, str(PACKAGE))
from lab_runtime.common import byte_digest, digest, load
from lab_runtime.profiles import select
from lab_runtime.sources import capture

LEGACY = REPO / 'implementation/lab-runtime/v2'
spec = importlib.util.spec_from_file_location('measurement_frozen_v2', LEGACY / 'lab_runtime/__init__.py',
                                            submodule_search_locations=[str(LEGACY / 'lab_runtime')])
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
from measurement_frozen_v2.cli import example
from measurement_frozen_v2.common import digest as old_digest
from measurement_frozen_v2.graph import build
from measurement_frozen_v2.operations import validate_record
from measurement_frozen_v2.session import Session
from measurement_frozen_v2.store import Store, keygen


def main():
    global STARTED, ATTEMPT, PROTOCOL
    protocol_path = Path(__file__).with_name('protocol.json')
    protocol = load(protocol_path)
    started = STARTED = time.monotonic()
    PROTOCOL = protocol
    attempts = Path(__file__).with_name('attempts')
    index = 1
    while (attempts / f'{index:04d}').exists():
        index += 1
    ATTEMPT = attempts / f'{index:04d}'
    ATTEMPT.mkdir(parents=True)
    (ATTEMPT / 'protocol.json').write_bytes(protocol_path.read_bytes())
    (ATTEMPT / 'measure.py').write_bytes(Path(__file__).read_bytes())
    signal.signal(signal.SIGALRM, timeout)
    signal.setitimer(signal.ITIMER_REAL, protocol['resource_limits']['max_total_seconds'])
    sample_count = protocol['samples_per_operation']
    results = ACTIVE_RESULTS
    selected_row = next(s for s in load(PACKAGE / 'profiles/selections.json')['selections'] if s['name'] == 'd75')
    selected = select(REPO, **{k: v for k, v in selected_row.items() if k not in ['name', 'source_materials', 'source_bytes']})
    def measure(name, count, function, *, output_digest=digest):
        phase(name, count)
        durations, digests = [], []
        for _ in range(sample_count):
            if time.monotonic() - started >= protocol['resource_limits']['max_total_seconds']:
                raise RuntimeError('overall measurement budget exceeded')
            t0 = time.perf_counter()
            remaining = protocol['resource_limits']['max_total_seconds'] - (time.monotonic() - started)
            signal.setitimer(signal.ITIMER_REAL, min(remaining, protocol['resource_limits']['per_operation_sample_seconds']))
            try:
                value = function()
            finally:
                remaining = protocol['resource_limits']['max_total_seconds'] - (time.monotonic() - started)
                signal.setitimer(signal.ITIMER_REAL, max(0.001, remaining))
            elapsed = time.perf_counter() - t0
            durations.append(elapsed)
            digests.append(output_digest(value))
            persist_event({'kind': 'sample', 'phase': dict(ACTIVE_PHASE), 'duration_seconds': elapsed,
                           'output_digest': digests[-1], 'sample_index': len(durations)})
            if elapsed > protocol['resource_limits']['per_operation_sample_seconds']:
                raise RuntimeError('operation resource ceiling exceeded: ' + name)
        if len(set(digests)) != 1:
            raise RuntimeError('nonrepeatable output: ' + name)
        results.append({'operation': name, 'transaction_count': count, 'sample_seconds': durations,
            'mean_seconds': statistics.mean(durations), 'stdev_seconds': statistics.pstdev(durations),
            'minimum_seconds': min(durations), 'maximum_seconds': max(durations),
            'identical_output_digests': True, 'output_digest': digests[0]})
        persist_event({'kind': 'completed-operation', 'result': results[-1]})
        print(json.dumps({'operation': name, 'transactions': count, 'mean_seconds': statistics.mean(durations)}), flush=True)
        return value
    initial = measure('independent_source_capture', None, lambda: capture(selected), output_digest=lambda s: s['snapshot_digest'])
    raw_contents = {name: base64.b64decode(value, validate=True) for name, value in initial['byte_contents'].items()}
    measure('source_byte_hashing_in_memory', None, lambda: {name: byte_digest(value) for name, value in raw_contents.items()})
    with TemporaryDirectory(prefix='lab-replay-measurement-') as temp:
        root = Path(temp)
        private = root / 'test-only-operator.pem'
        public = root / 'test-only-operator.pub'
        keygen(private, public)
        for count in protocol['transaction_counts']:
            phase('case-setup', count)
            store = Store(root / f'case-{count}', REPO)
            store.initialize(load(LEGACY / 'profile.json'), f'measurement-{count}', 'role:test-only-candidate-operator', public.read_text().strip())
            for i in range(count):
                phase('case-setup-transaction-' + str(i), count)
                proposal = example(store, f'measurement-{count}-{i}')
                store.apply(proposal, store.authorize(proposal, private))
            data = measure('full_replay', count, lambda: store.replay(require_current=True), output_digest=old_digest)
            work = next(v for v in data['projection']['subjects'].values() if v['kind'] == 'work' and v.get('carrier_ref') == 'cal.artifact-type.work/v1')
            def schema():
                validate_record(work['record'], work['carrier_ref'], data['projection'])
                return {'body_sha256': old_digest(work['record']), 'carrier': work['carrier_ref'], 'conformance': 'valid'}
            measure('one_work_schema_validation', count, schema)
            measure('graph_build', count, lambda: build(data), output_digest=old_digest)
            def context():
                with patch('measurement_frozen_v2.session.uuid.uuid4', return_value=uuid.UUID(int=1)):
                    session = Session(store, 'product:cyberalchemy-lab', clock=lambda: 1791424453.0)
                result = session.context()
                session.note('isolated benchmark short memory')
                closed = session.close()
                if not closed['short_memory_erased'] or session.memory or session.pack is not None:
                    raise RuntimeError('session memory retained')
                return {'pack': result, 'closed': closed}
            measure('session_context_and_close', count, context, output_digest=old_digest)
    elapsed = time.monotonic() - started
    replay = [r for r in results if r['operation'] == 'full_replay']
    captured_files = [protocol_path, Path(__file__).resolve()]
    captured_files += [p for p in (LEGACY / 'lab_runtime').glob('*.py')]
    receipt = {'schema_version': 'lab-replay-measurement/v1-candidate', 'authority_effect': 'none', 'task': 'C03', 'result': 'PASS',
        'protocol_binding': {'path': protocol_path.relative_to(REPO).as_posix(), 'sha256': byte_digest(protocol_path.read_bytes())},
        'duration_seconds': elapsed, 'environment': {'python': sys.version, 'platform': platform.platform(), 'processor': platform.processor()},
        'source_cut': initial['expected_cut'], 'source_snapshot_digest': initial['snapshot_digest'],
        'source_materials': len(initial['materials']), 'source_bytes': sum(len(v) for v in raw_contents.values()),
        'source_profile_sha256': initial['source_profile_sha256'], 'results': results,
        'cache_recommendation': 'Measure process-local full-verifier reuse against these baseline costs in C06. Keep full byte/approval/source bindings; no persistent checkpoint trust is justified here.',
        'replay_cost_growth': {'transaction_counts': [r['transaction_count'] for r in replay], 'mean_seconds': [r['mean_seconds'] for r in replay]},
        'threshold_failures': [], 'isolated_local_test_transactions': sum(protocol['transaction_counts']),
        'real_operational_stores_provisioned': 0, 'repository_admissions_applied': 0,
        'scope': 'Per-operation bounded candidate/frozen-v2 measurements; fixed session inputs; not a Product SLA, genuine work episode or pilot.',
        'source_files': [{'path': p.relative_to(REPO).as_posix(), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in captured_files]}
    out = PACKAGE / 'receipts/replay-measurement.json'
    if out.exists():
        raise RuntimeError('measurement receipt already exists; choose a new evidence version')
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    signal.setitimer(signal.ITIMER_REAL, 0)
    (ATTEMPT / 'result.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'result': 'PASS', 'operations_measured': len(results), 'samples': len(results) * sample_count,
                      'duration_seconds': elapsed, 'receipt': out.relative_to(REPO).as_posix()}), flush=True)


if __name__ == '__main__':
    try:
        main()
    except BaseException as exc:
        signal.setitimer(signal.ITIMER_REAL, 0)
        if ATTEMPT is not None:
            failure = {'schema_version': 'lab-measurement-failure/v1-candidate', 'authority_effect': 'none',
                'task': 'C03', 'result': 'FLAG', 'task_complete': False,
                'phase': dict(ACTIVE_PHASE), 'elapsed_seconds': time.monotonic() - STARTED,
                'error_type': type(exc).__name__, 'error': str(exc),
                'completed_results': ACTIVE_RESULTS, 'protocol': PROTOCOL,
                'event_log_sha256': byte_digest((ATTEMPT / 'events.jsonl').read_bytes()) if (ATTEMPT / 'events.jsonl').exists() else None,
                'repository_admissions_applied': 0, 'real_operational_stores_provisioned': 0}
            (ATTEMPT / 'failure.json').write_text(json.dumps(failure, indent=2, sort_keys=True) + '\n')
            print(json.dumps({k: v for k, v in failure.items() if k not in ['completed_results', 'protocol']}, indent=2), flush=True)
        raise
