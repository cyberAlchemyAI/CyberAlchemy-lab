import unittest
from unittest.mock import patch

import release as R


class FakeStage:
    STAGE_RELEASE_ENABLED = False
    calls = 0

    def preflight(self):
        return {'status': 'READY_FOR_INDEPENDENT_DISPATCH_REVIEW'}

    def execute(self):
        self.calls += 1
        if not self.STAGE_RELEASE_ENABLED:
            raise AssertionError('effect was not enabled')
        return {'overall': 'OBSERVED_STAGE_ONLY'}


class ReleaseTests(unittest.TestCase):
    def test_exact_reviewed_basis_and_live_no_archive_preflight(self):
        result = R.preflight()
        self.assertEqual(result['files'], 986)
        self.assertFalse(result['archive_body_opened'])
        self.assertEqual(result['stage_plan_sha256'], R.PLAN_SHA)

    def test_review_drift_refuses(self):
        with patch.object(R, 'STAGE_REVIEW_SHA', '0' * 64):
            with self.assertRaisesRegex(R.Refused, 'STAGE_REVIEW_OR_FREEZE_DRIFT'):
                R.basis()

    def test_execution_gate_is_scoped_and_restored(self):
        fake = FakeStage()
        with patch.object(R, 'basis', return_value=fake):
            self.assertEqual(R.execute()['overall'], 'OBSERVED_STAGE_ONLY')
        self.assertEqual(fake.calls, 1)
        self.assertFalse(fake.STAGE_RELEASE_ENABLED)


if __name__ == '__main__':
    unittest.main()
