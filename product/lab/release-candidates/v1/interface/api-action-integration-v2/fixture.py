"""Host-only isolated actor provisioning. All credentials are fresh and temporary."""
import base64,copy,os,time,uuid
from pathlib import Path
from dataclasses import asdict
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
from .runtime import *
KINDS=('principal','role','role-assignment','agent-assignment','delegation','tool','agent-instance','agent-session','agent-profile')
def put(path,raw):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
def public(key):return base64.b64encode(key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)).decode()

class OwnedActor:
 def __init__(self,root,schemas,*,approval_required=False,recovery_allowed=True,integration_profile_binding=None):
  self.root=Path(root);self.root.mkdir(mode=0o700)
  self.session=SessionLease(ttl=900);started=time.time();expires=self.session.expires
  self.scope='scope:R03-action-0148:'+self.root.name;self.key=Ed25519PrivateKey.generate();signer=Ed25519PrivateKey.generate()
  records={};refs={};token=uuid.uuid4().hex
  for kind in KINDS:
   d=parse((ROOT/f'authority/artifact-types/{kind}/v1/fixtures/valid/record.json').read_bytes())
   d.update(node_id=kind+':R03-action-0148:'+token,scope_ref=self.scope,owner_ref='principal:R03-action-0148:'+token,claim_ceiling=CEILING,successor_refs=[])
   if 'name' in d:d['name']='Owned isolated Action '+kind
   if 'relation_refs' in d:
    relation=copy.deepcopy(d['relation_refs'][0]);relation['counterpart_ref']='protocol:action-0148:'+relation['counterpart_kind'];d['relation_refs']=[relation]
   if 'evidence_refs' in d:d['evidence_refs']=['action-source:development-authorization']
   records[kind]=d;refs[kind]=d['node_id']+'@isolated-action.1'
  p=records['principal'];p['payload'].update(principal_kind='service',stable_subject_ref='person-reference:owned-action-operator:'+token,recognition_boundary_refs=[self.scope],registry_ref='registry:owned-action:'+token)
  role=records['role'];role.update(name='Owned local counter Action operator',purpose='Evaluate, dispatch and observationally reconcile one owned local counter',functions=['Evaluate fresh delegated Action permission','Execute bounded local counter','Observe selected pending Action'],responsibility_refs=['responsibility:owned-action-accountability'],authority_boundary=CEILING)
  records['role-assignment'].update(assignee_ref=p['payload']['stable_subject_ref'],role_ref=role['node_id'],period={'start':datetime.fromtimestamp(started-10,timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),'end':None},assignment_basis_ref='action-source:development-authorization',authority_claim_refs=['action-grant:independent-host-permission'],responsibility_refs=role['responsibility_refs'])
  assignment=records['agent-assignment']['payload'];assignment.update(eligible_agent_ref=records['agent-instance']['node_id'],owner_ref=p['node_id'],project_ref=self.scope,period='period:action-0148',work_ref='work:owned-counter-qualification:'+token,intent_ref='intent:owned-action-qualification',expected_output_refs=['agent-action:owned-counter-observation'],stop_conditions=['action-authority-ended','owned-counter-budget-reached'])
  records['delegation']['payload'].update(eligible_agent_ref=records['agent-instance']['node_id'],delegator_principal_ref=p['node_id'],scope_refs=[self.scope],allowed_action_kinds=['increment-local-counter'],approval_gate_refs=[],policy_refs=['policy:action-0148-owned-local'],effective_period='period:action-0148')
  if approval_required:records['delegation']['payload']['approval_gate_refs']=['gate:owned-action-development-approval']
  records['agent-instance']['payload'].update(accountable_principal_ref=p['node_id'],profile_ref=refs['agent-profile'],session_ref=records['agent-session']['node_id'],started_at=iso(self.session.started),implementation_ref='implementation:R03-action-0148',capability_refs=['agent-capability:bounded-local-counter'])
  records['agent-session']['payload'].update(agent_instance_ref=records['agent-instance']['node_id'],assignment_ref=refs['agent-assignment'],authority_envelope_ref=refs['delegation'],policy_refs=['policy:action-0148-owned-local'],context_view_ref='context-view:owned-action-source',ontology_view_ref='ontology-view:owned-action-source',event_cursor='cursor:action-source:0',input_refs=['input:owned-action-counter'],budget_refs=['budget:owned-action-counter'],session_memory={'expires_with_session':True,'selected_input_refs':['input:owned-action-counter'],'unresolved_questions':['actual-human-R08-outcome'],'working_record_refs':[]})
  records['agent-profile']['payload'].update(profile_purpose='Bounded isolated owned counter Action qualification',allowed_input_kinds=['action-request'],allowed_output_kinds=['agent-action'],tool_class_refs=['tool-class:bounded-local-counter'],policy_refs=['policy:action-0148-owned-local'],stop_conditions=['action-authority-ended','owned-counter-budget-reached'])
  records['tool']['payload'].update(tool_name='bounded-local-counter',interface_version='bounded-local-counter/v1-candidate',input_contract_ref='protocol:w02-counter-input:'+byte_sha(encoded(INPUT_CONTRACT)),output_contract_ref='protocol:w02-counter-output:'+byte_sha(encoded(OUTPUT_CONTRACT)),failure_boundary_refs=['protocol:w02-counter-indeterminate-recovery/v1'],evidence_route_ref='protocol:w02-host-operational-ledger')
  for kind,relation_kind,target,direction in [('principal','relation.acts-for','agent-instance','target'),('agent-instance','relation.profiled-by','agent-profile','source'),('agent-profile','relation.profiled-by','agent-instance','target'),('agent-session','relation.member-of','agent-instance','source'),('tool','relation.uses-tool','agent-session','target')]:
   records[kind]['relation_refs']=[{'relation_kind_ref':relation_kind,'direction':direction,'counterpart_kind':target,'counterpart_ref':records[target]['node_id']}]
  records['agent-assignment']['relation_refs'][0]['counterpart_ref']=assignment['intent_ref']
  selected={}
  for kind,d in records.items():
   from jsonschema import Draft202012Validator
   errors=list(Draft202012Validator(parse((ROOT/f'authority/artifact-types/{kind}/v1/schema.json').read_bytes())).iter_errors(d))
   require(not errors,kind+': '+str(errors[0]) if errors else kind)
   raw=encoded(d);SelectedRecord(refs[kind],raw,byte_sha(raw),'isolated-candidate-current','owned-action-source').record(kind)
   selected[refs[kind]]={'original_b64':base64.b64encode(raw).decode(),'sha256':byte_sha(raw)}
  head=byte_sha(encoded(selected))
  status={'head':head,'stopped':False,'revoked_refs':[],'periods':{'period:action-0148':[started-10,expires]},'reached_stop_conditions':[],'active_policy_refs':['policy:action-0148-owned-local'],'gates':{},'role_versions':{role['node_id']:refs['role']},'runtime_handle_bindings':{refs['agent-instance']:self.session.instance_ref,refs['agent-session']:self.session.session_ref},'tool_classes':{refs['tool']:'tool-class:bounded-local-counter'},'selected_work_ref':assignment['work_ref']}
  src={'schema_version':'lab-action-owned-source/v1-candidate','authority_effect':'none','actual_owner_outcome':None,'scope_ref':self.scope,'records':selected,'refs':refs,'runtime_bindings':{'instance':self.session.instance_ref,'session':self.session.session_ref},'initial_status':status}
  raw=encoded(src);put(self.root/'source.json',raw);put(self.root/'source.signature',base64.b64encode(signer.sign(raw)));put(self.root/'status.json',encoded(status))
  self.source_sha=byte_sha(raw);self.source_public_key=public(signer)
  authorization=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
  grant={'schema_version':'lab-action-private-grant/v1-candidate','source_sha256':self.source_sha,'principal_ref':refs['principal'],'scope_ref':self.scope,'action_kinds':['increment-local-counter'],'tool_ref':refs['tool'],'role_assignment_ref':refs['role-assignment'],'not_before':started-10,'expires_at':expires,'max_actions':8,'max_input_bytes':4096,'max_output_bytes':4096,'recovery_allowed':True,'allowed_operations':list(OPERATIONS),'authorization_binding':binding(str(authorization.relative_to(ROOT)),authorization.read_bytes())}
  grant['recovery_allowed']=recovery_allowed
  grant['inspection_operations']=['operation.inspect']
  grant['adapter_sha256']=byte_sha((W02/'tools/counter.py').read_bytes())
  grant['environment_sha256']=byte_sha(encoded({'python':__import__('sys').version,'network':False,'filesystem':str(self.root/'ledger')}))
  raw=encoded(grant);put(self.root/'grant.json',raw);self.grant_sha=byte_sha(raw)
  expected=initialize(self.root/'ledger');put(self.root/'ledger-pins.json',encoded(asdict(expected)))
  (self.root/'materials').mkdir(mode=0o700);(self.root/'operations').mkdir(mode=0o700)
  (self.root/'calls').mkdir(mode=0o700)
  self.runtime=ActionRuntime(self.root,self.session,self.source_sha,self.source_public_key,self.grant_sha)
  self.policy={'schema_version':'lab-local-action-policy/v1-candidate','host_uid':os.getuid(),'public_key':public(self.key),'principal_ref':refs['principal'],'scope_ref':self.scope,'expires_at':iso(expires),'allowed_operations':list(OPERATIONS),'source_binding':binding('action-source:'+self.source_sha,private(self.root/'source.json')),'source_public_key':self.source_public_key,'grant_binding':binding('action-grant:'+self.grant_sha,private(self.root/'grant.json')),'authority_effect':'none','actual_owner_outcome':None,'revoked':False,'max_calls':128,'max_request_bytes':65536,'max_response_bytes':1048576}
  self.policy['contract_profile_binding']=copy.deepcopy(integration_profile_binding or binding(str((HERE/'contract-profile.json').relative_to(ROOT)),(HERE/'contract-profile.json').read_bytes()))
  self.policy['inspection_operations']=['operation.inspect']
  raw=encoded(self.policy);put(self.root/'channel-policy.json',raw);self.policy_sha=byte_sha(raw)
  self.channel=ActionChannel(self.root/'channel-policy.json',self.policy_sha,self.runtime,schemas,integration_profile_binding=integration_profile_binding)
  self.channel.authenticate(P.compact({'schema_version':'lab-local-action-proof/v1-candidate','challenge':self.channel.challenge,'signature':base64.b64encode(self.key.sign(P.compact(self.channel.challenge))).decode()}))
  self.actor={k:self.channel.context[k] for k in ('principal_ref','agent_instance_ref','session_ref','assignment_ref')};self.actor['role_assignment_refs']=copy.deepcopy(self.channel.context['role_assignment_bindings'])
  self.refs=refs;self.records=records
  self.cut={'store_ref':'store:owned-action:'+self.root.name,'branch_ref':'branch:isolated-action-0148','commit_sequence':0,'commit_sha256':head,'source_profile_sha256':selected[refs['agent-profile']]['sha256'],'streams':[]}
  self.deadline=iso(expires-5)
 def material(self,raw):
  digest=byte_sha(raw);path=self.root/'materials'/digest
  if not path.exists():put(path,raw)
  return content('action-content:'+digest,raw)
 def request(self,*,key='counter-1',increment=1):
  ref=self.refs['agent-assignment'];raw=encoded(self.records['agent-assignment'])
  return {'schema_version':'lab-action-request/v1-candidate','request_ref':'request:action:'+key,'actor':copy.deepcopy(self.actor),'assignment':{'scope_ref':self.scope,'identity_ref':self.records['agent-assignment']['node_id'],'version_ref':ref,'carrier_ref':'cal.artifact-type.agent-assignment/v1','byte_sha256':byte_sha(raw)},'action_kind':'increment-local-counter','tool_adapter_binding':binding(str((W02/'tools/counter.py').relative_to(ROOT)),(W02/'tools/counter.py').read_bytes()),'input_bindings':[self.material(encoded({'increment':increment}))],'source_cut':copy.deepcopy(self.cut),'authority_envelope_binding':binding(self.refs['delegation'],encoded(self.records['delegation'])),'idempotency_key':key,'expected_output_contracts':[binding('protocol:w02-counter-output:'+byte_sha(encoded(OUTPUT_CONTRACT)),encoded(OUTPUT_CONTRACT))],'bounds':{'filesystem_scope_refs':[self.scope],'network_scope_refs':[],'allowed_action_kinds':['increment-local-counter'],'stop_conditions':['action-authority-ended','owned-counter-budget-reached'],'budget':{'max_actions':8,'max_input_bytes':4096,'max_output_bytes':4096,'deadline':self.deadline}},'authority_effect':'none'}
 def recovery(self,receipt,key='recovery-1'):
  envelope=binding(self.refs['delegation'],encoded(self.records['delegation']))
  return {'schema_version':'lab-recovery-request/v1-candidate','request_ref':'request:recovery:'+key,'actor':copy.deepcopy(self.actor),'expected_cut':copy.deepcopy(self.cut),'subject_binding':binding(receipt['receipt_ref'],P.compact(receipt)),'recovery_kind':'action-reconciliation','recovery_contract_binding':binding(str((W02/'authority/dispatch.py').relative_to(ROOT)),(W02/'authority/dispatch.py').read_bytes()),'authority_basis':{'authority_scope':'delegated-action','owner_principal_ref':self.actor['principal_ref'],'evidence_bindings':[envelope],'policy_bindings':[self.policy['grant_binding']],'scope_refs':[self.scope],'expires_at':self.deadline},'allowed_residue_bindings':copy.deepcopy(receipt['residue_bindings']),'authority_effect':'none'}
 def close(self):self.channel.close();self.key=None
