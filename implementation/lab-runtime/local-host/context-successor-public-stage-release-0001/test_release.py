"""Inert release tests; production stage entrypoint is never invoked."""
import types
import unittest
from unittest import mock

import release as R


class ReleaseTests(unittest.TestCase):
    def test_live_basis_and_read_only_preflight(self):
        stage = R.basis()
        self.assertFalse(stage.EFFECT_ENABLED)
        result = R._strict_preflight(stage)
        self.assertEqual(result['rows'], 1570)
        self.assertEqual(result['directories'], 1021)
        self.assertEqual(result['auth'], 'UNMINTED_UNSELECTED')
        self.assertEqual(result['selection_reads']['mapped_package_buffers'], 55)
        self.assertFalse(R.ATTEMPT.exists())

    def test_exact_checked_source_buffer_executed(self):
        actual = R._module
        observed = []
        def capture(raw):
            observed.append(R.sha(raw))
            return actual(raw)
        with mock.patch.object(R, '_module', side_effect=capture):
            R.basis()
        self.assertEqual(observed, [R.STAGE_CODE_SHA])

    def test_one_shot_route_and_effect_reset(self):
        calls = []
        stage = types.SimpleNamespace(EFFECT_ENABLED=False)
        def run():
            self.assertTrue(stage.EFFECT_ENABLED)
            calls.append('run')
            return {'status':'PROVISIONAL_STAGE_ONLY_EXTERNAL_OS_REVIEW_REQUIRED',
                    'files':1570,'directories':1021,'attempt':str(R.ATTEMPT),
                    'retry_allowed':False}
        stage.run_effect = run
        with mock.patch.object(R,'basis',return_value=stage), \
             mock.patch.object(R,'_strict_preflight',return_value={'attempt':str(R.ATTEMPT)}):
            result = R.execute_reviewed_one_shot()
        self.assertEqual(calls,['run'])
        self.assertFalse(stage.EFFECT_ENABLED)
        self.assertFalse(result['retry_allowed'])

    def test_preflight_failure_never_enables_or_runs(self):
        stage = types.SimpleNamespace(EFFECT_ENABLED=False,
                                      run_effect=mock.Mock(side_effect=AssertionError('ran')))
        with mock.patch.object(R,'basis',return_value=stage), \
             mock.patch.object(R,'_strict_preflight',side_effect=R.Refused('STALE')):
            with self.assertRaisesRegex(R.Refused,'STALE'):
                R.execute_reviewed_one_shot()
        self.assertFalse(stage.EFFECT_ENABLED)
        stage.run_effect.assert_not_called()

    def test_postterminal_close_failure_propagates(self):
        stage = types.SimpleNamespace(EFFECT_ENABLED=False)
        def fail():
            self.assertTrue(stage.EFFECT_ENABLED)
            raise OSError('final descriptor close uncertain')
        stage.run_effect = fail
        with mock.patch.object(R,'basis',return_value=stage), \
             mock.patch.object(R,'_strict_preflight',return_value={'attempt':str(R.ATTEMPT)}):
            with self.assertRaisesRegex(OSError,'final descriptor close uncertain'):
                R.execute_reviewed_one_shot()
        self.assertFalse(stage.EFFECT_ENABLED)

    def test_noninteger_provisional_result_rejected(self):
        stage = types.SimpleNamespace(EFFECT_ENABLED=False)
        stage.run_effect = lambda:{'status':'PROVISIONAL_STAGE_ONLY_EXTERNAL_OS_REVIEW_REQUIRED',
                                   'files':1570.0,'directories':1021,
                                   'attempt':str(R.ATTEMPT),'retry_allowed':False}
        with mock.patch.object(R,'basis',return_value=stage), \
             mock.patch.object(R,'_strict_preflight',return_value={'attempt':str(R.ATTEMPT)}):
            with self.assertRaisesRegex(R.Refused,'PROVISIONAL_STAGE_RESULT'):
                R.execute_reviewed_one_shot()
        self.assertFalse(stage.EFFECT_ENABLED)

    def test_authority_jit_and_docker_refused(self):
        for fn in (R.issue_authority,R.jit_or_docker):
            with self.assertRaises(R.Refused):
                fn()


if __name__ == '__main__':
    unittest.main()
