"""Cold serial coordinator checks; no inherited regression is run."""

import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('t16_api53_coordinator_v2', HERE / 'run_all.py')
coordinator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(coordinator)
IDS = ['sample.py:Cases.test_01', 'sample.py:Cases.test_02']


def result():
    return {
        'schema_version': 'lab-t16-api53-serial-bucket/v1',
        'bucket': 'sample.py:Cases', 'run_id': 'sample', 'selected_ids': IDS,
        'source_sha256': coordinator.SOURCE_SHA, 'profile_sha256': coordinator.PROFILE_SHA,
        'inventory_sha256': coordinator.INVENTORY_SHA, 'runner_sha256': coordinator.WORKER_SHA,
        'result': 'PASS', 'tests_run': 2, 'exact_case_set': True,
        'all_methods_executed': True, 'entry_guard_passed': True,
        'exit_guard_passed': True,
        'cases': [{'id': identity, 'result': 'PASS', 'executed': True} for identity in IDS],
    }


class ColdCoordinator(unittest.TestCase):
    def test_exact_pass_requires_successful_process(self):
        coordinator.validate_worker_result(result(), 'sample.py:Cases', 'sample', IDS, 0, False)
        with self.assertRaisesRegex(ValueError, 'process and guard proof'):
            coordinator.validate_worker_result(result(), 'sample.py:Cases', 'sample', IDS, 1, False)
        with self.assertRaisesRegex(ValueError, 'process and guard proof'):
            coordinator.validate_worker_result(result(), 'sample.py:Cases', 'sample', IDS, None, True)

    def test_guard_or_case_omission_cannot_pass(self):
        for change in ({'exit_guard_passed': False}, {'tests_run': 1},
                       {'all_methods_executed': False}):
            candidate = result()
            candidate.update(change)
            with self.assertRaisesRegex(ValueError, 'process and guard proof'):
                coordinator.validate_worker_result(candidate, 'sample.py:Cases', 'sample', IDS, 0, False)

    def test_changed_selection_refuses(self):
        candidate = result()
        candidate['source_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'selection or case set differs'):
            coordinator.validate_worker_result(candidate, 'sample.py:Cases', 'sample', IDS, 0, False)
        with self.assertRaisesRegex(ValueError, 'selected byte differs'):
            coordinator.selected_inventory('0' * 64)

    def test_malformed_result_cannot_abort_accounting(self):
        with self.assertRaisesRegex(ValueError, 'object required'):
            coordinator.validate_worker_result([], 'sample.py:Cases', 'sample', IDS, 0, False)
        candidate = result()
        candidate['cases'][1] = None
        with self.assertRaisesRegex(ValueError, 'selection or case set differs'):
            coordinator.validate_worker_result(candidate, 'sample.py:Cases', 'sample', IDS, 0, False)

    def test_truthful_failure_preserves_case_rows(self):
        candidate = result()
        candidate['result'] = 'FAIL'
        candidate['cases'][1]['result'] = 'FAIL'
        coordinator.validate_worker_result(candidate, 'sample.py:Cases', 'sample', IDS, 1, False)
        with self.assertRaisesRegex(ValueError, 'disagrees with process exit'):
            coordinator.validate_worker_result(candidate, 'sample.py:Cases', 'sample', IDS, 0, False)


if __name__ == '__main__':
    unittest.main(verbosity=2)
