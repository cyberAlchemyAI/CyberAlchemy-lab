"""Small failure-boundary checks for the installed Docker runner."""

import importlib.util
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('t25_installed_runner', HERE / 'run_installed_fixture.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class InstalledRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (HERE / 'working').mkdir(mode=0o700, exist_ok=True)

    def test_owned_empty_root_and_dirty_refusal(self):
        with tempfile.TemporaryDirectory(dir=HERE / 'working') as name:
            root = Path(name)
            root.chmod(0o700)
            runner.private_empty_root(root)
            (root / 'foreign').write_text('keep')
            with self.assertRaisesRegex(ValueError, 'empty result root'):
                runner.private_empty_root(root)
            self.assertEqual((root / 'foreign').read_text(), 'keep')

    def test_linked_ancestor_refuses_before_write(self):
        with tempfile.TemporaryDirectory(dir=HERE / 'working') as name:
            parent = Path(name)
            target = parent / 'target'
            target.mkdir(mode=0o700)
            alias = parent / 'alias'
            alias.symlink_to(target, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'ancestry is redirected'):
                runner.private_empty_root(alias)
            self.assertEqual(list(target.iterdir()), [])

    def test_missing_docker_command_has_terminal_step(self):
        with tempfile.TemporaryDirectory(dir=HERE / 'working') as name:
            log = Path(name) / 'missing-command.log'
            row = runner.run('missing-command', ['/definitely-missing-cal-docker'], log)
            self.assertIsNone(row['exit_code'])
            self.assertFalse(row['timed_out'])
            self.assertIn(b'FileNotFoundError', log.read_bytes())
            self.assertEqual(row['log_sha256'], runner.sha(log.read_bytes()))


if __name__ == '__main__':
    unittest.main()
