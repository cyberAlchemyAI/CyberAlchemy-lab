"""Actual signed-source scope checks with a new private host for each case."""
import argparse
import base64
import copy
from dataclasses import replace
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest

from . import scope as K

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
SOURCE = HERE / 'source-manifest.json'
API = HERE.parent / 'api-v30'
PIN = '5973db88ae487bda98f8f149776b1d55221fab00986e028aad3b8f2a4e0d39e6'
name = '_cal_fact_scope_actual_api30'
spec = importlib.util.spec_from_file_location(name, API / '__init__.py', submodule_search_locations=[str(API)])
module = importlib.util.module_from_spec(spec);sys.modules[name] = module;spec.loader.exec_module(module)
P = __import__(name + '.protocol', fromlist=['source'])
D = P.source.custody_delivery()


class Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manager = P.source.replay_source('custody-participation')
        cls.view = cls.manager.__enter__();cls.parent = cls.view.custody_signed_sources
        cls.schemas = D.API.Schemas(D.API_PROFILE_PIN)

    @classmethod
    def tearDownClass(cls):
        cls.parent.guard();cls.manager.__exit__(None, None, None)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='cal-R03-fact-scope-check-')
        self.root = Path(self.tmp.name);self.root.chmod(0o700)
        self.policy = self.root / 'permission.json'
        self.key, self.pin = D.provision(self.policy, self.parent)
        self.channel = D.HostChannel(self.policy, self.pin, PIN, self.parent, self.schemas)
        raw = D.wire({'challenge': self.channel.challenge,
                      'signature': base64.b64encode(self.key.sign(D.wire(self.channel.challenge))).decode()})
        self.channel.authenticate(raw)
        self.callback = self.parent.sources.current_guard
        self.check_calls = []
        def checker(pin):
            self.check_calls.append(pin)
            return D.verify_source(pin)
        self.checker = checker

    def tearDown(self):
        self.assertEqual(self.parent.sources.current_guard, self.callback)
        self.channel.close();self.key = None;self.tmp.cleanup()
        self.assertFalse(self.root.exists());self.parent.guard()

    def capture(self):
        return K.read_scope(self.parent, D.EL, self.channel, producer=D,
                            package_checks=[(self.checker, PIN)])

    def test_01_actual_original_facts_and_witnesses(self):
        with self.capture() as snapshot:
            self.assertIs(type(snapshot), D.EL.ExactSources)
            self.assertEqual(set(snapshot.records), set(self.parent.sources.records))
            for original in self.parent.sources.records.values():
                selected, body = snapshot.get(original.artifact)
                self.assertEqual(selected, original)
                self.assertEqual(body, D.EL.parse(original.original))

    def test_02_original_callbacks_are_preserved(self):
        with self.capture() as snapshot:
            self.assertEqual(self.parent.sources.current_guard, self.callback)
            self.assertNotEqual(snapshot.current_guard, self.callback)
            self.assertTrue(K.parent_guard(self.parent))
        self.assertEqual(self.parent.sources.current_guard, self.callback)

    def test_03_package_checks_are_real_at_both_boundaries(self):
        with self.capture():
            self.assertEqual(self.check_calls, [PIN])
            self.assertTrue(K.package_guard(self.parent, self.checker, PIN))
            self.assertEqual(self.check_calls, [PIN])
        self.assertEqual(self.check_calls, [PIN, PIN])

    def test_04_unselected_package_check_is_refused(self):
        with self.capture():
            with self.assertRaisesRegex(ValueError, 'not selected'):
                K.package_guard(self.parent, self.checker, '0' * 64)

    def test_05_snapshot_closed_after_use(self):
        with self.capture() as snapshot:
            snapshot.guard()
        with self.assertRaisesRegex(ValueError, 'closed'):
            snapshot.guard()
        self.assertIsNone(K.active_scope())

    def test_06_header_mutation_refused(self):
        with self.assertRaisesRegex(ValueError, 'records changed'):
            with self.capture() as snapshot:
                next(iter(snapshot.records.values())).artifact['byte_sha256'] = '0' * 64

    def test_07_original_bytes_mutation_refused(self):
        with self.assertRaisesRegex(ValueError, 'records changed'):
            with self.capture() as snapshot:
                key = next(iter(snapshot.records));record = snapshot.records[key]
                snapshot.records[key] = replace(record, original=record.original + b' ')

    def test_08_schema_mutation_refused(self):
        with self.assertRaisesRegex(ValueError, 'schemas or validators changed'):
            with self.capture() as snapshot:
                key = next(iter(snapshot.schemas));schema = snapshot.schemas[key]
                snapshot.schemas[key] = replace(schema, original_schema=schema.original_schema + b' ')

    def test_09_validator_mutation_refused(self):
        with self.assertRaisesRegex(ValueError, 'schemas or validators changed'):
            with self.capture() as snapshot:
                next(iter(snapshot.validators.values())).schema['unknown'] = True

    def test_10_copied_cut_and_scope_mutation_refused(self):
        for field in ['scope_ref', 'source_cut']:
            with self.assertRaisesRegex(ValueError, 'copied scope, cut or callback changed'):
                with self.capture() as snapshot:
                    if field == 'scope_ref':snapshot.scope_ref = 'project:foreign'
                    else:snapshot.source_cut['commit_sha256'] = '0' * 64

    def test_11_revision_witness_mutation_refused(self):
        with self.assertRaisesRegex(ValueError, 'records changed'):
            with self.capture() as snapshot:
                record = next(row for row in snapshot.records.values() if row.revision_witness is not None)
                record.revision_witness.source_cut['commit_sha256'] = '0' * 64

    def test_12_original_source_corruption_refused_at_exit(self):
        original = self.view.data['config']['scope_ref']
        try:
            with self.assertRaises(ValueError):
                with self.capture() as snapshot:
                    self.view.data['config']['scope_ref'] = 'project:owned-test-corruption'
                    row = next(iter(snapshot.records.values()));snapshot.get(row.artifact)
        finally:
            self.view.data['config']['scope_ref'] = original

    def test_13_foreign_host_and_source_refused(self):
        with self.capture():
            with self.assertRaisesRegex(ValueError, 'another host'):
                K.policy_scope(object())
            with self.assertRaisesRegex(ValueError, 'another source'):
                K.parent_guard(object())
            self.assertIs(K.policy_scope(self.channel).producer, D)

    def test_14_threads_do_not_inherit_scope(self):
        result = []
        with self.capture() as snapshot:
            def other_thread():
                result.append(K.active_scope() is None)
                try:snapshot.guard()
                except ValueError:result.append(True)
                else:result.append(False)
            thread = threading.Thread(target=other_thread);thread.start();thread.join(5)
            self.assertFalse(thread.is_alive());self.assertEqual(result, [True, True])

    def test_15_nested_dispatch_and_scope_refused(self):
        with self.capture():
            with self.assertRaisesRegex(ValueError, 'durable effects'):
                K.require_outside_scope()
            with self.assertRaisesRegex(ValueError, 'durable effects'):
                with self.capture():self.fail('nested scope must not enter')
        K.require_outside_scope()

    def test_16_actual_private_host_revocation_is_still_observed(self):
        original = self.policy.read_bytes()
        try:
            with self.assertRaisesRegex(ValueError, 'revoked or changed'):
                with self.capture():
                    self.policy.write_bytes(original + b' ')
                    self.channel.permission()
        finally:
            self.policy.write_bytes(original)

    def test_17_permission_and_fixed_period_are_not_renewed(self):
        period = D.reader.HERE / 'packages/0001/period.json';original = period.read_bytes()
        before = self.channel.permission()
        with self.capture():
            self.assertEqual(self.channel.permission(), before)
            self.assertEqual(period.read_bytes(), original)
            self.assertEqual(self.channel.permission().max_session_seconds, 900)
        self.assertEqual(period.read_bytes(), original)

    def test_18_exception_closes_scope_and_retains_original_guards(self):
        with self.assertRaisesRegex(RuntimeError, 'owned intentional failure'):
            with self.capture() as snapshot:
                raise RuntimeError('owned intentional failure')
        self.assertIsNone(K.active_scope())
        with self.assertRaisesRegex(ValueError, 'closed'):
            snapshot.guard()
        self.parent.guard()


def main():
    parser = argparse.ArgumentParser();parser.add_argument('--source-sha256', required=True)
    args = parser.parse_args()
    require = K.require
    require(hashlib.sha256(SOURCE.read_bytes()).hexdigest() == args.source_sha256,
            'independent fact scope source pin differs')
    manifest = json.loads(SOURCE.read_bytes())
    def guard():
        for row in manifest['files']:
            path = ROOT / row['path']
            require(path.is_file() and not path.is_symlink()
                    and hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'],
                    'fact scope exact input changed ' + row['path'])
    guard()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Checks)
    count = suite.countTestCases();require(count == 18, 'complete selected18fact-scope cases required')
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    guard()
    report = {'schema_version': 'lab-actual-fact-scope-checks/v1-candidate',
              'result': 'PASS' if result.wasSuccessful() and result.testsRun == count else 'FAIL',
              'tests_run': result.testsRun, 'expected_tests': count,
              'failures': len(result.failures), 'errors': len(result.errors),
              'source_sha256': args.source_sha256, 'actual_signed_original_source': True,
              'actual_private_host_nonce_authentication': True,
              'integration_qualified': False, 'current_Agent_qualified': False,
              'task_complete': False, 'goal_complete': False,
              'authority_effect': 'none', 'actual_owner_outcome': None}
    out = HERE / 'receipts/checks-0001.json';out.parent.mkdir(exist_ok=True)
    with out.open('x') as stream:json.dump(report, stream, indent=2, sort_keys=True);stream.write('\n')
    print(json.dumps(report), flush=True)
    raise SystemExit(0 if report['result'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
