"""Cryptographic authentication and real handler/domain/error conformance guards."""
from contextlib import ExitStack
import copy
import tempfile
import unittest
from unittest.mock import patch
from fixtures import *
from service import *


class ApiGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stack=ExitStack();cls.root=Path(cls.stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-R03-api-unit-')))
        cls.key,cls.policy,cls.policy_sha=provision(cls.root);cls.schemas=Schemas()
        cls.view=cls.stack.enter_context(source.replay_source('engineering'))
    @classmethod
    def tearDownClass(cls):cls.stack.close()
    def setUp(self):
        self.channel=ReaderChannel(self.policy,self.policy_sha,self.schemas)
        self.authenticated=self.channel.authenticate(proof(self.key,self.channel.challenge))
        self.service=Service(self.view,self.channel,self.schemas)
    def tearDown(self):self.service.close()
    def invoke(self,operation='lab.status',**changes):
        c=call(self.channel.context,operation,cut(self.view) if operation=='catalog.get' else None,**changes)
        return self.service.call(compact(c)),c

    def test_actual_signature_authenticates(self):
        self.assertTrue(self.schemas.valid('trusted-call-context',self.channel.context))
        self.assertEqual(self.channel.context['principal_ref'],'principal:R03-api-fixture-reader')
        self.assertEqual(self.channel.context['origin'],'verified-local-adapter')
    def test_challenge_one_use(self):
        with self.assertRaises(Exception):self.channel.authenticate(proof(self.key,self.channel.challenge))
    def test_wrong_key_not_authenticated(self):
        channel=ReaderChannel(self.policy,self.policy_sha,self.schemas)
        with self.assertRaises(Exception):channel.authenticate(proof(Ed25519PrivateKey.generate(),channel.challenge))
        self.assertIsNone(channel.context)
    def test_cross_connection_challenge_rejected(self):
        channel=ReaderChannel(self.policy,self.policy_sha,self.schemas)
        with self.assertRaises(Exception):channel.authenticate(proof(self.key,self.channel.challenge))
    def test_tampered_policy_pin_rejected(self):
        with self.assertRaises(Exception):ReaderChannel(self.policy,'0'*64,self.schemas)
    def test_policy_revocation_invalidates_calls(self):
        raw=self.policy.read_bytes()
        try:
            value=frame_parse(raw);value['revoked']=True;self.policy.write_bytes(compact(value))
            result,_=self.invoke();self.assertEqual(result['code'],'unauthenticated-channel')
        finally:self.policy.write_bytes(raw)
    def test_policy_expiry_invalidates_calls(self):
        self.channel.context['expires_at']='2000-01-01T00:00:00Z'
        result,_=self.invoke();self.assertEqual(result['code'],'unauthenticated-channel')
    def test_closed_context_erased(self):
        self.service.close();self.assertIsNone(self.channel.context);self.assertIsNone(self.channel.nonce)
    def test_no_private_credentials_or_session_memory_context(self):
        self.assertFalse(self.channel.context['private_credentials_in_context'])
        self.assertIsNone(self.channel.context['session_ref']);self.assertIsNone(self.channel.context['agent_instance_ref'])
    def test_status_actual_result_conforms(self):
        result,_=self.invoke();self.assertEqual(result['kind'],'result');self.assertTrue(self.schemas.valid('api-reply',result))
        self.assertEqual(result['message']['source_cut'],cut(self.view))
    def test_status_support_is_actual_two_operations(self):
        result,_=self.invoke();self.assertEqual(result['message']['supported_operations'],list(SUPPORTED))
        self.assertEqual(result['message']['implementation_posture'],'implemented-local')
        self.assertTrue(result['message']['gaps'])
    def test_status_null_bootstrap_cut(self):
        result,c=self.invoke();self.assertIsNone(c['expected_source_cut']);self.assertEqual(result['message']['source_cut'],cut(self.view))
    def test_status_supplied_historical_cut_exact(self):
        selected=cut(self.service.handlers.available_views[0]);c=call(self.channel.context,'lab.status',selected)
        r=self.service.call(compact(c));self.assertEqual(r['kind'],'result');self.assertEqual(r['message']['source_cut'],selected)
        self.assertEqual(selected['commit_sequence'],0)
        self.assertTrue(all(s['cursor']==5 for s in selected['streams']))
        self.assertEqual(self.view.data['head']['sequence'],1)
    def test_catalog_supplied_historical_cut_exact(self):
        selected=cut(self.service.handlers.available_views[0]);c=call(self.channel.context,'catalog.get',selected,limit=143)
        r=self.service.call(compact(c));self.assertEqual(r['kind'],'result');self.assertEqual(r['message']['source_cut'],selected)
        self.assertEqual(len(r['message']['contract_entries']),143)
    def test_cursor_cannot_cross_verified_historical_cuts(self):
        r,_=self.invoke('catalog.get');cursor=r['message']['next_page_cursor']
        selected=cut(self.service.handlers.available_views[0]);c=call(self.channel.context,'catalog.get',selected,page_cursor=cursor)
        self.assertEqual(self.service.call(compact(c))['message']['code'],'invalid-cursor')
    def test_status_scope_not_authorized(self):
        result,_=self.invoke(scope_refs=['scope:unrelated']);self.assertEqual(result['message']['code'],'unauthorized')
    def test_actor_claim_cannot_grant_authority(self):
        c=call(self.channel.context,'lab.status');c['message']['actor']['principal_ref']='role:repository-owner'
        result=self.service.call(compact(c));self.assertEqual(result['message']['code'],'unauthorized')
    def test_role_claim_mismatch_rejected(self):
        c=call(self.channel.context,'lab.status');c['message']['actor']['role_assignment_refs']=[{'ref':'role:owner','sha256':'0'*64}]
        result=self.service.call(compact(c));self.assertEqual(result['message']['code'],'unauthorized')
    def test_opaque_context_substitution_rejected(self):
        c=call(self.channel.context,'lab.status');c['caller_context_ref']='context:other'
        result=self.service.call(compact(c));self.assertEqual(result['message']['code'],'unauthorized')
    def test_client_authority_object_rejected(self):
        c=call(self.channel.context,'lab.status');c['trusted_context']={'principal_ref':'owner'}
        self.assertEqual(self.service.call(compact(c))['code'],'invalid-envelope')
    def test_wire_and_inner_message_bindings_distinct(self):
        c=call(self.channel.context,'lab.status');raw=compact(c);result=self.service.call(raw)
        self.assertEqual(result['request_binding']['sha256'],source.sha(raw))
        self.assertEqual(result['message']['request_binding']['sha256'],source.sha(message_bytes(raw)))
        self.assertNotEqual(result['request_binding']['sha256'],result['message']['request_binding']['sha256'])
    def test_received_message_whitespace_preserved(self):
        c=call(self.channel.context,'lab.status');raw=json.dumps(c,separators=(', ',': ')).encode()
        result=self.service.call(raw);self.assertEqual(result['message']['request_binding']['sha256'],source.sha(message_bytes(raw)))
        self.assertNotEqual(message_bytes(raw),compact(c['message']))
    def test_utf8_message_span_preserved(self):
        c=call(self.channel.context,'lab.status');c['message']['request_ref']='request:áção'
        raw=json.dumps(c,ensure_ascii=False,separators=(', ',': ')).encode();r=self.service.call(raw)
        self.assertEqual(r['message']['request_binding']['sha256'],source.sha(message_bytes(raw)))
    def test_reply_context_exact_server_binding(self):
        r,_=self.invoke();self.assertEqual(r['trusted_context_binding'],binding(self.channel.context['context_ref'],compact(self.channel.context)))
    def test_reply_handler_binding_real_bytes(self):
        r,_=self.invoke();self.assertEqual(r['handler_binding']['sha256'],source.sha((HERE/'handlers.py').read_bytes()))
    def test_unknown_operation_is_not_success(self):
        c=call(self.channel.context,'lab.status');c['operation']='not.real'
        self.assertEqual(self.service.call(compact(c))['code'],'unsupported-operation')
    def test_declared_unimplemented_operation_explicit(self):
        c=call(self.channel.context,'lab.status');c['operation']='artifact.inspect'
        self.assertEqual(self.service.call(compact(c))['code'],'unsupported-operation')
    def test_unknown_protocol_rejected(self):
        c=call(self.channel.context,'lab.status');c['schema_version']='unknown'
        self.assertEqual(self.service.call(compact(c))['code'],'unsupported-protocol')
    def test_duplicate_call_id_rejected(self):
        c=call(self.channel.context,'lab.status');raw=compact(c);self.assertEqual(self.service.call(raw)['kind'],'result')
        self.assertEqual(self.service.call(raw)['code'],'invalid-call-id')
    def test_invalid_call_id_rejected(self):
        c=call(self.channel.context,'lab.status');c['call_id']='bad id'
        self.assertEqual(self.service.call(compact(c))['code'],'invalid-call-id')
    def test_duplicate_json_key_rejected(self):
        self.assertEqual(self.service.call(b'{"a":1,"a":2}')['code'],'malformed-json')
    def test_nonfinite_number_rejected(self):
        for raw in [b'{"a":NaN}',b'{"a":Infinity}']:
            self.assertEqual(self.service.call(raw)['code'],'malformed-json')
    def test_invalid_utf8_rejected(self):
        self.assertEqual(self.service.call(b'{"a":"\xff"}')['code'],'malformed-json')
    def test_surrogate_and_nul_rejected(self):
        for raw in [b'{"a":"\\ud800"}',b'{"a":"\\u0000"}']:
            self.assertEqual(self.service.call(raw)['code'],'malformed-json')
    def test_excessive_depth_rejected(self):
        self.assertEqual(self.service.call(b'['*40+b'0'+b']'*40)['code'],'malformed-json')
    def test_large_integer_rejected(self):
        self.assertEqual(self.service.call(b'{"a":9223372036854775808}')['code'],'malformed-json')
    def test_oversized_request_rejected(self):
        self.assertEqual(self.service.call(b'x'*65537)['code'],'input-too-large')
    def test_expired_deadline_rejected_before_handler(self):
        c=call(self.channel.context,'lab.status');c['deadline']='2000-01-01T00:00:00Z'
        with patch.object(self.service.handlers,'status',side_effect=AssertionError('must not dispatch')):
            self.assertEqual(self.service.call(compact(c))['message']['code'],'deadline-exceeded')
    def test_inner_deadline_strictest(self):
        c=call(self.channel.context,'lab.status');c['message']['budget']['deadline']='2000-01-01T00:00:00Z'
        self.assertEqual(self.service.call(compact(c))['message']['code'],'deadline-exceeded')
    def test_zero_action_reader_enforced(self):
        c=call(self.channel.context,'lab.status');c['message']['budget']['max_actions']=1
        self.assertEqual(self.service.call(compact(c))['message']['code'],'unauthorized')
    def test_input_budget_enforced(self):
        c=call(self.channel.context,'lab.status');c['message']['budget']['max_input_bytes']=1
        self.assertEqual(self.service.call(compact(c))['message']['code'],'budget-exceeded')
    def test_response_budget_no_partial_result(self):
        r,_=self.invoke('catalog.get',limit=143);c=call(self.channel.context,'catalog.get',cut(self.view),limit=143)
        self.assertEqual(r['kind'],'result');c['max_response_bytes']=4096
        denied=self.service.call(compact(c));self.assertEqual(denied['kind'],'error')
        self.assertEqual(denied['message']['code'],'budget-exceeded');self.assertNotIn('contract_entries',denied['message'])
    def test_stale_cut_rejected(self):
        c=call(self.channel.context,'catalog.get',cut(self.view));c['expected_source_cut']['commit_sha256']='0'*64
        self.assertEqual(self.service.call(compact(c))['message']['code'],'stale-cut')
    def test_outer_inner_cut_disagreement_rejected(self):
        c=call(self.channel.context,'catalog.get',cut(self.view));c['expected_source_cut']=copy.deepcopy(c['expected_source_cut']);c['expected_source_cut']['commit_sha256']='0'*64
        self.assertEqual(self.service.call(compact(c))['message']['code'],'invalid-contract')
    def test_changed_sources_stale_not_current(self):
        with patch.object(self.view.handle.sources,'freshness',return_value={'status':'stale','changed':['source-drift']}):
            r,_=self.invoke();self.assertEqual(r['message']['code'],'stale-cut')
    def test_catalog_actual_result_conforms(self):
        r,_=self.invoke('catalog.get');self.assertEqual(r['kind'],'result');self.assertTrue(self.schemas.valid('api-reply',r))
        self.assertEqual(len(r['message']['contract_entries']),20);self.assertEqual(len(r['message']['relation_signatures']),41)
    def test_catalog_exact_schema_descriptor_bytes(self):
        r,_=self.invoke('catalog.get',limit=143)
        for entry in r['message']['contract_entries']:
            for key in ['schema_binding','descriptor_binding']:
                self.assertEqual(source.sha((ROOT/entry[key]['ref']).read_bytes()),entry[key]['sha256'])
        self.assertEqual(len(r['message']['contract_entries']),143)
    def test_catalog_historical_posture_retained(self):
        r,_=self.invoke('catalog.get',limit=143)
        self.assertTrue(any(e['write_posture']=='historical-read-only' for e in r['message']['contract_entries']))
    def test_catalog_relation_signature_binding_exact(self):
        r,_=self.invoke('catalog.get');
        for entry in r['message']['relation_signatures']:
            self.assertEqual(source.sha((ROOT/entry['signature_binding']['ref']).read_bytes()),entry['signature_binding']['sha256'])
    def test_catalog_explicit_selection(self):
        r,_=self.invoke('catalog.get',carrier_refs=['cal.artifact-type.project-identity/v1'])
        self.assertEqual([e['carrier_ref'] for e in r['message']['contract_entries']],['cal.artifact-type.project-identity/v1'])
    def test_catalog_relations_omitted_when_not_requested(self):
        r,_=self.invoke('catalog.get',include_relations=False);self.assertEqual(r['message']['relation_signatures'],[])
    def test_catalog_paging_exact_nonoverlap(self):
        r,_=self.invoke('catalog.get',limit=10);first=r['message'];r,_=self.invoke('catalog.get',limit=10,page_cursor=first['next_page_cursor'])
        self.assertFalse({e['carrier_ref'] for e in first['contract_entries']} & {e['carrier_ref'] for e in r['message']['contract_entries']})
    def test_cursor_substitution_rejected(self):
        r,_=self.invoke('catalog.get',page_cursor='cursor:forged');self.assertEqual(r['message']['code'],'invalid-cursor')
    def test_cursor_filter_change_rejected(self):
        r,_=self.invoke('catalog.get');cursor=r['message']['next_page_cursor'];r,_=self.invoke('catalog.get',include_relations=False,page_cursor=cursor)
        self.assertEqual(r['message']['code'],'invalid-cursor')
    def test_cursor_page_size_change_rejected(self):
        r,_=self.invoke('catalog.get');cursor=r['message']['next_page_cursor'];r,_=self.invoke('catalog.get',limit=30,page_cursor=cursor)
        self.assertEqual(r['message']['code'],'invalid-cursor')
    def test_cursor_other_connection_rejected(self):
        r,_=self.invoke('catalog.get');cursor=r['message']['next_page_cursor']
        channel=ReaderChannel(self.policy,self.policy_sha,self.schemas);channel.authenticate(proof(self.key,channel.challenge));svc=Service(self.view,channel,self.schemas)
        try:
            c=call(channel.context,'catalog.get',cut(self.view),page_cursor=cursor);self.assertEqual(svc.call(compact(c))['message']['code'],'invalid-cursor')
        finally:svc.close()
    def test_catalog_large_page_budget_rejected(self):
        r,_=self.invoke('catalog.get',limit=1001);self.assertEqual(r['message']['code'],'budget-exceeded')
    def test_unknown_message_field_rejected(self):
        c=call(self.channel.context,'lab.status');c['message']['extra']=True
        self.assertEqual(self.service.call(compact(c))['code'],'invalid-envelope')
    def test_read_idempotency_key_rejected(self):
        c=call(self.channel.context,'lab.status');c['idempotency_key']='key:write'
        self.assertEqual(self.service.call(compact(c))['code'],'invalid-envelope')
    def test_transport_errors_validate(self):
        for code in ['malformed-json','invalid-envelope','unauthenticated-channel','unsupported-protocol','unsupported-operation','invalid-call-id','input-too-large','deadline-exceeded']:
            self.assertTrue(self.schemas.valid('transport-error',transport(code)))


if __name__=='__main__':unittest.main(verbosity=2)
