"""Original API contracts, exact durable retries and explicit publication uncertainty."""
import copy,secrets
from .governance import *
class GovernanceService:
 def __init__(self,host,channel):
  need(type(host) is GovernanceHost and type(channel) is GovernanceChannel and channel.host is host,'unauthorized','Actual independent governance host/channel required.')
  self.host=host;self.channel=channel;self.schemas=host.schemas;self.profile_binding=host.profile_binding;self.seen=set()
 def reply(self,call,raw,domain,kind='result'):
  privacy(domain)
  result={'schema_version':'lab-api-reply/v2-candidate','contract_profile_binding':self.profile_binding,'call_id':call['call_id'],'operation':call['operation'],'request_binding':binding('call:governance:'+self.channel.connection+':'+call['call_id'],raw),'trusted_context_binding':binding(self.channel.context['context_ref'],encoded(self.channel.context)),'handler_binding':binding((HERE/'service.py').relative_to(ROOT).as_posix(),(HERE/'service.py').read_bytes()),'observed_at':iso(now()),'kind':kind,'message':domain}
  need(self.schemas.valid('api-reply',result),'integrity-failed','Actual governance reply violates exact original public envelope.')
  need(len(encoded(result))<=min(call['max_response_bytes'],self.host.policy['max_response_bytes']),'budget-exceeded','Actual governance result exceeds response bound.')
  if kind=='result' and self.host.active_deadline is not None and now()>=self.host.active_deadline:raise Refusal('indeterminate' if call['operation'] in OPERATIONS else 'deadline-exceeded','Actual reply deadline expired; inspect any durable governance effect before retry.')
  return result
 def error(self,call,raw,inner,code,message):
  return self.reply(call,raw,{'schema_version':'lab-error-result/v1-candidate','request_binding':binding('message:'+call['call_id'],inner),'code':code,'message':message,'gaps':[],'retry_policy':'reconcile-first' if code in ('indeterminate','recovery-required') else 'no-retry','evidence_bindings':[],'authority_effect':'none'},'error')
 def transport(self,raw,code,call_id=None):
  return {'schema_version':'lab-api-transport-error/v1-candidate','call_id':call_id,'request_byte_sha256':sha(raw),'code':code,'public_message':'Governance transport rejected this bounded unauthenticated or invalid original envelope.','effect_may_have_started':False,'recovery_policy':'no-retry','authority_effect':'none'}
 def operation_path(self,name,key):
  c=self.channel.guard();return self.host.root/'operations'/sha(encoded([c['principal_ref'],c['authority_scope'],c['scope_refs'],name,key]))
 def fingerprint(self,call):
  jcs=__import__(BASE_NAME+'.jcs',fromlist=['*'])
  return sha(jcs.dumps({'operation':call['operation'],'expected_source_cut':call['expected_source_cut'],'profile':call['expected_contract_profile_binding'],'message':call['message']}))
 def execute(self,call,inner,raw):
  host=self.host;m=call['message'];name=call['operation'];key=call['idempotency_key'];path=self.operation_path(name,key);fp=self.fingerprint(call)
  if path.exists():
   prior=parse(private(path));need(prior['fingerprint']==fp,'idempotency-conflict','Durable key selects different exact governance control inputs.')
   need(prior.get('result') is not None,'recovery-required','Durable governance key is pending or uncertain; inspect owned original residue without redispatch.')
   # Current channel, policy and full source guards were checked before lookup.
   # Exact retry is historical evidence; never reapply against a new HEAD.
   if name=='admission.apply':
    d=host.snapshot();need(any(tx['digest']==prior['result']['commit_binding']['sha256'] or sha(encoded(tx))==prior['result']['commit_binding']['sha256'] for tx in d['transactions']),'integrity-failed','Recorded admitted transaction is missing from verified current history.')
   return prior['result']
  current=host.cut();need(call['expected_source_cut']==current,'stale-cut','Governance call does not select exact current owned native cut.')
  if name=='checkpoint.resolve':
   for oldpath in (host.root/'operations').iterdir():
    if oldpath.name.endswith('.governance-staging'):continue
    old=parse(private(oldpath))
    if old['operation']=='checkpoint.resolve' and old.get('result') is not None:
     oldmessage=host.document(old['message_binding']);need(oldmessage['checkpoint_binding']!=m['checkpoint_binding'],'conflict','This exact checkpoint already has a durably recorded outcome; inspect it rather than recording a second fresh resolution.')
   verify_checkpoint(host,m,current)
  elif name=='admission.apply':
   native,approval=admission_preflight(host,m,current,key)
  else:
   # Run exact full capability selection before any durable claim/effect.
   capability_preflight(host,self.channel,m,current)
  host.guard();need(now()<host.active_deadline,'deadline-exceeded','Deadline expired before governance journal claim.')
  need(len([p for p in (host.root/'operations').iterdir() if not p.name.endswith('.governance-staging')])<host.policy['max_actions'],'budget-exceeded','Owned governance action budget exhausted.')
  item={'schema_version':'lab-owned-governance-operation/v1-candidate','operation':name,'fingerprint':fp,'message_binding':host.object(inner),'original_call_binding':host.object(raw),'pre_cut':current,'started_at':iso(now()),'result':None,'posture':'pending','effect_may_have_started':False,'authority_effect':'none'}
  # The final actual-clock check directly precedes the durable claim.
  need(now()<host.active_deadline,'deadline-exceeded','Deadline expired before governance durable key creation.');put(path,encoded(item))
  try:
   host.guard();item['effect_may_have_started']=True;save(path,item)
   if name=='checkpoint.resolve':result=checkpoint_result(host,m,inner,current)
   elif name=='admission.apply':result=admission_result(host,m,inner,native,approval)
   else:result=capability_result(host,self.channel,m,inner,key,current)
   contract=host.schemas.operations[name]
   need(host.schemas.protocol_valid(contract['result_schema']['resource_uri'],result),'integrity-failed','Actual governance domain result violates exact original result schema.')
   item['result']=result;item['result_binding']=host.object(encoded(result));item['posture']='recorded';item['ended_at']=iso(now());save(path,item)
   if now()>=host.active_deadline:raise Refusal('indeterminate','Actual governance result was recorded after response deadline; inspect the exact durable key before retry.')
   return result
  except Exception as error:
   if item['result'] is None:
    item['posture']='uncertain';item['failure_observed_at']=iso(now());save(path,item)
   if isinstance(error,Refusal):raise
   raise Refusal('indeterminate','Owned governance effect may have started; its durable key retains uncertainty and must not redispatch.') from error
 def call(self,raw):
  try:context=self.channel.guard()
  except Exception:return self.transport(raw,'unauthenticated-channel')
  if type(raw) is not bytes or len(raw)>self.host.policy['max_request_bytes']:return self.transport(raw,'input-too-large')
  try:call=parse(raw)
  except Exception:return self.transport(raw,'malformed-json')
  if not self.schemas.valid('api-call',call):return self.transport(raw,'invalid-envelope')
  if call['operation'] not in (*OPERATIONS,'operation.inspect'):return self.transport(raw,'unsupported-operation',call['call_id'])
  if call['call_id'] in self.seen:return self.transport(raw,'invalid-call-id',call['call_id'])
  self.seen.add(call['call_id']);inner=P.message_bytes(raw)
  try:
   need(len(self.seen)<=self.host.policy['max_calls'],'budget-exceeded','Governance authenticated call budget exhausted.')
   need(call['caller_context_ref']==context['context_ref'],'unauthorized','Opaque governance context differs from authenticated nonce channel.')
   need(call['expected_contract_profile_binding']==self.profile_binding,'invalid-contract','Call selects another governance profile.')
   need(call['max_response_bytes']>=65536,'budget-exceeded','Response budget cannot hold bounded governance evidence.')
   if call['operation']!='operation.inspect':need(isinstance(call['idempotency_key'],str) and call['idempotency_key'],'invalid-contract','Governance operation requires an exact durable command key.')
   privacy(call)
   m=call['message'];contract=self.schemas.operations[call['operation']]
   need(self.schemas.protocol_valid(contract['request_schema']['resource_uri'],m),'invalid-contract','Governance request violates original exact API domain contract.')
   if 'actor' in m:need(m['actor']==self.channel.actor(),'unauthorized','Caller Actor differs from actual authenticated governance channel.')
   self.host.active_deadline=min(instant(call['deadline']),instant(context['expires_at']))
   if call['operation']=='operation.inspect':self.host.active_deadline=min(self.host.active_deadline,instant(m['budget']['deadline']))
   if call['operation']=='capability.adoption.prepare':self.host.active_deadline=min(self.host.active_deadline,instant(m['authority_basis']['expires_at']))
   need(now()<self.host.active_deadline,'deadline-exceeded','Strictest actual governance deadline has expired.')
   self.host.guard()
   with self.host.locked():
    # Lock wait is included in the actual strictest deadline.
    self.channel.guard();need(now()<self.host.active_deadline,'deadline-exceeded','Deadline expired while waiting for owned governance lock.');self.host.guard()
    result=self.inspection_result(call,inner) if call['operation']=='operation.inspect' else self.execute(call,inner,raw)
   return self.reply(call,raw,result)
  except Refusal as error:return self.error(call,raw,inner,error.code,error.message)
  except Exception:return self.error(call,raw,inner,'integrity-failed','Independent source, exact material closure or selected owner/channel signature could not be verified.')
  finally:self.host.active_deadline=None
 def inspection_result(self,call,inner):
  m=call['message'];budget=m['budget'];need(budget['max_actions']==0 and budget['max_input_bytes']>=len(encoded(call)),'budget-exceeded','Governance inspection requires a sufficient read-only budget.')
  need(now()<instant(budget['deadline']),'deadline-exceeded','Governance inspection message deadline expired.')
  lookup=m['lookup'];found=[]
  if 'operation' in lookup:
   need(lookup['operation'] in OPERATIONS,'unauthorized','Independent governance inspection scope names only its owned operations.')
   path=self.operation_path(lookup['operation'],lookup['idempotency_key'])
   if path.exists():found=[parse(private(path))]
  else:
   for path in (self.host.root/'operations').iterdir():
    if path.name.endswith('.governance-staging'):continue
    row=parse(private(path))
    if row.get('original_call_binding')==lookup['call_binding']:found.append(row)
  need(len(found)==1,'not-found','Exact scoped governance operation key/call is unavailable.')
  row=found[0];result=row.get('result');posture='completed' if result is not None else 'indeterminate' if row['effect_may_have_started'] else 'pending'
  rb=row.get('result_binding') if result is not None else None
  if rb is not None:need(self.host.document(rb)==result,'integrity-failed','Original recorded domain result bytes changed.')
  # Read-only inspection never clears keys, removes residue, or reapplies.
  evidence=[binding('owned-operation:'+row['fingerprint'],encoded(row))]
  if row['operation']=='admission.apply':
   data=self.host.snapshot()
   matches=[t for t in data['transactions'][1:] if t['proposal']==self.host.document(self.host.policy['review_selection']['target_package_binding'])]
   for tx in matches:evidence.append(binding('native-transaction:'+tx['digest'],encoded(tx)))
   for relative in self.host.store.leftovers(data['head']):
    path=self.host.store.path/relative;need(path.is_file() and not path.is_symlink(),'integrity-failed','Unrecognized native publication residue boundary.');evidence.append(binding('owned-native-residue:'+relative,path.read_bytes()))
  return {'schema_version':'lab-operation-inspect-result/v1-candidate','request_binding':binding(m['request_ref'],inner),'original_call_binding':row['original_call_binding'],'operation':row['operation'],'posture':posture,'result_binding':rb,'effect_evidence_bindings':evidence,'reconciliation_required':result is None,'retry_allowed':False,'gaps':[],'claim_ceiling':CEILING+' Inspection preserves uncertain keys and committed history.','authority_effect':'none'}
 def inspect_owned(self,operation,key):
  self.channel.guard();self.host.guard();path=self.operation_path(operation,key)
  need(path.exists(),'not-found','Owned durable governance key is unavailable.');return copy.deepcopy(parse(private(path)))
 def close(self):self.channel.close()
