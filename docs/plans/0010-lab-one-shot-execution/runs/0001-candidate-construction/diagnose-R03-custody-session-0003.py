"""Actual API19 Session04/05 with method timing only; no line tracing."""
import argparse
import functools
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-v19'
PIN = 'fcd98b74253bc5a7f081faed13c2b4c198df55ff3f6e6772563e1d50a784ff1b'
PROFILE = '67a1302de125dd05a28ac036b6eb183634d76bc43fce777fc9579287fc0313d2'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def guard(pin):
    path = HERE / 'custody-session-diagnostic-source-0003.json'
    assert sha(path.read_bytes()) == pin
    for row in json.loads(path.read_bytes())['files']:
        path = ROOT / row['path']
        assert path.is_file() and not path.is_symlink() and sha(path.read_bytes()) == row['sha256'], row['path']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-sha256', required=True)
    args = parser.parse_args()
    guard(args.source_sha256)
    name = '_cal_raw_session_causal_diagnostic_v3'
    spec = importlib.util.spec_from_file_location(name, API / '__init__.py', submodule_search_locations=[str(API)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)

    def imported(n):
        return __import__(name + '.' + n, fromlist=['*'])

    G = imported('guard')
    G.verify(PIN)
    T = imported('test_custody_sessions')
    T.PROFILE = PROFILE
    F, W, C = imported('example_fixture'), imported('workspace'), imported('custody_context_sessions')
    timings, witnesses, roots = [], [], []
    assert sys.gettrace() is None

    def timer(original, label):
        @functools.wraps(original)
        def run(*positional, **keywords):
            start = time.perf_counter()
            entry = {'method': label, 'result': 'PASS'}
            try:
                return original(*positional, **keywords)
            except Exception as error:
                entry.update(result='FAIL', exception_type=type(error).__name__, message=str(error)[:2000])
                raise
            finally:
                entry['elapsed_seconds'] = time.perf_counter() - start
                W.privacy(entry)
                timings.append(entry)
                print(json.dumps({'method_observation': entry}), flush=True)
        return run

    class Actual(T.Sessions):
        def setUp(self):
            super().setUp()
            roots.append(self.root)
            proof = F.proof(self.key, self.channel.challenge)
            witnesses.append({'public_policy': json.loads(self.policy.read_bytes()), 'signed_nonce_proof': json.loads(proof),
                              'challenge': self.channel.challenge, 'authenticated': self.authenticated})

        def tearDown(self):
            self.diagnostic_journal = [json.loads(p.read_bytes()) for p in self.root.joinpath('workspace/journal').glob('session-*.json')]
            super().tearDown()

    Actual.setUpClass()
    cases = [Actual(n) for n in ['test_04_no_instance_identity_reuse', 'test_05_same_key_no_second_creation']]
    methods = ['view_get', 'open_plan', 'delivery', 'classification', 'connections', 'open', 'persist', 'dispose']
    from contextlib import ExitStack
    try:
        with ExitStack() as wrappers:
            for method in methods:
                original = getattr(C.ContextSessions, method)
                wrappers.enter_context(patch.object(C.ContextSessions, method, timer(original, 'ContextSessions.' + method)))
            result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(cases))
    finally:
        Actual.stack.close()
    assert sys.gettrace() is None
    report = {'schema_version': 'lab-raw-session-method-diagnostic/v1-candidate',
              'result': 'PASS' if result.wasSuccessful() else 'FAIL', 'tests_run': result.testsRun,
              'diagnostic_only': True, 'trace_enabled': False, 'production_source_files_changed': False,
              'original_methods_called_under_timing_wrappers': True, 'source_sha256': PIN, 'profile_sha256': PROFILE,
              'original_test_methods': ['test_04_no_instance_identity_reuse', 'test_05_same_key_no_second_creation'],
              'method_timings': timings, 'actual_wire_events': Actual.events, 'public_witnesses': witnesses,
              'observed_session_journal': [row for case in cases for row in getattr(case, 'diagnostic_journal', [])],
              'owned_hosts_removed': all(not p.exists() for p in roots), 'authority_effect': 'none',
              'actual_owner_outcome': None, 'task_complete': False}
    W.privacy(report)
    assert report['owned_hosts_removed']
    G.verify(PIN)
    guard(args.source_sha256)
    fd = os.open(HERE / 'custody-session-diagnostic-result-0003.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as f:
        json.dump(report, f, indent=2, sort_keys=True)
        f.write('\n')
    print(json.dumps({'result': 'OBSERVED', 'actual_test_result': report['result'], 'tests_run': result.testsRun,
                      'method_observations': len(timings), 'trace_enabled': False, 'owned_hosts_removed': True}), flush=True)


if __name__ == '__main__':
    main()
