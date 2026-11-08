"""Synthetic tests for honest terminal accounting; no signed Source replay."""

import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('t16_api53_worker', HERE / 'run_bucket.py')
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)
IDS = ['sample.py:Cases.test_01', 'sample.py:Cases.test_02', 'sample.py:Cases.test_03']


class TerminalRows(unittest.TestCase):
    def test_setup_error_never_counts_methods_executed(self):
        rows, exact, executed = worker.terminalize(IDS, [], [{'fixture': 'setUpClass', 'result': 'ERROR'}], 0, None, 'now')
        self.assertTrue(exact)
        self.assertFalse(executed)
        self.assertEqual([row['result'] for row in rows], ['SETUP-ERROR'] * 3)
        self.assertTrue(all(row['executed'] is False for row in rows))

    def test_partial_worker_preserves_real_case_and_marks_rest(self):
        actual = {'id': IDS[0], 'result': 'PASS', 'executed': True,
                  'started_at_utc': 'start', 'ended_at_utc': 'end'}
        rows, exact, executed = worker.terminalize(IDS, [actual], [], 1, 'interrupted', 'now')
        self.assertTrue(exact)
        self.assertFalse(executed)
        self.assertIs(rows[0], actual)
        self.assertEqual([row['result'] for row in rows[1:]], ['WORKER-INTERRUPTED'] * 2)

    def test_all_pass_is_fully_executed_only_with_exact_count(self):
        actual = [{'id': identity, 'result': 'PASS', 'executed': True} for identity in IDS]
        self.assertEqual(worker.terminalize(IDS, actual, [], 3, None, 'now')[1:], (True, True))
        self.assertEqual(worker.terminalize(IDS, actual, [], 2, None, 'now')[1:], (True, False))

    def test_duplicate_or_foreign_actual_refuses(self):
        with self.assertRaisesRegex(ValueError, 'ID set differs'):
            worker.terminalize(IDS, [{'id': IDS[0]}, {'id': IDS[0]}], [], 2, None, 'now')
        with self.assertRaisesRegex(ValueError, 'ID set differs'):
            worker.terminalize(IDS, [{'id': 'foreign'}], [], 1, None, 'now')


if __name__ == '__main__':
    unittest.main(verbosity=2)
