"""Bounded no-effect checks for the selected T31 API46 successor."""

import ast
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-integration-v42-r03-0005-current-0001'
NEW = BASE / 'api-integration-v46-t31-workflow-current-0002'
SCRIPT = Path(__file__).with_name('build_api46.py')
OLD_ID = 'legacy-local-710362c855a8a11c'
NEW_ID = 'legacy-local-ce4d53a6479188a5'
SOURCE_SHA = 'caf4aa1f4dbfcc8a5eab336e15704487f3e1913b8d76bfbcfbd88b56204a0969'
PROFILE_SHA = 'a4a2afdf2853f135a473c19b8dd83dc4cd3b587bc00821a227a4790a365c7402'


def builder():
    spec = importlib.util.spec_from_file_location('_cal_t31_api46_cold', SCRIPT)
    selected = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(selected)
    return selected


def rows(doc):
    return {row['path']: row['sha256'] for row in doc['files']}


def package():
    name = '_cal_api46_t31_cold_test'
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            name, NEW / '__init__.py', submodule_search_locations=[str(NEW)])
        selected = importlib.util.module_from_spec(spec)
        sys.modules[name] = selected
        spec.loader.exec_module(selected)
    return name


class ColdAPI46(unittest.TestCase):
    def test_01_source_profile_rebinding_is_closed(self):
        m = builder()
        old_source = rows(json.loads(m.read_regular(OLD / 'source-manifest.json')))
        new_source = rows(json.loads(m.read_regular(NEW / 'source-manifest.json')))
        old_profile = rows(json.loads(m.read_regular(OLD / 'contract-profile.json')))
        new_profile = rows(json.loads(m.read_regular(NEW / 'contract-profile.json')))
        old_prefix = m.relative(OLD) + '/'
        new_prefix = m.relative(NEW) + '/'
        old_family = m.OLD_FAMILY_PREFIX
        new_family = m.NEW_FAMILY_PREFIX
        self.assertEqual((len(old_source), len(new_source)), (207, 207))
        self.assertEqual((len(old_profile), len(new_profile)), (33424, 33424))
        self.assertEqual(sum(x.startswith(new_prefix) for x in new_source), 201)
        for path, digest in old_source.items():
            selected = new_prefix + path[len(old_prefix):] if path.startswith(old_prefix) else path
            self.assertIn(selected, new_source)
            if selected == path:
                self.assertEqual(new_source[selected], digest)
        self.assertEqual(sum(x.startswith(old_family) for x in old_profile), 20)
        self.assertEqual(sum(x.startswith(new_family) for x in new_profile), 20)
        for path, digest in old_profile.items():
            if path.startswith(old_prefix):
                selected = new_prefix + path[len(old_prefix):]
            elif path.startswith(old_family):
                selected = new_family + path[len(old_family):]
            elif path == m.OLD_SELECTION:
                selected = m.NEW_SELECTION
            else:
                selected = path
            self.assertIn(selected, new_profile)
            if selected == path:
                self.assertEqual(new_profile[selected], digest)
        self.assertFalse(any(OLD_ID in path for path in new_profile))

    def test_02_selected_native_family_preflight(self):
        m = builder()
        selection = m.preflight()
        self.assertEqual(selection['family'], m.relative(m.FAMILY))
        self.assertEqual(selection['source_subjects'], 616)
        self.assertEqual(selection['authority_effect'], 'none')

    def test_03_changed_selection_refused_before_write(self):
        m = builder()
        original = json.loads(m.read_regular(m.SELECTION))
        with tempfile.TemporaryDirectory(prefix='cal-t31-api46-negative-') as temporary:
            p = Path(temporary) / 'selection.json'
            original['family_bindings']['family_context_package_binding'] = '0' * 64
            p.write_text(json.dumps(original))
            m.SELECTION = p
            with self.assertRaisesRegex(ValueError, 'native family binding differs'):
                m.preflight()

    def test_04_linked_selection_ancestor_refused(self):
        m = builder()
        with tempfile.TemporaryDirectory(prefix='cal-t31-api46-link-') as temporary:
            root = Path(temporary)
            (root / 'linked').symlink_to(m.SELECTION.parent, target_is_directory=True)
            m.SELECTION = root / 'linked' / m.SELECTION.name
            with self.assertRaisesRegex(ValueError, 'selected file missing or linked'):
                m.preflight()

    def test_05_receipt_and_rebound_code(self):
        m = builder()
        self.assertEqual(m.sha(NEW / 'source-manifest.json'), SOURCE_SHA)
        self.assertEqual(m.sha(NEW / 'contract-profile.json'), PROFILE_SHA)
        receipt = json.loads(m.read_regular(NEW / 'rebind-receipt.json'))
        self.assertEqual(receipt['successor_manifest_sha256'], SOURCE_SHA)
        self.assertEqual(receipt['successor_profile_binding']['sha256'], PROFILE_SHA)
        self.assertEqual(receipt['authority_effect'], 'none')
        self.assertIsNone(receipt['actual_owner_outcome'])
        self.assertFalse(receipt['current_ReaderChannel_Service_tested'])
        for name in m.REBOUND_FILES:
            raw = m.read_regular(NEW / name)
            self.assertNotIn(OLD_ID.encode(), raw)
            if name.endswith('.py'):
                ast.parse(raw, filename=name)

    def test_06_current_source_and_schema_guard(self):
        name = package()
        guard = __import__(name + '.guard', fromlist=['verify'])
        guard.verify(SOURCE_SHA)
        with self.assertRaises(ValueError):
            guard.verify('0' * 64)
        protocol = __import__(name + '.protocol', fromlist=['Schemas'])
        schemas = protocol.Schemas(PROFILE_SHA)
        self.assertEqual(schemas.profile_sha, PROFILE_SHA)
        with self.assertRaises(ValueError):
            protocol.Schemas('0' * 64)


if __name__ == '__main__':
    unittest.main(verbosity=2)
