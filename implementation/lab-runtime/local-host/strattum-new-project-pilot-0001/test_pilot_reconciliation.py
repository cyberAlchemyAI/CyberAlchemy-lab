"""Exercise Project pilot cleanup across governance uncertainty boundaries."""
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
import unittest


SOURCE = Path(__file__).with_name('pilot.py')
tree = ast.parse(SOURCE.read_bytes())
functions = ast.Module(body=[node for node in tree.body
                             if isinstance(node, ast.FunctionDef) and node.name in
                             {'digest', 'write_new', 'write_raw_new', 'run'}], type_ignores=[])


class PilotReconciliationTests(unittest.TestCase):
    def exercise(self, mode):
        holder = {}

        class Service:
            def __init__(self):
                self.calls = 0

            def call(self, raw):
                self.calls += 1
                if mode == 'checkpoint_refusal' or (mode == 'admission_refusal' and self.calls == 2):
                    return {'kind': 'refusal', 'message': {'code': 'indeterminate'}}
                return {'kind': 'result', 'message': {}}

            def close(self):
                holder['closed'] = True

        class Fixture:
            def __init__(self, root, schemas):
                holder['private'] = root
                if mode == 'preflight_failure':
                    raise ValueError('preflight failed')
                self.service = Service()
                self.host = SimpleNamespace(object=lambda raw: self.binding(raw))
                self.resolution = {'selected_outcome': 'approve-exact-effect'}

            def binding(self, raw):
                if mode == 'post_checkpoint_local_failure':
                    raise ValueError('local binding failed')
                return {'ref': 'resolution:mock', 'sha256': hashlib.sha256(raw).hexdigest()}

            def checkpoint_call(self, key):
                return {'operation': 'checkpoint.resolve', 'key': key}

            def admission_call(self, binding, key):
                return {'operation': 'admission.apply', 'key': key}

        encoded = lambda value: json.dumps(value, sort_keys=True).encode()
        ns = {'Path': Path, 'os': os, 'tempfile': tempfile, 'shutil': shutil,
              'hashlib': hashlib, 'json': json, 'PROJECT': 'project:lab-strattum-feature-gap-pilot',
              'ProjectFixture': Fixture, 'ROOT': SOURCE.parents[4],
              'PICK': SimpleNamespace(binding=lambda name: {'sha256': '0' * 64}),
              'P': SimpleNamespace(Schemas=lambda pin: object(), compact=lambda item: encoded(item)),
              'G': SimpleNamespace(encoded=encoded)}
        exec(compile(functions, str(SOURCE), 'exec'), ns)
        with tempfile.TemporaryDirectory(prefix='cal-pilot-reconciliation-test-') as parent:
            output = Path(parent) / 'result'
            with self.assertRaises((RuntimeError, ValueError)):
                ns['run'](output)
            private = holder['private']
            if mode == 'preflight_failure':
                self.assertFalse(private.exists())
                self.assertFalse((output / 'RECONCILIATION-REQUIRED.json').exists())
            else:
                self.assertTrue(private.is_dir(), 'uncertain operation lost private Store')
                receipt = json.loads((output / 'RECONCILIATION-REQUIRED.json').read_bytes())
                self.assertFalse(receipt['retry_allowed'])
                self.assertEqual(receipt['last_started_operation'],
                                 'admission.apply' if mode == 'admission_refusal' else 'checkpoint.resolve')
                self.assertEqual(receipt['checkpoint_result_observed'],
                                 mode != 'checkpoint_refusal')
                self.assertEqual(receipt['idempotency_key'],
                                 'pilot:admission' if mode == 'admission_refusal' else 'pilot:checkpoint')
                shutil.rmtree(private)

    def test_preflight_cleans_store(self):
        self.exercise('preflight_failure')

    def test_checkpoint_uncertainty_retains_store(self):
        self.exercise('checkpoint_refusal')

    def test_local_error_after_checkpoint_retains_store(self):
        self.exercise('post_checkpoint_local_failure')

    def test_admission_uncertainty_retains_store(self):
        self.exercise('admission_refusal')


if __name__ == '__main__':
    unittest.main(verbosity=2)
