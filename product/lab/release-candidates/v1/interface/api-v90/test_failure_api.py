"""Full actual public failure preparation, with explicit uncertainty and cleanup."""
import copy
import unittest
import uuid

from . import failure_fixture as FF, protocol as P, workspace as W, auth as A
from .guard import verify

SOURCE = None
PROFILE = None


class FailureAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        verify(SOURCE)
        cls.schemas = P.Schemas(PROFILE)
        cls.manager = P.source.replay_source('custody-participation')
        cls.view = cls.manager.__enter__()
        cls.projection = P.compact(cls.view.data['projection'])
        cls.observations = []

    @classmethod
    def tearDownClass(cls):
        assert P.compact(cls.view.data['projection']) == cls.projection
        cls.manager.__exit__(None, None, None)
        verify(SOURCE)

    def example(self, **kwargs):
        return self.enterContext(FF.example(self.view, self.schemas, **kwargs))

    def invoke(self, host, request):
        raw = P.compact(request); reply = host.call(raw)
        from .fixture_observation import record
        record(self.id(), host, raw, reply)
        W.privacy(reply)
        if 'kind' in reply:
            self.assertTrue(self.schemas.valid('api-reply', reply), reply)
            self.assertEqual(reply['request_binding']['sha256'], P.source.sha(raw))
        self.observations.append({'request': copy.deepcopy(request), 'reply': copy.deepcopy(reply)})
        return reply

    def rules(self, host):
        result = []
        for path in (host.vault.root / 'objects').glob('*.json'):
            raw = W.read_private(path)
            self.assertEqual(path.stem, P.source.sha(raw))
            row = P.frame_parse(raw)
            if isinstance(row, dict) and row.get('schema_version') == 'lab-failure-assessment-rule-checks/v1-candidate':
                result.append(row)
        return result

    def journal(self, host):
        return {path.name: path.read_bytes() for path in (host.vault.root / 'journal').glob('*') if path.is_file()}

    def assert_live(self, host, request):
        host.channel.guard()
        self.assertLess(A.now(), A.instant(request['deadline']))

    def preclaim_error(self, host, request, code):
        before = self.journal(host); reply = self.invoke(host, request)
        self.assertEqual(reply['kind'], 'error', reply)
        self.assertEqual(reply['message']['code'], code, reply)
        self.assertEqual(self.journal(host), before)
        self.assert_live(host, request)

    def test_01_exact_original_ChangeProposal_and_connections(self):
        host, request, selected = self.example()
        reply = self.invoke(host, request)
        self.assertEqual(reply['kind'], 'result', reply)
        self.assertEqual(reply['message'], selected['proposal'])
        self.assertEqual(len(reply['message']['targets']), 13)
        self.assertEqual(len(reply['message']['connection_proposals']), 5)
        self.assertTrue(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:change-proposal:v1-candidate', reply['message']))
        self.assertEqual(self.rules(host)[0]['result'], 'pass')
        self.assertEqual(reply['handler_binding']['ref'], str((FF.HERE / 'failure_preparation.py').relative_to(FF.ROOT)))
        self.assert_live(host, request)

    def test_02_axes_and_evidence_do_not_supply_cause_or_effectiveness(self):
        host, request, _ = self.example()
        self.assertEqual(self.invoke(host, request)['kind'], 'result')
        checked = self.rules(host)[0]
        self.assertEqual(set(checked['axis_claims']), {'occurrence', 'mode', 'cause', 'impact', 'containment', 'recovery', 'uncertainty'})
        self.assertFalse(checked['confirmed_cause_inferred'])
        self.assertFalse(checked['recovery_or_control_effectiveness_inferred'])
        self.assertFalse(checked['incident_threshold']['Incident_created'])
        self.assertEqual(checked['authority_effect'], 'none')
        self.assertIsNone(checked['actual_owner_outcome'])

    def test_03_missed_threshold_preserves_valid_assessment(self):
        host, request, _ = self.example(mode='threshold-missed')
        self.assertEqual(self.invoke(host, request)['kind'], 'result')
        checked = self.rules(host)[0]
        self.assertEqual(checked['result'], 'pass')
        self.assertEqual(checked['incident_threshold']['result'], 'fail')
        self.assertFalse(checked['incident_threshold']['eligible_under_declared_rule'])
        self.assertEqual(checked['axis_claims']['recovery'], 'not-attempted')

    def test_04_met_threshold_creates_no_Incident(self):
        host, request, _ = self.example(mode='threshold-met')
        self.assertEqual(self.invoke(host, request)['kind'], 'result')
        threshold = self.rules(host)[0]['incident_threshold']
        self.assertTrue(threshold['eligible_under_declared_rule'])
        self.assertFalse(threshold['Incident_created'])

    def test_05_unknown_threshold_is_not_evaluable(self):
        host, request, _ = self.example(mode='threshold-unknown')
        reply = self.invoke(host, request)
        self.assertEqual(reply['kind'], 'error', reply)
        self.assertEqual(reply['message']['code'], 'closure-missing')
        self.assertEqual(self.rules(host)[0]['result'], 'not-evaluable')
        self.assertIsNone(self.rules(host)[0]['incident_threshold']['eligible_under_declared_rule'])
        self.assert_live(host, request)

    def test_06_recovery_claim_coexists_with_unconfirmed_cause(self):
        host, request, _ = self.example(mode='independent-recovery')
        self.assertEqual(self.invoke(host, request)['kind'], 'result')
        checked = self.rules(host)[0]
        self.assertEqual(checked['axis_claims']['recovery'], 'authored-recovered-with-residue')
        self.assertEqual(checked['axis_claims']['cause'], [request['message']['cause_hypothesis_refs'][0]['version_ref']])
        self.assertFalse(checked['confirmed_cause_inferred'])

    def test_07_exact_retry_has_no_new_dispatch(self):
        host, request, _ = self.example()
        first = self.invoke(host, request); self.assertEqual(first['kind'], 'result', first)
        before = self.journal(host); request['call_id'] = 'call:failure:retry:' + uuid.uuid4().hex
        second = self.invoke(host, request)
        self.assertEqual(second['message'], first['message'])
        self.assertEqual(self.journal(host), before)
        self.assertEqual(len(self.rules(host)), 1)
        self.assert_live(host, request)

    def test_08_same_key_different_inputs_conflicts(self):
        host, request, _ = self.example()
        self.assertEqual(self.invoke(host, request)['kind'], 'result')
        request['call_id'] = 'call:failure:conflict:' + uuid.uuid4().hex
        request['message']['request_ref'] += ':different'
        self.preclaim_error(host, request, 'idempotency-conflict')

    def test_09_public_Actor_cannot_replace_transport(self):
        host, request, _ = self.example()
        request['message']['actor']['principal_ref'] = 'principal:forged-owner'
        self.preclaim_error(host, request, 'unauthorized')

    def test_10_missing_grant_refuses_before_claim(self):
        host, request, _ = self.example(grant=False)
        before = self.journal(host); reply = self.invoke(host, request)
        self.assertEqual(reply['code'], 'unsupported-operation')
        self.assertFalse(reply['effect_may_have_started'])
        self.assertEqual(self.journal(host), before)
        self.assert_live(host, request)

    def test_11_wrong_candidate_binding_refuses_before_claim(self):
        host, request, _ = self.example()
        request['message']['assessment_candidate_binding']['sha256'] = '0' * 64
        self.preclaim_error(host, request, 'invalid-contract')

    def test_12_full_postimage_annotation_conflict_is_recorded(self):
        host, request, _ = self.example(mode='conflict')
        reply = self.invoke(host, request)
        self.assertEqual(reply['message']['code'], 'conflict')
        self.assertEqual(self.rules(host)[0]['result'], 'fail')
        self.assert_live(host, request)

    def test_13_known_failure_retries_without_dispatch(self):
        host, request, _ = self.example(mode='unknown-rule')
        first = self.invoke(host, request)
        self.assertEqual(first['message']['code'], 'closure-missing')
        before = self.journal(host); request['call_id'] = 'call:failure:known:' + uuid.uuid4().hex
        second = self.invoke(host, request)
        self.assertEqual(second['message'], first['message'])
        self.assertEqual(self.journal(host), before)
        self.assertEqual(len(self.rules(host)), 1)
        self.assert_live(host, request)

    def test_14_uncertain_core_failure_stays_pending(self):
        host, request, _ = self.example(mode='bad-core')
        first = self.invoke(host, request)
        self.assertEqual(first['message']['code'], 'indeterminate')
        self.assertEqual(self.rules(host), [])
        before = self.journal(host); request['call_id'] = 'call:failure:pending:' + uuid.uuid4().hex
        second = self.invoke(host, request)
        self.assertEqual(second['message']['code'], 'recovery-required')
        self.assertEqual(self.journal(host), before)
        self.assert_live(host, request)

    def test_15_invalid_schema_is_never_assessed(self):
        host, request, _ = self.example(mode='invalid-schema')
        reply = self.invoke(host, request)
        self.assertEqual(reply['kind'], 'error', reply)
        self.assertEqual(self.rules(host), [])
        reports = [P.frame_parse(path.read_bytes()) for path in (host.vault.root / 'objects').glob('*.json')]
        self.assertTrue(any(isinstance(row, dict) and row.get('schema_version') == 'lab-validation-report/v1-candidate' and row['result'] == 'fail' for row in reports))
        self.assert_live(host, request)

    def test_16_changed_routing_refuses_authentication(self):
        host, request, selected = self.example()
        binding = selected['routing_binding']; path = host.vault.root / 'objects' / (binding['sha256'] + '.json')
        before = self.journal(host); path.write_bytes(path.read_bytes() + b' ')
        reply = self.invoke(host, request)
        self.assertEqual(reply['code'], 'unauthenticated-channel')
        self.assertFalse(reply['effect_may_have_started'])
        self.assertEqual(self.journal(host), before)

    def test_17_threshold_cannot_be_caller_selected(self):
        host, request, _ = self.example(mode='threshold-met')
        request['message']['incident_threshold_binding']['sha256'] = '0' * 64
        self.preclaim_error(host, request, 'invalid-contract')

    def test_18_expired_caller_deadline_creates_no_journal(self):
        host, request, _ = self.example()
        request['deadline'] = '2000-01-01T00:00:00+00:00'
        before = self.journal(host); reply = self.invoke(host, request)
        self.assertEqual(reply['message']['code'], 'deadline-exceeded')
        self.assertEqual(self.journal(host), before)
        host.channel.guard()
