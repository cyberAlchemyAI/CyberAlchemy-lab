"""Public-only portable closure tests; no actual Reader or private archive."""
import datetime as dt
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import portable as p

NOW=dt.datetime(2026,10,20,18,30,tzinfo=dt.timezone.utc)

class PortableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle_tmp=tempfile.TemporaryDirectory(
            prefix='fixture-portable-bundle-',dir=p.FAMILY)
        cls.stage_tmp=tempfile.TemporaryDirectory(
            prefix='fixture-portable-stage-',dir=p.FAMILY)
        cls.bundle=Path(cls.bundle_tmp.name)/'bundle'
        cls.stage=Path(cls.stage_tmp.name)/'root'
        cls.result=p.publish(cls.bundle,NOW)
        p.materialize_synthetic_stage(cls.bundle,p.BUNDLE_MANIFEST_SHA,cls.stage)

    @classmethod
    def tearDownClass(cls):
        cls.stage_tmp.cleanup()
        cls.bundle_tmp.cleanup()

    def test_exact_owner_only_bundle_and_no_private_archive(self):
        audited=p.audit_bundle(self.bundle)
        self.assertEqual(audited['blobs'],105)
        self.assertEqual(self.result['manifest_sha256'],p.BUNDLE_MANIFEST_SHA)
        self.assertEqual(self.bundle.stat().st_mode&0o777,0o700)
        self.assertEqual((self.bundle/'manifest.json').stat().st_mode&0o777,0o600)
        manifest=p.parse((self.bundle/'manifest.json').read_bytes())
        self.assertEqual(len(manifest['source_manifest']['files']),940)
        self.assertEqual(len(manifest['reader_rows']),948)
        self.assertNotIn('branch.snapshot',str(manifest['code']))
        self.assertNotIn('branch.snapshot',str(manifest['metadata']))
        self.assertFalse(any(path.name=='branch.snapshot'
                             for path in self.stage.rglob('*')))

    def test_synthetic_stage_loads_original_reader_from_buffers(self):
        loader,capture,manifest=p.reconstruct(
            self.bundle,p.BUNDLE_MANIFEST_SHA,self.stage,
            Path('/usr/lib/python3/dist-packages'))
        with loader.checked_modules(capture) as (reader,finder):
            self.assertEqual(reader.SelectedReader.__module__,loader.READER_NAME+'.reader')
            names=[name for name,_,_ in finder.executed]
            self.assertGreaterEqual(len(names),13)
            self.assertIn(loader.SOURCE_NAME,names)
            self.assertIn(loader.ENGINE_LOADER_NAME,names)
            self.assertIn(loader.BRIDGE_NAME,names)
        self.assertEqual(manifest['private_archive'],'NOT_COPIED')

    def test_bundle_only_cannot_construct_original_reader(self):
        loader,capture,_=p.reconstruct(
            self.bundle,p.BUNDLE_MANIFEST_SHA,self.stage,
            Path('/usr/lib/python3/dist-packages'))
        with loader.checked_modules(capture) as (reader,_finder):
            with self.assertRaises(FileNotFoundError) as caught:
                reader.SelectedReader(loader.READER_MANIFEST_SHA,
                                      capture.selected['reader']['source_manifest_sha256'],
                                      capture.selected['reader']['source_package_manifest_sha256'])
        self.assertEqual(Path(caught.exception.filename).name,'source-manifest.json')
        self.assertTrue(str(caught.exception.filename).startswith(str(self.stage)))

    def test_blob_drift_and_missing_synthetic_marker_refuse(self):
        with self.assertRaisesRegex(p.Refused,'BUNDLE_MANIFEST_NOT_SELECTED'):
            p.reconstruct(self.bundle,'0'*64,self.stage,
                          Path('/usr/lib/python3/dist-packages'))
        blob=self.bundle/'blobs'/p.LOADER_CODE_SHA
        original=blob.read_bytes()
        try:
            blob.write_bytes(b'forged loader buffer')
            with self.assertRaisesRegex(p.Refused,'PIN_DRIFT'):
                p.audit_bundle(self.bundle)
        finally:blob.write_bytes(original)
        with self.assertRaises(FileNotFoundError):
            p.reconstruct(self.bundle,p.BUNDLE_MANIFEST_SHA,
                          Path(self.stage_tmp.name)/'missing',
                          Path('/usr/lib/python3/dist-packages'))

    def test_predecessor_hold_is_explicit_and_all_authority_refuses(self):
        manifest=p.parse((self.bundle/'manifest.json').read_bytes())
        self.assertEqual(manifest['plan_hold_review_sha256'],p.PLAN_REVIEW_SHA)
        self.assertEqual(p.reviewed_loader().EFFECT_ENABLED,False)
        for fn in (p.open_real_signed,p.issue_auth):
            with self.assertRaisesRegex(p.Refused,'EFFECT_DISABLED'):
                fn()

    def test_extra_root_file_and_symlink_refuse(self):
        extra=self.bundle/'unexpected'
        try:
            extra.write_bytes(b'public extra')
            with self.assertRaisesRegex(p.Refused,'BUNDLE_EXACT_ROOT_TREE'):
                p.audit_bundle(self.bundle)
        finally:extra.unlink()
        try:
            extra.symlink_to(self.bundle/'manifest.json')
            with self.assertRaisesRegex(p.Refused,'BUNDLE_EXACT_ROOT_TREE'):
                p.audit_bundle(self.bundle)
        finally:extra.unlink()

    def test_blob_mode_0644_and_extra_blob_refuse(self):
        blob=self.bundle/'blobs'/p.LOADER_CODE_SHA
        try:
            blob.chmod(0o644)
            with self.assertRaisesRegex(p.Refused,'BUNDLE_EXACT_BLOB_SET_AND_MODE'):
                p.audit_bundle(self.bundle)
        finally:blob.chmod(0o600)
        extra=self.bundle/'blobs'/('0'*64)
        try:
            extra.write_bytes(b'public extra')
            with self.assertRaisesRegex(p.Refused,'BUNDLE_EXACT_BLOB_SET_AND_MODE'):
                p.audit_bundle(self.bundle)
        finally:extra.unlink()

    def test_manifest_and_directory_modes_refuse(self):
        manifest=self.bundle/'manifest.json'
        try:
            manifest.chmod(0o644)
            with self.assertRaisesRegex(p.Refused,'BUNDLE_EXACT_ROOT_TREE'):
                p.audit_bundle(self.bundle)
        finally:manifest.chmod(0o600)
        blobs=self.bundle/'blobs'
        try:
            blobs.chmod(0o755)
            with self.assertRaisesRegex(p.Refused,'BUNDLE_DIRECTORY_CUSTODY'):
                p.audit_bundle(self.bundle)
        finally:blobs.chmod(0o700)

    def test_publish_fsyncs_containing_parent_after_bundle(self):
        with tempfile.TemporaryDirectory(prefix='fixture-portable-bundle-',dir=p.FAMILY) as temporary:
            target=Path(temporary)/'bundle'
            parent=os.stat(temporary)
            actual_fsync=os.fsync
            synced=[]
            def fsync(fd):
                held=os.fstat(fd)
                if (held.st_dev,held.st_ino)==(parent.st_dev,parent.st_ino):
                    synced.append('parent')
                elif (held.st_dev,held.st_ino)==(os.stat(target).st_dev,os.stat(target).st_ino):
                    synced.append('bundle')
                return actual_fsync(fd)
            with mock.patch.object(p.os,'fsync',side_effect=fsync):
                p.publish(target,NOW)
            self.assertEqual(synced[-2:],['bundle','parent'])
            self.assertEqual(p.audit_bundle(target)['blobs'],105)

    def test_parent_fsync_failure_is_unknown_and_no_retry(self):
        with tempfile.TemporaryDirectory(prefix='fixture-portable-bundle-',dir=p.FAMILY) as temporary:
            target=Path(temporary)/'bundle'
            parent=os.stat(temporary)
            actual_fsync=os.fsync
            seen=[]
            def fsync(fd):
                held=os.fstat(fd)
                if (held.st_dev,held.st_ino)==(parent.st_dev,parent.st_ino):
                    seen.append('parent')
                    raise OSError('injected parent fsync failure')
                return actual_fsync(fd)
            with mock.patch.object(p.os,'fsync',side_effect=fsync):
                with self.assertRaisesRegex(p.Refused,'PARENT_FSYNC_UNKNOWN_CONSUMED_NO_RETRY'):
                    p.publish(target,NOW)
            self.assertEqual(seen,['parent'])
            self.assertTrue(target.is_dir())
            with self.assertRaisesRegex(p.Refused,'BUNDLE_PARENT_OR_EXISTING'):
                p.publish(target,NOW)

if __name__=='__main__':unittest.main()
