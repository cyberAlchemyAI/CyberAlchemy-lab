"""Public classification against actual signed source and owned transport."""
import copy
import unittest
import uuid

from . import classification_fixture as CF, protocol as P, workspace as W, auth as A
from .guard import verify

SOURCE = None
PROFILE = None


class ClassificationAPI(unittest.TestCase):
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
        return self.enterContext(CF.example(self.view, self.schemas, **kwargs))

    def invoke(self, host, request):
        raw = P.compact(request)
        reply = host.call(raw)
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
            if isinstance(row, dict) and row.get('schema_version') == 'lab-classification-rule-checks/v1-candidate':
                result.append(row)
        return result

    def journal(self, host):
        return {path.name: path.read_bytes() for path in (host.vault.root / 'journal').glob('*') if path.is_file()}

    def assert_live(self, host, request):
        host.channel.guard()
        self.assertLess(A.now(), A.instant(request['deadline']))

    def assert_preclaim_error(self, host, request, code):
        before = self.journal(host)
        reply = self.invoke(host, request)
        self.assertEqual(reply['kind'], 'error', reply)
        self.assertEqual(reply['message']['code'], code, reply)
        self.assertEqual(self.journal(host), before)
        self.assert_live(host, request)

    def test_01_exact_original_ChangeProposal_result(self):
        host, request, selected = self.example()
        reply = self.invoke(host, request)
        self.assertEqual(reply['kind'], 'result', reply)
        self.assertEqual(reply['message'], selected['proposal'])
        self.assertTrue(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:change-proposal:v1-candidate', reply['message']))
        self.assertEqual(len(reply['message']['targets']), 5)
        self.assertEqual(reply['handler_binding']['ref'], str((CF.HERE / 'classification_preparation.py').relative_to(CF.ROOT)))
        rules = self.rules(host)
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0]['result'], 'pass')
        self.assertEqual(rules[0]['complete_postimage_assignment_refs'], [])
        self.assert_live(host, request)

    def test_02_rules_do_not_claim_runtime_causality_or_authority(self):
        host, request, _ = self.example()
        self.assertEqual(self.invoke(host, request)['kind'], 'result')
        checked = self.rules(host)[0]
        self.assertEqual({row['rule'] for row in checked['checks']},
                         {'one-active-value-per-subject-axis', 'annotation-never-grants-authority'})
        self.assertFalse(checked['runtime_conformance_proven'])
        self.assertFalse(checked['causality_proven'])
        self.assertEqual(checked['authority_effect'], 'none')
        self.assertIsNone(checked['actual_owner_outcome'])
        self.assertEqual(checked['original_source_cut'], request['expected_source_cut'])
        self.assertEqual(checked['record_basis'], 'current-plus-exact-prospective-postimage')

    def test_03_exact_retry_does_not_redispatch(self):
        host, request, _ = self.example()
        first = self.invoke(host, request)
        self.assertEqual(first['kind'], 'result', first)
        before = self.journal(host)
        request['call_id'] = 'call:classification:retry:' + uuid.uuid4().hex
        second = self.invoke(host, request)
        self.assertEqual(second['kind'], 'result', second)
        self.assertEqual(second['message'], first['message'])
        self.assertEqual(self.journal(host), before)
        self.assertEqual(len(self.rules(host)), 1)
        self.assert_live(host, request)

    def test_04_same_key_different_control_inputs_conflicts(self):
        host, request, _ = self.example()
        self.assertEqual(self.invoke(host, request)['kind'], 'result')
        request['call_id'] = 'call:classification:conflict:' + uuid.uuid4().hex
        request['message']['axis_ref'] = 'axis:different-control-input'
        self.assert_preclaim_error(host, request, 'idempotency-conflict')

    def test_05_public_Actor_cannot_replace_transport_identity(self):
        host, request, _ = self.example()
        request['message']['actor']['principal_ref'] = 'principal:claimed-owner'
        self.assert_preclaim_error(host, request, 'unauthorized')
        self.assertIsNone(host.channel.context['agent_instance_ref'])
        self.assertEqual(host.channel.context['role_assignment_bindings'], [])

    def test_06_missing_operator_grant_refuses_before_claim(self):
        host, request, _ = self.example(grant=False)
        before = self.journal(host)
        reply = self.invoke(host, request)
        self.assertEqual(reply['schema_version'], 'lab-api-transport-error/v1-candidate')
        self.assertEqual(reply['code'], 'unsupported-operation')
        self.assertFalse(reply['effect_may_have_started'])
        self.assertEqual(self.journal(host), before)
        self.assert_live(host, request)

    def test_07_wrong_selected_assignment_bytes_refuse_before_claim(self):
        host, request, _ = self.example()
        request['message']['assignment_candidate_binding']['sha256'] = '0' * 64
        self.assert_preclaim_error(host, request, 'invalid-contract')

    def test_08_other_prospective_assignment_participates_in_cardinality(self):
        host, request, _ = self.example(mode='conflict')
        reply = self.invoke(host, request)
        self.assertEqual(reply['kind'], 'error', reply)
        self.assertEqual(reply['message']['code'], 'conflict')
        checked = self.rules(host)[0]
        self.assertEqual(checked['result'], 'fail')
        self.assertEqual(len(checked['complete_postimage_assignment_refs']), 1)
        self.assertTrue(any(row['rule'] == 'one-active-value-per-subject-axis' and row['result'] == 'fail'
                            and 'already occupies' in row['reason'] for row in checked['checks']))
        self.assertEqual(len(list((host.vault.root / 'journal').glob('*.claim.json'))), 1)
        self.assertEqual(len(list((host.vault.root / 'journal').glob('*.result.json'))), 1)
        self.assertTrue(reply['message']['evidence_bindings'])
        self.assert_live(host, request)

    def test_09_independent_axis_is_preserved(self):
        host, request, selected = self.example(mode='independent-axis')
        reply = self.invoke(host, request)
        self.assertEqual(reply['kind'], 'result', reply)
        checked = self.rules(host)[0]
        self.assertEqual(checked['result'], 'pass')
        self.assertEqual(len(checked['complete_postimage_assignment_refs']), 1)
        self.assertEqual(checked['axis_ref'], request['message']['axis_ref'])
        self.assertEqual(reply['message'], selected['proposal'])
        self.assertEqual(len(reply['message']['targets']), 9)
        from collections import Counter
        counts=Counter(t['artifact']['carrier_ref'] for t in reply['message']['targets'])
        self.assertEqual(counts, {'cal.artifact-type.classification-scheme/v1':1,
            'cal.artifact-type.classification-value/v1':2,
            'cal.artifact-type.classification-assignment/v1':2,
            'cal.artifact-type.typed-relation/v3':4})
        relations=[t for t in reply['message']['targets']
                   if t['artifact']['carrier_ref']=='cal.artifact-type.typed-relation/v3']
        connections=reply['message']['connection_proposals']
        self.assertEqual(len(connections),4)
        from .artifact_model import signature
        for target,connection in zip(relations,connections,strict=True):
            content=target['content']
            raw=host.vault.material({'ref':content['content_ref'],'sha256':content['byte_sha256']})
            body=P.frame_parse(raw);payload=body['payload']
            contract,binding=signature(host.handlers.view,payload['relation_kind_ref'])
            self.assertEqual(connection['relation_kind_ref'],payload['relation_kind_ref'])
            self.assertEqual(connection['signature_sha256'],binding['sha256'])
            self.assertEqual(connection['axis_ref'],contract['payload']['axis_id'])
            self.assertIn({'source_kind':payload['source']['kind'],
                           'target_kind':payload['target']['kind']},
                          contract['payload']['allowed_endpoint_pairs'])
            self.assertEqual(connection['qualifiers'],payload['qualifiers'])
            for end in ['source','target']:
                self.assertEqual(connection[end]['semantic_kind'],payload[end]['kind'])
                self.assertEqual(connection[end]['artifact']['identity_ref'],payload[end]['ref'])
                self.assertEqual(connection[end]['artifact']['version_ref'],payload[end]['version_ref'])
        self.assert_live(host, request)

    def test_10_missing_other_assignment_reference_is_retained_and_refused(self):
        host, request, _ = self.example(mode='missing-reference')
        reply = self.invoke(host, request)
        self.assertEqual(reply['kind'], 'error', reply)
        checked = self.rules(host)[0]
        self.assertEqual(checked['result'], 'fail')
        self.assertEqual(len(checked['complete_postimage_assignment_refs']), 1)
        self.assertTrue(any(row['result'] == 'fail' and 'missing or ambiguous' in row['reason'] for row in checked['checks']))
        self.assert_live(host, request)

    def test_11_unknown_declared_rule_is_not_a_pass(self):
        host, request, _ = self.example(mode='unknown-rule')
        reply = self.invoke(host, request)
        self.assertEqual(reply['kind'], 'error', reply)
        self.assertEqual(reply['message']['code'], 'closure-missing')
        checked = self.rules(host)[0]
        self.assertEqual(checked['result'], 'not-evaluable')
        self.assertTrue(any(row['rule'] == 'unselected-classification-rule' and row['result'] == 'not-evaluable'
                            for row in checked['checks']))
        self.assert_live(host, request)

    def test_12_wrong_original_stable_core_is_not_classified(self):
        host, request, _ = self.example(mode='bad-core')
        reply = self.invoke(host, request)
        self.assertEqual(reply['kind'], 'error', reply)
        self.assertEqual(self.rules(host), [])
        reports = [P.frame_parse(path.read_bytes()) for path in (host.vault.root / 'objects').glob('*.json')]
        self.assertTrue(any(isinstance(row, dict) and row.get('schema_version') == 'lab-validation-report/v1-candidate'
                            and row['result'] == 'fail' for row in reports))
        self.assert_live(host, request)

    def test_13_schema_invalid_assignment_is_not_classified(self):
        host, request, _ = self.example(mode='invalid-schema')
        reply = self.invoke(host, request)
        self.assertEqual(reply['kind'], 'error', reply)
        self.assertEqual(self.rules(host), [])
        reports = [P.frame_parse(path.read_bytes()) for path in (host.vault.root / 'objects').glob('*.json')]
        self.assertTrue(any(isinstance(row, dict) and row.get('schema_version') == 'lab-validation-report/v1-candidate'
                            and row['result'] == 'fail' for row in reports))
        self.assert_live(host, request)

    def test_14_changed_bound_routing_refuses_before_claim(self):
        host, request, selected = self.example()
        binding = selected['routing_binding']
        path = host.vault.root / 'objects' / (binding['sha256'] + '.json')
        before = self.journal(host)
        path.write_bytes(path.read_bytes() + b' ')
        reply = self.invoke(host, request)
        self.assertEqual(reply['code'], 'unauthenticated-channel')
        self.assertEqual(self.journal(host), before)
        self.assertFalse(reply['effect_may_have_started'])

    def test_15_known_failed_rule_result_retries_without_redispatch(self):
        host, request, _ = self.example(mode='conflict')
        first = self.invoke(host, request)
        self.assertEqual(first['message']['code'], 'conflict')
        before = self.journal(host)
        self.assertEqual(self.rules(host)[0]['result'], 'fail')
        request['call_id'] = 'call:classification:failed:' + uuid.uuid4().hex
        reply = self.invoke(host, request)
        self.assertEqual(reply['kind'], 'error', reply)
        self.assertEqual(reply['message'], first['message'])
        self.assertEqual(self.journal(host), before)
        self.assertEqual(len(self.rules(host)), 1)
        self.assert_live(host, request)

    def test_16_uncertain_core_failure_stays_pending_without_redispatch(self):
        host, request, _ = self.example(mode='bad-core')
        first = self.invoke(host, request)
        self.assertEqual(first['kind'], 'error', first)
        self.assertEqual(first['message']['code'], 'indeterminate')
        before = self.journal(host)
        self.assertEqual(self.rules(host), [])
        request['call_id'] = 'call:classification:pending:' + uuid.uuid4().hex
        reply = self.invoke(host, request)
        self.assertEqual(reply['message']['code'], 'recovery-required')
        self.assertEqual(self.journal(host), before)
        self.assertEqual(list((host.vault.root / 'journal').glob('*.result.json')), [])
        self.assert_live(host, request)

    def test_17_pending_native_evidence_is_inspectable_and_tamper_refused(self):
        host, request, _ = self.example(mode='bad-core')
        first=self.invoke(host,request)
        self.assertEqual(first['message']['code'],'indeterminate',first)
        before=self.journal(host)
        self.assertEqual(list((host.vault.root/'journal').glob('*.result.json')),[])
        inspect=copy.deepcopy(request)
        inspect['call_id']='call:pending:inspect:'+uuid.uuid4().hex
        inspect['operation']='operation.inspect';inspect['idempotency_key']=None
        inspect['message']={'schema_version':'lab-operation-inspect-request/v1-candidate',
            'request_ref':'request:pending-inspection', 'actor':copy.deepcopy(request['message']['actor']),
            'budget':{'max_actions':0,
                'max_input_bytes':host.channel.context['limits']['max_request_bytes'],
                'max_output_bytes':host.channel.context['limits']['max_response_bytes'],
                'deadline':host.channel.context['limits']['deadline']},'authority_effect':'none',
            'lookup':{'operation':'classification.prepare','idempotency_key':request['idempotency_key']}}
        reply=self.invoke(host,inspect)
        self.assertEqual(reply['kind'],'result',reply)
        result=reply['message']
        self.assertEqual(result['posture'],'indeterminate')
        self.assertIsNone(result['result_binding'])
        self.assertTrue(result['reconciliation_required'])
        self.assertFalse(result['retry_allowed'])
        reports=[]
        for binding in result['effect_evidence_bindings'][1:]:
            body=P.frame_parse(host.vault.object_read(binding))
            if body.get('schema_version')=='lab-validation-report/v1-candidate':reports.append(body)
        self.assertEqual(len(reports),1)
        self.assertEqual(reports[0]['result'],'fail')
        self.assertEqual(self.journal(host),before)
        retry=copy.deepcopy(request);retry['call_id']='call:pending:retry:'+uuid.uuid4().hex
        self.assertEqual(self.invoke(host,retry)['message']['code'],'recovery-required')
        self.assertEqual(self.journal(host),before)
        pending=next((host.vault.root/'journal').glob('*.pending-evidence.json'))
        original=pending.read_bytes()
        altered=P.frame_parse(original);altered['claim_sha256']='0'*64
        pending.write_bytes(P.compact(altered))
        inspect['call_id']='call:pending:tamper:'+uuid.uuid4().hex
        try:
            refused=self.invoke(host,inspect)
            self.assertEqual(refused['kind'],'error',refused)
            self.assertEqual(refused['message']['code'],'integrity-failed')
            self.assertEqual(refused['message']['evidence_bindings'],[])
        finally:pending.write_bytes(original)
        self.assertEqual(self.journal(host),before)
        self.assertEqual(self.rules(host),[])
        self.assert_live(host,request)
