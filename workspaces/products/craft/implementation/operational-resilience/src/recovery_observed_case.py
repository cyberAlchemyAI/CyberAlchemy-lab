"""One bounded instrumented test case; effects belong to temporary test fixtures.

The observer is a separate read-only child. Source tests remain unchanged.
A campaign, freeze and owner decision are deliberately separate callers.
"""
import argparse
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
EVIDENCE = ROOT / 'projects/domainspec-v2/development/completion-dag/v1/evidence'
R07 = EVIDENCE / 'r07-recovery-v1'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run_case(scenario_id, repetition, manifest_sha256, observer_sha256):
    manifest_path = R07 / 'PRODUCT-TEST-MANIFEST.json'
    observer = HERE / 'recovery_test_observer.py'
    if digest(manifest_path) != manifest_sha256 or digest(observer) != observer_sha256:
        raise ValueError('manifest or observer differs from caller-pinned bytes')
    manifest = json.loads(manifest_path.read_text())
    source_path = R07 / 'source-manifest.json'
    if digest(source_path) != manifest['source_manifest_sha256']:
        raise ValueError('source manifest drift')
    sources = json.loads(source_path.read_text())['files']
    def check_sources():
        for entry in sources:
            path = (ROOT / entry['path']).resolve()
            if not path.is_relative_to(ROOT) or digest(path) != entry['sha256']:
                raise ValueError('source drift: ' + entry['path'])
        for name, expected in manifest['harness_files'].items():
            if digest(R07 / name) != expected:
                raise ValueError('harness drift: ' + name)
    check_sources()
    scenarios = json.loads((R07 / 'scenario-map.json').read_text())['scenarios']
    scenario = next(row for row in scenarios if row['scenario_id'] == scenario_id)
    for directory in ['r03-recovery-v1', 'r04-recovery-v1', 'r05-recovery-v1', 'r06-recovery-v1', 'r07-recovery-v1']:
        sys.path.insert(0, str(EVIDENCE / directory))
    records = []
    sequence = 0
    def capture(instance, test_id, phase):
        nonlocal sequence
        sequence += 1
        stores = []
        for attr, role in [('cp', 'coordination'), ('op', 'operation'), ('path', None)]:
            path = getattr(instance, attr, None)
            if isinstance(path, Path):
                actual_role = role or ('operation' if test_id.startswith('test_ledger.') else 'coordination')
                stores.append({'role': actual_role, 'path': str(path)})
        clock = getattr(instance, 'clock', None)
        clock_value = clock() if clock else None
        request = {'schema_version': 'domainspec.orodi.recovery-observer/v1-candidate',
                   'scenario_id': scenario_id, 'repetition': repetition, 'test_id': test_id,
                   'subject_digest': manifest_sha256, 'producer_pid': os.getpid(),
                   'barrier_id': phase, 'sequence': sequence,
                   'clock': {'kind': 'injected' if clock_value else 'not-supplied',
                             'boot_id': clock_value[0] if clock_value else None,
                             'monotonic_value': clock_value[1] if clock_value else None},
                   'fixture_root': instance.tmp.name, 'stores': stores}
        child = subprocess.run([sys.executable, '-B', str(observer)], input=json.dumps(request), capture_output=True, text=True, timeout=5)
        if child.returncode:
            return {'state': 'invalid', 'cause': child.stdout + child.stderr}
        return json.loads(child.stdout)
    for test_id in scenario['tests']:
        module_name, class_name, method = test_id.split('.')
        instance = getattr(importlib.import_module(module_name), class_name)(method)
        record = {'test': test_id}
        setup, teardown = instance.setUp, instance.tearDown
        def before():
            setup()
            # Clean a fixture even if instrumentation fails before unittest teardown.
            instance.addCleanup(instance.tmp.cleanup)
            record['before'] = capture(instance, test_id, 'before-test')
        def after():
            try:
                record['after'] = capture(instance, test_id, 'after-test')
            finally:
                teardown()
        instance.setUp, instance.tearDown = before, after
        stream = io.StringIO()
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(instance)
        record.update(result='PASS' if result.wasSuccessful() and not result.skipped else 'FAIL', tests_run=result.testsRun, raw_output=stream.getvalue())
        records.append(record)
    contract = None
    formation_observations = []
    if scenario['contract_probe']:
        lock = json.loads((EVIDENCE / 'r02-recovery-v1/compiler-lock.json').read_text())
        if digest(Path(lock['node']['path'])) != lock['node']['sha256']:
            raise ValueError('formation runtime drift')
        formation_instance = SimpleNamespace(tmp=SimpleNamespace(name=str(R07)))
        formation_observations.append(capture(formation_instance, 'formation-probe', 'before-formation'))
        child = subprocess.run([lock['node']['path'], str(R07 / 'contracts.mjs'), str(ROOT)], capture_output=True, text=True, timeout=20)
        formation_observations.append(capture(formation_instance, 'formation-probe', 'after-formation'))
        contract = {'exit_code': child.returncode, 'stdout': child.stdout, 'stderr': child.stderr}
    check_sources()
    passed = all(r['result'] == 'PASS' for r in records) and (contract is None or contract['exit_code'] == 0)
    return {'scenario_id': scenario_id, 'repetition': repetition, 'result': 'PASS' if passed else 'FAIL', 'exit_code': 0 if passed else 1,
            'observation': {'scenario_id': scenario_id, 'pid': os.getpid(), 'result': 'PASS' if passed else 'FAIL', 'tests': records, 'contract_probe': contract,
                            'formation_observations': formation_observations, 'process_trace': getattr(sys.modules.get('additional_tests'), 'TRACE', [])},
            'provenance': {'mode': 'fresh-instrumented', 'manifest_sha256': manifest_sha256, 'observer_sha256': observer_sha256,
                           'driver_sha256': digest(Path(__file__)), 'source_manifest_sha256': digest(source_path),
                           'python': sys.version, 'executable_sha256': digest(Path(sys.executable))},
            'authority_effect': 'none'}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--scenario', required=True, choices=[f'R01-F{i:02}' for i in range(1, 31)])
    parser.add_argument('--repetition', type=int, required=True, choices=[1, 2])
    parser.add_argument('--manifest-sha256', required=True)
    parser.add_argument('--observer-sha256', required=True)
    args = parser.parse_args()
    try:
        result = run_case(args.scenario, args.repetition, args.manifest_sha256, args.observer_sha256)
        print(json.dumps(result, sort_keys=True))
        sys.exit(0 if result['result'] == 'PASS' else 1)
    except Exception as error:
        print(json.dumps({'state': 'invalid', 'cause': type(error).__name__ + ': ' + str(error), 'authority_effect': 'none'}))
        sys.exit(2)
