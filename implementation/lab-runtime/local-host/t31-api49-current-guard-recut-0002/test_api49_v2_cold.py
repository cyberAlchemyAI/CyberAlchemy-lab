"""Closed API49 v1 to v2 recut checks without native effects."""

import ast
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
OLD = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v49-t31-output-schema-current-0001'
NEW = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v49-t31-current-guard-0002'
ADAPTER = ROOT / 'implementation/lab-runtime/local-host/t31-api49-current-guard-bootstrap-0002/bootstrap.py'
SOURCE = 'e283b71d9947be8f1dde8ce714664eefd3743fc2f872add5b586fb9bcf86cae1'
PROFILE = 'dc0106126515b58907fa299987c52e9b4afb79ca4c482fb9428f3d12a453cbb5'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rows(path):
    return {r['path']: r['sha256'] for r in json.loads(path.read_bytes())['files']}


class ColdAPI49V2(unittest.TestCase):
    def test_01_source_profile_closed(self):
        self.assertEqual(sha(NEW / 'source-manifest.json'), SOURCE)
        self.assertEqual(sha(NEW / 'contract-profile.json'), PROFILE)
        old_source, new_source = rows(OLD / 'source-manifest.json'), rows(NEW / 'source-manifest.json')
        old_profile, new_profile = rows(OLD / 'contract-profile.json'), rows(NEW / 'contract-profile.json')
        self.assertEqual((len(old_source), len(new_source)), (208, 208))
        self.assertEqual((len(old_profile), len(new_profile)), (33425, 33425))
        old_prefix, new_prefix = OLD.relative_to(ROOT).as_posix() + '/', NEW.relative_to(ROOT).as_posix() + '/'
        old_adapter = 'implementation/lab-runtime/local-host/t31-api49-output-bootstrap-0001/bootstrap.py'
        new_adapter = ADAPTER.relative_to(ROOT).as_posix()
        for predecessor, successor in ((old_source, new_source), (old_profile, new_profile)):
            for path, pin in predecessor.items():
                target = new_prefix + path[len(old_prefix):] if path.startswith(old_prefix) else new_adapter if path == old_adapter else path
                self.assertIn(target, successor)
                if path == target:
                    self.assertEqual(successor[target], pin)

    def test_02_current_guard_and_preserved_historical_branch(self):
        old = (OLD / 'integrated_guard.py').read_text()
        new = (NEW / 'integrated_guard.py').read_text()
        ast.parse(new)
        self.assertIn("source.current_legacy_view(view)", new)
        self.assertIn("source.reader_for_view(view)", new)
        self.assertIn("source.current_workflow_bindings()", new)
        self.assertIn("source.workflow_bindings()", new)
        self.assertIn("'_cal_api_workflow_reader9.inspection'", new)
        self.assertIn("'_cal_api87_integrated_reader7.inspection'", new)
        self.assertNotEqual(old, new)
        receipt = json.loads((NEW / 'rebind-receipt.json').read_bytes())
        self.assertTrue(receipt['current_workflow_guard_replaced'])
        self.assertEqual(receipt['actual_workflow_transitions'], 0)
        self.assertEqual(receipt['authority_effect'], 'none')

    def test_03_output_schema_and_origins_remain_current(self):
        schema = (NEW / 'workflow-output-plan.schema.json').read_text()
        self.assertEqual(schema.count(NEW.relative_to(ROOT).as_posix() + '/service.py'), 2)
        registry = (NEW / 'workflow_output_registry.py').read_text()
        self.assertEqual(registry.count(NEW.name + '/workflow_'), 7)
        self.assertEqual(sha(ADAPTER), '8eb20c56a330cdb05fdaea7287901e6605b252f776aedaf2ebd6ac6d515a0325')


if __name__ == '__main__':
    unittest.main(verbosity=2)
