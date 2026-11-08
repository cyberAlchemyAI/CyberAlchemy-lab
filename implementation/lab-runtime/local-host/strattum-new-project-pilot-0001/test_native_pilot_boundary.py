"""Verify direct native pilot keeps an uncertain Store and cleans pre-effect setup."""
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import tempfile
from types import SimpleNamespace
import unittest


HERE = Path(__file__).resolve().parent
HELPER = HERE / 'pilot.py'
SOURCE = HERE / 'pilot_native.py'
helper_tree = ast.parse(HELPER.read_bytes())
source_tree = ast.parse(SOURCE.read_bytes())
helper_functions = ast.Module(body=[node for node in helper_tree.body
                                    if isinstance(node, ast.FunctionDef) and node.name in
                                    {'digest', 'write_new', 'write_raw_new'}], type_ignores=[])
run_function = ast.Module(body=[node for node in source_tree.body
                                if isinstance(node, ast.FunctionDef) and node.name in
                                {'run', 'fsync_directory', 'read_native_config'}],
                          type_ignores=[])
EXPECTED_ROOT = Path('/home/vlad_/.local/share/cyberalchemy-lab/strattum-new-project-pilot/api76-build-0003/installation/runtime/repository')
EXPECTED_PACKAGE = 'e4d30e95c73aa6a537f0bb922008955414aabea9d49bc472b395e2d43c350c6e'
EXPECTED_SOURCE = '9b8020f40e37940c5b331138554c9a62e9d3c854e738f4cc06447162f06d7cda'
EXPECTED_PROFILE = 'b0037a7b55b3c94d6713cd21072dcb51ec2617f51c548ae44e0861ce60646184'
EXPECTED_API = 'product/lab/release-candidates/v1/interface/api-integration-v76-current-repairs-0001'


class NativeBoundaryTests(unittest.TestCase):
    def exercise(self, mode):
        holder = {}
        proposal = b'{"proposal_id":"proposal:pilot"}'
        approval = b'{"approval_id":"approval:pilot"}'
        encoded = lambda item: json.dumps(item, sort_keys=True).encode()

        class Store:
            def replay(self, require_current):
                return {'head': {'sequence': 0}}

            def apply(self, proposal, approval):
                raise RuntimeError('native apply uncertain')

        class Fixture:
            def __init__(self, root, schemas):
                holder['private'] = root
                self.service = SimpleNamespace(close=lambda: None)
                self.store = Store()
                self.native = json.loads(proposal)
                self.target_package = {'ref': 'package:pilot-native',
                                       'sha256': hashlib.sha256(proposal).hexdigest()}
                self.approval = {'ref': 'approval:pilot-native',
                                 'sha256': hashlib.sha256(approval).hexdigest()}
                self.memory = {self.target_package['ref']: proposal,
                               self.approval['ref']: approval if mode != 'pre_effect_drift'
                               else b'changed approval'}

        bindings = {'api.source': {'sha256': EXPECTED_SOURCE},
                    'api.profile': {'sha256': EXPECTED_PROFILE}}
        selected = SimpleNamespace(package_pin=EXPECTED_PACKAGE,
                                   package={'entrypoint': {'api_directory': EXPECTED_API}})
        ns = {'Path': Path, 'os': os, 'tempfile': tempfile, 'shutil': shutil,
              'hashlib': hashlib, 'json': json,
              'PICK': SimpleNamespace(require_runtime_ready=lambda: None,
                                      root=lambda: EXPECTED_ROOT,
                                      current=lambda: selected,
                                      binding=lambda name: bindings[name]),
              'P': SimpleNamespace(Schemas=lambda pin: object()),
              'G': SimpleNamespace(encoded=encoded, parse=json.loads),
              'PROJECT': 'project:lab-strattum-feature-gap-pilot',
              'ProjectFixture': Fixture, 'ROOT': HERE.parents[4],
              'EXPECTED_ROOT': EXPECTED_ROOT, 'EXPECTED_PACKAGE': EXPECTED_PACKAGE,
              'EXPECTED_SOURCE': EXPECTED_SOURCE, 'EXPECTED_PROFILE': EXPECTED_PROFILE,
              'EXPECTED_API': EXPECTED_API}
        exec(compile(helper_functions, str(HELPER), 'exec'), ns)
        exec(compile(run_function, str(SOURCE), 'exec'), ns)
        with tempfile.TemporaryDirectory(prefix='cal-native-boundary-test-') as parent:
            out = Path(parent) / 'result'
            if mode == 'foreign_cut':
                selected.package_pin = '0' * 64
                with self.assertRaisesRegex(ValueError, 'foreign installed API76'):
                    ns['run'](out)
                self.assertFalse(out.exists())
                self.assertNotIn('private', holder)
                return
            with self.assertRaises(RuntimeError):
                ns['run'](out)
            private = holder['private']
            if mode == 'pre_effect_drift':
                self.assertFalse(private.exists())
                self.assertFalse((out / 'RECONCILIATION-REQUIRED.json').exists())
            else:
                self.assertTrue(private.exists())
                receipt = json.loads((out / 'RECONCILIATION-REQUIRED.json').read_bytes())
                self.assertEqual(receipt['operation'], 'native-Store.apply')
                self.assertFalse(receipt['retry_allowed'])
                shutil.rmtree(private)

    def test_pre_effect_drift_cleans_store(self):
        self.exercise('pre_effect_drift')

    def test_apply_uncertainty_retains_store(self):
        self.exercise('apply_uncertain')

    def test_foreign_ready_cut_refuses_before_effect(self):
        self.exercise('foreign_cut')

    def test_config_original_read_refuses_symlink(self):
        ns = {'os': os, 'stat': stat, 'Path': Path}
        exec(compile(run_function, str(SOURCE), 'exec'), ns)
        with tempfile.TemporaryDirectory(prefix='cal-native-config-test-') as parent:
            store = Path(parent) / 'native-store'
            store.mkdir()
            original = b'{"public_key":"sample"}\n'
            (store / 'config.json').write_bytes(original)
            self.assertEqual(ns['read_native_config'](parent), original)
            (store / 'config.json').unlink()
            (store / 'outside.json').write_bytes(original)
            (store / 'config.json').symlink_to('outside.json')
            with self.assertRaises(OSError):
                ns['read_native_config'](parent)


if __name__ == '__main__':
    unittest.main(verbosity=2)
