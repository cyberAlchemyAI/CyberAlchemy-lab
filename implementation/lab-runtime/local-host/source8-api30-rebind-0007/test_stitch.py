"""Pure negative probes of the bounded T02 sequential evidence join."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

import stitch as S


class StitchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a = json.loads(S.PINS['v4_result'][0].read_bytes())
        cls.b = json.loads(S.PINS['v5_result'][0].read_bytes())
        cls.failed = json.loads(S.PINS['v6_result'][0].read_bytes())
        ids = cls.a['selected_case_ids'][85:]
        cls.c = {'result': 'PASS', 'predecessor_v6_result_sha256': S.PINS['v6_result'][1],
                 'runner_sha256': S.PINS['v8_runner'][1],
                 'source_manifest_sha256': S.PINS['source_manifest'][1],
                 'profile_sha256': S.PINS['contract_profile'][1],
                 'source_unchanged_during_run': True,
                 'started_at_utc': '2026-10-23T08:39:41+00:00',
                 'completed_at_utc': '2026-10-23T08:39:42+00:00',
                 'selected_case_ids': ids, 'tests_run': 14,
                 'case_rows': [{'test_id': ident, 'result': 'PASS'} for ident in ids],
                 'split_seven_read_evidence': [
                     {'first_operations': ['lab.status', 'catalog.get', 'artifact.query', 'artifact.inspect'],
                      'second_operations': ['context.get', 'session.inspect', 'operation.inspect'],
                      'first_session_ref_sha256': 'a' * 64,
                      'second_session_ref_sha256': 'b' * 64,
                      'fresh_second_context_delivery': True,
                      'original_session_expiry_unchanged': True}],
                 'failures': [], 'errors': []}

    def check_refusal(self, change, message):
        a, b, failed, c = deepcopy((self.a, self.b, self.failed, self.c))
        change(a, b, c)
        with self.assertRaisesRegex(ValueError, message):
            S.reconcile(a, b, failed, c)

    def test_01_exact_synthetic_join(self):
        self.assertEqual(S.reconcile(self.a, self.b, self.failed, self.c)['passed_case_count'], 99)

    def test_02_duplicate_machine_row_refused(self):
        self.check_refusal(lambda a, b, c: c['case_rows'].__setitem__(1, c['case_rows'][0]),
                           'v8 14-case evidence differs')

    def test_03_missing_machine_row_refused(self):
        self.check_refusal(lambda a, b, c: c['case_rows'].pop(),
                           'v8 14-case evidence differs')

    def test_04_changed_source_during_machine_refused(self):
        self.check_refusal(lambda a, b, c: c.__setitem__('source_unchanged_during_run', False),
                           'v8 14-case evidence differs')

    def test_05_prior_case_swap_refused(self):
        self.check_refusal(lambda a, b, c: b['case_rows'].__setitem__(0, b['case_rows'][1]),
                           'v5 corrected negative/17-case evidence differs')

    def test_06_wrong_origin_negative_missing_refused(self):
        self.check_refusal(lambda a, b, c: a.__setitem__('wrong_origin_old_source_refused', False),
                           'v4 source or harness evidence differs')

    def test_07_changed_predecessor_binding_refused(self):
        self.check_refusal(lambda a, b, c: c.__setitem__('predecessor_v6_result_sha256', '0' * 64),
                           'v8 14-case evidence differs')

    def test_08_expired_source_completion_refused(self):
        self.check_refusal(lambda a, b, c: c.__setitem__(
            'completed_at_utc', '2026-10-23T20:31:06+00:00'),
            'sequential source-period chronology differs')

    def test_09_same_session_reuse_refused(self):
        self.check_refusal(lambda a, b, c: c['split_seven_read_evidence'][0].__setitem__(
            'second_session_ref_sha256', 'a' * 64),
            'v8 real split-Session proof differs')


if __name__ == '__main__':
    unittest.main()
