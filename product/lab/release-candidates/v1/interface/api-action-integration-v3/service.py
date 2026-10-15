"""Original public Action contracts with fresh authority and durable recovery."""
import base64,copy,fcntl,os,re,time
from dataclasses import replace
from contextlib import contextmanager
from .runtime import *

class Refusal(ValueError):
 def __init__(self,code,message):self.code=code;self.message=message

def need(value,code,message):
 if not value:raise Refusal(code,message)

def save(path,value):
 """Host-owned private atomic evidence/checkpoint update."""
 staging=path.with_name(path.name+'.action-staging')
 fd=os.open(staging,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as stream:stream.write(P.compact(value));stream.flush();os.fsync(stream.fileno())
 os.replace(staging,path)
 from counter import fsync_directory
 fsync_directory(path.parent)

class ActionService:
 def __init__(self,runtime,channel,schemas,*,source_sha256,profile_sha256,integration_profile_binding=None):
  require(type(runtime) is ActionRuntime and type(channel) is ActionChannel and channel.runtime is runtime,'independent actual Action runtime/channel required')
  self.runtime=runtime;self.channel=channel;self.schemas=schemas;self.seen=set()
  self.profile_path=HERE/'contract-profile.json';self.profile_raw=self.profile_path.read_bytes()
  require(byte_sha(self.profile_raw)==profile_sha256,'independent Action profile pin differs')
  require(byte_sha((HERE/'source-manifest.json').read_bytes())==source_sha256,'independent Action source pin differs')
  self.runtime.source_pin=source_sha256
  self.profile_binding=binding(str(self.profile_path.relative_to(ROOT)),self.profile_raw)
  self.profile=parse(self.profile_raw)
  require(self.profile['implemented_operations']==list(OPERATIONS),'exact additive Action operation profile differs')
  if integration_profile_binding is None:
   require(self.profile['base_contract_profile_binding']==schemas.profile_binding,'exact default original schema profile differs')
  else:
   require(integration_profile_binding==schemas.profile_binding,'independent shared schema profile differs')
   G._verify_files(ROOT,[{'path':integration_profile_binding['ref'],'sha256':integration_profile_binding['sha256']}])
   shared=parse((ROOT/integration_profile_binding['ref']).read_bytes())
   require(shared==schemas.profile and set(OPERATIONS)<=set(shared['implemented_operations']) and shared['authority_effect']=='none' and shared['actual_owner_outcome'] is None and shared['original_operation_catalog_binding']==self.profile['original_operation_catalog_binding'],'shared profile does not declare exact contributed Action operations')
   original={r['operation']:r for r in parse((ROOT/'docs/proposals/0008-lab-api-contracts/api-contracts.json').read_bytes())['operations']}
   require(schemas.operations==original,'shared schemas changed original API operation meanings')
   original_selection=parse((BASE/'contract-profile.json').read_bytes())['protocol_resource_selection_binding'];original_mapping=parse((ROOT/original_selection['path']).read_bytes())['uri_mapping']
   require(schemas.uri_mapping==original_mapping,'shared schemas changed original exact protocol URI meanings')
   self.profile_binding=copy.deepcopy(integration_profile_binding)
   self.runtime.integration_profile_binding=copy.deepcopy(integration_profile_binding)
  require(channel.selected_profile_binding==self.profile_binding,'authenticated nonce was not bound to this selected integration profile')
  self.lock_path=runtime.root/'.api-action.lock'
  if not self.lock_path.exists():
   fd=os.open(self.lock_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.close(fd)
  runtime.checkpoint=lambda observed:save(runtime.root/'ledger-pins.json',__import__('dataclasses').asdict(observed))
 @contextmanager
 def locked(self):
  private(self.lock_path);fd=os.open(self.lock_path,os.O_RDWR|os.O_NOFOLLOW)
  try:
   fcntl.flock(fd,fcntl.LOCK_EX);yield
  finally:fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
 def cut(self):
  src=self.runtime.source();ref=src['refs']['agent-profile']
  return {'store_ref':'store:owned-action:'+self.runtime.root.name,'branch_ref':'branch:isolated-action-0148','commit_sequence':0,'commit_sha256':self.runtime.status()['head'],'source_profile_sha256':src['records'][ref]['sha256'],'streams':[]}
 def actor(self):
  c=self.channel.guard()
  return {'principal_ref':c['principal_ref'],'role_assignment_refs':c['role_assignment_bindings'],'agent_instance_ref':c['agent_instance_ref'],'session_ref':c['session_ref'],'assignment_ref':c['assignment_ref']}
 def evidence(self,ref,raw):
  digest=byte_sha(raw);path=self.runtime.root/'materials'/digest
  if not path.exists():
   from .fixture import put
   put(path,raw)
  need(private(path)==raw,'integrity-failed','Owned immutable evidence differs.')
  return binding(ref,raw)
 def material(self,b):
  need(b['content_ref']=='action-content:'+b['byte_sha256'],'unresolved-reference','Input is not an independently selected owned content reference.')
  try:raw=private(self.runtime.root/'materials'/b['byte_sha256'])
  except Exception as error:raise Refusal('unresolved-reference','Selected owned content is unavailable.') from error
  need(content(b['content_ref'],raw)==b,'integrity-failed','Selected input original bytes differ.')
  return raw
 def preflight(self,message,call):
  need(message['actor']==self.actor(),'unauthorized','Action Actor differs from this authenticated live channel.')
  need(call['expected_source_cut']==self.cut(),'stale-cut','Selected public source cut differs.')
  if call['operation']=='action.reconcile':
   need(message['expected_cut']==self.cut(),'stale-cut','Recovery source cut differs.');return
  need(message['source_cut']==self.cut(),'stale-cut','Action source cut differs.')
  src=self.runtime.source();refs=src['refs'];assignment=self.runtime.resolve(refs['agent-assignment']);d=parse(assignment.original)
  need(message['assignment']=={'scope_ref':src['scope_ref'],'identity_ref':d['node_id'],'version_ref':assignment.version_ref,'carrier_ref':'cal.artifact-type.agent-assignment/v1','byte_sha256':assignment.expected_sha256},'unresolved-reference','Exact selected live Assignment differs.')
  delegation=self.runtime.resolve(refs['delegation'])
  need(message['authority_envelope_binding']==binding(delegation.version_ref,delegation.original),'unauthorized','Exact independently selected Delegation differs.')
  need(message['tool_adapter_binding']==binding(str((W02/'tools/counter.py').relative_to(ROOT)),(W02/'tools/counter.py').read_bytes()),'integrity-failed','Selected qualified adapter bytes differ.')
  need(message['expected_output_contracts']==[binding('protocol:w02-counter-output:'+byte_sha(encoded(OUTPUT_CONTRACT)),encoded(OUTPUT_CONTRACT))],'invalid-contract','Exact adapter output contract differs.')
  bounds=message['bounds'];grant=self.runtime.grant()
  need(bounds['filesystem_scope_refs']==[grant.scope_ref] and bounds['network_scope_refs']==[] and bounds['allowed_action_kinds']==['increment-local-counter'] and message['action_kind']=='increment-local-counter' and bounds['stop_conditions']==['action-authority-ended','owned-counter-budget-reached'],'unauthorized','Independent local Action scope or stop conditions differ.')
  budget=bounds['budget'];need(1<=budget['max_actions']<=grant.max_actions and 1<=budget['max_input_bytes']<=grant.max_input_bytes and 1<=budget['max_output_bytes']<=grant.max_output_bytes,'budget-exceeded','Action budget exceeds independent host grant.')
  need(timestamp(budget['deadline'])>time.time(),'deadline-exceeded','Action message deadline expired.')
  need(len(message['input_bindings'])==1,'invalid-contract','Exactly one selected local Tool input is required.')
  raw=self.material(message['input_bindings'][0]);need(len(raw)<=budget['max_input_bytes'],'budget-exceeded','Original local Tool input exceeds caller budget.')
  from jsonschema import Draft202012Validator
  need(Draft202012Validator(INPUT_CONTRACT).is_valid(parse(raw)),'invalid-contract','Original input does not match the qualified local Tool contract.')
 def mapped(self,message):
  src=self.runtime.source();refs=src['refs']
  request={'principal_ref':refs['principal'],'instance_ref':self.runtime.session.instance_ref,'session_ref':self.runtime.session.session_ref,'assignment_ref':refs['agent-assignment'],'delegation_ref':refs['delegation'],'role_assignment_ref':refs['role-assignment'],'tool_ref':refs['tool'],'scope_ref':src['scope_ref'],'action_kind':message['action_kind'],'idempotency_key':message['idempotency_key'],'input_sha256':message['input_bindings'][0]['byte_sha256'],'deadline':message['bounds']['budget']['deadline'],'expected_head':self.runtime.status()['head'],'redelegating':False,'instance_record_ref':refs['agent-instance'],'session_record_ref':refs['agent-session'],'profile_ref':refs['agent-profile']}
  return encoded(request)
 def evaluation(self,message,inner,raw,*,recovery=False):
  observed=self.runtime.authority.check(raw,recovery=recovery);evidence=observed['evidence_bindings']
  value={'schema_version':'lab-authority-evaluation/v1-candidate','evaluation_ref':'evaluation:action:'+byte_sha(inner),'request_binding':binding(message['request_ref'],inner),'authority_envelope_binding':message['authority_envelope_binding'],'source_cut':message['source_cut'],'evaluated_at':now(),'expires_at':iso(min(timestamp(message['bounds']['budget']['deadline']),self.runtime.grant().expires_at,self.runtime.session.expires)),'posture':observed['posture'],'checks':[{'check_ref':'check:action:'+c['check'],'obligation_ref':'O-AUTHORITY','result':'pass' if c['result']=='PASS' else 'fail','evidence_bindings':evidence,'claim_ceiling':CEILING} for c in observed['checks']],'evidence_bindings':evidence,'gaps':[],'authority_effect':'none'}
  self.evidence(value['evaluation_ref'],P.compact(value));return value
 def receipt(self,message,inner,evaluation,observed,started):
  outputs=[]
  if observed.get('output') is not None:
   raw=encoded(observed['output']);digest=byte_sha(raw);self.evidence('action-content:'+digest,raw);outputs=[content('action-content:'+digest,raw)]
  residue=[]
  if observed['posture']=='indeterminate':
   raw=private(self.runtime.root/'ledger'/'journal.json') if (self.runtime.root/'ledger'/'journal.json').stat().st_mode&0o777==0o600 else (self.runtime.root/'ledger'/'journal.json').read_bytes()
   residue=[self.evidence('action-residue:'+observed['action_id'],raw)]
  value={'schema_version':'lab-action-receipt/v1-candidate','receipt_ref':'receipt:action:'+byte_sha(inner),'request_binding':binding(message['request_ref'],inner),'authority_evaluation_binding':binding(evaluation['evaluation_ref'],P.compact(evaluation)),'actor':message['actor'],'started_at':None if observed['posture']=='denied' else started,'ended_at':None if observed['posture']=='indeterminate' else now(),'posture':observed['posture'],'output_bindings':outputs,'observation_refs':[],'residue_bindings':residue,'reconciliation_required':observed.get('reconciliation_required',False),'retry_allowed':False,'claim_ceiling':CEILING,'authority_effect':'none'}
  if observed['posture'] in ('completed','failed','indeterminate','denied'):
   action=materialize_action(self.mapped(message),observed,value['receipt_ref']);raw=encoded(action);self.evidence(action['node_id'],raw)
   value['observation_refs']=[{'scope_ref':action['scope_ref'],'identity_ref':action['node_id'],'version_ref':action['node_id']+'@observed.1','carrier_ref':'cal.artifact-type.agent-action/v1','byte_sha256':byte_sha(raw)}]
  self.evidence(value['receipt_ref'],P.compact(value));return value
 def operation_path(self,name,key):
  c=self.channel.context;namespace=[c['principal_ref'],c['authority_scope'],c['scope_refs'][0],name,key]
  return self.runtime.root/'operations'/byte_sha(P.compact(namespace))
 def fingerprint(self,message):
  from .dependencies import P
  return byte_sha(__import__(P.__package__+'.jcs',fromlist=['dumps']).dumps(message))
 def recover(self,message,call,inner):
  need(message['recovery_kind']=='action-reconciliation','invalid-contract','Only selected Action observational recovery is supported.')
  need(message['recovery_contract_binding']==binding(str((W02/'authority/dispatch.py').relative_to(ROOT)),(W02/'authority/dispatch.py').read_bytes()),'integrity-failed','Exact qualified recovery contract differs.')
  basis=message['authority_basis'];src=self.runtime.source();delegation=self.runtime.resolve(src['refs']['delegation'])
  need(basis['authority_scope']=='delegated-action' and basis['owner_principal_ref']==self.actor()['principal_ref'] and basis['scope_refs']==[src['scope_ref']] and basis['evidence_bindings']==[binding(delegation.version_ref,delegation.original)] and basis['policy_bindings']==[self.channel.policy['grant_binding']],'unauthorized','Independent recovery permission or authority basis differs.')
  need(time.time()<timestamp(basis['expires_at'])<=self.runtime.grant().expires_at,'expired-authority','Recovery authority period differs or expired.')
  subject=message['subject_binding'];found=[]
  for path in (self.runtime.root/'operations').iterdir():
   item=parse(private(path));receipt=item.get('result')
   if item['operation']=='action.dispatch' and receipt is not None and receipt['receipt_ref']==subject['ref'] and byte_sha(P.compact(receipt))==subject['sha256']:found.append((path,item))
  need(len(found)==1,'not-found','Exact owned Action receipt is unavailable.')
  path,item=found[0];receipt=item['result']
  need(message['allowed_residue_bindings']==receipt['residue_bindings'],'unauthorized','Recovery residue selection differs from the exact owned Action receipt.')
  original=base64.b64decode(item['mapped_b64'],validate=True);recovery=parse(original);recovery['deadline']=iso(min(timestamp(call['deadline']),timestamp(basis['expires_at']),self.runtime.grant().expires_at))
  dispatcher=self.runtime.dispatcher();observed=dispatcher.reconcile(original,recovery_request=encoded(recovery));self.runtime.checkpoint(dispatcher.expected)
  need(observed['posture']!='denied','unauthorized','Current selected recovery authority denied.')
  raw=encoded(observed);observed_binding=self.evidence('reconciliation:'+byte_sha(inner),raw)
  return {'schema_version':'lab-recovery-receipt/v1-candidate','request_binding':binding(message['request_ref'],inner),'pre_cut':message['expected_cut'],'post_cut':self.cut(),'posture':'indeterminate' if observed['posture']=='indeterminate' else 'recovered','observed_bindings':[observed_binding],'removed_uncommitted_bindings':[],'committed_history_removed':False,'gaps':[],'claim_ceiling':CEILING,'authority_effect':'none','retry_allowed':False}
 def execute(self,call,inner):
  from .inspection import inspect,record_call,dispatch_original
  name=call['operation'];m=call['message']
  if name=='operation.inspect':return inspect(self,m,call,inner)
  self.preflight(m,call)
  if name=='action.evaluate':
   raw=self.mapped(m);result=self.evaluation(m,inner,raw);record_call(self,name,m['idempotency_key'],raw,result=result);return result
  key=call['idempotency_key'];need(name!='action.dispatch' or key==m['idempotency_key'],'invalid-contract','Outer and inner Action idempotency keys differ.')
  path=self.operation_path(name,key);fingerprint=self.fingerprint(m);existing=None
  if name=='action.dispatch':record_call(self,name,key,self.mapped(m),operation_path=path)
  if path.exists():
   existing=parse(private(path));need(existing['fingerprint']==fingerprint,'idempotency-conflict','Key names a different exact semantic Action request.')
   if existing.get('result') is not None:
    original=base64.b64decode(existing['mapped_b64'],validate=True) if name=='action.dispatch' else None
    if name=='action.dispatch':
     need(self.runtime.authority.check(original)['posture']=='permitted','unauthorized','Current permission denies reading the recorded Action result.')
    else:
     # Reconciliation of a completed ledger entry only observes its receipt.
     # Recheck the full current recovery actor before returning recorded bytes.
     self.recover(m,call,inner)
    return existing['result']
  if name=='action.reconcile':
   result=self.recover(m,call,inner);save(path,{'operation':name,'fingerprint':fingerprint,'result':result});record_call(self,name,key,dispatch_original(self,m['subject_binding']),operation_path=path);return result
  raw=self.mapped(m);evaluation=self.evaluation(m,inner,raw)
  dispatcher=self.runtime.dispatcher()
  budget=m['bounds']['budget']
  # Restrict host permission to caller budgets for the duration of the locked actual dispatch.
  grant_reader=self.runtime.authority.grant_reader
  self.runtime.authority.grant_reader=lambda:replace(grant_reader(),max_actions=min(grant_reader().max_actions,budget['max_actions']),max_input_bytes=min(grant_reader().max_input_bytes,budget['max_input_bytes']),max_output_bytes=min(grant_reader().max_output_bytes,budget['max_output_bytes']))
  item=existing or {'operation':name,'fingerprint':fingerprint,'mapped_b64':base64.b64encode(raw).decode(),'started_at':now(),'result':None}
  if existing is None:save(path,item)
  try:
   self.effect_possible=True
   observed=dispatcher.dispatch(raw,self.material(m['input_bindings'][0]),pending_observer=self.runtime.checkpoint)
   self.runtime.checkpoint(dispatcher.expected)
  finally:self.runtime.authority.grant_reader=grant_reader
  result=self.receipt(m,inner,evaluation,observed,item['started_at']);item['result']=result;save(path,item);return result
 def reply(self,call,raw,message,kind='result'):
  value={'schema_version':'lab-api-reply/v2-candidate','contract_profile_binding':self.profile_binding,'call_id':call['call_id'],'operation':call['operation'],'request_binding':binding('call:'+self.channel.connection+':'+call['call_id'],raw),'trusted_context_binding':binding(self.channel.context['context_ref'],P.compact(self.channel.context)),'handler_binding':binding(str((HERE/'service.py').relative_to(ROOT)),(HERE/'service.py').read_bytes()),'observed_at':now(),'kind':kind,'message':message}
  require(self.schemas.valid('api-reply',value),'actual public Action reply violates original exact schema')
  require(len(P.compact(value))<=min(call['max_response_bytes'],self.channel.policy['max_response_bytes']),'actual public Action result exceeds preflight bound')
  return value
 def error(self,call,raw,inner,code,message):
  return self.reply(call,raw,{'schema_version':'lab-error-result/v1-candidate','request_binding':binding('message:'+call['call_id'],inner),'code':code,'message':message,'gaps':[],'retry_policy':'reconcile-first' if code in ('indeterminate','recovery-required') else 'no-retry','evidence_bindings':[],'authority_effect':'none'},'error')
 def transport(self,raw,code):
  messages={'unauthenticated-channel':'This channel has no current verified Action authentication.','malformed-json':'Input is not a supported bounded UTF-8 JSON object.','invalid-envelope':'Call does not match its exact declared Action envelope.'}
  value={'schema_version':'lab-api-transport-error/v1-candidate','call_id':None,'request_byte_sha256':byte_sha(raw) if type(raw) is bytes else None,'code':code,'public_message':messages[code],'effect_may_have_started':False,'recovery_policy':'no-retry','authority_effect':'none'}
  require(self.schemas.valid('transport-error',value),'actual Action transport refusal violates original exact schema')
  return value
 def call(self,raw):
  from .dependencies import P
  try:context=self.channel.guard()
  except Exception:return self.transport(raw,'unauthenticated-channel')
  try:call=P.frame_parse(raw)
  except Exception:return self.transport(raw,'malformed-json')
  if not self.schemas.valid('api-call',call) or call['operation'] not in OPERATIONS+('operation.inspect',):return self.transport(raw,'invalid-envelope')
  inner=P.message_bytes(raw)
  self.effect_possible=False
  try:
   need(len(raw)<=self.channel.policy['max_request_bytes'],'budget-exceeded','Original public Action call exceeds request budget.')
   need(call['call_id'] not in self.seen,'invalid-contract','Public Action call identifier already used.')
   self.seen.add(call['call_id']);need(len(self.seen)<=self.channel.policy['max_calls'],'budget-exceeded','Action channel call budget exceeded.')
   need(call['caller_context_ref']==context['context_ref'],'unauthorized','Public Action call context differs.')
   need(call['expected_contract_profile_binding']==self.profile_binding,'invalid-contract','Public Action call selects a different Action profile.')
   need(call['max_response_bytes']>=32768,'budget-exceeded','Response ceiling cannot hold the bounded actual Action evidence.')
   need(timestamp(call['deadline'])>time.time(),'deadline-exceeded','Public Action deadline expired.')
   self.runtime.current_call_deadline=min(timestamp(call['deadline']),timestamp(context['expires_at']))
   self.active_original_call_binding=binding('call:'+self.channel.connection+':'+call['call_id'],raw)
   guard(self.runtime.source_pin,integration_profile_binding=self.runtime.integration_profile_binding);self.schemas.guard()
   with self.locked():result=self.execute(call,inner)
   return self.reply(call,raw,result)
  except Refusal as error:return self.error(call,raw,inner,error.code,error.message)
  except BoundaryFault as error:
   detail=str(error);code='idempotency-conflict' if detail=='idempotency-conflict' else 'recovery-required' if 'reconciliation-required' in detail else 'integrity-failed'
   return self.error(call,raw,inner,code,'Current exact Action authority, Tool state or independent ledger binding could not be verified.')
  except (AssertionError,OSError,ValueError) as error:
   return self.error(call,raw,inner,'recovery-required' if self.effect_possible else 'integrity-failed','Current selected Action source or execution state could not be verified; any recorded pending Action must be reconciled.')
  finally:self.runtime.current_call_deadline=None;self.active_original_call_binding=None
 def owns_inspection(self,message):
  from .inspection import owns_inspection
  return owns_inspection(self,message)
 def close(self):self.channel.close()
