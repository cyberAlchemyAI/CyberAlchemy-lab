"""Actual original public calls and bounded synthetic owned operators only."""
import base64,copy,hashlib,importlib.util,json,os,sys,tempfile,time,traceback,uuid
from pathlib import Path
from datetime import timedelta
ROOT=Path(__file__).resolve().parents[5];HERE=ROOT/'product/lab/release-candidates/v1/interface/api-governance-integration-v3';RUN=Path(__file__).resolve().parent
name='_cal_public_governance_qualification0148v3';spec=importlib.util.spec_from_file_location(name,HERE/'__init__.py',submodule_search_locations=[str(HERE)]);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
from importlib import import_module
F=import_module(name+'.fixture');SC=import_module(name+'.schemas');B=import_module(name+'.bridge')
SOURCE=F.sha((HERE/'source-manifest.json').read_bytes());PROFILE=F.sha((HERE/'contract-profile.json').read_bytes())
results=[];responses=[];start=F.iso(F.now())
def case(label,function):
 print('START '+label,flush=True);started=time.monotonic()
 try:function();row={'case':label,'result':'PASS'}
 except Exception as e:traceback.print_exc();row={'case':label,'result':'FAIL','error_type':type(e).__name__,'message':str(e)}
 row['elapsed_seconds']=time.monotonic()-started;results.append(row);print(json.dumps(row),flush=True)
def call(f,c,expected_kind='result',code=None,raw=None):
 raw=raw or F.encoded(c);r=f.service.call(raw);responses.append({'original_call_sha256':F.sha(raw),'operation':c['operation'],'reply':r});assert r.get('kind')==expected_kind,r
 if code is not None:assert r['message']['code']==code,r
 if expected_kind=='result':assert f.schemas.protocol_valid(f.schemas.operations[c['operation']]['result_schema']['resource_uri'],r['message']),r
 return r
print('Full frozen history guard at qualification entry',flush=True);F.G.verify(F.BASE_SOURCE)
schemas=SC.GovernanceSchemas()
with tempfile.TemporaryDirectory(prefix='cal-governance-0148-qualification-') as tmp:
 f=F.Fixture(tmp,schemas);initial=f.host.cut();cap_call=f.capability_call();cap_result=None;checkpoint_call=f.checkpoint_call();checkpoint_result=None;admission=None
 def nonce():
  channel=F.GovernanceChannel(f.host);service=F.GovernanceService(f.host,channel);r=service.call(F.encoded(f.checkpoint_call('nonce-refusal')));assert r['code']=='unauthenticated-channel'
  wrong=F.Ed25519PrivateKey.generate()
  try:channel.authenticate({'challenge':channel.challenge,'signature_base64':base64.b64encode(wrong.sign(F.encoded(channel.challenge))).decode()})
  except Exception:pass
  else:raise AssertionError('forged nonce admitted')
  try:f.channel.authenticate({'challenge':f.channel.challenge,'signature_base64':base64.b64encode(f.reader.sign(F.encoded(f.channel.challenge))).decode()})
  except Exception:pass
  else:raise AssertionError('nonce reused')
 case('01-independent-real-nonce-forgery-and-reuse-refusal',nonce)
 def trusted_context():
  c=f.channel.guard();assert f.schemas.valid('trusted-call-context',c)
  assert c['origin']=='verified-local-adapter' and c['accept_client_supplied_authority_context'] is False and c['private_credentials_in_context'] is False
  assert c['agent_instance_ref'] is None and c['session_ref'] is None and c['assignment_ref'] is None and c['role_assignment_bindings']==[]
  assert f.host.document(c['authentication_evidence_binding'])['challenge']==f.channel.challenge
  assert f.channel.challenge['source_sha256']==SOURCE and f.channel.challenge['contract_profile_binding']==f.host.profile_binding
  assert c['limits']['max_actions']==f.policy['max_actions'] and c['limits']['deadline']==f.policy['expires_at']
 case('01b-original-trusted-context-contract-real-proof-source-policy-and-no-Agent-inference',trusted_context)
 def protected_input():
  before=list((f.root/'operations').iterdir());objects=list((f.root/'objects').iterdir())
  for field,value in [('password','controlled-qualification-secret'),('api_key','controlled-qualification-api-key'),('session_ram',{'value':'controlled-qualification-memory'})]:
   c=f.capability_call('private-refusal:'+field);c['message'][field]=value;call(f,c,'error','unauthorized')
  c=f.capability_call('PEM-refusal');c['message']['request_ref']='-----BEGIN PRIVATE KEY-----\ncontrolled-fixture-not-a-real-key\n-----END PRIVATE KEY-----';call(f,c,'error','unauthorized')
  assert list((f.root/'operations').iterdir())==before and list((f.root/'objects').iterdir())==objects
  try:f.host.object(F.encoded({'session_memory':{'body':'controlled-fixture'}}))
  except F.Refusal:pass
  else:raise AssertionError('protected RAM candidate object written')
  assert list((f.root/'objects').iterdir())==objects
 case('01c-controlled-secret-key-PEM-and-RAM-refusal-before-any-public-object-or-journal',protected_input)
 def actor():
  c=f.capability_call('actor-refusal');c['message']['actor']['principal_ref']='principal:caller-invented';before=list((f.root/'operations').iterdir());call(f,c,'error','unauthorized');assert list((f.root/'operations').iterdir())==before
 case('02-Actor-and-independent-local-scope-refusal',actor)
 def expiry():
  c=f.capability_call('deadline-refusal');c['deadline']=F.iso(F.now()-timedelta(seconds=1));call(f,c,'error','deadline-exceeded');assert not f.service.operation_path(c['operation'],c['idempotency_key']).exists()
 case('03-real-expired-deadline-before-any-journal',expiry)
 def malformed():
  c=f.capability_call('scope-refusal');c['message']['operational_scope_ref']='scope:invented';call(f,c,'error','unauthorized')
  c=f.capability_call('observation-refusal');c['message']['observation_contract_bindings'][0]['sha256']='1'*64;call(f,c,'error','unauthorized')
 case('04-exact-capability-scope-and-observation-selection-refusal',malformed)
 def drift():
  b=f.manifest;p=f.root/'materials'/b['sha256'];raw=p.read_bytes()
  try:p.write_bytes(raw+b' ');call(f,f.checkpoint_call('material-drift'),'error','integrity-failed')
  finally:p.write_bytes(raw)
  p=f.root/'operator-policy.json';raw=p.read_bytes()
  try:p.write_bytes(raw+b' ');r=f.service.call(F.encoded(f.capability_call('private-policy-drift')));assert r.get('code')=='unauthenticated-channel',r
  finally:p.write_bytes(raw)
 case('05-private-policy-and-original-material-drift-refusal',drift)
 def capability():
  global cap_result
  r=call(f,cap_call);cap_result=r['message'];declaration=f.host.document(cap_result['evidence_bindings'][0]);assert declaration['actual_adoption'] is False and declaration['usefulness_observed'] is False and declaration['runtime_activations']==0;assert f.host.cut()==initial
 case('06-positive-capability-preparation-without-activation',capability)
 def retry():
  c=copy.deepcopy(cap_call);c['call_id']='call:retry:'+uuid.uuid4().hex;r=call(f,c);assert r['message']==cap_result
  c=copy.deepcopy(cap_call);c['call_id']='call:conflict:'+uuid.uuid4().hex;c['message']['request_ref']+=':changed';call(f,c,'error','idempotency-conflict')
  f.open();c=copy.deepcopy(cap_call);c['call_id']='call:cold-retry:'+uuid.uuid4().hex;c['caller_context_ref']=f.channel.context['context_ref'];r=call(f,c);assert r['message']==cap_result
 case('07-exact-durable-retry-conflict-and-cold-authentication',retry)
 def shared():
  shared=copy.copy(f.schemas);shared.profile_binding=copy.deepcopy(f.host.profile_binding)
  host=F.GovernanceHost(f.root,f.policy_pin,shared,SOURCE,PROFILE,integration_profile_binding=shared.profile_binding);channel=F.GovernanceChannel(host);channel.authenticate({'challenge':channel.challenge,'signature_base64':base64.b64encode(f.reader.sign(F.encoded(channel.challenge))).decode()});service=F.GovernanceService(host,channel)
  c=copy.deepcopy(cap_call);c['call_id']='call:shared:'+uuid.uuid4().hex;c['caller_context_ref']=channel.context['context_ref'];r=service.call(F.encoded(c));assert r['kind']=='result' and r['message']==cap_result and r['contract_profile_binding']==shared.profile_binding
  assert channel.challenge['profile_sha256']==shared.profile_binding['sha256']
  try:F.GovernanceHost(f.root,f.policy_pin,shared,SOURCE,PROFILE,integration_profile_binding={'ref':shared.profile_binding['ref'],'sha256':'1'*64})
  except F.Refusal:pass
  else:raise AssertionError('mismatched constructor profile admitted')
 case('08-constructor-selected-shared-profile-positive-and-mismatch-refusal',shared)
 def caller_approval():
  c=f.checkpoint_call('caller-outcome');c['message']['ordered_outcomes'][0]['selected_outcome']='reject';c['message']['all_required_members_authorized']=False;call(f,c,'error','integrity-failed')
  c=f.admission_call(f.host.object(F.encoded(f.resolution)),'unrecorded-admission');call(f,c,'error','gate-required')
  c=f.admission_call(f.host.object(F.encoded(f.resolution)),'repository-admission');c['message']['authority_scope']='repository';call(f,c,'error','gate-required');assert f.host.cut()==initial
 case('09-unsigned-changed-owner-outcome-and-unrecorded-or-repository-admission-refusal',caller_approval)
 def accountable_caller():
  original=copy.deepcopy(f.policy);f.service.close();f.policy['principal_ref']='principal:independently-authenticated-other-operator';f.write_policy();f.open()
  try:call(f,f.checkpoint_call('alternate-accountable-caller'),'error','unauthorized')
  finally:f.service.close();f.policy=original;f.write_policy();f.open()
 case('09b-actual-alternate-nonce-authenticated-caller-cannot-resolve-owner-bundle',accountable_caller)
 def checkpoint():
  global checkpoint_result,checkpoint_call
  checkpoint_call=f.checkpoint_call();r=call(f,checkpoint_call);checkpoint_result=r['message'];assert checkpoint_result['result']=='pass';assert f.host.cut()==initial
  c=copy.deepcopy(checkpoint_call);c['call_id']='call:checkpoint-retry:'+uuid.uuid4().hex;assert call(f,c)['message']==checkpoint_result
  c=f.checkpoint_call('second-fresh-resolution');call(f,c,'error','conflict')
 case('10-positive-materialized-checkpoint-and-exact-retry-no-second-resolution',checkpoint)
 def uncertainty():
  row=f.service.inspect_owned('checkpoint.resolve',checkpoint_call['idempotency_key']);c=f.admission_call(row['message_binding'],'fault:admission');native_atomic=F.C.atomic
  def interfered(path,raw):
   native_atomic(path,raw)
   if Path(path).name=='PENDING.json':
    native_atomic(f.root/'native-store/transactions/0000000001.json',b'owned qualification fault: uncommitted next sequence occupied')
  try:F.C.atomic=interfered;r=call(f,c,'error','indeterminate')
  finally:F.C.atomic=native_atomic
  assert f.host.cut()==initial and (f.root/'native-store/PENDING.json').exists()
  c['call_id']='call:uncertain-retry:'+uuid.uuid4().hex;call(f,c,'error','recovery-required')
  ic=f.call('operation.inspect',{'schema_version':'lab-operation-inspect-request/v1-candidate','request_ref':'request:inspect-uncertain','actor':f.actor,'lookup':{'operation':'admission.apply','idempotency_key':'fault:admission'},'budget':{'max_actions':0,'max_input_bytes':1048576,'max_output_bytes':1048576,'deadline':F.iso(F.now()+timedelta(minutes=10))},'authority_effect':'none'},None)
  inspect=call(f,ic)['message'];assert inspect['posture']=='indeterminate' and inspect['retry_allowed'] is False
  f.host.store.recover(initial['commit_sha256']);assert f.host.cut()==initial and not (f.root/'native-store/PENDING.json').exists()
  c['call_id']='call:post-recovery-no-redispatch:'+uuid.uuid4().hex;call(f,c,'error','recovery-required')
 case('11-real-native-pending-fault-inspection-and-owned-recovery-with-no-redispatch',uncertainty)
 def admission_positive():
  global admission
  row=f.service.inspect_owned('checkpoint.resolve',checkpoint_call['idempotency_key']);c=f.admission_call(row['message_binding'],'positive:admission');r=call(f,c);admission=r['message'];assert admission['posture']=='committed' and admission['post_cut']['commit_sequence']==1 and admission['file_generation_posture']=='not-selected' and admission['projection_posture']=='pending'
  tx=f.host.snapshot()['transactions'][-1];assert F.U.original_bytes(f.host.store,f.native['targets'][0]['version_ref'],tx['digest'])==F.U.decode_content(f.native['targets'][0]['content'])
  c['call_id']='call:committed-retry:'+uuid.uuid4().hex;assert call(f,c)['message']==admission and f.host.cut()['commit_sequence']==1
 case('12-positive-signed-owned-admission-exact-byte-readback-and-no-double-commit',admission_positive)
 def source_drift():
  p=HERE/'service.py';raw=p.read_bytes()
  try:p.write_bytes(raw+b'\n');c=f.capability_call('code-drift');call(f,c,'error','integrity-failed');assert not f.service.operation_path(c['operation'],c['idempotency_key']).exists()
  finally:p.write_bytes(raw)
  p=HERE/'execution-dependency-selection.json';raw=p.read_bytes()
  try:p.write_bytes(raw+b' ');call(f,f.capability_call('selected-schema-closure-drift'),'error','integrity-failed')
  finally:p.write_bytes(raw)
 case('13-selected-source-code-and-schema-closure-drift-refusal',source_drift)
 f.service.close()
with tempfile.TemporaryDirectory(prefix='cal-governance-0148-rejection-') as tmp:
 f=F.Fixture(tmp,schemas);f.service.close();f.resolution=f.outcome('reject');f.write_policy();f.open()
 def reject():
  c=f.checkpoint_call('reject:checkpoint');r=call(f,c);assert r['message']['result']=='pass' and 'False' in r['message']['claim_ceiling'];row=f.service.inspect_owned('checkpoint.resolve',c['idempotency_key']);call(f,f.admission_call(row['message_binding'],'reject:admission'),'error','gate-required');assert f.host.cut()['commit_sequence']==0
 case('14-valid-actual-synthetic-rejection-records-no-admission',reject);f.service.close()
print('Full frozen history guard at qualification exit',flush=True);F.G.verify(F.BASE_SOURCE);F.guard(SOURCE)
proof={'schema_version':'lab-public-governance-qualification/v1-candidate','result':'PASS' if all(r['result']=='PASS' for r in results) else 'FAIL','started_at':start,'ended_at':F.iso(F.now()),'source_sha256':SOURCE,'profile_sha256':PROFILE,'base_source_sha256':F.BASE_SOURCE,'base_profile_sha256':F.BASE_PROFILE,'actual_cases':len(results),'actual_public_calls':len(responses),'cases':results,'responses':responses,'full_history_entry_exit_guards':True,'fresh_selected_execution_guards_every_boundary':True,'actual_owner_outcome':None,'canonical_admissions_applied':0,'runtime_activations':0,'external_effects':0,'goal_complete':False,'whole_api_qualified':False,'claim_ceiling':F.CEILING+' Real synthetic operator signatures, nonce proofs, original public envelopes, owned native transactions, fault residue and recovery only.'}
path=RUN/'Governance-public-qualification-0148-v3.json';path.write_text(json.dumps(proof,indent=2,sort_keys=True)+'\n');print(json.dumps({k:v for k,v in proof.items() if k not in ('cases','responses')}),flush=True)
raise SystemExit(0 if proof['result']=='PASS' else 1)
