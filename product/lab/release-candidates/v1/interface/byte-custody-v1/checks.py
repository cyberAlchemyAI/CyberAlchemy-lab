"""Real filesystem custody refusals and original full-closure comparison."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
NAME = '_cal_byte_custody_v1'
spec = importlib.util.spec_from_file_location(NAME, HERE / '__init__.py', submodule_search_locations=[str(HERE)])
module = importlib.util.module_from_spec(spec)
sys.modules[NAME] = module
spec.loader.exec_module(module)
K = __import__(NAME + '.custody', fromlist=['*'])


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class CustodyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='cal-R03-byte-custody-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / 'nested').mkdir()
        (self.root / 'nested/a').write_bytes(b'original a')
        (self.root / 'nested/b').write_bytes(b'original b')
        self.rows = [{'path': 'nested/' + name, 'sha256': sha((self.root / 'nested' / name).read_bytes())}
                     for name in ('a', 'b')]

    def capture(self, rows=None, external=None, **kwargs):
        return K.Custody(self.rows if rows is None else rows, self.root,
                         [] if external is None else external, **kwargs)

    def test_01_all_original_bytes_and_descriptor_disposal(self):
        with self.capture() as custody:
            self.assertEqual([custody.read(row) for row in self.rows], [b'original a', b'original b'])
            custody.guard()
            descriptors = [row[0] for row in custody.directories.values()]
        self.assertTrue(custody.closed)
        self.assertFalse(custody.directories)
        for descriptor in descriptors:
            with self.assertRaises(OSError):
                os.fstat(descriptor)

    def test_02_actual_changed_file_hash_refused(self):
        (self.root / 'nested/a').write_bytes(b'changed')
        with self.assertRaises(K.Refusal):
            with self.capture() as custody:
                custody.read(self.rows[0])
        self.assertTrue(custody.closed)

    def test_03_actual_leaf_symlink_refused(self):
        (self.root / 'nested/a').unlink()
        (self.root / 'nested/a').symlink_to('b')
        with self.assertRaises((OSError, K.Refusal)):
            with self.capture() as custody:
                custody.read(self.rows[0])

    def test_04_actual_ancestor_symlink_refused(self):
        (self.root / 'nested').rename(self.root / 'original')
        (self.root / 'nested').symlink_to('original', target_is_directory=True)
        with self.assertRaises((OSError, K.Refusal)):
            with self.capture() as custody:
                custody.read(self.rows[0])

    def test_05_absolute_dependency_requires_explicit_selection(self):
        row = {'path': str(self.root / 'nested/a'), 'sha256': self.rows[0]['sha256']}
        with self.assertRaises(K.Refusal):
            self.capture([row])
        with self.capture([row], [row]) as custody:
            self.assertEqual(custody.read(row), b'original a')

    def test_06_duplicate_selected_path_refused(self):
        with self.assertRaises(K.Refusal):
            self.capture([self.rows[0], self.rows[0]])

    def test_07_parent_traversal_refused(self):
        row = {'path': '../outside', 'sha256': self.rows[0]['sha256']}
        with self.assertRaises(K.Refusal):
            self.capture([row])

    def test_08_incomplete_manifest_cannot_pass(self):
        with self.assertRaisesRegex(K.Refusal, 'complete selected dependency'):
            with self.capture() as custody:
                custody.read(self.rows[0])
        self.assertTrue(custody.closed)

    def test_09_directory_replacement_refused_even_with_identical_file_bytes(self):
        with self.assertRaisesRegex(K.Refusal, 'directory path changed'):
            with self.capture() as custody:
                custody.read(self.rows[0])
                (self.root / 'nested').rename(self.root / 'original')
                (self.root / 'nested').mkdir()
                for name in ('a', 'b'):
                    (self.root / 'nested' / name).write_bytes((self.root / 'original' / name).read_bytes())
                self.assertEqual(custody.read(self.rows[1]), b'original b')

    def test_10_leaf_replacement_after_read_refused(self):
        with self.assertRaisesRegex(K.Refusal, 'file changed after reading'):
            with self.capture() as custody:
                for row in self.rows:
                    custody.read(row)
                replacement = self.root / 'replacement'
                replacement.write_bytes(b'original a')
                os.replace(replacement, self.root / 'nested/a')

    def test_11_in_place_file_change_after_read_refused(self):
        with self.assertRaisesRegex(K.Refusal, 'file changed after reading'):
            with self.capture() as custody:
                for row in self.rows:
                    custody.read(row)
                (self.root / 'nested/a').write_bytes(b'changed after read')

    def test_12_closed_pass_cannot_be_reused(self):
        with self.capture() as custody:
            for row in self.rows:
                custody.read(row)
        with self.assertRaises(K.Refusal):
            custody.read(self.rows[0])
        with self.assertRaises(K.Refusal):
            custody.__enter__()

    def test_13_foreign_thread_cannot_read_or_close_pass(self):
        errors = []
        with self.capture() as custody:
            def foreign():
                for attempt in (lambda: custody.read(self.rows[0]), lambda: custody.__exit__(None, None, None)):
                    try:
                        attempt()
                    except K.Refusal as error:
                        errors.append(str(error))
            thread = threading.Thread(target=foreign)
            thread.start()
            thread.join()
            self.assertEqual(len(errors), 2)
            self.assertFalse(custody.closed)
            for row in self.rows:
                custody.read(row)

    def test_14_original_error_preserved_and_descriptors_closed(self):
        with self.assertRaisesRegex(RuntimeError, 'owned intentional failure'):
            with self.capture() as custody:
                custody.read(self.rows[0])
                raise RuntimeError('owned intentional failure')
        self.assertTrue(custody.closed)
        self.assertFalse(custody.directories)

    def test_15_host_file_byte_ceiling_refused(self):
        with self.assertRaisesRegex(K.Refusal, 'file-byte ceiling'):
            with self.capture(max_file_bytes=3) as custody:
                custody.read(self.rows[0])

    def test_16_FIFO_refused_before_blocking_open(self):
        (self.root / 'nested/a').unlink()
        os.mkfifo(self.root / 'nested/a')
        with self.assertRaisesRegex(K.Refusal, 'regular file'):
            with self.capture() as custody:
                custody.read(self.rows[0])

    def test_17_unselected_row_refused(self):
        with self.assertRaisesRegex(K.Refusal, 'unselected dependency'):
            with self.capture() as custody:
                custody.read({'path': 'nested/a', 'sha256': '0' * 64})


def benchmark():
    context = HERE.parent / 'current-context-delivery-v5'
    manifest = json.loads((context / 'source-manifest.json').read_bytes())
    rows, external = manifest['files'], manifest['external_dependency_bindings']
    require_count = 11165
    assert len(rows) == require_count and len(external) == 66
    name = '_cal_original_context_byte_custody_measurement'
    spec = importlib.util.spec_from_file_location(name, context / '__init__.py', submodule_search_locations=[str(context)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[name] = package
    spec.loader.exec_module(package)
    original = __import__(name + '.base', fromlist=['dependency_input_bytes'])
    results = []
    # Both implementations follow the same full source guard, which has
    # already read all inputs. ABBA preserves two measurements of each path.
    for selected in ('original', 'descriptor', 'descriptor', 'original'):
        started = time.monotonic()
        count = total = 0
        hashes = []
        if selected == 'original':
            for row in rows:
                raw = original.dependency_input_bytes(row, external)
                hashes.append(sha(raw))
                count += 1
                total += len(raw)
        else:
            with K.Custody(rows, ROOT, external) as custody:
                for row in rows:
                    raw = custody.read(row)
                    hashes.append(sha(raw))
                    count += 1
                    total += len(raw)
                directories = len(custody.directories)
        assert count == require_count and hashes == [row['sha256'] for row in rows]
        results.append({'implementation': selected, 'duration_seconds': time.monotonic() - started,
                        'actual_files': count, 'actual_bytes': total,
                        'directory_descriptors': directories if selected == 'descriptor' else None,
                        'all_original_file_hashes_matched': True})
    assert len({row['actual_bytes'] for row in results}) == 1
    old = sum(row['duration_seconds'] for row in results if row['implementation'] == 'original') / 2
    new = sum(row['duration_seconds'] for row in results if row['implementation'] == 'descriptor') / 2
    return {'result': 'PASS', 'measurements': results,
            'component_speed_ratio': old / new,
            'measurement_order': 'ABBA after common full source guard',
            'permission_or_clock_checks_cached': False,
            'claim_ceiling': 'Two measured passes of each dependency-byte verification implementation only. Original Context preflight semantics, complete API throughput and Agent lifecycle are unqualified.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-sha256', required=True)
    args = parser.parse_args()
    source = HERE / 'source-manifest.json'
    assert sha(source.read_bytes()) == args.source_sha256
    manifest = json.loads(source.read_bytes())
    def guard():
        for row in manifest['files']:
            path = ROOT / row['path']
            assert path.is_file() and not path.is_symlink() and sha(path.read_bytes()) == row['sha256'], row['path']
    guard()
    cases = []
    class Result(unittest.TextTestResult):
        def addSuccess(self, test):
            super().addSuccess(test)
            cases.append({'test': test.id(), 'result': 'PASS'})
        def addFailure(self, test, error):
            super().addFailure(test, error)
            cases.append({'test': test.id(), 'result': 'FAIL', 'detail': self._exc_info_to_string(error, test)})
        def addError(self, test, error):
            super().addError(test, error)
            cases.append({'test': test.id(), 'result': 'ERROR', 'detail': self._exc_info_to_string(error, test)})
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(CustodyTests)
    assert suite.countTestCases() == 17
    result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(suite)
    measurement = benchmark() if result.wasSuccessful() and result.testsRun == 17 else None
    guard()
    report = {'schema_version': 'lab-descriptor-byte-custody-checks/v1-candidate',
              'result': 'PASS' if measurement is not None else 'FAIL',
              'tests_run': result.testsRun, 'expected_tests': 17, 'cases': cases,
              'actual_full_closure_measurement': measurement, 'source_sha256': args.source_sha256,
              'Context_or_API_or_Agent_qualified': False, 'authority_effect': 'none',
              'actual_owner_outcome': None, 'task_complete': False}
    out = HERE / 'receipts'
    out.mkdir(mode=0o700, exist_ok=True)
    with (out / 'checks-0001.json').open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': report['result'], 'actual_cases': result.testsRun,
                      'measurement': measurement}), flush=True)
    raise SystemExit(0 if report['result'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
