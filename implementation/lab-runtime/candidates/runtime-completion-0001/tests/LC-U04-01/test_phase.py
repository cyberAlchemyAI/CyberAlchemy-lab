"""Inert C03/R05 refusal tests; no actual source, permission, or worker effects."""
import copy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
import tempfile
import unittest

S = Path(__file__).absolute().parents[2]
R = S.parents[3]
DEPS = R / 'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004/deps'
sys.path[:0] = [str(S / 'contracts'), str(S / 'selectors'), str(S / 'diagnostics'),
                str(S / 'callers'), str(DEPS)]
from lab_contracts.codec import Refusal, canonical, sha
from lab_contracts.validation import validate
from lab_selectors.anchors import RootAnchor, AnchoredReader, identity
from lab_selectors.chains import phase_remaining
from phase import begin_phase, finish_phase
from uncertainty import FailureChain, classify_reply


def stamp(delta):
    return (datetime.now(timezone.utc) + timedelta(seconds=delta)).isoformat()


def ref(n):
    return {'kind': 'execution', 'root_id': 'fixture', 'relative_path': f'{n}.json',
            'sha256': 'a' * 64, 'size_bytes': 1}


class Cases(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='owned-phase-', dir=Path(__file__).parent)
        self.root = Path(self.temp.name)
        self.budget = {'schema_version': 'lab-completion-diagnostic-bounds/v1',
                       'attempt_id': 'fixture-attempt',
                       'phase_caps': [{'phase_id': 'inspect', 'hard_cap_ms': 1000,
                                       'max_staged_effect_bytes': 0}],
                       'total_cap_ms': 5000, 'cleanup_reserve_ms': 500,
                       'load_binding': ref('load'), 'justification_binding': ref('justification'),
                       'review_binding': ref('independent-review'),
                       'kill_reap_policy_binding': ref('kill-reap'), 'no_extra_effects': True}
        self.persist()

    def tearDown(self):
        self.temp.cleanup()

    def persist(self):
        raw = canonical(self.budget)
        (self.root / 'budget.json').write_bytes(raw)
        self.binding = {'kind': 'execution', 'root_id': 'fixture', 'relative_path': 'budget.json',
                        'sha256': sha(raw), 'size_bytes': len(raw)}
        self.reader = AnchoredReader([RootAnchor('fixture', str(self.root),
                                                 identity(self.root.stat()))], [self.binding])
        self.permit = {'schema_version': 'lab-completion-phase-permit/v1', 'phase_id': 'inspect',
                       'mode': 'diagnostic', 'diagnostic_bounds_binding': self.binding,
                       'measured_budget_binding': None, 'intent_binding': ref('intent'),
                       'execution_selection_binding': ref('execution'),
                       'slot_receipt_binding': ref('slot'), 'prior_receipt_bindings': [],
                       'input_bindings': [], 'allowed_output_roots': ['fixture'],
                       'expected_output_names': [], 'effect_kind': 'none',
                       'principal_permission_binding': ref('permission'),
                       'reviewer_acceptance_binding': ref('acceptance'),
                       'not_before': stamp(-10), 'expires_at': stamp(30),
                       'cleanup_reserve_seconds': 1}

    def begin(self, **kw):
        return begin_phase(self.reader, self.permit, self.binding,
                           source_deadline=stamp(20), permission_deadline=stamp(20),
                           current_guard=lambda: True, **kw)

    def test_zero_sample_diagnostic_is_observed_not_qualified(self):
        start = self.begin()
        result = finish_phase(start, outcome='success', effect_state='none',
                              containment_terminal=True, cleanup_state='complete')
        self.assertFalse(result['timing_qualified'])
        self.assertFalse(result['censored'])
        self.assertGreaterEqual(result['monotonic_elapsed_ns'], 0)
        self.assertEqual(result['load_binding'], self.budget['load_binding'])

    def test_expired_permission_and_permit_refuse_before_effect(self):
        with self.assertRaisesRegex(Refusal, 'DEADLINE_EXPIRED'):
            begin_phase(self.reader, self.permit, self.binding,
                        source_deadline=stamp(20), permission_deadline=stamp(-1),
                        current_guard=lambda: True)
        self.permit['expires_at'] = stamp(-1)
        with self.assertRaisesRegex(Refusal, 'PERMIT_NOT_CURRENT'):
            self.begin()

    def test_guard_must_be_present_and_selected_budget_exact(self):
        with self.assertRaisesRegex(Refusal, 'CURRENT_GUARD_REQUIRED'):
            begin_phase(self.reader, self.permit, self.binding,
                        source_deadline=stamp(20), permission_deadline=stamp(20))
        with self.assertRaisesRegex(Refusal, 'INDEPENDENT_BUDGET_BINDING'):
            begin_phase(self.reader, self.permit, ref('wrong'),
                        source_deadline=stamp(20), permission_deadline=stamp(20),
                        current_guard=lambda: True)
        with self.assertRaisesRegex(Refusal, 'CURRENT_GUARD_REFUSED'):
            begin_phase(self.reader, self.permit, self.binding,
                        source_deadline=stamp(20), permission_deadline=stamp(20),
                        current_guard=lambda: False)

    def test_cap_cleanup_and_total_strict_equality_refuse(self):
        self.budget['total_cap_ms'] = 2000
        self.persist()
        # Equality: elapsed 0 + cap 1000 + permit reserve 1000 == total 2000.
        with self.assertRaisesRegex(Refusal, 'INSUFFICIENT_WHOLE_ATTEMPT_BUDGET'):
            self.begin()
        self.budget['total_cap_ms'] = 5000
        self.persist()
        with self.assertRaisesRegex(Refusal, 'INSUFFICIENT_WHOLE_ATTEMPT_BUDGET'):
            self.begin(elapsed_attempt_ms=3000)

    def test_missing_finite_cap_and_duplicate_phase_refuse(self):
        self.budget['phase_caps'] = []
        self.persist()
        with self.assertRaisesRegex(Refusal, 'SCHEMA_DiagnosticBounds'):
            self.begin()
        self.budget['phase_caps'] = [
            {'phase_id': 'inspect', 'hard_cap_ms': 1000, 'max_staged_effect_bytes': 0},
            {'phase_id': 'inspect', 'hard_cap_ms': 2000, 'max_staged_effect_bytes': 0}]
        self.persist()
        with self.assertRaisesRegex(Refusal, 'DUPLICATE_PHASE'):
            self.begin()

    def test_timeout_or_lost_reply_is_censored_unknown_and_no_retry(self):
        start = self.begin()
        for outcome, received in [('timeout', True), ('success', False)]:
            result = finish_phase(start, outcome=outcome, effect_state='none',
                                  containment_terminal=False, cleanup_state='unknown',
                                  response_received=received)
            self.assertEqual(result['outcome'], 'censored')
            self.assertEqual(result['effect_state'], 'unknown')
            self.assertFalse(result['timing_qualified'])
            self.assertFalse(result['retry_allowed'])

    def test_unknown_success_never_proves_qualification_or_retry(self):
        start = self.begin()
        result = finish_phase(start, outcome='success', effect_state='unknown',
                              containment_terminal=True, cleanup_state='complete')
        self.assertFalse(result['timing_qualified'])
        self.assertFalse(result['retry_allowed'])
        self.assertTrue(result['censored'])
        self.assertFalse(result['continue_positive'])
        chain = FailureChain(effect_state='unknown')
        self.assertFalse(chain.public()['retry_allowed'])

    def test_deadline_after_start_is_censored_without_erasing_effect(self):
        from dataclasses import replace
        start = replace(self.begin(), strictest_deadline_utc=stamp(-1))
        result = finish_phase(start, outcome='success', effect_state='observed',
                              containment_terminal=True, cleanup_state='complete')
        self.assertTrue(result['censored'])
        self.assertTrue(result['deadline_passed_after_start'])
        self.assertEqual(result['effect_state'], 'unknown')
        self.assertTrue(result['observed_partial_effect'])

    def test_wall_clock_discontinuity_is_censored(self):
        from dataclasses import replace
        start = replace(self.begin(), started_at_utc=stamp(-30))
        result = finish_phase(start, outcome='success', effect_state='none',
                              containment_terminal=True, cleanup_state='complete')
        self.assertTrue(result['clock_discontinuity'])
        self.assertEqual(result['effect_state'], 'unknown')

    def test_backward_utc_second_read_refuses_pre_effect(self):
        from unittest.mock import patch
        now = datetime.now(timezone.utc)
        with patch('phase._utc_now', side_effect=[now, now - timedelta(seconds=2)]):
            with self.assertRaisesRegex(Refusal, 'UTC_CLOCK_MOVED_BACKWARD'):
                self.begin()

    def test_qualification_requires_measured_selected_budget(self):
        wrong = copy.deepcopy(self.permit)
        wrong['mode'] = 'qualification'
        with self.assertRaisesRegex(Refusal, 'BUDGET_MODE'):
            validate('PhasePermit', wrong)

    def test_primary_survives_caller_cleanup_and_lost_reply(self):
        chain = FailureChain()
        chain.primary('SOURCE_EXPIRED')
        chain.caller('CALLER_EXCEPTION')
        chain.cleanup('CLEANUP_EXCEPTION')
        chain.lost_response()
        self.assertEqual(chain.public()['primary_failure'], 'SOURCE_EXPIRED')
        self.assertEqual(chain.public()['effect_state'], 'unknown')
        self.assertFalse(chain.public()['retry_allowed'])
        self.assertEqual(chain.protected()['cleanup_failures'], ['CLEANUP_EXCEPTION'])
        with self.assertRaisesRegex(Refusal, 'FAILURE_CODE'):
            chain.caller('secret: token=123')

    def test_expired_lesson_select_transport_has_no_message_keyerror(self):
        reply = {'schema_version': 'lab-api-transport-error/v1-candidate',
                 'call_id': 'lesson:select:expired', 'request_byte_sha256': 'a' * 64,
                 'code': 'deadline-exceeded', 'public_message': 'Deadline expired.',
                 'effect_may_have_started': False, 'recovery_policy': 'no-retry',
                 'authority_effect': 'none'}
        classified = classify_reply(reply, operation_id='lesson:select:owned')
        self.assertEqual(classified['state'], 'unknown')
        classified = classify_reply(reply, operation_id='lesson:select:owned',
                                    expected_call_id='lesson:select:expired',
                                    expected_request_sha256='a' * 64)
        self.assertEqual(classified['state'], 'refused-no-effect')
        self.assertIsNone(classified['inspect_operation_id'])
        self.assertFalse(classified['retry_allowed'])

    def test_uncertain_transport_requires_exact_inspection_not_retry(self):
        reply = {'schema_version': 'lab-api-transport-error/v1-candidate',
                 'call_id': 'call:owned', 'request_byte_sha256': 'a' * 64,
                 'code': 'deadline-exceeded', 'public_message': 'Inspect operation.',
                 'effect_may_have_started': True, 'recovery_policy': 'inspect-first',
                 'authority_effect': 'none'}
        classified = classify_reply(reply, operation_id='operation:owned',
                                    expected_call_id='call:owned',
                                    expected_request_sha256='a' * 64)
        self.assertEqual(classified['state'], 'unknown')
        self.assertEqual(classified['inspect_operation_id'], 'operation:owned')
        self.assertFalse(classified['retry_allowed'])
        self.assertFalse(classified['continue_positive'])

    def test_incomplete_or_foreign_transport_never_clears_effect(self):
        envelope = {'schema_version': 'lab-api-transport-error/v1-candidate',
                    'code': 'deadline-exceeded', 'effect_may_have_started': False,
                    'recovery_policy': 'no-retry'}
        for reply in [envelope, {**envelope, 'call_id': 'foreign',
                 'request_byte_sha256': 'a' * 64, 'public_message': 'Expired.',
                 'authority_effect': 'none'},
                 {**envelope, 'call_id': 'call:owned',
                  'request_byte_sha256': 'a' * 64, 'public_message': 'Expired.',
                  'authority_effect': 'some-effect'}]:
            with self.subTest(reply=reply):
                result = classify_reply(reply, operation_id='operation:owned',
                                        expected_call_id='call:owned',
                                        expected_request_sha256='a' * 64)
                self.assertEqual(result['state'], 'unknown')
                self.assertEqual(result['inspect_operation_id'], 'operation:owned')

    def test_unverified_domain_result_cannot_claim_completion(self):
        reply = {'schema_version': 'lab-api-reply/v2-candidate', 'kind': 'result',
                 'call_id': 'call:owned', 'operation': 'lesson.select',
                 'request_binding': {'sha256': 'a' * 64},
                 'message': {'posture': 'completed'}}
        self.assertEqual(classify_reply(reply, operation_id='operation:owned')['state'],
                         'unknown')
        self.assertEqual(classify_reply(reply, operation_id='operation:owned',
                                        expected_call_id='call:owned',
                                        expected_request_sha256='a' * 64,
                                        expected_operation='lesson.select',
                                        domain_verified=True)['state'], 'completed')
        reply['kind'] = None
        self.assertEqual(classify_reply(reply, operation_id='operation:owned',
                                        expected_call_id='call:owned',
                                        expected_request_sha256='a' * 64,
                                        expected_operation='lesson.select',
                                        domain_verified=True)['state'], 'unknown')
        reply['kind'] = 'result'
        for changed in [{'operation': 'session.close'},
                        {'request_binding': {'sha256': 'b' * 64}}]:
            foreign = {**reply, **changed}
            self.assertEqual(classify_reply(foreign, operation_id='operation:owned',
                                            expected_call_id='call:owned',
                                            expected_request_sha256='a' * 64,
                                            expected_operation='lesson.select',
                                            domain_verified=True)['state'], 'unknown')

    def test_incomplete_containment_retains_uncertain_observation(self):
        start = self.begin()
        result = finish_phase(start, outcome='success', effect_state='none',
                              containment_terminal=False, cleanup_state='unknown')
        self.assertEqual(result['outcome'], 'censored')
        self.assertEqual(result['effect_state'], 'unknown')
        self.assertFalse(result['continue_positive'])


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Cases))
    print(json.dumps({'schema_version': 'lab-case-command-result/v1',
                      'result': 'PASS' if result.wasSuccessful() else 'FAIL',
                      'checks': result.testsRun, 'effect_state': 'owned-inert', 'cleanup': 'clean'}))
    sys.exit(0 if result.wasSuccessful() else 1)
