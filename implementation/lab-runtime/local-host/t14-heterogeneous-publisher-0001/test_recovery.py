import fcntl
import os
from pathlib import Path
import tempfile
import unittest

import recovery


class Recovery(unittest.TestCase):
    def setUp(self):
        self.context = tempfile.TemporaryDirectory(prefix='cal-T14-publisher-', dir='/tmp')
        self.addCleanup(self.context.cleanup)
        self.root = Path(self.context.name)
        self.root.chmod(0o700)
        (self.root / 'publisher.lock').write_bytes(b'')
        (self.root / 'publisher.lock').chmod(0o600)
        self.stage = self.root / '.technical-stage-pinned'
        self.stage.mkdir(mode=0o700)
        self.files = {'bundle.json': b'body', 'targets/a.json': b'A'}

    def selected(self, content=b'body'):
        path = self.stage / 'bundle.json'
        path.write_bytes(content)
        path.chmod(0o600)
        return path

    def test_exact_partial_owned_stage_rolls_back(self):
        self.selected()
        result = recovery.rollback(self.root, self.stage.name, self.files)
        self.assertEqual(result['rolled_back_selected_files'], 1)
        self.assertEqual({p.name for p in self.root.iterdir()}, {'publisher.lock'})

    def test_foreign_leaf_is_preserved(self):
        self.selected()
        foreign = self.stage / 'foreign.json'
        foreign.write_bytes(b'foreign')
        foreign.chmod(0o600)
        with self.assertRaisesRegex(ValueError, 'foreign stage leaf'):
            recovery.rollback(self.root, self.stage.name, self.files)
        self.assertEqual(foreign.read_bytes(), b'foreign')
        self.assertEqual((self.stage / 'bundle.json').read_bytes(), b'body')

    def test_changed_selected_bytes_are_preserved(self):
        path = self.selected(b'changed')
        with self.assertRaisesRegex(ValueError, 'unselected stage bytes'):
            recovery.rollback(self.root, self.stage.name, self.files)
        self.assertEqual(path.read_bytes(), b'changed')

    def test_nested_exact_partial_stage_rolls_back(self):
        nested = self.stage / 'targets'
        nested.mkdir(mode=0o700)
        target = nested / 'a.json'
        target.write_bytes(b'A')
        target.chmod(0o600)
        result = recovery.rollback(self.root, self.stage.name, self.files)
        self.assertEqual(result['rolled_back_selected_files'], 1)
        self.assertFalse(self.stage.exists())

    def test_symlink_residue_is_preserved(self):
        self.selected()
        link = self.stage / 'targets'
        link.symlink_to(self.root / 'publisher.lock')
        with self.assertRaisesRegex(ValueError, 'foreign stage leaf'):
            recovery.rollback(self.root, self.stage.name, self.files)
        self.assertTrue(link.is_symlink())
        self.assertEqual((self.stage / 'bundle.json').read_bytes(), b'body')

    def test_commit_receipt_prevents_rollback(self):
        path = self.selected()
        receipt = self.root / 'technical.commit.json'
        receipt.write_bytes(b'foreign')
        receipt.chmod(0o600)
        with self.assertRaisesRegex(ValueError, 'foreign root residue'):
            recovery.rollback(self.root, self.stage.name, self.files)
        self.assertEqual(path.read_bytes(), b'body')
        self.assertEqual(receipt.read_bytes(), b'foreign')

    def test_concurrent_publisher_lock_prevents_rollback(self):
        path = self.selected()
        ready_read, ready_write = os.pipe()
        release_read, release_write = os.pipe()
        pid = os.fork()
        if pid == 0:
            os.close(ready_read)
            os.close(release_write)
            fd = os.open(self.root / 'publisher.lock', os.O_RDWR)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX)
                os.write(ready_write, b'1')
                os.read(release_read, 1)
                fcntl.flock(fd, fcntl.LOCK_UN)
            finally:
                os.close(fd)
                os.close(ready_write)
                os.close(release_read)
            os._exit(0)
        os.close(ready_write)
        os.close(release_read)
        try:
            self.assertEqual(os.read(ready_read, 1), b'1')
            with self.assertRaisesRegex(ValueError, 'publisher lock busy'):
                recovery.rollback(self.root, self.stage.name, self.files)
            self.assertEqual(path.read_bytes(), b'body')
            self.assertTrue(self.stage.is_dir())
        finally:
            os.write(release_write, b'1')
            os.close(ready_read)
            os.close(release_write)
            _, status = os.waitpid(pid, 0)
            self.assertTrue(os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0)


if __name__ == '__main__':
    unittest.main()
