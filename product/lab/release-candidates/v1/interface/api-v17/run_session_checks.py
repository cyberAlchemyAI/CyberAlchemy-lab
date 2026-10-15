"""Real eleven-operation integration, Session custody and original preparation guards."""

# Keep this successor in its own module namespace. Frozen producers retain
# their exact original top-level dependency modules.
if __package__ in (None,''):
    import importlib.util as _boot_util,sys as _boot_sys
    from pathlib import Path as _BootPath
    _boot_root=_BootPath(__file__).resolve().parent
    _boot_name='_cal_'+_boot_root.name.replace('-','_')
    if _boot_name not in _boot_sys.modules:
        _boot_spec=_boot_util.spec_from_file_location(_boot_name,_boot_root/'__init__.py',submodule_search_locations=[str(_boot_root)])
        _boot_module=_boot_util.module_from_spec(_boot_spec);_boot_sys.modules[_boot_name]=_boot_module;_boot_spec.loader.exec_module(_boot_module)
    __package__=_boot_name
from .example_fixture import *
from .service import *
from .projection_refresh import control as projection_control
from .context_sessions import stable_policy,R,D,EL
from .workspace import privacy
from contextlib import ExitStack
from datetime import timedelta
import argparse,copy,json,os,tempfile,threading,time,unittest
from unittest.mock import patch

class Sessions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stack=ExitStack();cls.addClassCleanup(cls.stack.close)
        cls.view=cls.stack.enter_context(source.replay_source('fresh-participation'));cls.schemas=Schemas(PROFILE)
        cls.materials,cls.metadata,cls.target=materials_for(cls.view)
        cls.root=Path(cls.stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-R03-real-Session-suite-')));cls.root.chmod(0o700)
        cls.key,cls.policy,cls.policy_pin=provision(cls.root,'fresh-participation',cls.materials,cls.metadata,principal=R.PRINCIPAL,projection_control=projection_control(cls.view))
        cls.channel=ReaderChannel(cls.policy,cls.policy_pin,cls.schemas);cls.authenticated=cls.channel.authenticate(proof(cls.key,cls.channel.challenge))
        cls.service=Service(cls.view,cls.channel,cls.schemas);cls.stack.callback(cls.service.close)
        cls.events=[];cls.delivery_result=None;cls.opened=[]
    def invoke(self,c,*,raw=None):
        raw=compact(c) if raw is None else raw;r=self.service.call(raw)
        self.assertTrue(self.schemas.valid('api-reply',r),r)
        self.assertEqual(r['request_binding']['sha256'],source.sha(raw));self.assertEqual(r['contract_profile_binding'],self.schemas.profile_binding)
        self.events.append({'original_call':json.loads(raw),'request_byte_sha256':source.sha(raw),'reply':r})
        return r
    def success(self,c):
        r=self.invoke(c);self.assertEqual(r['kind'],'result',r);return r['message']
    def fresh_delivery(self):
        if self.delivery_result is None or instant(self.delivery_result['expires_at'])<now()+timedelta(seconds=150):
            ctx=self.service.sessions.bridge;selected=self.view.fresh_signed_sources
            message=D.query(selected,ctx);message['budget'].update(max_input_bytes=65536,max_output_bytes=1048576)
            c=call(self.channel.context,'lab.status',cut(self.view));c.update(operation='context.get',message=message)
            self.__class__.delivery_result=self.success(c)
        return copy.deepcopy(self.delivery_result)
    def opening(self,*,key=None):
        delivery=self.fresh_delivery();selected=self.view.fresh_signed_sources
        ref=lambda i:selected.sources.resolve(i+'@'+R.VERSION)[0].artifact
        c=call(self.channel.context,'lab.status',cut(self.view));actor=c['message']['actor'];budget=c['message']['budget'];budget['max_actions']=1
        c.update(operation='session.open',idempotency_key=key or 'open:'+uuid.uuid4().hex,message={
            'schema_version':'lab-agent-session-open/v1-candidate','request_ref':'request:Session-open:'+uuid.uuid4().hex,
            'actor':actor,'assignment':ref(R.ASSIGNMENT),'profile':ref(R.PROFILE),'implementation':ref(R.IMPLEMENTATION),'capabilities':[ref(R.CAPABILITY)],
            'context_delivery_binding':binding('context-delivery:'+delivery['context_view']['version_ref'],compact(delivery)),
            'authority_envelope_binding':stable_policy(self.channel),'source_cut':copy.deepcopy(cut(self.view)),
            'budget':budget,'memory_policy':{'persistence_allowed':False,'expires_with_session':True},'authority_effect':'none'})
        return c
    def opening_success(self):
        c=self.opening();r=self.success(c);self.assertEqual(r['posture'],'active');self.opened.append(r['session_ref']);return r,c
    def inspection(self,sid):
        c=call(self.channel.context,'lab.status',cut(self.view));b=c['message']['budget'];a=c['message']['actor']
        c.update(operation='session.inspect',message={'schema_version':'lab-session-inspect-request/v1-candidate','request_ref':'request:Session-inspect:'+uuid.uuid4().hex,'actor':a,'session_ref':sid,'budget':b,'authority_effect':'none'})
        return c
    def closing(self,opened,state=None):
        state=self.success(self.inspection(opened['session_ref'])) if state is None else state
        c=call(self.channel.context,'lab.status',cut(self.view));c.update(operation='session.close',idempotency_key='close:'+uuid.uuid4().hex,
            message={'schema_version':'lab-agent-session-close/v1-candidate','request_ref':'request:Session-close:'+uuid.uuid4().hex,
                'session_ref':opened['session_ref'],'agent_instance_ref':opened['agent_instance_ref'],
                'expected_session_binding':state['last_receipt_binding'],'requested_at':now().isoformat(),'reason':'completed','eligible_audit_bindings':[],'authority_effect':'none'})
        return c
    def tearDown(self):
        # Clean up all test-owned resources, independent of original source validity.
        self.service.sessions.dispose_all()
    def test_00_all_eleven_actual_operations(self):
        for op in ['lab.status','catalog.get','artifact.query']:
            r=self.success(call(self.channel.context,op,cut(self.view)))
            if op=='lab.status':self.assertEqual(r['supported_operations'],list(SUPPORTED))
        s=next(s for s in self.view.subjects.values() if s['identity']==R.WORK)
        from .artifact_model import artifact_ref
        self.success(call(self.channel.context,'artifact.inspect',cut(self.view),artifact=artifact_ref(self.view,s),include=['body','contract','gaps']))
        self.success(candidate_call(self.service,self.target,'change.prepare','fixture:prepare'))
        self.success(candidate_call(self.service,self.target,'change.validate','validate:integrated'))
        self.success(call(self.channel.context,'operation.inspect',None,lookup={'operation':'change.prepare','idempotency_key':'fixture:prepare'}))
        self.success(self.refreshing());self.fresh_delivery();r,c=self.opening_success();self.success(self.inspection(r['session_ref']));closed=self.success(self.closing(r));self.assertTrue(closed['discarded_memory'])
        observed={x['reply']['operation'] for x in self.events if x['reply']['kind']=='result'};self.assertEqual(observed,set(SUPPORTED))
    def refreshing(self):
        c=call(self.channel.context,'lab.status',cut(self.view));budget=c['message']['budget'];budget['max_actions']=1
        grant=self.channel.policy['projection_control'];prior=self.service.handlers.generations.get(source.sha(compact(cut(self.view))))
        c.update(operation='projection.refresh',idempotency_key='projection:Session-suite:'+uuid.uuid4().hex,message={
            'schema_version':'lab-projection-refresh-request/v1-candidate','request_ref':'request:Session-suite-projection:'+uuid.uuid4().hex,
            'source_cut':copy.deepcopy(cut(self.view)), 'projector_binding':grant['projector_binding'],
            'contract_catalog_binding':grant['contract_catalog_binding'],'expected_generation_binding':None if prior is None else prior.binding,
            'budget':budget,'authority_effect':'none'})
        return c
    def test_01_actual_private_memory_erased(self):
        r,c=self.opening_success();resource=self.service.sessions.live[r['session_ref']];sentinel=b'R03-live-only-note-e4b125b02eac'
        resource.note(sentinel);held=resource.memory[0]
        for p in (self.root/'workspace').rglob('*'):
            if p.is_file():self.assertNotIn(sentinel,p.read_bytes())
        self.assertNotIn(sentinel,compact(self.success(self.inspection(r['session_ref']))))
        self.success(self.closing(r));self.assertEqual(held,bytearray(len(sentinel)));self.assertEqual(resource.memory,[]);self.assertTrue(resource.closed)
    def test_02_actual_machine_classification(self):
        r,c=self.opening_success();row=self.service.sessions.selected(r['session_ref']);b=row['classification_record']
        self.assertEqual(b['payload']['subject_ref'],r['agent_instance_ref']);self.assertEqual(b['payload']['subject_version_ref'],r['agent_instance_ref']+'@ephemeral.1')
        self.assertEqual(b['payload']['effective_period'],r['session_ref']);self.assertEqual(b['payload']['status'],'candidate-annotation')
        self.assertEqual(row['agent_record']['payload']['accountable_principal_ref'],R.PRINCIPAL);self.assertEqual(b['authority_effect'],'none')
    def test_03_seven_exact_candidate_connections(self):
        r,c=self.opening_success();rows=self.service.sessions.selected(r['session_ref'])['connection_records'];self.assertEqual(len(rows),7)
        for row in rows:
            p=row['record']['payload'];self.assertEqual(p['source']['version_ref'],row['source_artifact']['version_ref']);self.assertEqual(p['target']['version_ref'],row['target_artifact']['version_ref']);self.assertEqual(row['authority_effect'],'none')
    def test_04_no_instance_identity_reuse(self):
        first,c=self.opening_success();self.success(self.closing(first));second,_=self.opening_success()
        self.assertNotEqual(first['session_ref'],second['session_ref']);self.assertNotEqual(first['agent_instance_ref'],second['agent_instance_ref'])
    def test_05_same_key_no_second_creation(self):
        r,c=self.opening_success();count=len(self.service.sessions.live);c['call_id']='call:Session-retry:'+uuid.uuid4().hex
        with patch.object(self.service.sessions,'open',side_effect=AssertionError('must not recreate')):again=self.success(c)
        self.assertEqual(r,again);self.assertEqual(count,len(self.service.sessions.live))
    def test_06_changed_input_same_key_conflict(self):
        r,c=self.opening_success();c['call_id']='call:conflict:'+uuid.uuid4().hex;c['message']['request_ref']='request:changed'
        self.assertEqual(self.invoke(c)['message']['code'],'idempotency-conflict')
    def test_07_pending_key_no_creation(self):
        c=self.opening();self.service.vault.claim(c,compact(c),self.channel.context)
        with patch.object(self.service.sessions,'open',side_effect=AssertionError('must not redispatch')):r=self.invoke(c)
        self.assertEqual(r['message']['code'],'recovery-required')
        i=call(self.channel.context,'operation.inspect',None,lookup={'operation':'session.open','idempotency_key':c['idempotency_key']});self.assertEqual(self.success(i)['posture'],'indeterminate')
    def test_08_close_exact_retry(self):
        opened,_=self.opening_success();c=self.closing(opened);result=self.success(c);c['call_id']='call:close-retry:'+uuid.uuid4().hex
        with patch.object(self.service.sessions,'close_session',side_effect=AssertionError('must not redispose')):self.assertEqual(result,self.success(c))
    def test_09_closed_metadata_retained(self):
        opened,_=self.opening_success();self.success(self.closing(opened));row=self.success(self.inspection(opened['session_ref']))
        self.assertEqual(row['posture'],'closed');self.assertIsNotNone(row['ended_at']);self.assertFalse(row['short_memory_in_response'])
    def test_10_wrong_close_preimage_denied(self):
        r,c=self.opening_success();x=self.closing(r);x['message']['expected_session_binding']['sha256']='0'*64
        self.assertEqual(self.invoke(x)['message']['code'],'conflict');self.assertIn(r['session_ref'],self.service.sessions.live)
    def test_11_wrong_close_Agent_denied(self):
        r,c=self.opening_success();x=self.closing(r);x['message']['agent_instance_ref']='agent-instance:other'
        self.assertEqual(self.invoke(x)['message']['code'],'conflict')
    def test_12_audit_export_eligibility_denied(self):
        r,c=self.opening_success();x=self.closing(r);x['message']['eligible_audit_bindings']=[{'ref':'unselected','sha256':'0'*64}]
        self.assertEqual(self.invoke(x)['message']['code'],'unauthorized')
    def negative_open(self,change):
        c=self.opening();change(c['message']);before=set(self.service.sessions.live);r=self.invoke(c)
        self.assertEqual(r['kind'],'error',r);self.assertEqual(set(self.service.sessions.live),before);return r
    def test_13_wrong_principal_denied(self):self.assertEqual(self.negative_open(lambda m:m['actor'].update(principal_ref='principal:other'))['message']['code'],'unauthorized')
    def test_14_wrong_original_delivery_denied(self):self.negative_open(lambda m:m['context_delivery_binding'].update(sha256='0'*64))
    def test_15_wrong_authority_envelope_denied(self):self.negative_open(lambda m:m['authority_envelope_binding'].update(sha256='0'*64))
    def test_16_wrong_Implementation_denied(self):self.negative_open(lambda m:m['implementation'].update(byte_sha256='0'*64))
    def test_17_wrong_Agent_Capability_denied(self):self.negative_open(lambda m:m['capabilities'][0].update(byte_sha256='0'*64))
    def test_18_empty_reader_capability_denied(self):self.negative_open(lambda m:m.update(capabilities=[]))
    def test_19_wrong_Profile_denied(self):self.negative_open(lambda m:m['profile'].update(byte_sha256='0'*64))
    def test_20_old_instance_Assignment_denied(self):
        def old(m):
            from .artifact_model import artifact_ref
            m['assignment']=artifact_ref(self.view,next(s for s in self.view.subjects.values() if s['kind']=='agent-assignment' and s['identity']!=R.ASSIGNMENT))
        self.negative_open(old)
    def test_21_wrong_cut_denied(self):self.negative_open(lambda m:m['source_cut'].update(commit_sha256='0'*64))
    def test_22_original_wire_and_message_bytes(self):
        c=self.opening();raw=(json.dumps(c,indent=3,ensure_ascii=False)+'\n').encode();r=self.invoke(c,raw=raw)
        self.assertEqual(r['kind'],'result',r);self.assertEqual(r['message']['request_binding']['sha256'],source.sha(message_bytes(raw)))
        self.assertNotEqual(source.sha(raw),source.sha(jcs.dumps(c)))
    def test_23_metadata_does_not_recreate_live_resource(self):
        r,c=self.opening_success();old=self.service.sessions;old.close()
        from .context_sessions import ContextSessions
        fresh=ContextSessions(self.view,self.channel,self.schemas,self.service.vault);self.service.sessions=fresh
        self.assertFalse(fresh.live);i=self.success(self.inspection(r['session_ref']));self.assertEqual(i['posture'],'closed')
    def test_24_captured_source_corruption_disposes_on_inspection(self):
        r,c=self.opening_success();resource=self.service.sessions.live[r['session_ref']];resource.note(b'owned-fixture-source-invalidation')
        original=self.view.data['config']['scope_ref'];self.view.data['config']['scope_ref']='project:captured-corruption'
        try:
            # Direct kernel observation bypasses API source-selection policy so the
            # actual selected source guard can invalidate and dispose this resource.
            result=self.service.sessions.inspect(self.inspection(r['session_ref'])['message'],{'ref':'fixture','sha256':'0'*64},self.service.sessions.selected(r['session_ref'])['source_cut'])
            self.assertEqual(result['posture'],'indeterminate');self.assertTrue(resource.closed);self.assertEqual(resource.memory,[])
        finally:self.view.data['config']['scope_ref']=original
    def test_25_close_does_not_require_current_Project_State(self):
        r,c=self.opening_success();close=self.closing(r);original=self.view.data['config']['scope_ref'];self.view.data['config']['scope_ref']='project:captured-corruption'
        try:self.assertTrue(self.success(close)['discarded_memory'])
        finally:self.view.data['config']['scope_ref']=original
    def test_26_private_policy_revocation_disposes(self):
        r,c=self.opening_success();resource=self.service.sessions.live[r['session_ref']];raw=self.policy.read_bytes();self.policy.write_bytes(raw+b' ')
        try:
            result=self.service.call(compact(self.inspection(r['session_ref'])));self.assertEqual(result['code'],'unauthenticated-channel');self.assertTrue(resource.closed)
        finally:self.policy.write_bytes(raw)
    def test_27_actual_expiry_timer_disposes(self):
        c=self.opening();c['message']['budget']['deadline']=(now()+timedelta(seconds=70)).isoformat();r=self.success(c);self.assertEqual(r['posture'],'active')
        resource=self.service.sessions.live[r['session_ref']];resource.note(b'private-note-expiring-in-real-time');held=resource.memory[0]
        deadline=time.monotonic()+90
        while not resource.closed and time.monotonic()<deadline:time.sleep(0.2)
        self.assertTrue(resource.closed,'real deadline disposal timer did not finish');self.assertEqual(held,bytearray(len(held)))
        self.assertEqual(self.success(self.inspection(r['session_ref']))['posture'],'expired')
    def test_28_no_short_memory_in_any_recorded_reply(self):
        for row in self.events:privacy(row['reply']);EL.no_private_memory(row['reply'])
    def test_29_source_and_period_unchanged(self):
        self.view.fresh_signed_sources.guard();period=D.load(D.reader.HERE/'packages/0001/period.json')
        self.assertEqual(period['expires_at'],'2026-10-10T02:45:14.443492+00:00')
    def test_30_current_handler_profile_retains_all_original_contracts(self):
        self.assertEqual(len(self.schemas.operations),34);self.assertEqual(len(SUPPORTED),12)
        self.assertEqual(self.schemas.profile['actual_owner_outcome'],None);self.assertEqual(self.schemas.profile['authority_effect'],'none')

    def test_31_frozen_producer_modules_retain_original_origins(self):
        self.assertEqual(Path(D.reader.adapter.source.__file__).resolve(),HERE.parent/'api-v12/source_bridge.py')
        self.assertEqual(Path(D.reader.adapter.model.__file__).resolve(),HERE.parent/'api-v12/artifact_model.py')
        self.assertEqual(Path(D.API.__file__).resolve(),HERE.parent/'api-v12/protocol.py')
    def test_32_authentication_result_is_a_snapshot(self):
        before=copy.deepcopy(self.channel.context);response=copy.deepcopy(self.authenticated)
        response['context']['principal_ref']='principal:tampered-copy'
        self.assertEqual(self.channel.context,before)
        guarded=self.channel.guard();guarded['principal_ref']='principal:tampered-guard'
        self.assertEqual(self.channel.context,before)
    def test_33_reply_profile_binding_does_not_mutate_host(self):
        r=self.invoke(call(self.channel.context,'lab.status',cut(self.view)));old=copy.deepcopy(self.schemas.profile_binding)
        r['contract_profile_binding']['sha256']='0'*64
        self.assertEqual(self.schemas.profile_binding,old)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source-sha256',required=True);p.add_argument('--profile-sha256',required=True);a=p.parse_args();PROFILE=a.profile_sha256
    # Exact source freeze is verified before private fixture provisioning.
    freeze=HERE/'source-manifest.json';source.require(source.sha(freeze.read_bytes())==a.source_sha256,'independent API producer pin differs')
    for row in source.parse(freeze.read_bytes())['files']:source.original(row)
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Sessions))
    out=HERE/'receipts';out.mkdir(exist_ok=True)
    for name,value in [('session-tests.json',{'result':'PASS' if result.wasSuccessful() else 'FAIL','tests_run':result.testsRun,'errors':len(result.errors),'failures':len(result.failures),'source_sha256':a.source_sha256,'profile_sha256':PROFILE,'authority_effect':'none','actual_owner_outcome':None,'task_complete':False}),('session-wire-observations.json',getattr(Sessions,'events',[]))]:
        fd=os.open(out/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'wb') as f:f.write(source.encoded(value))
    raise SystemExit(0 if result.wasSuccessful() else 1)
