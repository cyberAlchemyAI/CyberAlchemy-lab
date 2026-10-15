"""Exact untrusted external caller; frozen API12, real independent private grants."""
import argparse,base64,copy,fcntl,hashlib,importlib,importlib.util,json,os,shutil,sys,tempfile,traceback,uuid
from contextlib import contextmanager,ExitStack
from datetime import datetime,timezone,timedelta
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
sys.dont_write_bytecode=True;os.environ['PYTHONDONTWRITEBYTECODE']='1'
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction';BASE=ROOT/'product/lab/release-candidates/v1/interface';API=BASE/'api-integration-v12';RETAINED=RUN/'qualify-API12-common-all34-0205.py'
def bind(p):return {'path':str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def require(v,message):
 if not v:raise ValueError(message)
def install(name,path):
 spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)]);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return name
def module(name,suffix):return importlib.import_module(name+'.'+suffix)
def snapshot(root):return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file() and not p.relative_to(root).as_posix().startswith('calls/')}
def event(value):
 with EVENTS.open('a') as stream:stream.write(json.dumps({'at':datetime.now(timezone.utc).isoformat(),**value},sort_keys=True)+'\n');stream.flush();os.fsync(stream.fileno())
def track(root):
 p=Path(root);require(p.is_relative_to(Path('/tmp')) and not p.is_relative_to(ROOT),'explicit owned private fixture required');ROOTS.add(p)
def common(host,**branches):return I.IntegrationService(host,**branches)
def positive_semantics(surface,request,reply):
 if reply.get('kind')!='result':return False
 op=request['operation'];message=reply['message'];postures={'action.evaluate':'permitted','action.dispatch':'completed','action.reconcile':'recovered','admission.apply':'committed','session.open':'active','installation.execute':'installed','release.prepare':'blocked','workflow.transition':'applied','ontology.project':'applied'}
 if op in postures and message.get('posture')!=postures[op]:return False
 if message.get('authority_effect')!='none':return False
 if op=='checkpoint.resolve' and message.get('result')!='pass':return False
 if op=='session.close' and message.get('discarded_memory') is not True:return False
 if op=='lab.status' and message.get('supported_operations')!=list(P.SUPPORTED):return False
 if op=='artifact.inspect':
  header=request['message']['artifact'];subject=surface.base.handlers.view.subjects[header['version_ref']];raw=M.record_bytes(surface.base.handlers.view,subject)[0]
  if message['envelope']['artifact']!=header or message['envelope']['content']['byte_sha256']!=P.source.sha(raw) or message['envelope']['decoded_artifact']['body']!=subject['record']:return False
 if op=='action.dispatch' and json.loads((surface.actions.runtime.root/'ledger/counter.json').read_bytes())['value']!=3:return False
 if op=='admission.apply' and surface.governance.host.snapshot()['head']['sequence']!=1:return False
 if op=='release.prepare' and not {'AC01','AC12','AC13','human-pilot','api-qualification','review-closure'}<={x['subject_ref'] for x in message['gaps']}:return False
 return True
def invoke(surface,request,label,expect,expected_code=None,root=None):
 for selected in PLAN['provider_bindings']:require(bind(ROOT/selected['path'])==selected,'exact independently selected provider changed at actual call boundary')
 raw=P.compact(request);operation=request['operation'];row=schemas.operations[operation];W.privacy(request)
 req_valid=schemas.valid('api-call',request);inner_valid=schemas.protocol_valid(row['request_schema']['resource_uri'],request['message'])
 require(req_valid and inner_valid,'case must reach an actual schema-valid request boundary')
 before=snapshot(root) if root is not None else None;started=datetime.now(timezone.utc).isoformat();reply=surface.call(raw);ended=datetime.now(timezone.utc).isoformat();W.privacy(reply)
 wire=schemas.valid('api-reply',reply) if 'kind' in reply else schemas.valid('transport-error',reply)
 actual_binding=reply.get('request_binding',{}).get('sha256',reply.get('request_byte_sha256'));bound=actual_binding==P.source.sha(raw)
 uri=row['result_schema' if reply.get('kind')=='result' else 'error_schema']['resource_uri']
 if operation=='artifact.inspect' and reply.get('kind')=='result':uri='urn:cyberalchemy-lab:protocol:artifact-inspect-result:v2-candidate'
 selected_uri=schemas.uri_mapping.get(uri,uri);domain='kind' in reply and schemas.protocol_valid(uri,reply['message']);profile='kind' in reply and reply['contract_profile_binding']==schemas.profile_binding
 code=reply.get('message',{}).get('code',reply.get('code'));allowed=reply.get('kind')!='error' or code in row['allowed_error_codes'];no_effect=before is None or snapshot(root)==before
 semantic=positive_semantics(surface,request,reply) if expect=='result' else None
 good=wire and bound and domain and profile and allowed and reply.get('kind')==expect and (expected_code is None or code==expected_code) and (expect!='error' or no_effect) and (expect!='result' or semantic)
 record={'operation':operation,'case':label,'result':'PASS' if good else 'FAIL','started_at':started,'ended_at':ended,'raw_request_base64':base64.b64encode(raw).decode(),'request_byte_sha256':P.source.sha(raw),'original_request':request,'actual_reply':reply,'expected_kind':expect,'expected_code':expected_code,'actual_code':code,'api_request_schema_valid':req_valid,'inner_request_schema_valid':inner_valid,'api_reply_or_transport_schema_valid':wire,'actual_domain_schema_valid':domain,'actual_profile_binding_matches':profile,'actual_request_byte_binding_matches':bound,'declared_error_code_matches':allowed,'positive_semantic_and_owned_effect_checks_passed':semantic,'selected_request_schema_uri':schemas.uri_mapping.get(row['request_schema']['resource_uri'],row['request_schema']['resource_uri']),'selected_actual_reply_schema_uri':selected_uri,'original_catalog_operation_contract':row,'negative_owned_effect_state_unchanged':no_effect if expect=='error' else None,'same_frozen_API12_common_dispatcher':True,'private_key_or_policy_exported':False}
 CASES.append(record);event({'phase':'case-completed',**record});print(operation,label,record['result'],code,flush=True);return reply
def pair(host,request,root=None,surface=None):
 surface=common(host) if surface is None else surface;negative=copy.deepcopy(request);negative['call_id']='call:all34:negative:'+uuid.uuid4().hex
 actor=negative['message'].get('actor')
 if isinstance(actor,dict):actor['principal_ref']='principal:all34-foreign';code='unauthorized';cause='foreign-public-Actor-does-not-replace-independent-principal'
 elif request['operation']=='session.close':negative['message']['agent_instance_ref']='agent-instance:all34-foreign';code='unauthorized';cause='foreign-Agent-does-not-replace-owned-live-Session'
 else:negative['deadline']=(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat();code='deadline-exceeded';cause='actual-expired-outer-deadline-before-effect'
 invoke(surface,negative,cause,'error',code,root);return invoke(surface,request,'actual-positive-domain-result','result',root=root)
@contextmanager
def base_fixture(view):
 with tempfile.TemporaryDirectory(prefix='cal-all34-base-0205-') as temporary:
  root=Path(temporary);root.chmod(0o700);track(root);materials,metadata,target=EF.materials_for(view);key,path,pin=F.provision(root,'custody-participation',materials,metadata,principal=P.source.custody_delivery().records.PRINCIPAL,projection_control=PR.control(view));channel=A.ReaderChannel(path,pin,schemas);channel.authenticate(F.proof(key,channel.challenge));key=None;host=S.Service(view,channel,schemas)
  try:yield host,target,root
  finally:host.close();channel.close()
def op_call(host,operation,message,key=None,cut=None):
 value=F.call(host.channel.context,'lab.status',H.cut(host.handlers.view) if cut is None else cut);value.update(operation=operation,message=copy.deepcopy(message),idempotency_key=key);return value
def base_episode():
 with P.source.replay_source('custody-participation') as view:
  for operation in ('lab.status','catalog.get','artifact.inspect','artifact.query','change.prepare','change.validate','projection.refresh','operation.inspect'):
   with base_fixture(view) as (host,target,root):
    if operation in ('change.prepare','change.validate'):request=EF.candidate_call(host,target,operation,key='all34:'+operation)
    elif operation=='artifact.inspect':subject=next(x for x in view.subjects.values() if x['identity']=='product:cyberalchemy-lab');request=F.call(host.channel.context,operation,H.cut(view),artifact=M.artifact_ref(view,subject),include=['body','contract','authority','provenance','gaps'])
    elif operation=='projection.refresh':
     seed=F.call(host.channel.context,'lab.status',H.cut(view));budget=seed['message']['budget'];budget['max_actions']=1;grant=host.channel.policy['projection_control'];message={'schema_version':'lab-projection-refresh-request/v1-candidate','request_ref':'request:all34-refresh','source_cut':H.cut(view),'projector_binding':grant['projector_binding'],'contract_catalog_binding':grant['contract_catalog_binding'],'expected_generation_binding':None,'budget':budget,'authority_effect':'none'};request=op_call(host,operation,message,'all34:refresh')
    elif operation=='operation.inspect':
     prepared=invoke(common(host),EF.candidate_call(host,target,key='all34:inspection-dependency'),'actual-owned-inspection-prerequisite','result');request=F.call(host.channel.context,operation,None,lookup={'operation':'change.prepare','idempotency_key':'all34:inspection-dependency'})
    else:request=F.call(host.channel.context,operation,H.cut(view))
    pair(host,request,root)
  with base_fixture(view) as (host,target,root):
   d=P.source.custody_delivery();context=d.query(view.custody_signed_sources,host.sessions.bridge);context['budget'].update(max_input_bytes=65536,max_output_bytes=1048576);delivery=pair(host,op_call(host,'context.get',context),root)
   selected=view.custody_signed_sources;R=d.records;ref=lambda identity:copy.deepcopy(selected.sources.resolve(identity+'@'+R.VERSION)[0].artifact);seed=F.call(host.channel.context,'lab.status',H.cut(view));budget=seed['message']['budget'];budget['max_actions']=1
   opening={'schema_version':'lab-agent-session-open/v1-candidate','request_ref':'request:all34-open','actor':seed['message']['actor'],'assignment':ref(R.ASSIGNMENT),'profile':ref(R.PROFILE),'implementation':ref(R.IMPLEMENTATION),'capabilities':[ref(R.CAPABILITY)],'context_delivery_binding':P.binding('context-delivery:'+delivery['message']['context_view']['version_ref'],P.compact(delivery['message'])),'authority_envelope_binding':CS.stable_policy(host.channel),'source_cut':H.cut(view),'budget':budget,'memory_policy':{'persistence_allowed':False,'expires_with_session':True},'authority_effect':'none'}
   opened=pair(host,op_call(host,'session.open',opening,'all34:session-open'),root)
   inspection={'schema_version':'lab-session-inspect-request/v1-candidate','request_ref':'request:all34-inspect','actor':seed['message']['actor'],'session_ref':opened['message']['session_ref'],'budget':budget,'authority_effect':'none'}
   inspected=pair(host,op_call(host,'session.inspect',inspection),root)
   closing={'schema_version':'lab-agent-session-close/v1-candidate','request_ref':'request:all34-close','session_ref':opened['message']['session_ref'],'agent_instance_ref':opened['message']['agent_instance_ref'],'expected_session_binding':inspected['message']['last_receipt_binding'],'requested_at':A.now().isoformat(),'reason':'completed','eligible_audit_bindings':[],'authority_effect':'none'};pair(host,op_call(host,'session.close',closing,'all34:session-close'),root)
def fixtures_episode():
 with P.source.replay_source('custody-participation') as view:
  for operation,stem in [('classification.prepare','classification_fixture'),('failure.assess','failure_fixture'),('challenge.submit','challenge_fixture'),('proposal.review','review_fixture'),('package.export','package_export_fixture'),('installation.execute','installation_release_fixture'),('release.prepare','installation_release_fixture')]:
   provider=module(NAME,stem)
   try:
    with provider.example(view,schemas,**({'release':True} if operation=='release.prepare' else {})) as values:
     host,request,witness=values;track(witness['root'] if 'root' in witness else host.vault.root.parent);request=request() if callable(request) else request;pair(host,request,host.vault.root)
   except Exception:FAILURES.append({'episode':'provider:'+operation,'detail':traceback.format_exc()});event({'phase':'provider-failed','operation':operation,'detail':FAILURES[-1]['detail']})
  export=module(NAME,'export_fixture')
  with tempfile.TemporaryDirectory(prefix='cal-all34-files-0205-') as temporary:
   root=Path(temporary);root.chmod(0o700);track(root);selected=export.selection(view);key,path,pin=export.provision(root,selected);channel=A.ReaderChannel(path,pin,schemas);channel.authenticate(F.proof(key,channel.challenge));key=None;host=S.Service(view,channel,schemas)
   try:pair(host,export.call(host,selected),host.vault.root)
   finally:host.close();channel.close()
  package=module(NAME,'package_fixture')
  with tempfile.TemporaryDirectory(prefix='cal-all34-import-0205-') as temporary:
   root=Path(temporary);root.chmod(0o700);track(root);key,path,pin,message,proposal,plan,archive=package.provision(root,view);channel=A.ReaderChannel(path,pin,schemas);channel.authenticate(F.proof(key,channel.challenge));key=None;host=S.Service(view,channel,schemas)
   try:pair(host,op_call(host,'package.import',message,package.KEY),host.vault.root)
   finally:host.close();channel.close()
  typedname=install('_cal_all34_typed_fixture',BASE/'api50-typed-checks-v1');typed=module(typedname,'fixture')
  with typed.example(API,view,schemas) as (host,request,witness):track(witness['root']);pair(host,request,host.vault.root)
def action_governance_episode():
 members=json.loads((API/'integration-members.json').read_bytes())['members'];an=install('_cal_all34_actions',BASE/members['actions']['directory']);gn=install('_cal_all34_governance',BASE/members['governance']['directory']);AF=module(an,'fixture');AS=module(an,'service');GF=module(gn,'fixture');GS=module(gn,'service')
 class SharedGovernance(GF.Fixture):
  def open(self):
   self.host=GF.GovernanceHost(self.root,self.policy_pin,self.schemas,members['governance']['source_sha256'],members['governance']['profile_sha256'],integration_profile_binding=self.schemas.profile_binding);self.channel=GF.GovernanceChannel(self.host);self.channel.authenticate({'challenge':self.channel.challenge,'signature_base64':base64.b64encode(self.reader.sign(GF.encoded(self.channel.challenge))).decode()});self.service=GS.GovernanceService(self.host,self.channel)
 with P.source.replay_source('custody-participation') as view,base_fixture(view) as (host,target,base_root),tempfile.TemporaryDirectory(prefix='cal-all34-branches-0205-') as temporary:
  owned=Path(temporary);owned.chmod(0o700);track(owned);action=AF.OwnedActor(owned/'actions',schemas,integration_profile_binding=schemas.profile_binding);gr=owned/'governance';gr.mkdir(mode=0o700);gov=SharedGovernance(gr,schemas);actions=AS.ActionService(action.runtime,action.channel,schemas,source_sha256=members['actions']['source_sha256'],profile_sha256=members['actions']['profile_sha256'],integration_profile_binding=schemas.profile_binding)
  try:
   surface=common(host,action_service=actions,governance_service=gov.service)
   def action_call(operation,message,key=None):return {'schema_version':'lab-api-call/v2-candidate','call_id':'call:all34-action:'+uuid.uuid4().hex,'operation':operation,'caller_context_ref':action.channel.context['context_ref'],'expected_source_cut':copy.deepcopy(action.cut),'deadline':action.deadline,'max_response_bytes':1048576,'idempotency_key':key,'message':copy.deepcopy(message),'expected_contract_profile_binding':schemas.profile_binding}
   request=action.request(increment=3);pair(actions,action_call('action.evaluate',request),action.root,surface);dispatched=pair(actions,action_call('action.dispatch',request,request['idempotency_key']),action.root,surface);recovery=action.recovery(dispatched['message'],key='all34:reconcile');pair(actions,action_call('action.reconcile',recovery,'all34:reconcile'),action.root,surface)
   checkpoint=pair(gov.service,gov.checkpoint_call('all34:checkpoint'),gr,surface);pair(gov.service,gov.capability_call('all34:capability'),gr,surface);pair(gov.service,gov.admission_call(checkpoint['message']['subject_binding'],'all34:admission'),gr,surface)
  finally:gov.service.close();gov.channel.close();action.close()
def resolution_episode():
 package=BASE/'current-participation-v8/packages/0001';plan=json.loads((package/'resolution-qualification-plan.json').read_bytes());period=json.loads((package/'period.json').read_bytes())
 with P.source.replay_source('integrated-participation') as view,tempfile.TemporaryDirectory(prefix='cal-all34-resolution-0205-') as temporary:
  owned=Path(temporary);owned.chmod(0o700);track(owned);workspace=owned/'workspace';workspace.mkdir(mode=0o700)
  for directory in ('inputs','objects','journal'):(workspace/directory).mkdir(mode=0o700)
  for original in (package/'qualification-workspace').rglob('*'):
   if original.is_file():target=workspace/original.relative_to(package/'qualification-workspace');target.write_bytes(original.read_bytes());target.chmod(0o600)
  key=Ed25519PrivateKey.generate();policy={'schema_version':'lab-local-integrated-challenge-resolution-policy/v3-candidate','principal_ref':plan['principal_ref'],'reader_public_key':base64.b64encode(key.public_key().public_bytes_raw()).decode(),'host_uid':os.getuid(),'source_name':'integrated-participation','scope_refs':[view.data['config']['scope_ref']],'expires_at':period['expires_at'],'max_request_bytes':1048576,'max_response_bytes':4194304,'max_calls':128,'allowed_operations':list(P.RESOLUTION_SUPPORTED),'revoked':False,'scope_posture':'isolated-candidate-preparation','purpose':'durable-metadata-and-exact-integrated-challenge-resolution','development_authorization_binding':P.binding(str((RUN/'authorization.json').relative_to(ROOT)),(RUN/'authorization.json').read_bytes()),'scope_control':None,'session_control':None,'projection_control':None,'workspace':{'root':str(workspace),'manifest_sha256':P.source.sha((workspace/'workspace.json').read_bytes()),'max_actions':64},'resolution_control':{'routing_binding':plan['routing_binding'],'method_binding':P.binding(str((BASE/'challenge-resolution-v6/preparation.py').relative_to(ROOT)),(BASE/'challenge-resolution-v6/preparation.py').read_bytes())},'resolution_reference_control':{'resolver_binding':P.binding(str((BASE/'challenge-resolution-v6/reference_roles.py').relative_to(ROOT)),(BASE/'challenge-resolution-v6/reference_roles.py').read_bytes()),'contract_binding':P.binding(str((BASE/'challenge-resolution-v6/reference-role-contract.json').relative_to(ROOT)),(BASE/'challenge-resolution-v6/reference-role-contract.json').read_bytes())},'integrated_source_control':P.source.integrated_bindings(),'authority_effect':'none','actual_owner_outcome':None};path=owned/'reader-policy.json';W.atomic(path,P.compact(policy));require(schemas.valid('reader-authentication',policy),'exact independent integrated policy invalid');channel=A.ReaderChannel(path,P.source.sha(path.read_bytes()),schemas);channel.authenticate(F.proof(key,channel.challenge));key=None;host=S.Service(view,channel,schemas)
  try:
   request=op_call(host,'challenge.resolve',plan['message'],plan['idempotency_key']);request.update(max_response_bytes=4194304,deadline=channel.context['expires_at']);pair(host,request,workspace)
  finally:host.close();channel.close()

def workflow_episode():
 component=install("_cal_all34_workflow_provider",BASE/"workflow-transition-v1");T=module(component,"fixtures");J=module(component,"journal")
 with P.source.replay_source('workflow-participation') as view,tempfile.TemporaryDirectory(prefix='cal-workflow-public-0146-') as temp:
     owned=Path(temp);owned.chmod(0o700);track(owned);workspace=owned/'workspace';workspace.mkdir(mode=0o700)
     for d in ('inputs','objects','journal','workflows'):(workspace/d).mkdir(mode=0o700)
     reader=P.source.workflow_reader();R=reader.records;cut=H.cut(view)
     message,facts=T.build();actor={'principal_ref':R.PRINCIPAL,'agent_instance_ref':None,'assignment_ref':None,'session_ref':None,'role_assignment_refs':[]}
     def selected(identity,kind):
         rows=[r for r in view.subjects.values() if r['identity']==identity and r['kind']==kind and r['effective_state'] in ('admitted-current','local-admitted-current')]
         assert len(rows)==1,(identity,kind)
         return M.artifact_ref(view,rows[0])
     with M.model_read_batch(view):
         headers={k:selected(identity,kind) for k,identity,kind in [
             ('intent',R.INTENT,'intent'),('work',R.WORK,'work'),('coordination_context',R.COORDINATION,'coordination-context'),
             ('intent_resolution','intent-resolution:R03-workflow-source-0011','intent-resolution'),
             ('decision_profile','workflow-decision-profile:lab-governance-single-checkpoint','workflow-decision-profile')]}
     definition=json.loads(facts['definition_raw']);run=json.loads(facts['run_raw'])
     definition['decision_profile']=headers['decision_profile']
     definition['transitions'][0]['actor_role_refs']=['role:owned-candidate-source-inspector']
     definition['transitions'][0]['relation_requirement_refs']=['obligation:exact-resolution-decision-edge']
     run.update(actor=actor,source_cut=cut,**{k:headers[k] for k in ('intent','intent_resolution','work','coordination_context')})
     grant=copy.deepcopy(facts['host_grant']);start=datetime.now(timezone.utc);end=start+timedelta(hours=1)
     grant.update(principal_ref=R.PRINCIPAL,scope_ref=view.data['config']['scope_ref'],source_cut=cut,
         actor_role_refs=['role:owned-candidate-source-inspector'],not_before=(start-timedelta(seconds=1)).isoformat(),expires_at=end.isoformat())
     materials={}
     def original(ref,value):
         raw=P.compact(value);materials[ref]=raw;return P.binding(ref,raw)
     # The grant core is independent input. Reports refer to its stable
     # bytes; the policy subsequently binds the complete selected grant.
     core=original('authority-core:owned-source-inspection',{'schema_version':'lab-isolated-operator-workflow-core/v1-candidate',
         'principal_ref':R.PRINCIPAL,'scope_ref':grant['scope_ref'],'source_cut':cut,'actor_role_refs':grant['actor_role_refs'],
         'permitted_effects':grant['permitted_effects'],'not_before':grant['not_before'],'expires_at':grant['expires_at'],
         'role_scope':'Explicit test-owned coordination permission only; no canonical governing role or human owner outcome.', 'authority_effect':'none'})
     observed=original('evidence:actual-workflow-source-inspection',{'schema_version':'lab-actual-workflow-source-inspection/v1-candidate',
         'source_cut':cut,'headers':headers,'signed_source_binding':P.source.workflow_bindings()['source_binding'],
         'signed_package_binding':P.source.workflow_bindings()['package_binding'],
         'actual_signed_transactions':view.data['head']['sequence'],'result':'PASS','authority_effect':'none',
         'claim_ceiling':'Actual cold/native original source and exact selected headers only; no human outcome or Work completion.'})
     t=definition['transitions'][0];obligations={r:[core] if r in t['authority_requirement_refs'] else [observed]
         for r in [*t['authority_requirement_refs'],*t['precondition_refs'],*t['satisfaction_check_refs'],*t['relation_requirement_refs']]}
     def check(ref):return {'check_ref':'check:'+ref,'obligation_ref':ref,'result':'pass','evidence_bindings':obligations[ref],
         'claim_ceiling':'Actual test-owned grant/source selection; semantic closure is rechecked by the public host before any effect.'}
     definition_b=original('workflow-definition:owned-source-inspection',definition);run['definition_binding']=definition_b
     run_b=original('workflow-run:owned-source-inspection:before',run)
     authority=json.loads(facts['authority_raw']);authority.update(source_cut=cut,evaluated_at=start.isoformat(),expires_at=end.isoformat(),
         authority_envelope_binding=core,checks=[check(r) for r in t['authority_requirement_refs']],evidence_bindings=[core])
     satisfaction=json.loads(facts['satisfaction_raw']);satisfaction.update(subject_binding=run_b,source_cut=cut,
         checks=[check(r) for r in [*t['precondition_refs'],*t['satisfaction_check_refs'],*t['relation_requirement_refs']]])
     authority_b=original('authority-evaluation:owned-source-inspection',authority)
     satisfaction_b=original('satisfaction:owned-source-inspection',satisfaction)
     message.update(actor=actor,source_cut=cut,run_binding=run_b,definition_binding=definition_b,input_artifacts=[headers['work']],
         authority_evaluation_binding=authority_b,satisfaction_report_binding=satisfaction_b)
     grant.update(run_binding=run_b,definition_binding=definition_b,authority_evaluation_binding=authority_b,
         satisfaction_report_binding=satisfaction_b,obligation_bindings=obligations)
     store=J.Journal.initialize(workspace/'workflows/source-inspection',materials[run_b['ref']],grant['scope_ref'],R.PRINCIPAL)
     grant_b=original('grant:owned-source-inspection',grant)
     routing_b=original('routing:owned-source-inspection',{'schema_version':'lab-owned-workflow-routing/v1-candidate',
         'grant_binding':grant_b,'journal_root':'workflows/source-inspection','journal_config_sha256':store.config_sha256})
     workspace_ref='R03-workflow-'+os.urandom(12).hex();rows=[]
     for index,(ref,raw) in enumerate(materials.items()):
         path='inputs/'+str(index)+'.json';W.atomic(workspace/path,raw);rows.append({'ref':ref,'path':path,'sha256':P.source.sha(raw)})
     manifest={'schema_version':'lab-owned-candidate-workspace/v1-candidate','workspace_ref':workspace_ref,'principal_ref':R.PRINCIPAL,
         'scope_refs':[grant['scope_ref']],'materials':rows,'target_metadata':{},'authority_effect':'none','actual_owner_outcome':None}
     manifest_raw=P.source.encoded(manifest);W.atomic(workspace/'workspace.json',manifest_raw)
     key=Ed25519PrivateKey.generate();component_path=BASE/'workflow-transition-v1'
     policy={'schema_version':'lab-local-workflow-transition-policy/v1-candidate','principal_ref':R.PRINCIPAL,
         'reader_public_key':base64.b64encode(key.public_key().public_bytes_raw()).decode(),'host_uid':os.getuid(),
         'source_name':'workflow-participation','scope_refs':[grant['scope_ref']],'expires_at':end.isoformat(),
         'max_request_bytes':1048576,'max_response_bytes':4194304,'max_calls':128,'allowed_operations':list(P.WORKFLOW_TRANSITION_SUPPORTED),
         'revoked':False,'scope_posture':'isolated-candidate-preparation','authority_effect':'none','actual_owner_outcome':None,
         'workspace':{'root':str(workspace),'manifest_sha256':P.source.sha(manifest_raw),'max_actions':8},'session_control':None,'projection_control':None,
         'purpose':'durable-metadata-and-exact-workflow-transition','development_authorization_binding':P.binding(str((RUN/'authorization.json').relative_to(ROOT)),(RUN/'authorization.json').read_bytes()),
         'scope_control':None,'workflow_source_control':P.source.workflow_bindings(),
         'workflow_control':{'routing_binding':routing_b,'kernel_binding':P.binding(str((component_path/'kernel.py').relative_to(ROOT)),(component_path/'kernel.py').read_bytes()),
             'journal_binding':P.binding(str((component_path/'journal.py').relative_to(ROOT)),(component_path/'journal.py').read_bytes())}}
     policy_path=owned/'reader-policy.json';raw=P.compact(policy);W.atomic(policy_path,raw)
     assert schemas.valid('reader-authentication',policy),'new private policy schema refused'
     channel=A.ReaderChannel(policy_path,P.source.sha(raw),schemas);context=channel.authenticate(F.proof(key,channel.challenge))['context'];key=None
     service=S.Service(view,channel,schemas)
     try:
      call=F.call(context,"lab.status",cut);call.update(operation="workflow.transition",idempotency_key=message["idempotency_key"],message=copy.deepcopy(message),max_response_bytes=4194304,deadline=end.isoformat());pair(service,call,workspace)
     finally:service.close();channel.close()
def ontology_episode():
 O=module(NAME,"ontology_projection")
 with P.source.replay_source('custody-participation') as view,tempfile.TemporaryDirectory(prefix='cal-ontology-public-0145-') as temp:
     owned=Path(temp);owned.chmod(0o700);track(owned);principal='principal:owned-ontology-operator:'+uuid.uuid4().hex
     key,policy_path,pin=F.provision(owned,'custody-participation',principal=principal,max_actions=8)
     workspace=owned/'workspace';native_root=workspace/'ontology';native_root.mkdir(mode=0o700)
     policy=P.frame_parse(policy_path.read_bytes());manifest=P.frame_parse((workspace/'workspace.json').read_bytes())
     materials={}
     def material(ref,value):
         raw=P.compact(value);materials[ref]=raw;return P.binding(ref,raw)
     current=datetime.now(timezone.utc);end=current+timedelta(hours=1)
     store='ontology-store:owned:'+uuid.uuid4().hex;branch='branch:'+store
     st=native_root.stat();identity={'device':st.st_dev,'inode':st.st_ino}
     genesis={'schema_version':'lab-owned-ontology-head/v1-candidate','sequence':0,'store_ref':store,'branch_ref':branch,
         'parent_head_sha256':None,'generation':None,'generation_sha256':None}
     W.atomic(native_root/'HEAD.json',P.compact(genesis))
     evidence=material('evidence:actual-owned-ontology-root',{'schema_version':'lab-owned-ontology-root-evidence/v1-candidate',
         'principal_ref':principal,'host_uid':os.getuid(),'root_identity':identity,'root_mode':oct(native_root.stat().st_mode&0o777),
         'scope':'New isolated candidate ontology only; no existing store, canonical owner outcome or Lab admission','authority_effect':'none'})
     grant=material('policy:owned-ontology-representation',{'schema_version':'lab-owned-ontology-representation-grant/v1-candidate',
         'principal_ref':principal,'store_ref':store,'effects':['ontology-representation'],'root_identity':identity,
         'not_before':(current-timedelta(seconds=1)).isoformat(),'expires_at':end.isoformat(),'authority_effect':'none','actual_owner_outcome':None})
     basis={'authority_scope':'operator-local','owner_principal_ref':principal,'evidence_bindings':[evidence],
         'policy_bindings':[grant],'scope_refs':[store],'expires_at':end.isoformat()}
     mapping=P.binding(str((O.MAPPER/'policy.json').relative_to(ROOT)),(O.MAPPER/'policy.json').read_bytes());cut=H.cut(view)
     route={'schema_version':'lab-owned-ontology-routing/v1-candidate','principal_ref':principal,'scope_ref':policy['scope_refs'][0],
         'store_ref':store,'branch_ref':branch,'root_identity':identity,'mapping_binding':mapping,
         'mapped_source_binding':{'ref':str((O.MAPPER/'source-manifest.json').relative_to(ROOT)),'sha256':O.MAPPER_PIN},
         'mapped_package_binding':{'ref':str((O.MAPPER/'packages/0001/manifest.json').relative_to(ROOT)),'sha256':O.PACKAGE_PIN},
         'expected_lab_cut':cut,'authorization_basis':basis,'not_before':(current-timedelta(seconds=1)).isoformat(),
         'expires_at':end.isoformat(),'permitted_effects':['ontology-representation']}
     routing=material('routing:owned-ontology',route)
     for i,(ref,raw) in enumerate(materials.items()):
         path='inputs/ontology-'+str(i)+'.json';W.atomic(workspace/path,raw);manifest['materials'].append({'ref':ref,'path':path,'sha256':P.source.sha(raw)})
     mraw=P.compact(manifest);(workspace/'workspace.json').write_bytes(mraw)
     policy.update(schema_version='lab-local-ontology-projection-policy/v1-candidate',session_control=None,
         purpose='durable-metadata-and-exact-ontology-projection',allowed_operations=list(P.ONTOLOGY_SUPPORTED),
         development_authorization_binding=P.binding(str((RUN/'authorization.json').relative_to(ROOT)),(RUN/'authorization.json').read_bytes()),
         scope_control=None,expires_at=end.isoformat(),max_request_bytes=1048576,
         ontology_control={'routing_binding':routing,'method_binding':P.binding(str((API/'ontology_projection.py').relative_to(ROOT)),(API/'ontology_projection.py').read_bytes())})
     policy['workspace']['manifest_sha256']=P.source.sha(mraw);praw=P.compact(policy);policy_path.write_bytes(praw)
     assert schemas.valid('reader-authentication',policy),'actual private ontology policy schema differs'
     channel=A.ReaderChannel(policy_path,P.source.sha(praw),schemas);context=channel.authenticate(F.proof(key,channel.challenge))['context'];key=None
     service=S.Service(view,channel,schemas)
     try:
      expected={'store_ref':store,'branch_ref':branch,'commit_sequence':0,'commit_sha256':P.source.sha(P.compact(genesis)),
          'source_profile_sha256':mapping['sha256'],'streams':[]}
      actor={k:context[k] for k in ('principal_ref','agent_instance_ref','assignment_ref','session_ref')};actor['role_assignment_refs']=context['role_assignment_bindings']
      message={'schema_version':'lab-ontology-project-request/v1-candidate','request_ref':'request:owned-ontology:'+uuid.uuid4().hex,
          'actor':actor,'lab_source_cut':cut,'ontology_expected_cut':expected,'mapping_binding':mapping,'subject_refs':[],
          'authorization_basis':basis,'idempotency_key':'ontology:'+uuid.uuid4().hex,'authority_effect':'none'}
      call=F.call(context,'lab.status',cut);call.update(operation='ontology.project',message=message,
          idempotency_key=message['idempotency_key'],deadline=end.isoformat(),max_response_bytes=1048576)
      pair(service,call,workspace)
     finally:service.close();channel.close()

def private_policy_branch(kind):
 tree=json.loads((API/'authentication.schema.json').read_bytes());found=[]
 def walk(value):
  if isinstance(value,dict):
   if value.get('properties',{}).get('schema_version',{}).get('const')==kind:found.append(value)
   for child in value.values():walk(child)
  elif isinstance(value,list):
   for child in value:walk(child)
 walk(tree);require(len(found)==1,'exact independently selected closed policy branch required');return found[0]
def lessons_episode():
 # Original negative/unavailable attempts only: never manufacture a current
 # Lesson, actual Application, live integrated Session or working host origin.
 for operation,kind in [('lesson.select','lab-local-lesson-read-policy/v1-candidate'),('lesson.apply','lab-local-lesson-application-policy/v2-candidate'),('lesson.assess','lab-local-lesson-assessment-policy/v1-candidate')]:
  try:
   with P.source.replay_source('custody-participation') as view,tempfile.TemporaryDirectory(prefix='cal-all34-'+operation.replace('.','-')+'-0205-') as temporary:
    root=Path(temporary);root.chmod(0o700);track(root);materials,metadata,target=EF.materials_for(view);witness={'schema_version':'lab-lesson-host-plan/v1-candidate' if operation=='lesson.select' else 'lab-opening-only-application-routing-witness/v1-candidate','source_cut':H.cut(view),'scope_ref':view.data['config']['scope_ref'],'application_runtime_qualified':False,'authority_effect':'none'};raw=P.compact(witness);materials['candidate:all34-unavailable-lesson-route']=raw;selected=P.binding('candidate:all34-unavailable-lesson-route',raw);key,path,pin=F.provision(root,'custody-participation',materials,metadata,principal=P.source.custody_delivery().records.PRINCIPAL);policy=P.frame_parse(path.read_bytes());branch=private_policy_branch(kind);policy['schema_version']=kind;policy['allowed_operations']=branch['properties']['allowed_operations']['const'];policy['development_authorization_binding']=P.binding(str((RUN/'authorization.json').relative_to(ROOT)),(RUN/'authorization.json').read_bytes())
    if operation=='lesson.select':policy['lesson_control']={'plan_binding':selected}
    else:
     policy['scope_control']=None;policy['max_request_bytes']=1048576;policy['purpose']=branch['properties']['purpose']['const'];control='application_control' if operation=='lesson.apply' else 'assessment_control';folder=BASE/('lesson-application-v2' if operation=='lesson.apply' else 'lesson-assessment-v1');digest=P.source.sha(raw);W.atomic(root/'workspace/objects'/(digest+'.json'),raw);manifest=P.frame_parse((root/'workspace/workspace.json').read_bytes());policy[control]={'routing_binding':{'ref':'workspace-object:'+manifest['workspace_ref']+':'+digest,'sha256':digest},'method_binding':P.binding(str((folder/'preparation.py').relative_to(ROOT)),(folder/'preparation.py').read_bytes())}
     if operation=='lesson.apply':policy[control]['runtime_identities']={'session_ref':'agent-session:R03-live:'+uuid.uuid4().hex,'agent_instance_ref':'agent-instance:R03-live:'+uuid.uuid4().hex}
     else:policy['session_control']=None
    require(schemas.valid('reader-authentication',policy),'actual unavailable policy must still match original closed authentication schema');W.atomic(path,P.compact(policy));channel=A.ReaderChannel(path,P.source.sha(path.read_bytes()),schemas);channel.authenticate(F.proof(key,channel.challenge));key=None;host=S.Service(view,channel,schemas)
    try:
     example=json.loads((ROOT/'docs/proposals/0008-lab-api-contracts/examples'/operation/'request.json').read_bytes());message=example['message'];message['actor']={k:channel.context[k] for k in ('principal_ref','agent_instance_ref','assignment_ref','session_ref')};message['actor']['role_assignment_refs']=[];message['source_cut']=H.cut(view);request=op_call(host,operation,message,'all34:'+operation);pair(host,request,host.vault.root)
    finally:host.close();channel.close()
  except Exception:
   failure={'episode':'unavailable-original-lesson-provider','operation':operation,'detail':traceback.format_exc(),'positive_path_qualified':False,'current_Lesson_or_Application_manufactured':False,'private_unavailable_fixture_witness_is_not_a_qualified_domain_route':True};FAILURES.append(failure);event({'phase':'original-provider-unavailable',**failure})
def main():
 global EVENTS,CASES,FAILURES,ROOTS,NAME,P,G,schemas,A,F,H,S,I,W,M,EF,PR,CS,PLAN
 parser=argparse.ArgumentParser()
 for key in ('source','profile','caller-sha256','plan-sha256'):parser.add_argument('--'+key,required=True)
 args=parser.parse_args();EVENTS=RUN/'API12-common-all34-0205.events.jsonl';out=RUN/'API12-common-all34-0205.json';plan_path=RUN/'API12-common-all34-plan-0205.json';are=RUN/'ARE-all34-wire-boundary-0197.json';CASES=[];FAILURES=[];ROOTS=set()
 require(not EVENTS.exists() and not out.exists(),'new exclusive actual all34 evidence required');require(Path(__file__).resolve().is_relative_to(Path('/tmp/cal-common-all34-0205')),'actual untrusted external client origin required');require(Path(__file__).read_bytes()==RETAINED.read_bytes() and bind(RETAINED)['sha256']==args.caller_sha256 and bind(plan_path)['sha256']==args.plan_sha256,'retained/runtime exact independent caller and plan bytes required');plan=json.loads(plan_path.read_bytes());PLAN=plan;require(plan['source_sha256']==args.source and plan['profile_sha256']==args.profile,'independent unchanged API12 source/profile required');require(json.loads(are.read_bytes())['authority_effect']=='none','ARE boundary grants no API authority')
 event({'phase':'starting','pid':os.getpid(),'runtime_caller_binding':bind(Path(__file__)),'retained_caller_binding':bind(RETAINED),'plan_binding':bind(plan_path),'source_sha256':args.source,'profile_sha256':args.profile});fd=os.open(RUN/'final-api-regression-0173-0190.execution.lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600);event({'phase':'waiting-real-SH0190-execution-lock'});fcntl.flock(fd,fcntl.LOCK_SH)
 try:
  NAME=install('_cal_api12_all34',API);P=module(NAME,'protocol');G=module(NAME,'guard');G.verify(args.source);schemas=P.Schemas(args.profile);A=module(NAME,'auth');F=module(NAME,'fixtures');H=module(NAME,'handlers');S=module(NAME,'service');I=module(NAME,'integration_dispatch');W=module(NAME,'workspace');M=module(NAME,'artifact_model');EF=module(NAME,'example_fixture');PR=module(NAME,'projection_refresh');CS=module(NAME,'custody_context_sessions');require(set(plan['operations'])==set(schemas.operations) and len(schemas.operations)==34,'exact all34 plan/catalog required');[require(bind(ROOT/x['path'])==x,'independent fixture/provider input changed at full entry') for x in plan['provider_bindings']];event({'phase':'full-history-entry-guard-passed'})
  for label,provider in [('action-governance',action_governance_episode),('base-and-original-Session',base_episode),('original-private-operation-fixtures',fixtures_episode),('workflow',workflow_episode),('ontology',ontology_episode),('integrated-resolution',resolution_episode),('lessons',lessons_episode)]:
   event({'phase':'episode-starting','episode':label})
   try:provider()
   except Exception:FAILURES.append({'episode':label,'detail':traceback.format_exc()});event({'phase':'episode-failed',**FAILURES[-1]})
   event({'phase':'episode-terminal','episode':label,'owned_fixture_roots_remaining':[str(x) for x in ROOTS if x.exists()]})
  G.verify(args.source);[require(bind(ROOT/x['path'])==x,'independent fixture/provider input changed at full exit') for x in plan['provider_bindings']];require(bind(RETAINED)['sha256']==args.caller_sha256 and Path(__file__).read_bytes()==RETAINED.read_bytes() and bind(plan_path)['sha256']==args.plan_sha256,'actual final caller/plan drift');exit_guard=True
 except Exception:FAILURES.append({'episode':'full-history-boundary','detail':traceback.format_exc()});exit_guard=False
 finally:fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
 coverage={op:{'positive':sum(x['operation']==op and x['expected_kind']=='result' and x['result']=='PASS' for x in CASES),'negative':sum(x['operation']==op and x['expected_kind']=='error' and x['result']=='PASS' for x in CASES)} for op in plan['operations']};missing={op:x for op,x in coverage.items() if not(x['positive'] and x['negative'])};cleanup=all(not x.exists() for x in ROOTS);passed=exit_guard and cleanup and not missing and not FAILURES and all(x['result']=='PASS' for x in CASES)
 event({'phase':'terminal','result':'PASS' if passed else 'FAIL','actual_calls':len(CASES),'missing_operation_paths':missing,'full_history_exit_guard_passed':exit_guard,'owned_fixtures_removed':cleanup})
 value={'schema_version':'lab-same-producer-common-all-operation-wire-qualification/v1-candidate','result':'PASS' if passed else 'FAIL','source_sha256':args.source,'profile_sha256':args.profile,'actual_calls':CASES,'coverage':coverage,'missing_operation_paths':missing,'failures':FAILURES,'source_guarded_entry_exit_completed':exit_guard,'owned_fixture_cleanup':[{'root':str(x),'removed':not x.exists()} for x in sorted(ROOTS)],'owned_fixture_removed':cleanup,'files':[bind(API/'source-manifest.json'),bind(API/'contract-profile.json'),bind(RETAINED),bind(plan_path)],'runtime_caller_binding':bind(Path(__file__)),'events_binding':bind(EVENTS),'are_boundary_binding':bind(are),'actual_all_calls_through_API12_common_dispatcher':True,'original345_regression_replaced':False,'original_clocks_or_callbacks_changed':False,'production_or_fixture_monkeypatches':False,'private_keys_or_policy_exported':False,'actual_owner_outcome':None,'authority_effect':'none','whole_API_qualified':False,'task_complete':False,'goal_complete':False,'claim_ceiling':'Only actual recorded same frozen API12 common-dispatcher wire calls and causal refusals. Missing positive paths and genuine provider/origin/material failures stay failures. Original345, human pilot, R08 and whole Lab acceptance remain separate.'}
 with out.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
 print(json.dumps({'result':value['result'],'actual_calls':len(CASES),'missing':missing,'report_binding':bind(out)}),flush=True);return 0 if passed else 1

if __name__=="__main__":raise SystemExit(main())
