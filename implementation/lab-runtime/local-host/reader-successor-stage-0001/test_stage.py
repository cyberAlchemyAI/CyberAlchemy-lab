from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import stage as S


class StageTests(unittest.TestCase):
    def test_live_selection_exact_and_no_archive_body_read(self):
        plan = S.selected()
        self.assertEqual(len(plan['files']), 986)
        self.assertEqual(plan['source_package_manifest_sha256'],
                         'bdb5eac92cbb3f96857c4d2ccb00880441d55fb8f1dbbeb5cdaae8d81c720653')
        self.assertEqual(plan['reader_manifest_sha256'],
                         '048ef6c1f54387fc6e593f38b29723cb06f84649f12e9c75a0340d389b0f5756')
        archive = S.R.SOURCE_ROOT / S.R.frozen_selector().SOURCE / 'packages/0001/branch.snapshot'
        real = S.hash_exact
        def guarded(path, digest, mode):
            self.assertNotEqual(path, archive)
            return real(path, digest, mode)
        with patch.object(S, 'hash_exact', guarded):
            observed = S.preflight()
        self.assertEqual(observed['status'], 'READY_FOR_INDEPENDENT_DISPATCH_REVIEW')
        self.assertFalse(observed['archive_body_opened'])

    def test_effect_refuses_before_any_attempt(self):
        self.assertFalse(S.R.STAGE_ATTEMPT.exists())
        with self.assertRaisesRegex(S.Refused, 'STAGE_EFFECT_DISABLED'):
            S.execute()
        self.assertFalse(S.R.STAGE_ATTEMPT.exists())

    def test_existing_attempt_refuses_preflight(self):
        with patch.object(S.os.path, 'lexists', return_value=True):
            with self.assertRaisesRegex(S.Refused, 'STAGE_ATTEMPT_CONSUMED'):
                S.preflight()

    def test_namespace_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'safe').write_text('x')
            (root / 'link').symlink_to(root / 'safe')
            with self.assertRaisesRegex(S.Refused, 'STAGE_NONREGULAR_ENTRY'):
                S.entries(root)

    def test_post_create_fault_retains_unknown_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            attempt = Path(temporary) / 'consumed'
            def partial_create(path, mode):
                self.assertEqual(path, attempt)
                path.mkdir(mode=mode)
                raise RuntimeError('after-create fault')
            with patch.object(S, 'STAGE_RELEASE_ENABLED', True), \
                 patch.object(S, 'preflight', return_value={}), \
                 patch.object(S, 'selected', return_value={}), \
                 patch.object(S, 'metadata', return_value=object()), \
                 patch.object(S, 'mkdir_exact', side_effect=partial_create), \
                 patch.object(S.R, 'STAGE_ATTEMPT', attempt):
                with self.assertRaisesRegex(RuntimeError, 'after-create fault'):
                    S.execute()
            receipt = attempt / 'stage-unknown.json'
            self.assertTrue(receipt.is_file())
            self.assertIn(b'"overall": "UNKNOWN"', receipt.read_bytes())


if __name__ == '__main__':
    unittest.main()
