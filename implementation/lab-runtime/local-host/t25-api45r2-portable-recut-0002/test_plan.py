"""Focused selected-closure and disposable partial-rootfs tests."""

import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import plan


HERE = Path(__file__).resolve().parent


class PortableRecutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (HERE / 'working').mkdir(mode=0o700, exist_ok=True)

    def root(self):
        return tempfile.TemporaryDirectory(prefix='recut-test-', dir=HERE / 'working')

    def tiny(self, base: Path):
        source = base / 'source.txt'
        source.write_bytes(b'cold selected input\n')
        row = {'target': 'rootfs/workspace/code/selected.txt', 'source': str(source),
               'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
               'size_bytes': None, 'mode': 0o644, 'origin': 'repository'}
        selected = {'files': [row], 'omitted_live_authority_rows': 1,
                    'full_api_ready': False, 'authority_effect': 'none'}
        target = base / 'stage'
        target.mkdir(mode=0o700)
        return source, selected, target

    def test_real_metadata_partition_and_absolute_abi_join(self):
        selected = plan.build_plan()
        self.assertEqual(selected['selected_api_rows'], 5265)
        self.assertEqual(selected['absolute_api_rows_satisfied_by_t07'], 625)
        self.assertEqual(selected['omitted_live_authority_rows'], 333)
        self.assertEqual(selected['staged_abi_rows'], 1010)
        self.assertEqual(selected['staged_repository_rows'], 4307)
        self.assertEqual(selected['staged_file_count'], 5317)
        self.assertEqual(selected['repository_source_mode_counts'], {'0600': 456, '0644': 3851})
        self.assertFalse(selected['full_api_ready'])
        self.assertFalse(any(row['target'].startswith('rootfs/workspace/authority/')
                             for row in selected['files']))
        self.assertIn('rootfs/usr/lib/python3.14/__future__.py',
                      {row['target'] for row in selected['files']})

    def test_wrong_inventory_pin_refuses(self):
        with patch.object(plan, 'INVENTORY_SHA', '0' * 64):
            with self.assertRaisesRegex(ValueError, 'selected file bytes differ'):
                plan.build_plan()

    def test_disposable_stage_and_cold_replay_refuse_extra_directory(self):
        with self.root() as name:
            _, selected, target = self.tiny(Path(name))
            result = plan.stage_rows(target, selected)
            self.assertEqual(result['staged_file_count'], 1)
            self.assertFalse(result['full_api_ready'])
            self.assertEqual(plan.verify_package(target / 'package', selected)['status'], 'PASS')
            (target / 'package' / 'rootfs' / 'extra-empty').mkdir(mode=0o700)
            with self.assertRaisesRegex(ValueError, 'file or directory closure differs'):
                plan.verify_package(target / 'package', selected)

    def test_installed_replay_needs_no_original_source_file(self):
        with self.root() as name:
            source, selected, target = self.tiny(Path(name))
            plan.stage_rows(target, selected)
            source.unlink()
            self.assertEqual(plan.verify_package(target / 'package', selected)['status'], 'PASS')

    def test_changed_source_refuses_without_published_package(self):
        with self.root() as name:
            source, selected, target = self.tiny(Path(name))
            source.write_bytes(b'changed input\n')
            with self.assertRaisesRegex(ValueError, 'selected file bytes differ'):
                plan.stage_rows(target, selected)
            self.assertEqual(list(target.iterdir()), [])

    def test_linked_source_refuses_without_published_package(self):
        with self.root() as name:
            source, selected, target = self.tiny(Path(name))
            link = source.parent / 'linked.txt'
            link.symlink_to(source)
            selected['files'][0]['source'] = str(link)
            with self.assertRaises(OSError):
                plan.stage_rows(target, selected)
            self.assertEqual(list(target.iterdir()), [])

    def test_changed_source_mode_refuses_without_published_package(self):
        with self.root() as name:
            source, selected, target = self.tiny(Path(name))
            source.chmod(0o600)
            with self.assertRaisesRegex(ValueError, 'selected file mode differs'):
                plan.stage_rows(target, selected)
            self.assertEqual(list(target.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
