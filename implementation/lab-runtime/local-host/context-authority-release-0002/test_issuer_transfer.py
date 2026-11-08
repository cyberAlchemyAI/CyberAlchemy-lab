import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('issuer_transfer', HERE / 'issuer_transfer.py')
I = importlib.util.module_from_spec(spec)
spec.loader.exec_module(I)


class Signed:
    class Sources:
        scope_ref = I.EXPECTED_SCOPE

    class View:
        data = {'config': {'scope_ref': I.EXPECTED_SCOPE}}

    def __init__(self, fail=False):
        self.view = self.View()
        self.sources = self.Sources()
        self.calls = 0
        self.fail = fail

    def guard(self):
        self.calls += 1
        if self.fail:
            raise I.Refused('signed view invalid')


class TransferTests(unittest.TestCase):
    def test_old_stage_absence_is_explicit_hold(self):
        with self.assertRaisesRegex(I.Refused, 'STALE_STAGE_ABSENT_FRESH_FAMILY_REQUIRED'):
            I.stale_stage_preflight()

    def test_live_issue_cannot_mutate_old_stage(self):
        with self.assertRaisesRegex(I.Refused, 'FRESH_STAGE_SELECTION'):
            I.live_issue()

    def test_signed_scope_exact_and_guarded(self):
        good = Signed()
        self.assertEqual(I.signed_scope_guard(good), I.EXPECTED_SCOPE)
        self.assertEqual(good.calls, 2)
        bad = Signed()
        bad.sources.scope_ref = 'scope:other'
        with self.assertRaisesRegex(I.Refused, 'SIGNED_SCOPE_MISMATCH'):
            I.signed_scope_guard(bad)
        with self.assertRaisesRegex(I.Refused, 'signed view invalid'):
            I.signed_scope_guard(Signed(fail=True))

    def test_one_shot_marker_durable_and_consumed(self):
        with tempfile.TemporaryDirectory(prefix='cal-authority-release-transfer-fixture-',
                                         dir='/tmp') as name:
            path = Path(name)
            result = I.exclusive_one_shot_fixture(path, {'kind': 'INTENT'})
            self.assertEqual(result['status'], 'FIXTURE_INTENT_DURABLE')
            self.assertFalse(result['retry_allowed'])
            self.assertEqual(json.loads((path / 'attempt.json').read_bytes())['event'],
                             {'kind': 'INTENT'})
            with self.assertRaises(FileExistsError):
                I.exclusive_one_shot_fixture(path, {'kind': 'RETRY'})

    def test_uncertainty_retains_marker_and_forbids_retry(self):
        for point in ('write', 'close', 'parent_fsync'):
            with self.subTest(point=point):
                with tempfile.TemporaryDirectory(
                    prefix='cal-authority-release-transfer-fixture-', dir='/tmp'
                ) as name:
                    path = Path(name)
                    result = I.exclusive_one_shot_fixture(path, {'kind': 'INTENT'}, point)
                    self.assertEqual(result['status'], 'UNKNOWN_PRESERVE_NO_RETRY')
                    self.assertFalse(result['retry_allowed'])
                    self.assertTrue((path / 'attempt.json').exists())
                    with self.assertRaises(FileExistsError):
                        I.exclusive_one_shot_fixture(path, {'kind': 'RETRY'})


if __name__ == '__main__':
    unittest.main()
