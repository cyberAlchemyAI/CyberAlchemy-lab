import datetime as dt
import importlib.util
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('recovery_probe', HERE / 'recovery_probe.py')
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)


class RecoveryProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan, cls.cut_sha = R.public_recipe()

    def test_public_cut_reconstructs_without_private_archive(self):
        self.assertEqual(len(self.plan['public_inputs']), 933)
        self.assertEqual(len(self.plan['generated_bindings']), 8)
        self.assertEqual(len(self.cut_sha), 64)
        self.assertEqual(self.plan['identity_prefix'], 'R03-docker-source-20261020-0002')
        self.assertEqual(self.plan['new_family'], R.SOURCE_ROLE)
        self.assertNotEqual(self.cut_sha,
                            'f38f13563c5ff86af9b4296a3280ddad2c2a9ac1688a3400801d26d341d2bfca')

    def test_period_boundaries(self):
        start = dt.datetime(2026, 10, 20, 15, 0, tzinfo=dt.timezone.utc)
        end = start + dt.timedelta(hours=24)
        self.assertEqual(R.selected_period(self.plan, start), end)
        self.assertEqual(R.selected_period(self.plan, end - dt.timedelta(seconds=1)), end)
        for instant in (start - dt.timedelta(seconds=1), end):
            with self.subTest(instant=instant), self.assertRaises(R.Refused):
                R.selected_period(self.plan, instant)

    def test_new_destination_is_persistent_and_fresh(self):
        value = R.persistent_destination()
        self.assertTrue(value.startswith('/home/vlad_/.local/state/'))
        self.assertNotIn('/tmp/', value)
        self.assertNotIn('/projects/CyberAlchemy-lab/', value)

    def test_old_attempt_presence_blocks_recovery_projection(self):
        when = dt.datetime(2026, 10, 20, 15, tzinfo=dt.timezone.utc)
        historical = Path('/tmp/old-attempt-present-for-test')
        with mock.patch.object(R, 'OLD_ATTEMPTS', (historical,)), \
             mock.patch.object(R, 'public_recipe', return_value=(self.plan, self.cut_sha)), \
             mock.patch.object(R, 'persistent_destination',
                               return_value=str(R.PERSISTENT_FAMILY)), \
             mock.patch.object(Path, 'exists', autospec=True,
                               side_effect=lambda path: path == historical):
            with self.assertRaisesRegex(R.Refused, 'historical attempt unexpectedly present'):
                R.probe(when)

    def test_probe_claim_ceiling(self):
        when = dt.datetime(2026, 10, 20, 15, tzinfo=dt.timezone.utc)
        result = R.probe(when)
        self.assertEqual(result['status'], 'PUBLIC_SOURCE_REBUILD_PREPARED_ONLY')
        self.assertFalse(result['private_archive_recovered'])
        self.assertFalse(result['old_package_pins_reusable'])
        self.assertEqual(result['source_effect'], 'NOT_RUN')
        self.assertTrue(result['source_role'].endswith('docker-source-20261020-0002'))


if __name__ == '__main__':
    unittest.main()
