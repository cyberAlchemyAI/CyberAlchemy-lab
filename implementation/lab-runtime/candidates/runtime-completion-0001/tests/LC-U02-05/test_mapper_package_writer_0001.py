"""Owned /tmp filesystem tests only; no builder, Bubblewrap or native run."""
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest import mock

from t35_external_v1.phase_scoped_v2 import mapper_package_writer_0001 as writer
from t35_external_v1.phase_scoped_v2 import mapper_package_plan_0002 as plan


SOURCE = {'path': plan.FAMILY + '/mapped/source-manifest.json',
          'sha256': 'a' * 64}


class MapperPackageWriterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(
            prefix='lc-u02-05-mapper-writer-', dir='/tmp')
        self.addCleanup(self.tmp.cleanup)
        self.scratch = Path(self.tmp.name)
        self.mapped = self.scratch / 'output/legacy-fixture-source/mapped'
        self.mapped.mkdir(parents=True, mode=0o700)
        for path in (self.scratch, self.scratch / 'output',
                     self.mapped.parent, self.mapped):
            path.chmod(0o700)

    @staticmethod
    def manifest(hashes):
        value = {
            'schema_version': 'lab-mapped-context-package/v1-candidate',
            'files': [{'path': plan.PACKAGE + '/' + name,
                       'sha256': hashes[name]}
                      for name in sorted(set(writer.SCHEDULE) - {'manifest.json'})],
            'source_manifest_binding': SOURCE,
            'authority_effect': 'none', 'actual_owner_outcome': None,
        }
        return (json.dumps(value, indent=2, sort_keys=True,
                           ensure_ascii=False, allow_nan=False) + '\n').encode()

    def new_family(self):
        root = Path(tempfile.mkdtemp(
            prefix='lc-u02-05-mapper-writer-', dir='/tmp'))
        self.addCleanup(lambda p=root: __import__('shutil').rmtree(p))
        mapped = root / 'output/legacy-fixture-source/mapped'
        mapped.mkdir(parents=True, mode=0o700)
        for path in (root, root / 'output', mapped.parent, mapped):
            path.chmod(0o700)
        return root, mapped

    def test_complete_55_leaf_package_and_no_retry(self):
        with writer.PackageWriter(self.mapped, SOURCE) as owned:
            for name in writer.SCHEDULE:
                raw = self.manifest(owned.hashes) if name == 'manifest.json' else \
                      (name + '\n').encode()
                receipt = owned.emit(name, raw)
                self.assertTrue(receipt['durable_observed'])
            result = owned.finish()
            self.assertEqual(result['leaf_count'], 55)
            self.assertEqual(result['manifest_row_count'], 54)
            self.assertTrue(result['scratch_retained'])
            self.assertFalse(owned.unknown)
            with self.assertRaises(writer.Refusal):
                owned.emit('manifest.json', b'again')
        self.assertTrue((self.scratch / writer.ATTEMPT).is_file())
        self.assertEqual(len(list((self.mapped / 'packages/0001').rglob('*'))), 57)
        with self.assertRaises(writer.Refusal):
            writer.PackageWriter(self.mapped, SOURCE)

    def test_umask_is_corrected_on_owned_inodes(self):
        for mode in (0o000, 0o077, 0o777):
            with self.subTest(umask=oct(mode)):
                root, mapped = self.new_family()
                old = os.umask(mode)
                try:
                    with writer.PackageWriter(mapped, SOURCE) as owned:
                        owned.emit(writer.SCHEDULE[0], b'x')
                        package = mapped / 'packages/0001'
                        self.assertEqual(stat.S_IMODE(package.stat().st_mode), 0o700)
                        self.assertEqual(stat.S_IMODE((package / 'semantic').stat().st_mode),
                                         0o700)
                        self.assertEqual(stat.S_IMODE((package / writer.SCHEDULE[0]).stat().st_mode),
                                         0o600)
                finally:
                    os.umask(old)

    def test_precreate_collision_and_aliases_refuse(self):
        packages = self.mapped / 'packages'
        packages.symlink_to(self.scratch / 'output')
        with self.assertRaises(writer.Refusal):
            writer.PackageWriter(self.mapped, SOURCE)
        self.assertTrue(packages.is_symlink())
        self.assertFalse((self.scratch / writer.ATTEMPT).exists())

    def test_symlink_hardlink_fifo_and_extra_directory_refuse(self):
        for kind in ('symlink', 'hardlink', 'fifo', 'directory'):
            with self.subTest(kind=kind):
                root, mapped = self.new_family()
                with writer.PackageWriter(mapped, SOURCE) as owned:
                    owned.emit(writer.SCHEDULE[0], b'first')
                    event_dir = mapped / 'packages/0001/semantic'
                    target = event_dir / '00000002.json'
                    if kind == 'symlink':
                        target.symlink_to(event_dir / '00000001.json')
                    elif kind == 'hardlink':
                        os.link(event_dir / '00000001.json', target)
                    elif kind == 'fifo':
                        os.mkfifo(target)
                    else:
                        target.mkdir()
                    with self.assertRaises(writer.Refusal):
                        owned.emit(writer.SCHEDULE[1], b'second')
                    self.assertTrue(owned.unknown)
                    with self.assertRaises(writer.Refusal):
                        owned.emit(writer.SCHEDULE[1], b'retry')
                    self.assertTrue((root / writer.ATTEMPT).exists())

    def test_partial_write_and_parent_fsync_failure_retain_scratch(self):
        with writer.PackageWriter(self.mapped, SOURCE) as owned:
            def partial(fd, raw):
                os.write(fd, raw[:1])
                raise OSError('injected write failure')
            with mock.patch.object(owned, '_write_all', side_effect=partial):
                with self.assertRaises(OSError):
                    owned.emit(writer.SCHEDULE[0], b'longer')
            self.assertTrue(owned.unknown)
            self.assertEqual((self.mapped / 'packages/0001/semantic/00000001.json').read_bytes(),
                             b'l')
            with self.assertRaises(writer.Refusal):
                owned.emit(writer.SCHEDULE[0], b'retry')
            self.assertTrue((self.scratch / writer.ATTEMPT).exists())

        # A second independent scratch exercises the fsync-after-readback path.
        root, mapped = self.new_family()
        with writer.PackageWriter(mapped, SOURCE) as owned:
            real = os.fsync
            def fail_parent(fd):
                if owned.event_fds.get('semantic') == fd:
                    raise OSError('injected parent fsync failure')
                return real(fd)
            with mock.patch.object(writer.os, 'fsync', side_effect=fail_parent):
                with self.assertRaises(OSError):
                    owned.emit(writer.SCHEDULE[0], b'x')
            self.assertTrue(owned.unknown)
            self.assertTrue((mapped / 'packages/0001/semantic/00000001.json').exists())
            self.assertTrue((root / writer.ATTEMPT).exists())

    def test_leaf_fsync_failure_is_unknown_and_not_retried(self):
        with writer.PackageWriter(self.mapped, SOURCE) as owned:
            real = os.fsync
            def fail_leaf(fd):
                row = os.fstat(fd)
                if stat.S_ISREG(row.st_mode) and row.st_size == 1:
                    raise OSError('injected leaf fsync failure')
                return real(fd)
            with mock.patch.object(writer.os, 'fsync', side_effect=fail_leaf):
                with self.assertRaises(OSError):
                    owned.emit(writer.SCHEDULE[0], b'x')
            self.assertTrue(owned.unknown)
            self.assertTrue((self.mapped / 'packages/0001/semantic/00000001.json').exists())
            with self.assertRaises(writer.Refusal):
                owned.emit(writer.SCHEDULE[0], b'x')

    def test_equal_byte_inode_swap_and_directory_detach_refuse(self):
        with writer.PackageWriter(self.mapped, SOURCE) as owned:
            owned.emit(writer.SCHEDULE[0], b'first')
            leaf = self.mapped / 'packages/0001/semantic/00000001.json'
            replacement = leaf.parent / 'replacement'
            replacement.write_bytes(b'first')
            replacement.chmod(0o600)
            os.replace(replacement, leaf)
            with self.assertRaises(writer.Refusal):
                owned.emit(writer.SCHEDULE[1], b'second')
            self.assertTrue(owned.unknown)

        root, mapped = self.new_family()
        with writer.PackageWriter(mapped, SOURCE) as owned:
            packages = mapped / 'packages'
            packages.rename(mapped / 'packages-detached')
            packages.mkdir(mode=0o700)
            with self.assertRaises(writer.Refusal):
                owned.emit(writer.SCHEDULE[0], b'first')
            self.assertTrue(owned.unknown)
            self.assertTrue((root / writer.ATTEMPT).exists())

    def test_manifest_must_bind_54_prior_hashes(self):
        with writer.PackageWriter(self.mapped, SOURCE) as owned:
            for name in writer.SCHEDULE[:-1]:
                owned.emit(name, name.encode())
            raw = self.manifest(owned.hashes)
            changed = json.loads(raw)
            changed['files'][0]['sha256'] = hashlib.sha256(b'wrong').hexdigest()
            bad = (json.dumps(changed, indent=2, sort_keys=True) + '\n').encode()
            with self.assertRaises(writer.Refusal):
                owned.emit('manifest.json', bad)
            self.assertTrue(owned.unknown)
            self.assertFalse((self.mapped / 'packages/0001/manifest.json').exists())


if __name__ == '__main__':
    unittest.main()
