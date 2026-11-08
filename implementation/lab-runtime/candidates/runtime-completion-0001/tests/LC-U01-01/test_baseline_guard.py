import hashlib
import os
from pathlib import Path
import tempfile
import unittest

import baseline_guard as guard


class BaselineGuardTests(unittest.TestCase):
    def setUp(self):
        # Test scratch remains entirely within the authorized unit test scope.
        self.temp = tempfile.TemporaryDirectory(prefix='owned-case-', dir=Path(__file__).parent)
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def binding(self, name, content=b'original'):
        (self.root / name).write_bytes(content)
        return {'path': name, 'sha256': hashlib.sha256(content).hexdigest(), 'size_bytes': len(content)}

    def test_source_drift_refuses_without_repin(self):
        row = self.binding('source')
        guard.verify_bindings(self.root, [row])
        (self.root / 'source').write_bytes(b'changed!')
        with self.assertRaisesRegex(ValueError, 'source drift'):
            guard.verify_bindings(self.root, [row])
        self.assertEqual(row['sha256'], hashlib.sha256(b'original').hexdigest())

    def test_duplicate_and_malformed_pins_refuse(self):
        row = self.binding('source')
        with self.assertRaisesRegex(ValueError, 'duplicate binding'):
            guard.verify_bindings(self.root, [row, row])
        for change in [{'sha256': 'x' * 64}, {'size_bytes': True}, {'path': '../source'}]:
            with self.assertRaises(ValueError):
                guard.verify_bindings(self.root, [dict(row, **change)])
        with self.assertRaisesRegex(ValueError, 'duplicate JSON'):
            guard.json.loads('{"x":1,"x":2}', object_pairs_hook=guard.unique_pairs)

    def test_symlink_member_and_parent_refuse(self):
        row = self.binding('source')
        (self.root / 'alias').symlink_to('source')
        with self.assertRaises(OSError):
            guard.verify_bindings(self.root, [dict(row, path='alias')])
        (self.root / 'directory').mkdir()
        (self.root / 'directory' / 'source').write_bytes(b'original')
        (self.root / 'parent-alias').symlink_to('directory')
        with self.assertRaises(OSError):
            guard.verify_bindings(self.root, [dict(row, path='parent-alias/source')])

    def test_each_ordinary_collision_prevents_first_root(self):
        for name in ('S', 'E', 'I'):
            with self.subTest(name=name):
                case = self.root / name
                case.mkdir()
                (case / name).mkdir()
                with self.assertRaises(FileExistsError):
                    guard.claim_pair(case, ['S', 'E'], 'I')
                if name != 'S':
                    self.assertFalse((case / 'S').exists())
                self.assertEqual(sorted(x.name for x in case.iterdir()), [name])

    def test_second_root_race_preserves_both_owned_and_foreign(self):
        def race(name):
            if name == 'E':
                (self.root / 'E').mkdir()
                (self.root / 'E' / 'foreign').write_bytes(b'preserve')
        with self.assertRaises(FileExistsError) as caught:
            guard.claim_pair(self.root, ['S', 'E'], 'I', interpose=race)
        self.assertEqual(caught.exception.created_roots, ['S'])
        self.assertTrue((self.root / 'S').is_dir())
        self.assertEqual((self.root / 'E' / 'foreign').read_bytes(), b'preserve')
        self.assertFalse((self.root / 'I').exists())

    def test_exclusive_output_preserves_equal_or_changed_foreign_file(self):
        fd = guard.open_directory(self.root)
        try:
            guard.exclusive_file(fd, 'result', b'original')
            for content in (b'original', b'other'):
                with self.assertRaises(FileExistsError):
                    guard.exclusive_file(fd, 'result', content)
            self.assertEqual((self.root / 'result').read_bytes(), b'original')
        finally:
            os.close(fd)

    def test_replaced_owned_root_refuses_even_with_same_bytes(self):
        (self.root / 'S').mkdir()
        fd = guard.open_directory(self.root / 'S')
        expected = guard.witness(fd)
        os.close(fd)
        (self.root / 'S').rename(self.root / 'retained')
        (self.root / 'S').mkdir()
        with self.assertRaisesRegex(ValueError, 'identity'):
            guard.verify_root(self.root / 'S', expected)

    def test_positive_claim_leaves_installation_logical_only(self):
        self.assertEqual(guard.claim_pair(self.root, ['S', 'E'], 'I'), ['S', 'E'])
        self.assertFalse((self.root / 'I').exists())


if __name__ == '__main__':
    unittest.main()
