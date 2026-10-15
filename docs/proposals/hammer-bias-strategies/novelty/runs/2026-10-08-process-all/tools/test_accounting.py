import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('accounting', Path(__file__).with_name('accounting.py'))
accounting = importlib.util.module_from_spec(spec)
spec.loader.exec_module(accounting)


class AccountingTests(unittest.TestCase):
    def test_failed_saved_and_causal_skips_remain_separate(self):
        jobs = [{'job_id': i, 'stage': 'main', 'case_id': 'X', 'role': role}
                for i, role in [('a', 'A'), ('d', 'D')]]
        states = {'a': {'status': 'failed'}, 'd': {'status': 'skipped'}}
        events = [{'event': 'spawn', 'job_id': 'a', 'agent': '/root/a'},
                  {'event': 'join', 'job_id': 'a', 'terminal_observed': True,
                   'known_words': 12, 'sha256': 'failed-bytes'}]
        result = accounting.summarize(jobs, states, events)
        self.assertEqual(result['attempts'], 2)
        self.assertEqual(result['native_spawns'], 1)
        self.assertEqual(result['native_terminal_joins'], 1)
        self.assertEqual(result['states'], {'failed': 1, 'skipped': 1})
        self.assertEqual(result['known_saved_words'], 12)
        self.assertIsNone(result['rows'][1]['known_saved_words'])


if __name__ == '__main__':
    unittest.main()
