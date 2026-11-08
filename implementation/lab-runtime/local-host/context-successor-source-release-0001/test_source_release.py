"""Effect-disabled checks for the successor Source Docker controller."""
import importlib.util
import os
import subprocess
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

MODULE_PATH = Path(__file__).with_name('source_release.py')
SPEC = importlib.util.spec_from_file_location('source_release_candidate', MODULE_PATH)
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)


class SourceReleaseTests(unittest.TestCase):
    def test_release_cannot_start_without_exact_independent_review(self):
        with mock.patch.object(release, 'RELEASE_REVIEW',
                               Path('/tmp/absent-source-release-review-never-create')):
            with mock.patch.object(release, 'cli', side_effect=AssertionError('Docker called')):
                with self.assertRaises(FileNotFoundError):
                    release.run()

    def test_stage_gate_cannot_start_without_exact_independent_review(self):
        with mock.patch.object(release, 'STAGE_REVIEW',
                               Path('/tmp/absent-source-stage-review-never-create')):
            with self.assertRaises((FileNotFoundError, ValueError)):
                release.reviewed_stage()

    def test_exclusive_evidence_exact_mode_under_restrictive_umask_and_no_retry(self):
        with tempfile.TemporaryDirectory(prefix='cal-source-release-test-', dir='/tmp') as temp:
            path = Path(temp) / 'consumed.json'
            previous = os.umask(0o277)
            try:
                release.exclusive(path, b'{"state":"CONSUMED_NO_RETRY"}\n')
            finally:
                os.umask(previous)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertEqual(path.read_bytes(), b'{"state":"CONSUMED_NO_RETRY"}\n')
            with self.assertRaises(FileExistsError):
                release.exclusive(path, b'changed')

    def test_docker_creation_contract_is_selected_and_no_network(self):
        argv = release.docker_create_argv('fixture-nonce')
        self.assertEqual(argv[:4], [release.DOCKER, 'create', '--name', release.NAME])
        self.assertIn('cal.source.attempt=fixture-nonce', argv)
        self.assertIn('none', argv)
        self.assertIn('no-new-privileges:true', argv)
        self.assertEqual(argv[argv.index('--user') + 1], '1000:1000')
        self.assertEqual(argv[argv.index('--userns') + 1], 'host')
        self.assertEqual(argv[-4:], [release.IMAGE, 'python', '-B',
                                     '/tool/source_once.py', '--execute-reviewed-one-shot'][-4:])
        self.assertEqual(release.IMAGE,
                         'sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874')

    def test_selected_image_preclaim_probe_rejects_identity_change(self):
        with mock.patch.object(release, 'cli', return_value=subprocess.CompletedProcess(
                [], 0, b'[{"Id":"sha256:other"}]', b'')):
            with self.assertRaisesRegex(ValueError, 'image identity differs'):
                release.selected_image_present()


if __name__ == '__main__':
    unittest.main()
