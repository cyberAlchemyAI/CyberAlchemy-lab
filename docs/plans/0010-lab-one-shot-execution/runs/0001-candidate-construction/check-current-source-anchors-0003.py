"""Actual filesystem tests and whole original file-set cost observation."""
import argparse
import errno
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
GUARD = ROOT / 'product/lab/release-candidates/v1/interface/api-v36/guard.py'
PARENT = GUARD.parent.parent / 'api-v35/source-manifest.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-sha256', required=True)
    args = parser.parse_args()
    inputs = RUN / 'current-source-anchor-inputs-0003.json'
    assert sha(inputs) == args.input_sha256
    for row in json.loads(inputs.read_bytes())['files']:
        assert sha(ROOT / row['path']) == row['sha256']
    spec = importlib.util.spec_from_file_location('_cal_current_source_anchor_unit_checks_0003', GUARD)
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    cases = []

    class Checks(unittest.TestCase):
        def setUp(self):
            self.temp = tempfile.TemporaryDirectory(prefix='cal-owned-source-anchor-unit-')
            self.addCleanup(self.temp.cleanup)
            self.root = Path(self.temp.name)
            self.file = self.root / 'nested/a.json'
            self.file.parent.mkdir()
            self.file.write_bytes(b'original exact source\n')
            self.rows = [{'path': 'nested/a.json', 'sha256': sha(self.file)}]

        def verify(self):
            return guard._verify_files(self.root, self.rows)

        def test_01_complete_exact_original_bytes(self):
            self.assertEqual(self.verify(), {'verified_files': 1, 'anchored_directories': len(self.root.parts) + 1})

        def test_02_shared_parent_anchored_once(self):
            other = self.file.with_name('b.json')
            other.write_bytes(b'second source')
            self.rows.append({'path': 'nested/b.json', 'sha256': sha(other)})
            self.assertEqual(self.verify(), {'verified_files': 2, 'anchored_directories': len(self.root.parts) + 1})

        def test_03_no_content_cache_across_calls(self):
            self.verify()
            self.file.write_bytes(b'different exact source')
            with self.assertRaisesRegex(AssertionError, 'source changed'):
                self.verify()

        def test_04_missing_source_refused(self):
            self.file.unlink()
            with self.assertRaises(FileNotFoundError):
                self.verify()

        def test_05_symbolic_file_refused(self):
            saved = self.file.with_name('saved.json')
            self.file.rename(saved)
            self.file.symlink_to(saved)
            with self.assertRaises(OSError) as error:
                self.verify()
            self.assertEqual(error.exception.errno, errno.ELOOP)

        def test_06_symbolic_parent_refused(self):
            nested = self.file.parent
            saved = nested.with_name('saved')
            nested.rename(saved)
            nested.symlink_to(saved, target_is_directory=True)
            with self.assertRaises(OSError) as error:
                self.verify()
            self.assertIn(error.exception.errno, (errno.ELOOP, errno.ENOTDIR))

        def test_07_symbolic_source_root_refused(self):
            link = self.root / 'root-link'
            link.symlink_to(self.root, target_is_directory=True)
            with self.assertRaisesRegex(AssertionError, 'unsafe source ancestor'):
                guard._verify_files(link, self.rows)

        def test_08_relative_source_root_refused(self):
            with self.assertRaisesRegex(AssertionError, 'absolute source root'):
                guard._verify_files(Path('.'), self.rows)

        def test_09_traversal_and_noncanonical_paths_refused(self):
            for path in ('../a.json', '/../a.json', './nested/a.json', 'nested//a.json', '.'):
                with self.subTest(path=path), self.assertRaisesRegex(AssertionError, 'unsafe source path'):
                    guard._verify_files(self.root, [{'path': path, 'sha256': self.rows[0]['sha256']}])

        def test_10_directory_instead_of_file_refused(self):
            with self.assertRaisesRegex(AssertionError, 'not a regular file'):
                guard._verify_files(self.root, [{'path': 'nested', 'sha256': self.rows[0]['sha256']}])

        def test_11_fifo_refused_without_blocking(self):
            self.file.unlink()
            os.mkfifo(self.file)
            with self.assertRaisesRegex(AssertionError, 'not a regular file'):
                self.verify()

        def test_12_duplicate_path_conflicting_digest_refused(self):
            self.rows.append({'path': 'nested/a.json', 'sha256': '0' * 64})
            with self.assertRaisesRegex(AssertionError, 'source changed'):
                self.verify()

        def test_13_leaf_replacement_during_actual_read_refused(self):
            original_read = os.read
            saved = self.file.with_name('replacement.json')
            saved.write_bytes(self.file.read_bytes())
            changed = False
            def read(handle, size):
                nonlocal changed
                raw = original_read(handle, size)
                if raw and not changed:
                    changed = True
                    os.replace(saved, self.file)
                return raw
            with patch.object(guard.os, 'read', side_effect=read), self.assertRaisesRegex(AssertionError, 'during read'):
                self.verify()
            self.assertTrue(changed)

        def test_14_directory_replacement_during_actual_read_refused(self):
            original_read = os.read
            changed = False
            def read(handle, size):
                nonlocal changed
                raw = original_read(handle, size)
                if raw and not changed:
                    changed = True
                    self.file.parent.rename(self.root / 'old-nested')
                    self.file.parent.mkdir()
                    self.file.write_bytes(raw)
                return raw
            with patch.object(guard.os, 'read', side_effect=read), self.assertRaisesRegex(AssertionError, 'directory attachment changed'):
                self.verify()
            self.assertTrue(changed)

        def test_15_earlier_file_mutation_during_later_read_refused(self):
            other = self.file.with_name('b.json')
            other.write_bytes(b'second source')
            self.rows.append({'path': 'nested/b.json', 'sha256': sha(other)})
            original_read = os.read
            changed = False
            def read(handle, size):
                nonlocal changed
                raw = original_read(handle, size)
                if raw == b'second source' and not changed:
                    changed = True
                    self.file.write_bytes(b'late mutation')
                return raw
            with patch.object(guard.os, 'read', side_effect=read), self.assertRaisesRegex(AssertionError, 'after read'):
                self.verify()
            self.assertTrue(changed)

        def test_16_file_descriptors_closed_on_success_and_failure(self):
            def descriptors():
                return set(os.listdir('/proc/self/fd'))
            before = descriptors()
            self.verify()
            self.assertEqual(descriptors(), before)
            self.rows.append({'path': 'nested/missing.json', 'sha256': '0' * 64})
            with self.assertRaises(FileNotFoundError):
                self.verify()
            self.assertEqual(descriptors(), before)

        def test_17_exact_absolute_source_inside_selected_root(self):
            self.rows[0]['path'] = str(self.file)
            self.assertEqual(self.verify()['verified_files'], 1)

        def test_18_exact_absolute_source_outside_selected_root(self):
            with tempfile.TemporaryDirectory(prefix='cal-owned-source-anchor-external-') as external:
                path = Path(external) / 'native-reader'
                path.write_bytes(b'original external selected source')
                self.rows.append({'path': str(path), 'sha256': sha(path)})
                self.assertEqual(self.verify()['verified_files'], 2)
                path.write_bytes(b'external source changed')
                with self.assertRaisesRegex(AssertionError, 'source changed'):
                    self.verify()

    class Result(unittest.TextTestResult):
        def addSuccess(self, test):
            super().addSuccess(test)
            cases.append({'test': test.id(), 'result': 'PASS'})
        def addFailure(self, test, error):
            super().addFailure(test, error)
            cases.append({'test': test.id(), 'result': 'FAIL'})
        def addError(self, test, error):
            super().addError(test, error)
            cases.append({'test': test.id(), 'result': 'ERROR'})

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Checks)
    assert suite.countTestCases() == 18
    result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(suite)
    measurement = None
    if result.wasSuccessful():
        # Preserve exact scope. Both algorithms read/hash every row of the same
        # original API35 source manifest. No runtime or authorization is invoked.
        rows = json.loads(PARENT.read_bytes())['files']
        started = time.monotonic()
        for row in rows:
            path = ROOT / row['path']
            assert path.is_file() and not path.is_symlink() and not any(a.is_symlink() for a in path.parents)
            assert sha(path) == row['sha256']
        old_seconds = time.monotonic() - started
        started = time.monotonic()
        checked = guard._verify_files(ROOT, rows)
        new_seconds = time.monotonic() - started
        assert checked['verified_files'] == len(rows)
        measurement = {'source_binding': {'path': PARENT.relative_to(ROOT).as_posix(), 'sha256': sha(PARENT)},
                       'verified_files_each_algorithm': len(rows),
                       'original_algorithm_elapsed_seconds': old_seconds,
                       'anchored_algorithm_elapsed_seconds': new_seconds,
                       'anchored_directories': checked['anchored_directories'],
                       'sampling_used': False, 'file_selection_reduced': False,
                       'limitation': 'One ordered observation under concurrent suite load; not a stable benchmark or whole API latency result.'}
    report = {'schema_version': 'lab-current-source-anchor-checks/v1-candidate',
              'result': 'PASS' if result.wasSuccessful() else 'FAIL',
              'tests_run': result.testsRun, 'expected_tests': 18, 'cases': cases,
              'input_sha256': args.input_sha256, 'whole_original_file_set_measurement': measurement,
              'source_frozen': False, 'whole_API_qualified': False, 'current_Agent_qualified': False,
              'clock_replaced': False, 'permission_cached': False, 'authority_effect': 'none',
              'actual_owner_outcome': None}
    with (RUN / 'current-source-anchor-checks-0003.json').open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': report['result'], 'tests_run': result.testsRun,
                      'whole_original_file_set_measurement': measurement}), flush=True)
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__ == '__main__':
    main()
