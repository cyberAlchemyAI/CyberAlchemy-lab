"""Real isolated filesystem tests; callbacks/Actors are fixtures, not permission evidence."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('_cal_package_publication', HERE / 'publication.py')
P = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = P
spec.loader.exec_module(P)
fixture_spec = importlib.util.spec_from_file_location('_cal_package_original_fixture', P.TRANSFER / 'test_transfer.py')
F = importlib.util.module_from_spec(fixture_spec)
sys.modules[fixture_spec.name] = F
fixture_spec.loader.exec_module(F)
# Only synthetic fixture construction uses the selected module identity. This
# does not alter any authenticated host/source selection or existing test source.
F.T = P.T


class Publication(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='cal-package-publication-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'owned-exports'
        self.root.mkdir(mode=0o700)
        self.fixture = F.Packages('test_export_preserves_whitespace_and_original_bytes')
        self.fixture.setUp()
        self.archive = self.fixture.export()
        self.archive_binding = P.pin('package:synthetic-filesystem', self.archive)
        self.request_binding = P.pin('request:synthetic-filesystem', b'{"synthetic":true}')
        self.cut, self.scope, self.principal = self.fixture.cut, 'output:synthetic-package', 'principal:synthetic-filesystem'
        self.root_identity = P.identity(self.root.stat())
        self.scope_value = {'schema_version': 'lab-owned-package-root/v1-candidate', 'output_root': str(self.root),
            'output_root_scope_ref': self.scope, 'principal_ref': self.principal,
            'output_root_identity': self.root_identity, 'authority_effect': 'none', 'actual_owner_outcome': None}
        raw = P.encoded(self.scope_value)
        fd = os.open(self.root / '.scope.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
        self.scope_binding = P.pin('scope:synthetic-filesystem', raw)
        self.permission = True
        self.source_current = True
        self.deadline = time.monotonic() + 120
        self.source_calls = 0
        self.permission_calls = 0
        self.host = self.builder()

    def source_guard(self):
        self.source_calls += 1
        P.require(self.source_current, 'fixture source changed')

    def permission_guard(self):
        self.permission_calls += 1
        return self.permission and time.monotonic() < self.deadline

    def builder(self, **changes):
        args = {'root': self.root, 'scope_ref': self.scope, 'root_identity': self.root_identity,
            'scope_binding': self.scope_binding, 'principal_ref': self.principal, 'transfer': self.fixture.engine,
            'source_guard': self.source_guard, 'permission_guard': self.permission_guard,
            'max_output_bytes': P.T.MAX_PACKAGE_BYTES, 'max_generations': 2}
        args.update(changes)
        return P.Publisher(**args)

    def publish(self, **options):
        return self.host.publish(self.archive, self.archive_binding, self.request_binding, self.cut, **options)

    def generation(self):
        dirs = list(self.root.glob('pkg-*'))
        self.assertEqual(len(dirs), 1)
        return dirs[0]

    def attributes(self):
        return {p.relative_to(self.root).as_posix(): (p.stat().st_ino, p.stat().st_size, p.stat().st_mtime_ns, p.stat().st_ctime_ns)
                for p in self.root.rglob('*')}

    def test_real_exact_package_published(self):
        result = self.publish()
        self.assertEqual(result['posture'], 'published')
        self.assertEqual((self.generation() / 'package.json').read_bytes(), self.archive)
        self.assertFalse(result['canonical_replay_source'])
        self.assertFalse(result['unmanaged_files_overwritten'])
        self.assertFalse(result['recovery_required'])
        self.assertEqual(result['output_bindings'][0]['size_bytes'], len(self.archive))
        self.assertGreaterEqual(self.source_calls, 4)
        self.assertGreaterEqual(self.permission_calls, 4)

    def test_readonly_retry_preserves_every_managed_file(self):
        first = self.publish()
        before = self.attributes()
        second = self.publish(existing_only=True)
        self.assertEqual(first, second)
        self.assertEqual(before, self.attributes())

    def test_same_generation_never_rewritten(self):
        self.publish()
        before = self.attributes()
        self.publish()
        self.assertEqual(before, self.attributes())

    def test_retry_absent_generation_never_writes(self):
        with self.assertRaises(P.RecoveryRequired):
            self.publish(existing_only=True)
        self.assertEqual(list(self.root.iterdir()), [self.root / '.scope.json'])

    def test_tampered_package_refused_without_rewrite(self):
        self.publish()
        path = self.generation() / 'package.json'
        path.write_bytes(b'{}')
        before = self.attributes()
        with self.assertRaises(P.RecoveryRequired):
            self.publish(existing_only=True)
        self.assertEqual(path.read_bytes(), b'{}')
        self.assertEqual(before, self.attributes())

    def test_tampered_marker_refused(self):
        self.publish()
        (self.generation() / 'PUBLISHED.json').write_bytes(b'{}')
        with self.assertRaises(P.RecoveryRequired):
            self.publish(existing_only=True)

    def test_tampered_manifest_refused(self):
        self.publish()
        (self.generation() / 'manifest.json').write_bytes(b'{}')
        with self.assertRaises(P.RecoveryRequired):
            self.publish(existing_only=True)

    def test_tampered_receipt_refused(self):
        self.publish()
        (self.generation() / 'receipt.json').write_bytes(b'{}')
        with self.assertRaises(P.RecoveryRequired):
            self.publish(existing_only=True)

    def test_missing_marker_is_uncertain_without_repair(self):
        self.publish()
        (self.generation() / 'PUBLISHED.json').unlink()
        before = self.attributes()
        with self.assertRaises(P.RecoveryRequired):
            self.publish()
        self.assertEqual(before, self.attributes())

    def test_interrupted_write_preserved_for_reconciliation(self):
        original = P.write
        def broken(fd, name, raw):
            if name == 'manifest.json':
                raise OSError('synthetic injected filesystem failure')
            return original(fd, name, raw)
        with patch.object(P, 'write', broken), self.assertRaises(P.RecoveryRequired):
            self.publish()
        self.assertEqual((self.generation() / 'package.json').read_bytes(), self.archive)
        self.assertFalse((self.generation() / 'PUBLISHED.json').exists())
        before = self.attributes()
        with self.assertRaises(P.RecoveryRequired):
            self.publish()
        self.assertEqual(before, self.attributes())

    def test_permission_denied_before_claim_leaves_no_generation(self):
        self.permission = False
        with self.assertRaises(ValueError):
            self.publish()
        self.assertFalse(list(self.root.glob('pkg-*')))

    def test_source_changed_before_claim_leaves_no_generation(self):
        self.source_current = False
        with self.assertRaises(ValueError):
            self.publish()
        self.assertFalse(list(self.root.glob('pkg-*')))

    def test_deadline_expired_before_claim(self):
        self.deadline = time.monotonic() - 1
        with self.assertRaises(ValueError):
            self.publish()
        self.assertFalse(list(self.root.glob('pkg-*')))

    def test_permission_revoked_before_marker(self):
        def permission():
            self.permission_calls += 1
            return self.permission_calls < 3
        self.host = self.builder(permission_guard=permission)
        with self.assertRaises(P.RecoveryRequired):
            self.publish()
        self.assertFalse((self.generation() / 'PUBLISHED.json').exists())

    def test_source_changed_before_marker(self):
        def source():
            self.source_calls += 1
            P.require(self.source_calls < 3, 'synthetic late source change')
        self.host = self.builder(source_guard=source)
        with self.assertRaises(P.RecoveryRequired):
            self.publish()
        self.assertFalse((self.generation() / 'PUBLISHED.json').exists())

    def test_late_denial_requires_readonly_recovery(self):
        def permission():
            self.permission_calls += 1
            return self.permission_calls < 4
        self.host = self.builder(permission_guard=permission)
        with self.assertRaises(P.RecoveryRequired):
            self.publish()
        self.assertTrue((self.generation() / 'PUBLISHED.json').exists())
        before = self.attributes()
        self.host = self.builder()
        self.assertEqual(self.publish(existing_only=True)['posture'], 'published')
        self.assertEqual(before, self.attributes())

    def test_generation_count_budget(self):
        self.host = self.builder(max_generations=1)
        self.publish()
        self.request_binding = P.pin('request:another', b'{"another":true}')
        with self.assertRaises(ValueError):
            self.publish()
        self.assertEqual(len(list(self.root.glob('pkg-*'))), 1)

    def test_output_byte_budget_before_claim(self):
        self.host = self.builder(max_output_bytes=len(self.archive) - 1)
        with self.assertRaises(ValueError):
            self.publish()
        self.assertFalse(list(self.root.glob('pkg-*')))

    def test_source_cut_mismatch_before_claim(self):
        self.cut = {**self.cut, 'commit_sequence': 2}
        with self.assertRaises(ValueError):
            self.publish()
        self.assertFalse(list(self.root.glob('pkg-*')))

    def test_original_package_hash_mismatch_before_claim(self):
        self.archive_binding = {**self.archive_binding, 'sha256': '0' * 64}
        with self.assertRaises(ValueError):
            self.publish()
        self.assertFalse(list(self.root.glob('pkg-*')))

    def test_manifest_hash_mismatch_before_claim(self):
        self.host = self.builder(scope_binding={**self.scope_binding, 'sha256': '0' * 64})
        with self.assertRaises(ValueError):
            self.publish()
        self.assertFalse(list(self.root.glob('pkg-*')))

    def test_root_identity_mismatch_before_claim(self):
        self.host = self.builder(root_identity={**self.root_identity, 'inode': self.root_identity['inode'] + 1})
        with self.assertRaises(ValueError):
            self.publish()
        self.assertFalse(list(self.root.glob('pkg-*')))

    def test_scope_manifest_principal_mismatch_before_claim(self):
        self.host = self.builder(principal_ref='principal:another')
        with self.assertRaises(ValueError):
            self.publish()
        self.assertFalse(list(self.root.glob('pkg-*')))

    def test_unmanaged_root_entry_preserved(self):
        path = self.root / 'unmanaged.txt'
        path.write_bytes(b'keep this fixture')
        with self.assertRaises(ValueError):
            self.publish()
        self.assertEqual(path.read_bytes(), b'keep this fixture')
        self.assertFalse(list(self.root.glob('pkg-*')))

    def test_unmanaged_generation_entry_preserved(self):
        self.publish()
        path = self.generation() / 'unmanaged.txt'
        path.write_bytes(b'keep this fixture')
        with self.assertRaises(P.RecoveryRequired):
            self.publish(existing_only=True)
        self.assertEqual(path.read_bytes(), b'keep this fixture')

    def test_symlink_root_refused(self):
        link = Path(self.temp.name) / 'link'
        link.symlink_to(self.root, target_is_directory=True)
        self.host = self.builder(root=link)
        with self.assertRaises(OSError):
            self.publish()
        self.assertFalse(list(self.root.glob('pkg-*')))

    def test_symlink_package_refused(self):
        self.publish()
        path = self.generation() / 'package.json'
        path.unlink()
        path.symlink_to(self.root / '.scope.json')
        before = (self.root / '.scope.json').read_bytes()
        with self.assertRaises(P.RecoveryRequired):
            self.publish(existing_only=True)
        self.assertEqual((self.root / '.scope.json').read_bytes(), before)

    def test_hardlink_package_refused(self):
        self.publish()
        path = self.generation() / 'package.json'
        os.link(path, Path(self.temp.name) / 'second-name')
        with self.assertRaises(P.RecoveryRequired):
            self.publish(existing_only=True)

    def test_nonprivate_managed_file_refused(self):
        self.publish()
        os.chmod(self.generation() / 'package.json', 0o644)
        with self.assertRaises(P.RecoveryRequired):
            self.publish(existing_only=True)

    def test_nonprivate_root_refused(self):
        os.chmod(self.root, 0o755)
        with self.assertRaises(ValueError):
            self.publish()

    def test_nonprivate_generation_refused(self):
        self.publish()
        os.chmod(self.generation(), 0o755)
        with self.assertRaises(P.RecoveryRequired):
            self.publish(existing_only=True)

    def test_fifo_package_refused_without_blocking(self):
        self.publish()
        path = self.generation() / 'package.json'
        path.unlink()
        os.mkfifo(path, 0o600)
        with self.assertRaises(P.RecoveryRequired):
            self.publish(existing_only=True)

    def test_large_package_publication_keeps_original_byte_size(self):
        self.fixture.change_dependency(P.T.encoded({'public': 'x' * (P.T.MAX_BYTES + 1)}), 'json-utf8')
        self.fixture.contract['maximum_package_bytes'] = P.T.MAX_PACKAGE_BYTES
        self.fixture.sync_export_controls()
        self.archive = self.fixture.export()
        self.archive_binding = P.pin('package:synthetic-large-filesystem', self.archive)
        receipt = self.publish()
        self.assertGreater(len(self.archive), P.T.MAX_BYTES)
        self.assertEqual((self.generation() / 'package.json').read_bytes(), self.archive)
        self.assertEqual(receipt['output_bindings'][0]['size_bytes'], len(self.archive))
        self.assertLess(len(P.encoded(receipt)), P.T.MAX_BYTES)
        self.assertEqual(self.publish(existing_only=True), receipt)
