"""Disposable proof for the reviewed one-shot public stage adapter."""
import importlib.util
import json
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

MODULE_PATH = Path(__file__).with_name('stage.py')
SPEC = importlib.util.spec_from_file_location('successor_stage', MODULE_PATH)
stage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(stage)


class DurableStageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cut, cls.rows, cls.generated = stage.profile()

    def fixture(self):
        return Path(tempfile.mkdtemp(prefix='cal-source-successor-stage-fixture-', dir='/tmp'))

    def invoke(self, base, **kwargs):
        return stage.stage_core(base, 'family', 'source-attempt', 'consumed.json',
                                rows=self.rows, generated=self.generated, **kwargs)

    def test_profile_excludes_protected_archive_and_has_exact_cut(self):
        self.assertEqual(len(self.rows), 941)
        self.assertEqual(len(self.generated), 8)
        self.assertFalse(any(row['path'].endswith('branch.snapshot') for row in self.rows))
        self.assertEqual(self.cut['private_archive_bodies_read'], False)

    def test_live_gate_refuses_without_independent_review(self):
        with mock.patch.object(stage, 'REVIEW', Path('/tmp/absent-stage-review-never-create')):
            with self.assertRaisesRegex(stage.Refused, 'INDEPENDENT_STAGE_REVIEW_REQUIRED'):
                stage.stage_live()

    def test_exact_durable_fixture_and_no_retry(self):
        base = self.fixture()
        try:
            receipt = self.invoke(base)
            self.assertEqual(receipt['status'], 'STAGE_ONLY_PASS')
            self.assertEqual(receipt['files'], 941)
            self.assertEqual(receipt['protected_archive_body'], 'ABSENT')
            root = base / 'family/source-attempt/root'
            self.assertEqual(stage.sha((root / stage.SOURCE_ROLE / 'source-manifest.json').read_bytes()),
                             stage.SOURCE_MANIFEST_SHA)
            self.assertEqual(len([p for p in root.rglob('*') if p.is_file()]), 941)
            self.assertTrue((root / stage.SOURCE_ROLE / 'packages').is_dir())
            self.assertTrue((root / stage.SOURCE_ROLE / 'receipts').is_dir())
            self.assertEqual(stat.S_IMODE((base / 'consumed.json').stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE((root / stage.SOURCE_ROLE / 'source-manifest.json').stat().st_mode), 0o444)
            evidence = json.loads((base / 'family/source-attempt/evidence/stage-receipt.json').read_text())
            self.assertEqual(evidence, receipt)
            with self.assertRaises(stage.Refused):
                self.invoke(base)
        finally:
            import shutil
            shutil.rmtree(base)

    def test_postclaim_failure_is_unknown_and_preserved(self):
        base = self.fixture()
        try:
            with self.assertRaises(stage.Unknown) as caught:
                self.invoke(base, inject_after=1)
            error = caught.exception
            self.assertEqual(error.status, 'UNKNOWN_PRESERVE_NO_RETRY')
            self.assertFalse(error.retry_allowed)
            self.assertIn('marker', error.identities)
            self.assertIn('root', error.identities)
            self.assertTrue((base / 'consumed.json').is_file())
            self.assertTrue((base / 'family/source-attempt/root').is_dir())
            with self.assertRaises(stage.Refused):
                self.invoke(base)
        finally:
            import shutil
            shutil.rmtree(base)

    def test_restrictive_umask_still_produces_exact_modes(self):
        base = self.fixture()
        try:
            former = os.umask(0o277)
            try:
                self.invoke(base)
            finally:
                os.umask(former)
            marker = base / 'consumed.json'
            receipt = base / 'family/source-attempt/evidence/stage-receipt.json'
            self.assertEqual(stat.S_IMODE(marker.stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE(receipt.stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE((base / 'family/source-attempt').stat().st_mode), 0o700)
        finally:
            import shutil
            shutil.rmtree(base)

    def test_close_uncertainty_is_unknown_and_preserved(self):
        base = self.fixture()
        real_close = stage.HeldAbsolute.close
        def uncertain_close(held):
            real_close(held)
            raise OSError('injected close uncertainty')
        try:
            with mock.patch.object(stage.HeldAbsolute, 'close', uncertain_close):
                with self.assertRaises(stage.Unknown) as caught:
                    self.invoke(base)
            self.assertIn('close uncertainty', str(caught.exception))
            self.assertIn('marker', caught.exception.identities)
            self.assertIn('root', caught.exception.identities)
            self.assertTrue((base / 'consumed.json').exists())
            self.assertTrue((base / 'family/source-attempt/evidence/stage-receipt.json').exists())
        finally:
            import shutil
            shutil.rmtree(base)

    def test_symlink_or_writable_ancestor_refused_before_claim(self):
        base = self.fixture()
        link = base.with_name(base.name + '-link')
        try:
            os.chmod(base, 0o722)
            with self.assertRaises(stage.Refused):
                self.invoke(base)
            self.assertFalse((base / 'consumed.json').exists())
            os.chmod(base, 0o700)
            link.symlink_to(base)
            with self.assertRaises(OSError):
                self.invoke(link)
            self.assertFalse((base / 'consumed.json').exists())
        finally:
            link.unlink(missing_ok=True)
            import shutil
            shutil.rmtree(base)


if __name__ == '__main__':
    unittest.main()
