"""Bounded source/profile and current workflow-control checks for API48."""

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
OLD = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v47-t31-output-current-0001'
NEW = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v48-t31-workflow-current-0002'
ADAPTER = ROOT / 'implementation/lab-runtime/local-host/t31-api48-workflow-bootstrap-0002/bootstrap.py'
SOURCE_SHA = '54c3c7a5f23cb52d16b14360985015404cc53ef0986d0f12ce31f6a8ee3ab2e6'
PROFILE_SHA = '5f6a745bd768edb0de261bcff201e91e3e775de56d6d9b61f2d6c08fa47650da'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    return {r['path']: r['sha256'] for r in json.loads(path.read_bytes())['files']}


def selected(name):
    spec = importlib.util.spec_from_file_location('_cal_api48_cold.' + name, NEW / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ColdAPI48(unittest.TestCase):
    def test_01_closed_recut_and_receipt(self):
        self.assertEqual(sha(NEW / 'source-manifest.json'), SOURCE_SHA)
        self.assertEqual(sha(NEW / 'contract-profile.json'), PROFILE_SHA)
        old_source, new_source = rows(OLD / 'source-manifest.json'), rows(NEW / 'source-manifest.json')
        old_profile, new_profile = rows(OLD / 'contract-profile.json'), rows(NEW / 'contract-profile.json')
        self.assertEqual((len(old_source), len(new_source)), (208, 208))
        self.assertEqual((len(old_profile), len(new_profile)), (33425, 33425))
        old_prefix = OLD.relative_to(ROOT).as_posix() + '/'
        new_prefix = NEW.relative_to(ROOT).as_posix() + '/'
        self.assertEqual(sum(p.startswith(new_prefix) for p in new_source), 201)
        for path, pin in old_source.items():
            target = new_prefix + path[len(old_prefix):] if path.startswith(old_prefix) else path
            if path == 'implementation/lab-runtime/local-host/t31-api47-output-bootstrap-0002/bootstrap.py':
                target = ADAPTER.relative_to(ROOT).as_posix()
            self.assertIn(target, new_source)
            if target == path:
                self.assertEqual(new_source[target], pin)
        for path, pin in old_profile.items():
            target = new_prefix + path[len(old_prefix):] if path.startswith(old_prefix) else path
            if path == 'implementation/lab-runtime/local-host/t31-api47-output-bootstrap-0002/bootstrap.py':
                target = ADAPTER.relative_to(ROOT).as_posix()
            self.assertIn(target, new_profile)
            if target == path:
                self.assertEqual(new_profile[target], pin)
        receipt = json.loads((NEW / 'rebind-receipt.json').read_bytes())
        self.assertEqual(receipt['actual_workflow_transitions'], 0)
        self.assertEqual(receipt['successor_package'], NEW.relative_to(ROOT).as_posix())
        self.assertEqual(receipt['successor_manifest_sha256'], SOURCE_SHA)
        self.assertEqual(receipt['authority_effect'], 'none')
        self.assertEqual(receipt['successor_source_binding']['sha256'], SOURCE_SHA)
        self.assertEqual(receipt['successor_profile_binding']['sha256'], PROFILE_SHA)

    def test_02_selected_code_and_seven_origins(self):
        for name in ('source_bridge.py', 'auth.py', 'guard.py', 'workflow_output_registry.py'):
            ast.parse((NEW / name).read_bytes(), filename=name)
        registry = (NEW / 'workflow_output_registry.py').read_text()
        self.assertEqual(registry.count(NEW.name + '/workflow_'), 7)
        self.assertNotIn(OLD.name + '/workflow_', registry)
        self.assertEqual(sha(ADAPTER), '180d86bd99021298d13bb1cbd01d6695836131aaed02460c511b90d90b75aa8d')

    def test_03_current_and_historical_source_control(self):
        bridge = selected('source_bridge')
        current = bridge.current_workflow_bindings()
        self.assertEqual(current['source_binding']['sha256'], '0dc869f614e4d1f4be29c4b85f60dd5abd8f25b9fe84e1dc779932aee90c50d4')
        self.assertEqual(current['package_binding']['sha256'], '7006fd4fac3327b76f4ffcc03d93ffb070bb25288ca7bab7e7e5b20470baf22c')
        self.assertEqual(current['adapter_binding']['sha256'], 'b3461a1e68a5da06ad6c47966eb4ed448e67f2318baf5e7e956937d15f007877')
        historical = bridge.workflow_bindings()
        self.assertEqual(historical['source_binding']['sha256'], bridge.WORKFLOW_SOURCE_PIN)
        self.assertNotEqual(current, historical)


if __name__ == '__main__':
    unittest.main(verbosity=2)
