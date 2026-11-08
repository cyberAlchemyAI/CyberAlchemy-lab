"""Bounded read-only API42 source/profile rebinding checks."""

import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-integration-v41-current-source8-0001'
NEW = BASE / 'api-integration-v42-r03-0005-current-0001'
SOURCE = '41aab1ef39fd93c33e2313a19466f4755a8ea14389c1d6abcfdb4ce461be3f50'
PROFILE = '043138382a4f3bc94e7c5ad00c957e6b1f91d0dd80cbb335941ade05ef942e4d'
OLD_ID = 'legacy-local-947e6c2a5b3d10f8'
NEW_ID = 'legacy-local-710362c855a8a11c'


def package():
    name = '_cal_api42_t22_cold_test'
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            name, NEW / '__init__.py', submodule_search_locations=[str(NEW)])
        selected = importlib.util.module_from_spec(spec)
        sys.modules[name] = selected
        spec.loader.exec_module(selected)
    return name


def rows(document):
    return {row['path']: row['sha256'] for row in document['files']}


class ColdRebind(unittest.TestCase):
    def test_01_closed_source_and_profile_diff(self):
        old_source = rows(json.loads((OLD / 'source-manifest.json').read_bytes()))
        new_source = rows(json.loads((NEW / 'source-manifest.json').read_bytes()))
        old_profile = rows(json.loads((OLD / 'contract-profile.json').read_bytes()))
        new_profile = rows(json.loads((NEW / 'contract-profile.json').read_bytes()))
        old_prefix = OLD.relative_to(ROOT).as_posix() + '/'
        new_prefix = NEW.relative_to(ROOT).as_posix() + '/'
        old_family = ('implementation/lab-runtime/local-host/source8-current-fixture/'
                      'instances/' + OLD_ID + '/')
        new_family = ('implementation/lab-runtime/local-host/source8-current-fixture/'
                      'instances/' + NEW_ID + '/')
        old_selection = ('implementation/lab-runtime/local-host/source8-current-fixture/'
                         'selections/' + OLD_ID + '.json')
        new_selection = ('implementation/lab-runtime/local-host/source8-current-fixture/'
                         'selections/' + NEW_ID + '.json')
        self.assertEqual((len(old_source), len(new_source)), (207, 207))
        self.assertEqual((len(old_profile), len(new_profile)), (33424, 33424))
        self.assertEqual(sum(k.startswith(new_prefix) for k in new_source), 201)
        for path, digest in old_source.items():
            selected = new_prefix + path[len(old_prefix):] if path.startswith(old_prefix) else path
            self.assertIn(selected, new_source)
            if not path.startswith(old_prefix):
                self.assertEqual(new_source[selected], digest)
        self.assertEqual(sum(k.startswith(old_family) for k in old_profile), 20)
        self.assertEqual(sum(k.startswith(new_family) for k in new_profile), 20)
        self.assertIn(old_selection, old_profile)
        self.assertIn(new_selection, new_profile)
        for path, digest in old_profile.items():
            if path.startswith(old_prefix):
                selected = new_prefix + path[len(old_prefix):]
            elif path.startswith(old_family):
                selected = new_family + path[len(old_family):]
            elif path == old_selection:
                selected = new_selection
            else:
                selected = path
            self.assertIn(selected, new_profile)
            if selected == path:
                self.assertEqual(new_profile[selected], digest)
        self.assertFalse(any(OLD_ID in path for path in new_profile))

    def test_02_native_chain_release_pin(self):
        spec = importlib.util.spec_from_file_location(
            '_cal_api42_t22_build_cold_test', Path(__file__).with_name('build_api42.py'))
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        builder.preflight()

    def test_03_source_guard_and_wrong_pin(self):
        name = package()
        guard = __import__(name + '.guard', fromlist=['verify'])
        guard.verify(SOURCE)
        with self.assertRaises(ValueError):
            guard.verify('0' * 64)

    def test_04_schema_guard_and_wrong_profile(self):
        name = package()
        protocol = __import__(name + '.protocol', fromlist=['Schemas'])
        selected = protocol.Schemas(PROFILE)
        self.assertEqual(selected.profile_sha, PROFILE)
        with self.assertRaises(ValueError):
            protocol.Schemas('0' * 64)

    def test_05_receipt_and_source_pins(self):
        import hashlib
        sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
        receipt = json.loads((NEW / 'rebind-receipt.json').read_bytes())
        self.assertEqual(sha(NEW / 'source-manifest.json'), SOURCE)
        self.assertEqual(sha(NEW / 'contract-profile.json'), PROFILE)
        self.assertEqual(receipt['successor_package'], NEW.relative_to(ROOT).as_posix())
        self.assertEqual(receipt['successor_manifest_sha256'], SOURCE)
        self.assertEqual(receipt['successor_profile_binding']['sha256'], PROFILE)
        self.assertEqual(receipt['authority_effect'], 'none')
        self.assertIsNone(receipt['actual_owner_outcome'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
