"""Small installer mechanics tests; the full archive/Docker run is separate."""

import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile


HERE = Path(__file__).resolve().parent
buffer = io.BytesIO()
with zipfile.ZipFile(buffer, 'w') as archive:
    archive.writestr('fixture/selected.txt', b'exact fixture bytes\n')
TINY_CANDIDATE = buffer.getvalue()
spec = importlib.util.spec_from_file_location('t25_public_installer', HERE / 'install.py')
installer = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = installer
spec.loader.exec_module(installer)


class TinyCandidate:
    def extract_verified(self, blob, root):
        if blob != TINY_CANDIDATE:
            raise ValueError('tiny candidate changed')
        target = root / 'fixture' / 'selected.txt'
        target.parent.mkdir(parents=True)
        target.write_bytes(b'exact fixture bytes\n')
        return {'original_members': 363, 'replayed_additions': 799,
                'extracted_fixture_context_verified': True}


class InstallerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.status = installer.selected_code(installer.STATUS_CODE, installer.STATUS_CODE_SHA)
        cls.guard_blob = installer.STATUS_ARCHIVE.read_bytes()
        (HERE / 'working').mkdir(mode=0o700, exist_ok=True)

    def root(self):
        return tempfile.TemporaryDirectory(prefix='installer-test-', dir=HERE / 'working')

    def selected(self):
        return TinyCandidate(), self.status, TINY_CANDIDATE, self.guard_blob

    def test_exact_status_members_and_changed_zip_refusal(self):
        self.assertEqual(installer.historical_inventory(), installer.HISTORICAL_RECONCILIATION_SHA)
        rows = installer.status_members(self.guard_blob, self.status)
        self.assertEqual(len(rows), 9)
        with self.assertRaises(Exception):
            installer.status_members(self.guard_blob[:-1] + b'X', self.status)

    def test_tiny_positive_install_and_cold_replay(self):
        with self.root() as name, patch.object(installer, 'selected_inputs', self.selected), \
             patch.object(installer, 'CANDIDATE_ARCHIVE_SHA', installer.sha(TINY_CANDIDATE)):
            result = installer.install(name)
            self.assertEqual(result['status'], 'PASS')
            self.assertEqual(result['status_guard']['verified_file_count'], 7)
            observed = installer.replay(name)
            self.assertEqual(observed['install_manifest_sha256'], result['install_manifest_sha256'])
            self.assertFalse(observed['original_service_executed'])
            self.assertEqual((Path(name) / 'runtime').stat().st_mode & 0o777, 0o700)
            self.assertEqual((Path(name) / 'runtime/install-manifest.json').stat().st_mode & 0o777,
                             0o600)

    def test_post_install_world_writable_root_refuses_replay(self):
        with self.root() as name, patch.object(installer, 'selected_inputs', self.selected), \
             patch.object(installer, 'CANDIDATE_ARCHIVE_SHA', installer.sha(TINY_CANDIDATE)):
            installer.install(name)
            root = Path(name)
            digest = installer.sha((root / 'runtime/install-manifest.json').read_bytes())
            root.chmod(0o777)
            try:
                with self.assertRaisesRegex(ValueError, 'owned mode-0700 directory'):
                    installer.replay(name)
                self.assertEqual(installer.sha((root / 'runtime/install-manifest.json').read_bytes()),
                                 digest)
            finally:
                root.chmod(0o700)

    def test_post_install_runtime_or_manifest_mode_refuses_replay(self):
        with self.root() as name, patch.object(installer, 'selected_inputs', self.selected), \
             patch.object(installer, 'CANDIDATE_ARCHIVE_SHA', installer.sha(TINY_CANDIDATE)):
            installer.install(name)
            runtime = Path(name) / 'runtime'
            manifest = runtime / 'install-manifest.json'
            runtime.chmod(0o777)
            try:
                with self.assertRaisesRegex(ValueError, 'control mode or owner changed'):
                    installer.replay(name)
            finally:
                runtime.chmod(0o700)
            manifest.chmod(0o644)
            try:
                with self.assertRaisesRegex(ValueError, 'control mode or owner changed'):
                    installer.replay(name)
            finally:
                manifest.chmod(0o600)
            self.assertEqual(installer.replay(name)['status'], 'PASS')

    def test_changed_installed_byte_refuses_cold_replay(self):
        with self.root() as name, patch.object(installer, 'selected_inputs', self.selected), \
             patch.object(installer, 'CANDIDATE_ARCHIVE_SHA', installer.sha(TINY_CANDIDATE)):
            installer.install(name)
            (Path(name) / 'runtime/candidate/fixture/selected.txt').write_bytes(b'changed\n')
            with self.assertRaisesRegex(ValueError, 'installed byte closure changed'):
                installer.replay(name)

    def test_extra_empty_directory_refuses_cold_replay(self):
        with self.root() as name, patch.object(installer, 'selected_inputs', self.selected), \
             patch.object(installer, 'CANDIDATE_ARCHIVE_SHA', installer.sha(TINY_CANDIDATE)):
            installer.install(name)
            (Path(name) / 'runtime/candidate/unselected-empty').mkdir()
            with self.assertRaisesRegex(ValueError, 'installed directory closure differs'):
                installer.replay(name)

    def test_changed_source_archive_refuses_before_install_effect(self):
        def wrong():
            return TinyCandidate(), self.status, TINY_CANDIDATE, self.guard_blob + b'changed'
        with self.root() as name, patch.object(installer, 'selected_inputs', wrong), \
             patch.object(installer, 'CANDIDATE_ARCHIVE_SHA', installer.sha(TINY_CANDIDATE)):
            with self.assertRaisesRegex(ValueError, 'status guard archive bytes changed'):
                installer.install(name)
            self.assertEqual(list(Path(name).iterdir()), [])

    def test_changed_candidate_archive_refuses_before_install_effect(self):
        def wrong():
            return TinyCandidate(), self.status, TINY_CANDIDATE + b'changed', self.guard_blob
        with self.root() as name, patch.object(installer, 'selected_inputs', wrong), \
             patch.object(installer, 'CANDIDATE_ARCHIVE_SHA', installer.sha(TINY_CANDIDATE)):
            with self.assertRaisesRegex(ValueError, 'selected candidate archive bytes changed'):
                installer.install(name)
            self.assertEqual(list(Path(name).iterdir()), [])

    def test_rewritten_manifest_cannot_authorize_changed_candidate(self):
        with self.root() as name, patch.object(installer, 'selected_inputs', self.selected), \
             patch.object(installer, 'CANDIDATE_ARCHIVE_SHA', installer.sha(TINY_CANDIDATE)):
            installer.install(name)
            body = Path(name) / 'runtime/candidate/fixture/selected.txt'
            body.write_bytes(b'changed\n')
            manifest_path = Path(name) / 'runtime/install-manifest.json'
            manifest = json.loads(manifest_path.read_bytes())
            item = next(x for x in manifest['files'] if x['path'] == 'candidate/fixture/selected.txt')
            item['sha256'] = installer.sha(body.read_bytes())
            item['size'] = body.stat().st_size
            manifest_path.write_bytes(installer.encode(manifest))
            with self.assertRaisesRegex(ValueError, 'selected archive bytes'):
                installer.replay(name)

    def test_canonical_extra_manifest_claim_refuses_cold_replay(self):
        with self.root() as name, patch.object(installer, 'selected_inputs', self.selected), \
             patch.object(installer, 'CANDIDATE_ARCHIVE_SHA', installer.sha(TINY_CANDIDATE)):
            installer.install(name)
            manifest_path = Path(name) / 'runtime/install-manifest.json'
            manifest = json.loads(manifest_path.read_bytes())
            manifest['unselected_claim'] = 'owner-approved'
            manifest_path.write_bytes(installer.encode(manifest))
            with self.assertRaisesRegex(ValueError, 'selected archive bytes'):
                installer.replay(name)

    def test_world_writable_root_refuses_before_staging(self):
        with self.root() as name:
            root = Path(name)
            root.chmod(0o777)
            try:
                with patch.object(installer, 'selected_inputs', side_effect=AssertionError('selected too early')):
                    with self.assertRaisesRegex(ValueError, 'mode-0700 directory'):
                        installer.install(root)
                self.assertEqual(list(root.iterdir()), [])
            finally:
                root.chmod(0o700)

    def test_symlinked_ancestor_refuses_before_staging(self):
        with self.root() as name:
            parent = Path(name)
            actual = parent / 'actual'
            child = actual / 'child'
            child.mkdir(parents=True, mode=0o700)
            alias = parent / 'alias'
            alias.symlink_to(actual, target_is_directory=True)
            with patch.object(installer, 'selected_inputs', side_effect=AssertionError('selected too early')):
                with self.assertRaisesRegex(ValueError, 'ancestry is redirected'):
                    installer.install(alias / 'child')
            self.assertEqual(list(child.iterdir()), [])

    def test_dirty_or_linked_root_refuses(self):
        with self.root() as name:
            root = Path(name)
            (root / 'foreign').write_bytes(b'keep')
            with self.assertRaisesRegex(ValueError, 'owned empty mode-0700 directory'):
                installer.clean_root(root)
            self.assertEqual((root / 'foreign').read_bytes(), b'keep')
            link = root.parent / (root.name + '-link')
            link.symlink_to(root, target_is_directory=True)
            try:
                with self.assertRaisesRegex(ValueError, 'ancestry is redirected'):
                    installer.clean_root(link)
            finally:
                link.unlink()


if __name__ == '__main__':
    unittest.main()
