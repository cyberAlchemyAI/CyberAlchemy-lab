"""Real public boundary calls; local OS crash preserves actual pending effect."""
import base64,copy,os,tempfile,time,unittest
from pathlib import Path
from .dependencies import *
from .runtime import *
from .fixture import OwnedActor
from .service import ActionService,save
SOURCE=None;PROFILE=None

class ActionAPI(unittest.TestCase):
 witnesses=[]
 @classmethod
 def setUpClass(cls):
  cls.schemas=P.Schemas(BASE_PROFILE);guard(SOURCE)
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='cal-action-0148-');self.fixture=OwnedActor(Path(self.tmp.name)/'actor',self.schemas)
  self.host=ActionService(self.fixture.runtime,self.fixture.channel,self.schemas,source_sha256=SOURCE,profile_sha256=PROFILE);self.count=0
 def tearDown(self):
  self.fixture.close();self.assertTrue(self.fixture.session.closed);self.tmp.cleanup()
 def call(self,operation,message,*,key=None,patch=None,wire=None):
  self.count+=1;f=self.fixture
  call={'schema_version':'lab-api-call/v2-candidate','call_id':'case-call-'+str(self.count),'operation':operation,'caller_context_ref':f.channel.context['context_ref'] if f.channel.context else 'context:closed','expected_source_cut':copy.deepcopy(f.cut),'deadline':f.deadline,'max_response_bytes':262144,'idempotency_key':message.get('idempotency_key') if operation=='action.dispatch' else key,'message':copy.deepcopy(message),'expected_contract_profile_binding':self.host.profile_binding}
  if patch:call.update(patch)
  raw=wire(call) if wire else P.compact(call);reply=self.host.call(raw)
  self.witnesses.append({'operation':operation,'call_sha256':byte_sha(raw),'reply':reply,'counter':regular_json(f.root/'ledger/counter.json'),'journal_sha256':byte_sha((f.root/'ledger/journal.json').read_bytes())})
  if reply.get('schema_version')=='lab-api-reply/v2-candidate':self.assertTrue(self.schemas.valid('api-reply',reply))
  return reply
 def code(self,reply,expected):self.assertEqual(reply.get('kind'),'error',reply);self.assertEqual(reply['message']['code'],expected,reply)
 def test_01_actual_evaluation_dispatch_output_and_exact_semantic_retry(self):
  m=self.fixture.request(increment=3);e=self.call('action.evaluate',m);self.assertEqual(e['message']['posture'],'permitted');self.assertEqual(regular_json(self.fixture.root/'ledger/counter.json')['value'],0)
  r=self.call('action.dispatch',m);self.assertEqual(r['message']['posture'],'completed');self.assertEqual(regular_json(self.fixture.root/'ledger/counter.json')['value'],3)
  output=r['message']['output_bindings'][0];self.assertEqual(parse(self.host.material(output))['value'],3);self.assertEqual(len(r['message']['observation_refs']),1)
  r2=self.call('action.dispatch',m,wire=lambda c:encoded(c));self.assertEqual(r2['message'],r['message']);self.assertEqual(regular_json(self.fixture.root/'ledger/counter.json')['value'],3)
 def test_02_wrong_actor_scope_profile_and_input_binding_refuse_without_effect(self):
  original=self.fixture.request()
  m=copy.deepcopy(original);m['actor']['principal_ref']='principal:Source5-readonly';self.code(self.call('action.dispatch',m),'unauthorized')
  m=copy.deepcopy(original);m['bounds']['filesystem_scope_refs']=['scope:outside'];self.code(self.call('action.dispatch',m),'unauthorized')
  self.code(self.call('action.dispatch',original,patch={'expected_contract_profile_binding':self.schemas.profile_binding}),'invalid-contract')
  m=copy.deepcopy(original);m['input_bindings'][0]['byte_sha256']='0'*64;self.code(self.call('action.dispatch',m),'unresolved-reference')
  self.assertEqual(regular_json(self.fixture.root/'ledger/counter.json')['value'],0)
 def test_03_real_clock_deadline_response_budget_and_call_reuse(self):
  m=self.fixture.request();self.code(self.call('action.dispatch',m,patch={'deadline':iso(time.time()-1)}),'deadline-exceeded')
  self.code(self.call('action.dispatch',m,patch={'max_response_bytes':4096}),'budget-exceeded')
  r=self.call('action.evaluate',m);self.assertEqual(r['message']['posture'],'permitted')
  self.count-=1;self.code(self.call('action.evaluate',m),'invalid-contract');self.assertEqual(regular_json(self.fixture.root/'ledger/counter.json')['value'],0)
 def test_04_current_revocation_and_stop_after_permitted_evaluation(self):
  m=self.fixture.request();self.assertEqual(self.call('action.evaluate',m)['message']['posture'],'permitted')
  state=self.fixture.runtime.status();state['revoked_refs']=[self.fixture.refs['delegation']];save(self.fixture.root/'status.json',state)
  self.assertEqual(self.call('action.dispatch',m)['message']['posture'],'denied');self.assertEqual(regular_json(self.fixture.root/'ledger/counter.json')['value'],0)
  state['revoked_refs']=[];state['stopped']=True;save(self.fixture.root/'status.json',state)
  m=self.fixture.request(key='stopped');self.assertEqual(self.call('action.evaluate',m)['message']['posture'],'denied')
 def test_05_idempotency_conflict_and_current_authority_before_recorded_retry(self):
  m=self.fixture.request();r=self.call('action.dispatch',m);self.assertEqual(r['message']['posture'],'completed')
  other=self.fixture.request(increment=2);self.code(self.call('action.dispatch',other),'idempotency-conflict')
  state=self.fixture.runtime.status();state['revoked_refs']=[self.fixture.refs['role-assignment']];save(self.fixture.root/'status.json',state)
  self.code(self.call('action.dispatch',m),'unauthorized');self.assertEqual(regular_json(self.fixture.root/'ledger/counter.json')['value'],1)
 def crash(self,m,*,after=True):
  self.count+=1;f=self.fixture
  call={'schema_version':'lab-api-call/v2-candidate','call_id':'real-crash-child','operation':'action.dispatch','caller_context_ref':f.channel.context['context_ref'],'expected_source_cut':f.cut,'deadline':f.deadline,'max_response_bytes':262144,'idempotency_key':m['idempotency_key'],'message':m,'expected_contract_profile_binding':self.host.profile_binding}
  pid=os.fork()
  if pid==0:
   if after:
    from counter import CounterTool
    actual=CounterTool.execute
    def interrupted(tool,original,action_id):
     actual(tool,original,action_id)
     os._exit(73)
    CounterTool.execute=interrupted
   else:
    original_checkpoint=self.fixture.runtime.checkpoint
    def interrupted(observed):
     original_checkpoint(observed)
     os._exit(74)
    self.fixture.runtime.checkpoint=interrupted
   try:self.host.call(P.compact(call))
   except BaseException:os._exit(91)
   os._exit(92)
  _,status=os.waitpid(pid,0);self.assertEqual(os.waitstatus_to_exitcode(status),73 if after else 74)
  self.witnesses.append({'operation':'action.dispatch','actual_child_exit_code':os.waitstatus_to_exitcode(status),'call_sha256':byte_sha(P.compact(call)),'counter':regular_json(f.root/'ledger/counter.json'),'pending_journal':regular_json(f.root/'ledger/journal.json'),'authority_effect':'none'})
 def test_06_real_process_death_after_effect_preserves_uncertainty_and_reconcile_no_redispatch(self):
  m=self.fixture.request(increment=4);self.crash(m)
  self.assertEqual(regular_json(self.fixture.root/'ledger/counter.json')['value'],4)
  r=self.call('action.dispatch',m);self.assertEqual(r['message']['posture'],'indeterminate');self.assertFalse(r['message']['retry_allowed']);self.assertTrue(r['message']['reconciliation_required'])
  self.assertEqual(regular_json(self.fixture.root/'ledger/counter.json')['value'],4)
  next_m=self.fixture.request(key='counter-next');self.code(self.call('action.dispatch',next_m),'recovery-required')
  recovery=self.fixture.recovery(r['message']);rr=self.call('action.reconcile',recovery,key='recover-after');self.assertEqual(rr['message']['posture'],'recovered');self.assertFalse(rr['message']['retry_allowed'])
  rr2=self.call('action.reconcile',recovery,key='recover-after',wire=lambda c:encoded(c));self.assertEqual(rr2['message'],rr['message'])
  self.assertEqual(regular_json(self.fixture.root/'ledger/counter.json')['value'],4)
  self.assertEqual(self.call('action.dispatch',next_m)['message']['posture'],'completed');self.assertEqual(regular_json(self.fixture.root/'ledger/counter.json')['value'],5)
 def test_07_real_process_death_before_effect_observes_failure_without_replay(self):
  m=self.fixture.request();self.crash(m,after=False);self.assertEqual(regular_json(self.fixture.root/'ledger/counter.json')['value'],0)
  r=self.call('action.dispatch',m);self.assertEqual(r['message']['posture'],'indeterminate')
  rr=self.call('action.reconcile',self.fixture.recovery(r['message']),key='recover-before');self.assertEqual(rr['message']['posture'],'recovered')
  observed=rr['message']['observed_bindings'][0];raw=private(self.fixture.root/'materials'/observed['sha256']);self.assertEqual(parse(raw)['posture'],'failed');self.assertEqual(regular_json(self.fixture.root/'ledger/counter.json')['value'],0)
  self.assertEqual(self.call('action.dispatch',m)['message']['posture'],'indeterminate');self.assertEqual(regular_json(self.fixture.root/'ledger/counter.json')['value'],0)
 def test_08_recovery_exact_residue_contract_and_actor_refusals(self):
  m=self.fixture.request();r=self.call('action.dispatch',m);recovery=self.fixture.recovery(r['message'])
  bad=copy.deepcopy(recovery);bad['recovery_contract_binding']['sha256']='0'*64;self.code(self.call('action.reconcile',bad,key='bad-contract'),'integrity-failed')
  bad=copy.deepcopy(recovery);bad['allowed_residue_bindings']=[binding('outside',b'outside')];self.code(self.call('action.reconcile',bad,key='bad-residue'),'unauthorized')
  bad=copy.deepcopy(recovery);bad['actor']['session_ref']='agent-session:reader';self.code(self.call('action.reconcile',bad,key='bad-actor'),'unauthorized')
  bad=copy.deepcopy(recovery);bad['subject_binding']['sha256']='0'*64;self.code(self.call('action.reconcile',bad,key='bad-subject'),'not-found');self.assertEqual(regular_json(self.fixture.root/'ledger/counter.json')['value'],1)
 def test_09_actual_nonce_replay_cross_connection_and_private_grant_changes(self):
  from .runtime import ActionChannel
  path=self.fixture.root/'channel-policy.json';channel=ActionChannel(path,self.fixture.policy_sha,self.fixture.runtime,self.schemas)
  proof={'schema_version':'lab-local-action-proof/v1-candidate','challenge':channel.challenge,'signature':base64.b64encode(self.fixture.key.sign(P.compact(channel.challenge))).decode()}
  channel.authenticate(P.compact(proof))
  with self.assertRaises(ValueError):channel.authenticate(P.compact(proof))
  other=ActionChannel(path,self.fixture.policy_sha,self.fixture.runtime,self.schemas)
  with self.assertRaises(ValueError):other.authenticate(P.compact(proof))
  self.fixture.runtime.channel=self.fixture.channel
  raw=private(self.fixture.root/'grant.json');save(self.fixture.root/'grant.json',{'revoked':True})
  reply=self.call('action.evaluate',self.fixture.request());self.assertEqual(reply['code'],'unauthenticated-channel')
  (self.fixture.root/'grant.json').write_bytes(raw)
 def test_10_closed_actual_lease_cannot_be_reused(self):
  m=self.fixture.request();self.fixture.session.close();self.assertEqual(self.call('action.dispatch',m)['code'],'unauthenticated-channel');self.assertEqual(regular_json(self.fixture.root/'ledger/counter.json')['value'],0)
 def test_11_declared_approval_gate_has_no_invented_approval(self):
  self.fixture.close();self.fixture=OwnedActor(Path(self.tmp.name)/'gated-actor',self.schemas,approval_required=True)
  self.host=ActionService(self.fixture.runtime,self.fixture.channel,self.schemas,source_sha256=SOURCE,profile_sha256=PROFILE)
  m=self.fixture.request();self.assertEqual(self.call('action.evaluate',m)['message']['posture'],'gate-required')
  self.assertEqual(self.call('action.dispatch',m)['message']['posture'],'denied');self.assertEqual(regular_json(self.fixture.root/'ledger/counter.json')['value'],0)
 def test_12_recovery_grant_denies_reconciliation_and_retry_after_revocation(self):
  m=self.fixture.request();r=self.call('action.dispatch',m);recovery=self.fixture.recovery(r['message'])
  rr=self.call('action.reconcile',recovery,key='recovery-current');self.assertEqual(rr['message']['posture'],'recovered')
  state=self.fixture.runtime.status();state['revoked_refs']=[self.fixture.refs['delegation']];save(self.fixture.root/'status.json',state)
  self.code(self.call('action.reconcile',recovery,key='recovery-current'),'unauthorized');self.assertEqual(regular_json(self.fixture.root/'ledger/counter.json')['value'],1)
 def test_13_signed_source_tamper_and_private_permission_refuse(self):
  m=self.fixture.request();raw=private(self.fixture.root/'source.json');(self.fixture.root/'source.json').write_bytes(raw+b' ')
  self.assertEqual(self.call('action.dispatch',m)['code'],'unauthenticated-channel');(self.fixture.root/'source.json').write_bytes(raw)
  os.chmod(self.fixture.root/'grant.json',0o644);self.assertEqual(self.call('action.evaluate',m)['code'],'unauthenticated-channel');os.chmod(self.fixture.root/'grant.json',0o600)
  self.assertEqual(regular_json(self.fixture.root/'ledger/counter.json')['value'],0)
 def test_14_selected_code_schema_tamper_and_unselected_import_refuse(self):
  m=self.fixture.request()
  for filename in ('service.py','action-runtime-policy.schema.json'):
   path=HERE/filename;original=path.read_bytes()
   try:
    path.write_bytes(original+b'\n');self.code(self.call('action.dispatch',m),'integrity-failed');self.assertEqual(regular_json(self.fixture.root/'ledger/counter.json')['value'],0)
   finally:path.write_bytes(original)
  path=HERE/'unselected_action_0148.py';module_name='_cal_action_0148_unselected_runtime_import'
  try:
   from .fixture import put
   put(path,b'LOCAL_CONSTANT = 1\n')
   spec=__import__('importlib.util',fromlist=['*']).spec_from_file_location(module_name,path)
   module=__import__('importlib.util',fromlist=['*']).module_from_spec(spec);__import__('sys').modules[module_name]=module;spec.loader.exec_module(module)
   self.code(self.call('action.dispatch',m),'integrity-failed');self.assertEqual(regular_json(self.fixture.root/'ledger/counter.json')['value'],0)
  finally:__import__('sys').modules.pop(module_name,None);path.unlink(missing_ok=True)
 def test_15_common_public_dispatcher_preserves_separate_reader_and_action_authority(self):
  from .dependencies import name
  F=__import__(name+'.fixtures',fromlist=['*']);A=__import__(name+'.auth',fromlist=['*']);S=__import__(name+'.service',fromlist=['*']);H=__import__(name+'.handlers',fromlist=['*'])
  from .bridge import IntegrationService
  root=Path(self.tmp.name)/'reader';root.mkdir(mode=0o700)
  key,path,policy_sha=F.provision(root)
  with P.source.replay_source('engineering') as view:
   channel=A.ReaderChannel(path,policy_sha,self.schemas);channel.authenticate(F.proof(key,channel.challenge));base=S.Service(view,channel,self.schemas)
   router=IntegrationService(base,self.host)
   call=F.call(channel.context,'lab.status');reply=router.call(P.compact(call));self.assertEqual(reply['kind'],'result');self.assertEqual(reply['contract_profile_binding'],self.schemas.profile_binding)
   m=self.fixture.request();self.count+=1
   action_call={'schema_version':'lab-api-call/v2-candidate','call_id':'common-action-call','operation':'action.dispatch','caller_context_ref':self.fixture.channel.context['context_ref'],'expected_source_cut':self.fixture.cut,'deadline':self.fixture.deadline,'max_response_bytes':262144,'idempotency_key':m['idempotency_key'],'message':m,'expected_contract_profile_binding':self.host.profile_binding}
   result=router.call(P.compact(action_call));self.assertEqual(result['message']['posture'],'completed');self.assertEqual(regular_json(self.fixture.root/'ledger/counter.json')['value'],1)
   action_call['call_id']='common-reader-denied';action_call['caller_context_ref']=channel.context['context_ref'];denied=router.call(P.compact(action_call));self.code(denied,'unauthorized')
   self.assertEqual(regular_json(self.fixture.root/'ledger/counter.json')['value'],1)
   self.witnesses.extend([{'operation':'lab.status','reply':reply,'common_dispatcher':True},{'operation':'action.dispatch','reply':result,'common_dispatcher':True},{'operation':'action.dispatch','reply':denied,'common_dispatcher':True}]);router.close();self.assertTrue(self.fixture.session.closed)
 def inspect_request(self,lookup):
  return {'schema_version':'lab-operation-inspect-request/v1-candidate','request_ref':'request:inspect:'+str(self.count),'actor':copy.deepcopy(self.fixture.actor),'lookup':lookup,'budget':{'max_actions':0,'max_input_bytes':65536,'max_output_bytes':262144,'deadline':self.fixture.deadline},'authority_effect':'none'}
 def test_16_actual_api7_shared_schema_profile_and_nonce_bound_profile_refusals(self):
  from .shared_schemas import IntegratedSchemas,API7
  shared=binding(str((HERE/'shared-contract-profile.json').relative_to(ROOT)),(HERE/'shared-contract-profile.json').read_bytes())
  schemas=IntegratedSchemas(byte_sha((API7/'contract-profile.json').read_bytes()),shared)
  self.fixture.close();self.fixture=OwnedActor(Path(self.tmp.name)/'shared-actor',schemas,integration_profile_binding=shared)
  self.host=ActionService(self.fixture.runtime,self.fixture.channel,schemas,source_sha256=SOURCE,profile_sha256=PROFILE,integration_profile_binding=shared)
  m=self.fixture.request(increment=2);r=self.call('action.dispatch',m);self.assertEqual(r['message']['posture'],'completed');self.assertEqual(r['contract_profile_binding'],shared)
  last=self.witnesses[-1];self.assertEqual(r['request_binding']['sha256'],last['call_sha256']);self.assertEqual(regular_json(self.fixture.root/'ledger/counter.json')['value'],2)
  self.assertEqual(self.fixture.channel.challenge['contract_profile_binding'],shared)
  self.code(self.call('action.evaluate',m,patch={'expected_contract_profile_binding':self.schemas.profile_binding}),'invalid-contract')
  with self.assertRaises(ValueError):ActionService(self.fixture.runtime,self.fixture.channel,schemas,source_sha256=SOURCE,profile_sha256=PROFILE,integration_profile_binding=self.schemas.profile_binding)
  path=HERE/'shared-contract-profile.json';raw=path.read_bytes()
  try:
   path.write_bytes(raw+b'\n');self.assertEqual(self.call('action.evaluate',m)['code'],'unauthenticated-channel')
  finally:path.write_bytes(raw)
 def test_17_completed_evaluation_dispatch_recovery_inspection_by_key_and_call_binding(self):
  m=self.fixture.request();e=self.call('action.evaluate',m);evaluation=self.call('operation.inspect',self.inspect_request({'operation':'action.evaluate','idempotency_key':m['idempotency_key']}));self.assertEqual(evaluation['message']['posture'],'completed');self.assertEqual(evaluation['message']['operation'],'action.evaluate')
  r=self.call('action.dispatch',m);exact=r['request_binding'];a=self.call('operation.inspect',self.inspect_request({'operation':'action.dispatch','idempotency_key':m['idempotency_key']}));self.assertEqual(a['message']['posture'],'completed');self.assertEqual(a['message']['original_call_binding'],exact)
  b=self.call('operation.inspect',self.inspect_request({'call_binding':exact}));self.assertEqual(b['message']['original_call_binding'],exact);self.assertEqual(b['message']['result_binding'],a['message']['result_binding'])
  rr=self.call('action.reconcile',self.fixture.recovery(r['message']),key='inspect-recovery');i=self.call('operation.inspect',self.inspect_request({'operation':'action.reconcile','idempotency_key':'inspect-recovery'}));self.assertEqual(i['message']['posture'],'completed');self.assertEqual(i['message']['original_call_binding'],rr['request_binding']);self.assertEqual(regular_json(self.fixture.root/'ledger/counter.json')['value'],1)
 def test_18_actual_pending_inspection_observes_then_recovered_completion_without_dispatch(self):
  m=self.fixture.request(increment=3);self.crash(m)
  i=self.call('operation.inspect',self.inspect_request({'operation':'action.dispatch','idempotency_key':m['idempotency_key']}));self.assertEqual(i['message']['posture'],'pending');self.assertTrue(i['message']['reconciliation_required']);self.assertFalse(i['message']['retry_allowed']);self.assertEqual(regular_json(self.fixture.root/'ledger/counter.json')['value'],3)
  r=self.call('action.dispatch',m);self.assertEqual(r['message']['posture'],'indeterminate')
  self.call('action.reconcile',self.fixture.recovery(r['message']),key='inspector-recovery')
  i=self.call('operation.inspect',self.inspect_request({'operation':'action.dispatch','idempotency_key':m['idempotency_key']}));self.assertEqual(i['message']['posture'],'completed');self.assertFalse(i['message']['reconciliation_required']);self.assertEqual(regular_json(self.fixture.root/'ledger/counter.json')['value'],3)
 def test_19_foreign_inspector_actor_unknown_key_and_current_revocation_refuse(self):
  m=self.fixture.request();r=self.call('action.dispatch',m)
  request=self.inspect_request({'call_binding':r['request_binding']});request['actor']['principal_ref']='principal:foreign';self.code(self.call('operation.inspect',request),'unauthorized')
  self.code(self.call('operation.inspect',self.inspect_request({'operation':'action.dispatch','idempotency_key':'unknown-action-key'})),'not-found')
  state=self.fixture.runtime.status();state['revoked_refs']=[self.fixture.refs['role-assignment']];save(self.fixture.root/'status.json',state)
  self.code(self.call('operation.inspect',self.inspect_request({'call_binding':r['request_binding']})),'unauthorized');self.assertEqual(regular_json(self.fixture.root/'ledger/counter.json')['value'],1)
