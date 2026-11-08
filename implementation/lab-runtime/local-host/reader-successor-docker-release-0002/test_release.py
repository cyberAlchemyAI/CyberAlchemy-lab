import subprocess
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import release as R


class ReleaseTests(unittest.TestCase):
    def test_exact_reviewed_live_read_only_preflight(self):
        observed = R.preflight()
        self.assertEqual(observed['status'], 'READY_FOR_INDEPENDENT_DISPATCH_REVIEW')
        self.assertEqual(observed['selected_files'], 986)
        self.assertTrue(observed['host']['container_absent'])
        self.assertEqual(observed['controller_freeze_sha256'], R.CONTROLLER_FREEZE_SHA)

    def test_controller_review_drift_refuses(self):
        with patch.object(R, 'CONTROLLER_REVIEW_SHA', '0' * 64):
            with self.assertRaisesRegex(R.Refused, 'CONTROLLER_FREEZE_OR_REVIEW_DRIFT'):
                R.basis()

    def test_host_observation_requires_exact_absence_and_image(self):
        good_image = subprocess.CompletedProcess([], 0,
            f'{R.IMAGE} amd64 20001:20001\n'.encode(), b'')
        absent = subprocess.CompletedProcess([], 1, b'\n',
            f'Error response from daemon: No such container: {R.NAME}\n'.encode())
        def runner(argv):
            return good_image if argv[1:3] == ['image', 'inspect'] else absent
        self.assertTrue(R.host_observation(runner)['container_absent'])
        wrong = subprocess.CompletedProcess([], 1, b'\n', b'connection refused\n')
        def bad_runner(argv):
            return good_image if argv[1:3] == ['image', 'inspect'] else wrong
        with self.assertRaisesRegex(R.Refused, 'DOCKER_NAME_NOT_EXCLUSIVELY_ABSENT'):
            R.host_observation(bad_runner)

    def test_effect_enablement_scoped_to_single_controller_run(self):
        fake = SimpleNamespace(EFFECT_ENABLED=False, STOP_REQUESTED=False)
        calls = []
        def prepare():
            calls.append('prepare')
            self.assertTrue(fake.EFFECT_ENABLED)
        def run():
            calls.append('run')
            self.assertTrue(fake.EFFECT_ENABLED)
            return {'overall': 'PASS'}
        fake.prepare_attempt, fake.run = prepare, run
        with patch.object(R, 'basis', return_value=fake), \
             patch.object(R, 'preflight', return_value={'status': 'READY'}):
            self.assertEqual(R.execute()['overall'], 'PASS')
        self.assertEqual(calls, ['prepare', 'run'])
        self.assertFalse(fake.EFFECT_ENABLED)

    def test_post_create_prepare_fault_retains_unknown_and_no_retry(self):
        controller = R.basis()
        with tempfile.TemporaryDirectory() as temporary:
            attempt = Path(temporary) / 'claimed-reader-attempt'
            def partial_prepare():
                attempt.mkdir(mode=0o700)
                raise RuntimeError('after-create prepare fault')
            with patch.object(R, 'basis', return_value=controller), \
                 patch.object(R, 'preflight', return_value={'status': 'READY'}), \
                 patch.object(controller, 'ATTEMPT', attempt), \
                 patch.object(controller, 'prepare_attempt', side_effect=partial_prepare):
                with self.assertRaisesRegex(RuntimeError, 'after-create prepare fault'):
                    R.execute()
            receipt = attempt / 'reader-release-unknown.json'
            self.assertTrue(receipt.is_file())
            self.assertIn(b'"overall":"UNKNOWN"', receipt.read_bytes())
            self.assertTrue(attempt.is_dir())
            self.assertFalse(controller.EFFECT_ENABLED)

    def test_stop_during_prepare_retains_unknown_without_run(self):
        controller = R.basis()
        with tempfile.TemporaryDirectory() as temporary:
            attempt = Path(temporary) / 'claimed-reader-attempt'
            def interrupted_prepare():
                attempt.mkdir(mode=0o700)
                controller.STOP_REQUESTED = True
            with patch.object(R, 'basis', return_value=controller), \
                 patch.object(R, 'preflight', return_value={'status': 'READY'}), \
                 patch.object(controller, 'ATTEMPT', attempt), \
                 patch.object(controller, 'prepare_attempt', side_effect=interrupted_prepare), \
                 patch.object(controller, 'run', side_effect=AssertionError('run must not start')):
                with self.assertRaisesRegex(R.Refused, 'STOP_AFTER_READER_ATTEMPT_PREPARE'):
                    R.execute()
            receipt = attempt / 'reader-release-unknown.json'
            self.assertIn(b'"stop_requested":true', receipt.read_bytes())
            self.assertTrue(attempt.is_dir())

    def test_stop_between_prepare_and_controller_marker_retains_unknown(self):
        controller = R.basis()
        with tempfile.TemporaryDirectory() as temporary:
            attempt = Path(temporary) / 'claimed-reader-attempt'
            def prepare():
                attempt.mkdir(mode=0o700)
            def stop_before_marker():
                controller.STOP_REQUESTED = True
                raise R.Refused('stop before consumed marker')
            with patch.object(R, 'basis', return_value=controller), \
                 patch.object(R, 'preflight', return_value={'status': 'READY'}), \
                 patch.object(controller, 'ATTEMPT', attempt), \
                 patch.object(controller, 'prepare_attempt', side_effect=prepare), \
                 patch.object(controller, 'run', side_effect=stop_before_marker):
                with self.assertRaisesRegex(R.Refused, 'stop before consumed marker'):
                    R.execute()
            self.assertIn(b'"stop_requested":true',
                          (attempt / 'reader-release-unknown.json').read_bytes())

    def test_competing_attempt_claim_is_not_modified(self):
        controller = R.basis()
        with tempfile.TemporaryDirectory() as temporary:
            attempt = Path(temporary) / 'claimed-reader-attempt'
            attempt.mkdir(mode=0o700)
            def lost_claim():
                raise FileExistsError(17, 'File exists', str(attempt))
            with patch.object(R, 'basis', return_value=controller), \
                 patch.object(R, 'preflight', return_value={'status': 'READY'}), \
                 patch.object(controller, 'ATTEMPT', attempt), \
                 patch.object(controller, 'prepare_attempt', side_effect=lost_claim), \
                 patch.object(controller, 'run', side_effect=AssertionError('run must not start')):
                with self.assertRaises(FileExistsError):
                    R.execute()
            self.assertEqual(list(attempt.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
