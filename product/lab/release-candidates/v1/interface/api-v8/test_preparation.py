"""Real prospective validation plus durable invocation and independent auth guards."""
from contextlib import ExitStack
import copy
import os
import tempfile
import unittest
from unittest.mock import patch
from example_fixture import *
from service import *

class Preparation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stack=ExitStack();cls.addClassCleanup(cls.stack.close)
        cls.view=cls.stack.enter_context(source.replay_source('reference-corrected'));cls.schemas=Schemas()
        cls.materials,cls.metadata,cls.target=materials_for(cls.view)
    def setUp(self):
        self.stack=ExitStack();self.addCleanup(self.stack.close)
        self.root=Path(self.stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-R03-preparation-test-')))
        self.key,self.policy,self.pin=provision(self.root,'reference-corrected',self.materials,self.metadata)
        self.channel=ReaderChannel(self.policy,self.pin,self.schemas);self.channel.authenticate(proof(self.key,self.channel.challenge))
        self.service=Service(self.view,self.channel,self.schemas);self.addCleanup(self.service.close)
    def prepare(self,key='fixture:prepare'):
        c=candidate_call(self.service,self.target,key=key);return self.service.call(compact(c)),c
    def inspect(self,key='fixture:prepare',**changes):
        c=call(self.channel.context,'operation.inspect',None,lookup={'operation':'change.prepare','idempotency_key':key},**changes)
        return self.service.call(compact(c)),c
    def test_actual_prepare_stages_exact_diff(self):
        r,c=self.prepare();self.assertEqual(r['kind'],'result',r);self.assertEqual(r['message']['posture'],'blocked')
        diff=source.parse(self.service.vault.object_read(r['message']['example_bindings'][0]))
        self.assertEqual(diff['targets'][0]['artifact'],c['message']['targets'][0]['artifact']);self.assertIsNone(diff['targets'][0]['before'])
        self.assertEqual(diff['targets'][0]['effective_admission'],'unadmitted-candidate')
    def test_actual_validation_uses_runtime_and_no_authority(self):
        c=candidate_call(self.service,self.target,'change.validate','validate:1');r=self.service.call(compact(c))
        self.assertEqual(r['kind'],'result',r);self.assertEqual(r['message']['result'],'not-evaluable',r)
        self.assertEqual(r['message']['authority_effect'],'none');self.assertIn('No owner approval',r['message']['claim_ceiling'])
    def test_no_signed_source_mutation(self):
        before=copy.deepcopy(self.view.data);self.prepare();self.assertEqual(self.view.data,before)
    def test_exact_idempotent_result_no_second_effect(self):
        r,c=self.prepare();files={p.name:p.read_bytes() for p in (self.root/'workspace/journal').iterdir()}
        c['call_id']='call:retry';c['max_response_bytes']=900000
        with patch.object(self.service.candidates,'prepare',side_effect=AssertionError('no redispatch')):r2=self.service.call(compact(c))
        self.assertEqual(r2['kind'],'result',r2);self.assertEqual(r2['message'],r['message'])
        self.assertEqual(files,{p.name:p.read_bytes() for p in (self.root/'workspace/journal').iterdir()})
    def test_whitespace_does_not_change_control_fingerprint(self):
        r,c=self.prepare();c['call_id']='call:whitespace'
        r2=self.service.call(json.dumps(c,indent=2).encode());self.assertEqual(r2['message'],r['message'])
        self.assertNotEqual(r2['request_binding']['sha256'],r['request_binding']['sha256'])
    def test_changed_full_message_conflicts(self):
        self.prepare();c=candidate_call(self.service,self.target);c['message']['proposal_ref']='proposal:changed'
        self.assertEqual(self.service.call(compact(c))['message']['code'],'idempotency-conflict')
    def test_profile_in_fingerprint_not_namespace(self):
        c=candidate_call(self.service,self.target);ctx=copy.deepcopy(self.channel.context)
        ns=jcs.namespace(c['operation'],c['idempotency_key'],ctx);fp=jcs.fingerprint(c,ctx)
        ctx['source_profile_binding']['sha256']='0'*64
        self.assertEqual(jcs.namespace(c['operation'],c['idempotency_key'],ctx),ns);self.assertNotEqual(jcs.fingerprint(c,ctx),fp)
    def test_nested_prepare_key_must_equal_envelope(self):
        c=candidate_call(self.service,self.target,key='different')
        self.assertEqual(self.service.call(compact(c))['message']['code'],'invalid-contract');self.assertFalse(list((self.root/'workspace/journal').iterdir()))
    def test_validate_retains_old_proposal_key(self):
        c=candidate_call(self.service,self.target,'change.validate','different-validation-key')
        self.assertNotEqual(c['idempotency_key'],c['message']['idempotency_key']);self.assertEqual(self.service.call(compact(c))['message']['result'],'not-evaluable')
    def test_completed_operation_inspection_bound(self):
        r,c=self.prepare();i,_=self.inspect();self.assertEqual(i['kind'],'result',i);self.assertEqual(i['message']['posture'],'completed')
        self.assertFalse(i['message']['retry_allowed']);self.assertFalse(i['message']['reconciliation_required'])
        self.assertEqual(source.parse(self.service.vault.object_read(i['message']['result_binding'])),r['message'])
        self.assertEqual(i['message']['original_call_binding']['sha256'],source.sha(compact(c)))
    def test_exact_call_binding_lookup(self):
        self.prepare();i,_=self.inspect();lookup={'call_binding':i['message']['original_call_binding']}
        c=call(self.channel.context,'operation.inspect',None,lookup=lookup)
        self.assertEqual(self.service.call(compact(c))['message']['result_binding'],i['message']['result_binding'])
    def test_unknown_operation_scoped_not_found(self):
        self.assertEqual(self.inspect('absent')[0]['message']['code'],'not-found')
    def test_claim_without_result_never_redispatches(self):
        c=candidate_call(self.service,self.target);self.service.vault.claim(c,compact(c),self.channel.context)
        with patch.object(self.service.candidates,'prepare',side_effect=AssertionError('no redispatch')):
            self.assertEqual(self.service.call(compact(c))['message']['code'],'recovery-required')
        i,_=self.inspect();self.assertEqual(i['message']['posture'],'indeterminate');self.assertTrue(i['message']['reconciliation_required'])
    def test_lost_claim_retains_allocation_tombstone(self):
        c=candidate_call(self.service,self.target);ns,*_=self.service.vault.claim(c,compact(c),self.channel.context)
        (self.root/'workspace/journal'/(ns+'.claim.json')).unlink()
        self.assertEqual(self.service.call(compact(c))['message']['code'],'recovery-required')
        self.assertEqual(self.inspect()[0]['message']['posture'],'indeterminate')
    def test_changed_core_returns_actual_failed_validation(self):
        c=candidate_call(self.service,self.target,'change.validate','core:invalid');c['message']['targets'][0]['decision_core_binding']['sha256']='0'*64
        r=self.service.call(compact(c));self.assertEqual(r['message']['result'],'fail');self.assertTrue(r['message']['gaps'])
    def test_changed_header_returns_failed_validation(self):
        c=candidate_call(self.service,self.target,'change.validate','header:invalid');c['message']['targets'][0]['artifact']['identity_ref']='goal:wrong'
        self.assertEqual(self.service.call(compact(c))['message']['result'],'fail')
    def test_wrong_candidate_contract_fails(self):
        c=candidate_call(self.service,self.target,'change.validate','schema:invalid');c['message']['targets'][0]['artifact']['candidate_contract_binding']['sha256']='0'*64
        self.assertEqual(self.service.call(compact(c))['message']['result'],'fail')
    def test_wrong_content_size_fails(self):
        c=candidate_call(self.service,self.target,'change.validate','size:invalid');c['message']['targets'][0]['content']['size_bytes']+=1
        self.assertEqual(self.service.call(compact(c))['message']['result'],'fail')
    def test_original_bytes_not_jcs_digest(self):
        self.assertNotEqual(self.target['artifact']['byte_sha256'],source.sha(jcs.dumps(source.parse(self.materials['candidate:work-content']))))
        self.assertEqual(self.target['artifact']['byte_sha256'],source.sha(self.materials['candidate:work-content']))
    def test_wrong_scope_refused_before_claim(self):
        c=candidate_call(self.service,self.target);c['message']['scope_ref']='scope:other'
        self.assertEqual(self.service.call(compact(c))['message']['code'],'unauthorized');self.assertFalse(list((self.root/'workspace/journal').iterdir()))
    def test_historical_preparation_refused(self):
        c=candidate_call(self.service,self.target);h=cut(self.service.handlers.available_views[0]);c['expected_source_cut']=h;c['message']['base_cut']=h
        self.assertEqual(self.service.call(compact(c))['message']['code'],'stale-cut')
    def test_mismatched_outer_cut_refused(self):
        c=candidate_call(self.service,self.target);c['expected_source_cut']=cut(self.service.handlers.available_views[0])
        self.assertEqual(self.service.call(compact(c))['message']['code'],'invalid-contract')
    def test_unselected_workspace_refused(self):
        c=candidate_call(self.service,self.target);c['message']['workspace_binding']['sha256']='0'*64
        self.assertEqual(self.service.call(compact(c))['message']['code'],'invalid-contract')
    def test_actor_claim_cannot_authorize_candidate(self):
        c=candidate_call(self.service,self.target);c['message']['actor']['principal_ref']='principal:owner'
        self.assertEqual(self.service.call(compact(c))['message']['code'],'unauthorized')
    def test_revoked_channel_no_result_redistribution(self):
        self.prepare();self.policy.write_bytes(b'{}')
        self.assertEqual(self.inspect()[0]['code'],'unauthenticated-channel')
    def test_deadline_before_claim_no_effect(self):
        c=candidate_call(self.service,self.target);c['deadline']='2000-01-01T00:00:00Z'
        self.assertEqual(self.service.call(compact(c))['message']['code'],'deadline-exceeded');self.assertFalse(list((self.root/'workspace/journal').iterdir()))
    def test_small_receipt_budget_refused_before_effect(self):
        c=candidate_call(self.service,self.target);c['max_response_bytes']=1
        self.assertEqual(self.service.call(compact(c))['message']['code'],'budget-exceeded');self.assertFalse(list((self.root/'workspace/journal').iterdir()))
    def test_unknown_remaining_handler_not_success(self):
        c=candidate_call(self.service,self.target);c['operation']='admission.apply'
        self.assertEqual(self.service.call(compact(c))['code'],'unsupported-operation')
    def test_workspace_input_tamper_revokes_channel(self):
        path=self.root/'workspace/inputs/input_0.json';path.write_bytes(b'{}')
        self.assertEqual(self.prepare()[0]['code'],'unauthenticated-channel')
    def test_private_session_memory_refused_by_vault(self):
        from workspace import privacy
        for v in [{'payload':{'session_memory':['private']}},{'private_key':'key'},{'text':'-----BEGIN PRIVATE KEY-----'}]:
            with self.assertRaises(Exception):privacy(v)
    def test_workspace_symlink_refused(self):
        path=self.root/'workspace/inputs/input_0.json';path.unlink();path.symlink_to(self.policy)
        self.assertEqual(self.prepare()[0]['code'],'unauthenticated-channel')
    def test_rfc8785_numeric_vector(self):
        self.assertEqual(jcs.dumps([333333333.33333329,1e30,4.50,2e-3,1e-27,-0.0]),b'[333333333.3333333,1e+30,4.5,0.002,1e-27,0]')
    def test_rfc8785_utf16_order(self):
        self.assertEqual(jcs.dumps({'\ue000':1,'\U00010000':2}),'{"\U00010000":2,"\ue000":1}'.encode())
    def test_jcs_unsafe_numeric_and_unicode_rejected(self):
        for v in [2**53,float('inf'),'\ud800']:
            with self.assertRaises(Exception):jcs.dumps(v)
    def test_four_retained_read_handlers_actual(self):
        for op in ('lab.status','catalog.get','artifact.query'):
            r=self.service.call(compact(call(self.channel.context,op,cut(self.view))));self.assertEqual(r['kind'],'result',r)
        from artifact_model import artifact_ref
        subject=next(s for s in self.view.subjects.values() if s['kind']=='work')
        c=call(self.channel.context,'artifact.inspect',cut(self.view),artifact=artifact_ref(self.view,subject))
        self.assertEqual(self.service.call(compact(c))['kind'],'result')
    def test_lost_result_retains_nonredispatchable_claim(self):
        r,c=self.prepare();ns=jcs.namespace(c['operation'],c['idempotency_key'],self.channel.context)
        (self.root/'workspace/journal'/(ns+'.result.json')).unlink();c['call_id']='call:lost-result'
        with patch.object(self.service.candidates,'prepare',side_effect=AssertionError('no redispatch')):
            self.assertEqual(self.service.call(compact(c))['message']['code'],'recovery-required')
        self.assertEqual(self.inspect()[0]['message']['posture'],'indeterminate')
    def test_result_object_tamper_is_integrity_refusal(self):
        self.prepare();i,_=self.inspect();b=i['message']['result_binding']
        (self.root/'workspace/objects'/(b['sha256']+'.json')).write_bytes(b'{}')
        self.assertEqual(self.inspect()[0]['message']['code'],'integrity-failed')
    def test_oversized_completed_report_retains_inspection(self):
        c=candidate_call(self.service,self.target,'change.validate','validate:small');c['max_response_bytes']=4096
        r=self.service.call(compact(c));self.assertEqual(r['message']['code'],'indeterminate',r)
        i=call(self.channel.context,'operation.inspect',None,lookup={'operation':'change.validate','idempotency_key':'validate:small'})
        result=self.service.call(compact(i));self.assertEqual(result['message']['posture'],'completed')
        self.assertIsNotNone(result['message']['result_binding'])
    def test_deadline_after_evidence_retains_completed_record(self):
        import service as module
        original=module.now;actual=self.service.candidates.validate;expired=[False]
        def validated(*args):
            result=actual(*args);expired[0]=True;return result
        c=candidate_call(self.service,self.target,'change.validate','validate:expired-after')
        with patch.object(self.service.candidates,'validate',side_effect=validated),patch.object(module,'now',side_effect=lambda:original()+timedelta(days=1) if expired[0] else original()):
            r=self.service.call(compact(c));self.assertEqual(r['message']['code'],'indeterminate',r)
        i=call(self.channel.context,'operation.inspect',None,lookup={'operation':'change.validate','idempotency_key':'validate:expired-after'})
        self.assertEqual(self.service.call(compact(i))['message']['posture'],'completed')
    def test_connection_without_explicit_target_is_failed_closure(self):
        from artifact_model import connections
        rows,_=connections(self.view,self.schemas)
        c=candidate_call(self.service,self.target,'change.validate','validate:undeclared-target');c['message']['connection_proposals']=[rows[0]['connection']]
        self.assertEqual(self.service.call(compact(c))['message']['result'],'fail')
    def test_prospective_historical_carrier_is_not_write_permission(self):
        c=candidate_call(self.service,self.target,'change.validate','validate:historical-carrier')
        c['message']['targets'][0]['artifact']['carrier_ref']='cal.artifact-type.typed-relation/v2'
        self.assertEqual(self.service.call(compact(c))['message']['result'],'fail')
    def test_workspace_pins_return_independent_objects(self):
        b=self.service.vault.control_binding;b['sha256']='0'*64
        self.assertNotEqual(self.service.vault.control_binding,b)
    def test_action_limit_counts_new_claims_and_allows_same_key_result(self):
        root=Path(self.stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-R03-limited-action-')))
        key,p,pin=provision(root,'reference-corrected',self.materials,self.metadata,max_actions=1)
        ch=ReaderChannel(p,pin,self.schemas);ch.authenticate(proof(key,ch.challenge));limited=Service(self.view,ch,self.schemas)
        try:
            c=candidate_call(limited,self.target);r=limited.call(compact(c));self.assertEqual(r['kind'],'result',r)
            c['call_id']='call:same-budget';self.assertEqual(limited.call(compact(c))['kind'],'result')
            c['call_id']='call:new-budget';c['idempotency_key']='new';c['message']['idempotency_key']='new'
            self.assertEqual(limited.call(compact(c))['message']['code'],'budget-exceeded')
        finally:limited.close()

if __name__=='__main__':unittest.main(verbosity=2)
