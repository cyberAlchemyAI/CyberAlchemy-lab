"""Fresh signed authority resolution, independent grant, actual runtime lease."""
import base64,copy,os,secrets,time,uuid
from pathlib import Path
from dataclasses import asdict
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from .dependencies import *
OPERATIONS=('action.evaluate','action.dispatch','action.reconcile')
CEILING='Observed isolated owned local counter action only; no canonical admission, Work satisfaction, service activation or human R08 outcome.'
POLICY_FIELDS={'schema_version','host_uid','public_key','principal_ref','scope_ref','expires_at','allowed_operations','source_binding','source_public_key','grant_binding','authority_effect','actual_owner_outcome','revoked','max_calls','max_request_bytes','max_response_bytes','contract_profile_binding','inspection_operations'}

def private(path):
 p=Path(path)
 require(p.is_absolute() and p.is_relative_to(Path('/tmp')) and p.resolve()==p and not any(a.is_symlink() for a in (p,*p.parents)),'owned absolute private /tmp file required')
 st=p.stat();require(p.is_file() and st.st_uid==os.getuid() and st.st_mode&0o777==0o600,'private file mode or owner differs')
 return p.read_bytes()

class ActionRuntime:
 def __init__(self,root,session,source_sha,source_public_key,grant_sha):
  require(isinstance(session,SessionLease) and session.clock is time.time,'actual UTC runtime Session lease required')
  self.root=Path(root);self.session=session;self.source_sha=source_sha;self.source_public_key=source_public_key;self.grant_sha=grant_sha
  self.adapter_sha256=byte_sha((W02/'tools/counter.py').read_bytes())
  self.environment_sha256=byte_sha(encoded({'python':__import__('sys').version,'network':False,'filesystem':str(self.root/'ledger')}))
  self.current_call_deadline=None;self.channel=None;self.source_pin=None;self.integration_profile_binding=None
  self.source();self.authority=HostAuthority(session,self.resolve,self.status,self.grant,adapter_sha256=self.adapter_sha256,environment_sha256=self.environment_sha256)
  session.context_reader=self.live
 def source(self):
  raw=private(self.root/'source.json');require(byte_sha(raw)==self.source_sha,'selected Action source changed')
  value=parse(raw);signature=private(self.root/'source.signature')
  Ed25519PublicKey.from_public_bytes(base64.b64decode(self.source_public_key,validate=True)).verify(base64.b64decode(signature,validate=True),raw)
  require(value['schema_version']=='lab-action-owned-source/v1-candidate' and value['authority_effect']=='none' and value['actual_owner_outcome'] is None,'owned Action source claim differs')
  require(value['runtime_bindings']=={'instance':self.session.instance_ref,'session':self.session.session_ref},'source does not bind the actual live lease')
  require(value['scope_ref']=='scope:R03-action-0148:'+self.root.name,'independent owned Action scope differs')
  return value
 def resolve(self,ref):
  value=self.source();row=value['records'].get(ref)
  if row is None:return None
  raw=base64.b64decode(row['original_b64'],validate=True)
  return SelectedRecord(ref,raw,row['sha256'],'isolated-candidate-current','action-source:'+self.source_sha+':'+ref)
 def status(self):
  value=self.source();raw=private(self.root/'status.json');status=parse(raw)
  require(set(status)==set(value['initial_status']),'closed current Action status required')
  # Revocation/stop/approval are current local host state. Stable attributions cannot be widened.
  for key in ('head','periods','active_policy_refs','role_versions','runtime_handle_bindings','tool_classes','selected_work_ref'):
   require(status[key]==value['initial_status'][key],'current Action status identity differs')
  require(type(status['stopped']) is bool and type(status['revoked_refs']) is list and type(status['reached_stop_conditions']) is list,'invalid current authority posture')
  return status
 def grant(self):
  raw=private(self.root/'grant.json');require(byte_sha(raw)==self.grant_sha,'independent Action grant changed or revoked')
  value=parse(raw);src=self.source()
  require(value['source_sha256']==self.source_sha and value['scope_ref']==src['scope_ref'] and value['allowed_operations']==list(OPERATIONS),'independent Action grant scope differs')
  require(value['inspection_operations']==['operation.inspect'],'explicit owned Action inspection permission differs')
  require(value['authorization_binding']==binding(str((ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json').relative_to(ROOT)),(ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json').read_bytes()),'development authorization changed')
  return HostGrant(value['principal_ref'],value['scope_ref'],frozenset(value['action_kinds']),value['tool_ref'],value['role_assignment_ref'],value['not_before'],value['expires_at'],value['max_actions'],value['max_input_bytes'],value['max_output_bytes'],'action-grant:'+self.grant_sha,raw,self.grant_sha,value['adapter_sha256'],value['environment_sha256'],value['recovery_allowed'])
 def live(self):
  guard(self.source_pin,integration_profile_binding=self.integration_profile_binding);self.source();self.grant()
  require(self.channel is not None,'independent authenticated Action channel absent')
  self.channel.guard(check_runtime=False)
  require(self.current_call_deadline is None or time.time()<self.current_call_deadline,'strict current public-call deadline expired')
  return {'head':self.status()['head']}
 def checkpoint(self,observed):
  atomic(self.root/'ledger-pins.json',asdict(observed))
 def dispatcher(self):
  value=parse(private(self.root/'ledger-pins.json'))
  return LocalDispatcher(self.root/'ledger',LedgerPins(**value),self.authority)
 def close(self):
  self.current_call_deadline=None;self.session.close()

class ActionChannel:
 def __init__(self,path,policy_sha,runtime,schemas,*,integration_profile_binding=None):
  require(type(runtime) is ActionRuntime,'selected Action runtime required')
  self.path=Path(path);self.expected_sha=policy_sha;self.runtime=runtime;self.schemas=schemas
  self.selected_profile_binding=copy.deepcopy(integration_profile_binding or binding(str((HERE/'contract-profile.json').relative_to(ROOT)),(HERE/'contract-profile.json').read_bytes()))
  self.context=None;self.used=False;self.closed=False
  self.connection='connection:R03-action:'+uuid.uuid4().hex;self.host='host:R03-action:'+uuid.uuid4().hex
  policy=self.policy_guard()
  self.challenge={'schema_version':'lab-local-action-challenge/v1-candidate','host_instance_ref':self.host,'connection_ref':self.connection,'nonce':secrets.token_hex(32),'policy_sha256':policy_sha,'contract_profile_binding':self.selected_profile_binding,'expires_at':policy['expires_at'],'authority_effect':'none'}
 def policy_guard(self):
  raw=private(self.path);require(byte_sha(raw)==self.expected_sha,'Action channel policy changed or revoked')
  p=parse(raw);require(set(p)==POLICY_FIELDS and p['schema_version']=='lab-local-action-policy/v1-candidate' and p['host_uid']==os.getuid() and p['authority_effect']=='none' and p['actual_owner_outcome'] is None and p['revoked'] is False,'closed independent Action policy required')
  from jsonschema import Draft202012Validator,FormatChecker
  require(Draft202012Validator(parse((HERE/'action-runtime-policy.schema.json').read_bytes()),format_checker=FormatChecker()).is_valid(p),'exact independent Action policy schema differs')
  require(p['allowed_operations']==list(OPERATIONS) and timestamp(p['expires_at'])>time.time(),'Action policy operations or lifetime differ')
  require(p['inspection_operations']==['operation.inspect'],'explicit owned Action channel inspection permission differs')
  require(p['source_binding']==binding('action-source:'+self.runtime.source_sha,private(self.runtime.root/'source.json')) and p['source_public_key']==self.runtime.source_public_key and p['grant_binding']==binding('action-grant:'+self.runtime.grant_sha,private(self.runtime.root/'grant.json')),'Action policy exact independent sources differ')
  require(p['contract_profile_binding']==self.selected_profile_binding,'nonce-bound selected integration profile differs')
  G._verify_files(ROOT,[{'path':self.selected_profile_binding['ref'],'sha256':self.selected_profile_binding['sha256']}])
  grant=self.runtime.grant();require(p['principal_ref']==grant.principal_ref and p['scope_ref']==grant.scope_ref,'Action policy recognized principal or scope differs')
  require(1<=p['max_calls']<=256 and 4096<=p['max_request_bytes']<=65536 and 32768<=p['max_response_bytes']<=1048576,'Action policy budgets invalid')
  self.policy=p;return copy.deepcopy(p)
 def authenticate(self,raw):
  require(not self.used and not self.closed and self.context is None,'Action nonce already consumed')
  self.used=True;p=self.policy_guard();proof=P.frame_parse(raw)
  require(set(proof)=={'schema_version','challenge','signature'} and proof['schema_version']=='lab-local-action-proof/v1-candidate' and proof['challenge']==self.challenge,'proof is not for this exact Action host/connection/nonce')
  Ed25519PublicKey.from_public_bytes(base64.b64decode(p['public_key'],validate=True)).verify(base64.b64decode(proof['signature'],validate=True),P.compact(self.challenge))
  src=self.runtime.source();refs=src['refs'];role=self.runtime.resolve(refs['role-assignment'])
  self.context={'schema_version':'lab-trusted-call-context/v1-candidate','context_ref':'context:R03-action:'+uuid.uuid4().hex,'host_instance_ref':self.host,'connection_ref':self.connection,'principal_ref':p['principal_ref'],'role_assignment_bindings':[binding(role.version_ref,role.original)],'authority_scope':'delegated-action','scope_refs':[p['scope_ref']],'source_profile_binding':binding('action-profile:'+refs['agent-profile'],self.runtime.resolve(refs['agent-profile']).original),'authentication_evidence_binding':binding('authentication:'+self.connection,raw),'policy_bindings':[binding('action-channel-policy:'+self.connection,private(self.path)),p['grant_binding']],'agent_instance_ref':refs['agent-instance'],'session_ref':refs['agent-session'],'assignment_ref':refs['agent-assignment'],'expires_at':p['expires_at'],'limits':{'max_request_bytes':p['max_request_bytes'],'max_response_bytes':p['max_response_bytes'],'max_actions':self.runtime.grant().max_actions,'deadline':p['expires_at']},'origin':'verified-local-adapter','accept_client_supplied_authority_context':False,'private_credentials_in_context':False}
  require(self.schemas.valid('trusted-call-context',self.context),'actual Action trusted context contract differs')
  self.runtime.channel=self
  return {'schema_version':'lab-local-action-authenticated/v1-candidate','context':copy.deepcopy(self.context),'trusted_context_binding':binding(self.context['context_ref'],P.compact(self.context)),'authority_effect':'none'}
 def guard(self,*,check_runtime=True):
  require(self.context is not None and not self.closed,'Action channel unauthenticated or closed');self.policy_guard()
  require(not self.runtime.session.closed and time.time()<self.runtime.session.expires,'actual Action runtime lease ended')
  if check_runtime:self.runtime.source();self.runtime.grant();self.runtime.status()
  return copy.deepcopy(self.context)
 def close(self):
  self.context=None;self.closed=True;self.used=True;self.challenge=None;self.runtime.close()
