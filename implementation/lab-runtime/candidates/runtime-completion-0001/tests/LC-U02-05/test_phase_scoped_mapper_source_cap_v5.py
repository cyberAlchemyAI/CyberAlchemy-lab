"""Source-only v5 timing policy; no Source/Reader/Mapper fixture effect."""
from __future__ import annotations

from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from t35_external_v1.path_contract import ContractError
from t35_external_v1.phase_scoped_v2 import mapper_build_refusal_0005 as candidate


class MapperSourceCapV5Tests(unittest.TestCase):
    def test_source_240_is_allowed_and_later_240_is_rejected_before_launch(self):
        rc, stdout, stderr, source = candidate._run_child(
            [sys.executable, '-c', 'print("ok")'], stage='source', timeout=240)
        self.assertEqual((rc, stdout, stderr), (0, b'ok\n', b''))
        self.assertEqual(source['timeout_cap_seconds'], 240)
        self.assertTrue(source['reaped_observed'])
        self.assertTrue(source['process_group_absent_observed'])
        self.assertEqual(candidate._safe_children({'source': source}, complete=False),
                         {'source': source})
        for stage in ('reader', 'mapper_readonly', 'mapper_build_guard'):
            with self.subTest(stage=stage), \
                 patch.object(candidate.subprocess, 'Popen',
                              side_effect=AssertionError('must not launch')):
                with self.assertRaises(ContractError):
                    candidate._run_child(
                        [sys.executable, '-c', 'pass'], stage=stage, timeout=240)
            self.assertEqual(candidate._remaining_stage_seconds(None, stage=stage), 180)
            with self.assertRaises(ContractError):
                candidate._safe_children({stage: source}, complete=False)
        self.assertEqual(candidate.RECEIPT_NAME,
                         'phase-mapper-build-refusal-result-0005.json')

    def test_stage_cap_is_clamped_by_unchanged_900_second_aggregate(self):
        self.assertEqual(candidate.milestone.PAIR_WALL_SECONDS, 900)
        with patch.object(candidate.time, 'monotonic', return_value=100.0):
            self.assertEqual(candidate._remaining_stage_seconds(None, stage='source'), 240)
            self.assertEqual(candidate._remaining_stage_seconds(1000.0, stage='source'), 240)
            self.assertEqual(candidate._remaining_stage_seconds(1000.0, stage='reader'), 180)
            self.assertEqual(candidate._remaining_stage_seconds(131.9, stage='source'), 31)
            self.assertEqual(candidate._remaining_stage_seconds(131.9,
                             stage='mapper_build_guard'), 31)
            with self.assertRaises(ContractError):
                candidate._remaining_stage_seconds(101.0, stage='source')
            with self.assertRaises(ContractError):
                candidate._remaining_stage_seconds(1000.0, stage='context')

    def test_source_timeout_still_refuses_success(self):
        rc, _, _, observed = candidate._run_child(
            [sys.executable, '-c', 'import time;time.sleep(2)'],
            stage='source', timeout=1)
        self.assertEqual(rc, 124)
        self.assertTrue(observed['forced_timeout'])
        self.assertTrue(observed['forced_group_cleanup'])
        self.assertTrue(observed['reaped_observed'])
        self.assertTrue(observed['process_group_absent_observed'])
        with self.assertRaises(ContractError):
            candidate._safe_children({'source': observed}, complete=True)


if __name__ == '__main__':
    unittest.main()
