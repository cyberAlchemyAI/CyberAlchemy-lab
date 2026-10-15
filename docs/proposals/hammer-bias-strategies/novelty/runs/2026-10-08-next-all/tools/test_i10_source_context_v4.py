"""Unscored counterexamples to incomplete-stage admission."""
import unittest
from copy import deepcopy
from i10_source_context_v4 import stage_coverage


def fixture():
    gs = {'RAW': 'valid', 'D': 'valid'}
    rs = {'RF': 'valid'}
    events = []
    for k in ['RAW', 'D', 'RF']:
        events.extend([{'event_kind': 'native_spawn', 'job_id': k},
                       {'event_kind': 'native_terminal_join', 'job_id': k,
                        'terminal_observed': True, 'validation': {'valid': True}}])
    return gs, rs, events


class StageCoverage(unittest.TestCase):
    def test_exact_valid_execution(self):
        self.assertTrue(stage_coverage(*fixture())['complete'])

    def test_invalid_raw_and_D_excluded(self):
        for key in ['RAW', 'D']:
            data = fixture();data[0][key] = 'invalid'
            next(e for e in data[2] if e['event_kind'] == 'native_terminal_join' and e['job_id'] == key)['validation']['valid'] = False
            self.assertFalse(stage_coverage(*data)['complete'])

    def test_skipped_missing_ready_D_excluded_without_invalid_output(self):
        for state in ['skipped', 'pending', 'ready']:
            gs, rs, events = fixture();gs['D'] = state
            events = [e for e in events if e['job_id'] != 'D']
            result = stage_coverage(gs, rs, events)
            self.assertFalse(result['complete'])
            self.assertFalse(result['exact_terminal_coverage'])

    def test_invalid_review_excluded(self):
        data = fixture();data[1]['RF'] = 'invalid'
        self.assertFalse(stage_coverage(*data)['complete'])

    def test_duplicate_start_or_terminal_excluded(self):
        for kind in ['native_spawn', 'native_terminal_join']:
            data = fixture();data[2].append(deepcopy(next(e for e in data[2] if e['event_kind'] == kind)))
            self.assertFalse(stage_coverage(*data)['complete'])

    def test_file_or_unobserved_terminal_cannot_substitute_for_actual_final(self):
        data = fixture();data[2][1]['terminal_observed'] = False
        self.assertFalse(stage_coverage(*data)['complete'])


if __name__ == '__main__':
    unittest.main()
