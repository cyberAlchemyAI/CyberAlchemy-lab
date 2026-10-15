"""Exact untrusted external caller; frozen selected-API, real independent private grants."""
import argparse,base64,copy,fcntl,hashlib,importlib,importlib.util,json,os,shutil,sys,tempfile,traceback,uuid
from contextlib import contextmanager,ExitStack
from datetime import datetime,timezone,timedelta
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
sys.dont_write_bytecode=True;os.environ['PYTHONDONTWRITEBYTECODE']='1'
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction';BASE=ROOT/'product/lab/release-candidates/v1/interface';API=None;TASK=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T04/revision-0002';RETAINED=TASK/'caller.py'
import caller_adapter as B
from caller_adapter import classify, result_message, CallerBoundaryError, RecoveryGate, OwnedOperation
ADAPTER_CALLBACKS=(classify,result_message,CallerBoundaryError,RecoveryGate,OwnedOperation)

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
def adapter_guard():
 selected=PLAN['caller_adapter_binding'];retained=ROOT/selected['path'];runtime=Path(B.__file__).resolve()
 require(bind(retained)==selected and runtime.parent==Path(__file__).resolve().parent and runtime.read_bytes()==retained.read_bytes(),'exact selected caller adapter/origin changed')
 require(ADAPTER_CALLBACKS==(B.classify,B.result_message,B.CallerBoundaryError,B.RecoveryGate,B.OwnedOperation),'selected caller boundary callbacks changed')
def retention_guard():
 # The future run plan independently selects a protected owned staging location.
 # No retained private bytes enter the repository or public report.
 selected=PLAN['pending_retention'];root=Path(selected['root'])
 require(root.is_absolute() and root.is_relative_to(Path('/tmp')) and not root.is_relative_to(ROOT) and root.resolve()==root and not any(p.is_symlink() for p in (root,*root.parents)),'unsafe pending-retention selection')
 st=root.stat();require(root.is_dir() and st.st_uid==os.getuid() and st.st_mode&0o777==0o700 and (st.st_dev,st.st_ino)==(selected['device'],selected['inode']),'pending retention custody/preimage differs');return root
def preserve_pending(root):
 retention=retention_guard();target=Path(root).resolve();owners=[p for p in ROOTS if target==p or target.is_relative_to(p)]
 require(len(owners)==1,'uncertain metadata must remain in one caller-owned fixture')
 owned=owners[0];require(owned.exists() and not owned.is_symlink(),'owned pending source absent')
 require(not any(p.is_symlink() for p in owned.rglob('*')),'pending source contains a foreign symlink')
 before=snapshot(owned);saved=retention/('pending-'+uuid.uuid4().hex);shutil.copytree(owned,saved,symlinks=False);saved.chmod(0o700)
 require(snapshot(saved)==before and snapshot(owned)==before,'pending custody copy differs or changed during retention')
 digest=hashlib.sha256(json.dumps(before,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 event({'phase':'owned-pending-evidence-retained','protected_root':str(saved),'inventory_sha256':digest,'files':len(before),'private_bytes_exported_to_repository':False});return saved
def inspect_uncertain(surface,request,reply,root,original_raw):
 # This one read never retries/reconciles the effect and never renews a deadline.
 operation=request['operation'];context=None
 for branch in surface.branches:
  candidate=getattr(branch.channel,'context',None)
  if isinstance(candidate,dict) and candidate.get('context_ref')==request.get('caller_context_ref'):context=candidate;break
 actor=request.get('message',{}).get('actor')
 require(context is not None and isinstance(actor,dict) and actor.get('principal_ref')==context.get('principal_ref') and root is not None,'owned current context/Actor/workspace needed for scoped inspection')
 owned=OwnedOperation(operation,request.get('idempotency_key'),context['context_ref'],context['principal_ref'],P.source.sha(original_raw),getattr(surface.base.vault,'manifest',{}).get('workspace_ref','caller-owned-fixture'))
 gate=RecoveryGate(owned,reply);call=gate.inspection_call(request,context,call_id='call:T04-inspection:'+uuid.uuid4().hex,original_raw=original_raw)
 observed=invoke(surface,call,'actual-owned-uncertain-operation-inspection','result',root=root)
 resolution=gate.observe_inspection(observed);event({'phase':'uncertain-operation-inspected','resolution':resolution,'automatic_effect_retry':False});return resolution

def positive_semantics(surface,request,reply):
 if reply.get('kind')!='result':return False
 op=request['operation'];message=result_message(reply,op);postures={'action.evaluate':'permitted','action.dispatch':'completed','action.reconcile':'recovered','admission.apply':'committed','session.open':'active','installation.execute':'installed','release.prepare':'blocked','workflow.transition':'applied','ontology.project':'applied'}
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
 require(type(surface) is I.IntegrationService,'actual selected common dispatcher type/origin required');adapter_guard();retention_guard()
 for selected in PLAN['provider_bindings']:require(bind(ROOT/selected['path'])==selected,'exact independently selected provider changed at actual call boundary')
 raw=P.compact(request);operation=request['operation'];row=schemas.operations[operation];W.privacy(request)
 req_valid=schemas.valid('api-call',request);inner_valid=schemas.protocol_valid(row['request_schema']['resource_uri'],request['message'])
 require(req_valid and inner_valid,'case must reach an actual schema-valid request boundary')
 before=snapshot(root) if root is not None else None;started=datetime.now(timezone.utc).isoformat();reply=surface.call(raw);ended=datetime.now(timezone.utc).isoformat();W.privacy(reply)
 decision=classify(reply);wire=schemas.valid('api-reply',reply) if decision.envelope in ('domain-result','domain-error') else schemas.valid('transport-error',reply) if decision.envelope=='transport-error' else False
 actual_binding=reply.get('request_binding',{}).get('sha256',reply.get('request_byte_sha256'));bound=actual_binding==P.source.sha(raw)
 uri=row['result_schema' if reply.get('kind')=='result' else 'error_schema']['resource_uri']
 if operation=='artifact.inspect' and reply.get('kind')=='result':uri='urn:cyberalchemy-lab:protocol:artifact-inspect-result:v2-candidate'
 selected_uri=schemas.uri_mapping.get(uri,uri);domain=decision.envelope in ('domain-result','domain-error') and schemas.protocol_valid(uri,reply['message']);profile=decision.envelope in ('domain-result','domain-error') and reply.get('contract_profile_binding')==schemas.profile_binding
 code=reply.get('message',{}).get('code',reply.get('code')) if isinstance(reply.get('message',{}),dict) else reply.get('code');allowed=reply.get('kind')!='error' or code in row['allowed_error_codes'];no_effect=before is None or snapshot(root)==before
 semantic=positive_semantics(surface,request,reply) if expect=='result' and decision.state=='completed' and wire and bound and domain and profile and allowed else False if expect=='result' else None
 good=wire and bound and domain and profile and allowed and reply.get('kind')==expect and (expected_code is None or code==expected_code) and (expect!='error' or no_effect) and (expect!='result' or semantic)
 record={'operation':operation,'case':label,'result':'PASS' if good else 'FAIL','started_at':started,'ended_at':ended,'raw_request_base64':base64.b64encode(raw).decode(),'request_byte_sha256':P.source.sha(raw),'original_request':request,'actual_reply':reply,'expected_kind':expect,'expected_code':expected_code,'actual_code':code,'api_request_schema_valid':req_valid,'inner_request_schema_valid':inner_valid,'api_reply_or_transport_schema_valid':wire,'actual_domain_schema_valid':domain,'actual_profile_binding_matches':profile,'actual_request_byte_binding_matches':bound,'declared_error_code_matches':allowed,'positive_semantic_and_owned_effect_checks_passed':semantic,'selected_request_schema_uri':schemas.uri_mapping.get(row['request_schema']['resource_uri'],row['request_schema']['resource_uri']),'selected_actual_reply_schema_uri':selected_uri,'original_catalog_operation_contract':row,'negative_owned_effect_state_unchanged':no_effect if expect=='error' else None,'same_frozen_selected-API_common_dispatcher':True,'private_key_or_policy_exported':False,'caller_boundary':decision.record()}
 CASES.append(record);event({'phase':'case-completed',**record});print(operation,label,record['result'],code,flush=True)
 if decision.state=='uncertain':
  # Retain protected owned evidence before provider/finalizer cleanup can run.
  if root is not None:preserve_pending(root)
  event({'phase':'owned-inspection-required','operation':operation,'idempotency_key':request.get('idempotency_key'),'caller_context_ref':request.get('caller_context_ref'),'original_request_sha256':P.source.sha(raw),'automatic_effect_retry':False,'next_action':decision.next_action})
  if operation!='operation.inspect':
   try:inspect_uncertain(surface,request,reply,root,raw)
   except Exception as error:event({'phase':'uncertain-inspection-unavailable','exception_class':type(error).__name__,'automatic_effect_retry':False,'next_action':'independent-owned-inspection-and-reconciliation-required'})
  raise CallerBoundaryError(operation,decision)
 if decision.state=='invalid':raise CallerBoundaryError(operation,decision)
 if expect=='result':
  result_message(reply,operation)
  if not (wire and bound and domain and profile and allowed and semantic):raise CallerBoundaryError(operation,B.Decision('invalid','domain-result','result-contract-failed','stop-inspect-known-operation',False,None))
 return reply
def pair(host,request,root=None,surface=None):
 surface=common(host) if surface is None else surface;negative=copy.deepcopy(request);negative['call_id']='call:all34:negative:'+uuid.uuid4().hex
 actor=negative['message'].get('actor')
 if isinstance(actor,dict):actor['principal_ref']='principal:all34-foreign';code='unauthorized';cause='foreign-public-Actor-does-not-replace-independent-principal'
 elif request['operation']=='session.close':negative['message']['agent_instance_ref']='agent-instance:all34-foreign';code='unauthorized';cause='foreign-Agent-does-not-replace-owned-live-Session'
 else:negative['deadline']=(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat();code='deadline-exceeded';cause='actual-expired-outer-deadline-before-effect'
 invoke(surface,negative,cause,'error',code,root);return invoke(surface,request,'actual-positive-domain-result','result',root=root)
@contextmanager
def base_fixture(view):
 with tempfile.TemporaryDirectory(prefix='cal-all34-base-0242-') as temporary:
  root=Path(temporary);root.chmod(0o700);track(root);materials,metadata,target=EF.materials_for(view);MF=module(NAME,'metadata_fixture');key,path,_=MF.provision(root,materials,metadata,scoped=False);policy=P.frame_parse(path.read_bytes());policy['projection_control']=PR.control(view);path.write_bytes(P.compact(policy));pin=P.source.sha(path.read_bytes());require(policy['session_control'] is None,'metadata fixture must not revive expired Assignment');channel=A.ReaderChannel(path,pin,schemas);channel.authenticate(F.proof(key,channel.challenge));key=None;host=S.Service(view,channel,schemas)
  try:yield host,target,root
  finally:host.close();channel.close()
def op_call(host,operation,message,key=None,cut=None):
 value=F.call(host.channel.context,'lab.status',H.cut(host.handlers.view) if cut is None else cut);value.update(operation=operation,message=copy.deepcopy(message),idempotency_key=key);return value
def align_outer_key(request):
 before=P.compact(request['message']);row=schemas.operations[request['operation']];selector=row['inner_idempotency_selector']
 require(isinstance(selector,str) and selector.startswith('/'),'actual declared inner selector required')
 value=request['message']
 for segment in selector[1:].split('/'):
  field=segment.replace('~1','/').replace('~0','~');value=value[int(field)] if isinstance(value,list) else value[field]
 require(isinstance(value,str) and value,'actual nonempty inner key required');original=request['idempotency_key'];request['idempotency_key']=value
 require(P.compact(request['message'])==before,'supplement may not alter original message')
 event({'phase':'caller-envelope-key-aligned','operation':request['operation'],'selector':selector,'original_outer_key':original,'aligned_outer_key':value,'original_inner_message_byte_sha256':P.source.sha(before),'inner_message_unchanged':True})
 return request

def base_episode():
 with P.source.replay_source('custody-participation') as view:
  for operation in [UNIT.split(':',1)[1]]:
   with base_fixture(view) as (host,target,root):
    if operation in ('change.prepare','change.validate'):
     request=EF.candidate_call(host,target,operation,key='all34:'+operation)
     if operation=='change.prepare':align_outer_key(request)
    elif operation=='artifact.inspect':subject=next(x for x in view.subjects.values() if x['identity']=='product:cyberalchemy-lab');request=F.call(host.channel.context,operation,H.cut(view),artifact=M.artifact_ref(view,subject),include=['body','contract','authority','provenance','gaps'])
    elif operation=='projection.refresh':
     seed=F.call(host.channel.context,'lab.status',H.cut(view));budget=seed['message']['budget'];budget['max_actions']=1;grant=host.channel.policy['projection_control'];message={'schema_version':'lab-projection-refresh-request/v1-candidate','request_ref':'request:all34-refresh','source_cut':H.cut(view),'projector_binding':grant['projector_binding'],'contract_catalog_binding':grant['contract_catalog_binding'],'expected_generation_binding':None,'budget':budget,'authority_effect':'none'};request=op_call(host,operation,message,'all34:refresh')
    elif operation=='operation.inspect':
     dependency=align_outer_key(EF.candidate_call(host,target,key='all34:inspection-dependency'));prepared=invoke(common(host),dependency,'actual-owned-inspection-prerequisite','result');request=F.call(host.channel.context,operation,None,lookup={'operation':'change.prepare','idempotency_key':dependency['idempotency_key']})
    else:request=F.call(host.channel.context,operation,H.cut(view))
    pair(host,request,root)

def fixtures_episode():
    with P.source.replay_source('custody-participation') as view:
        if UNIT.startswith('fixture:'):
            for operation, stem in [('classification.prepare', 'classification_fixture'), ('failure.assess', 'failure_fixture'), ('challenge.submit', 'challenge_fixture'), ('proposal.review', 'review_fixture'), ('package.export', 'package_export_fixture'), ('installation.execute', 'installation_release_fixture'), ('release.prepare', 'installation_release_fixture')]:
                if operation != UNIT.split(':', 1)[1]:
                    continue
                provider = module(NAME, stem)
                try:
                    with provider.example(view, schemas, **{'release': True} if operation == 'release.prepare' else {}) as values:
                        host, request, witness = values
                        track(witness['root'] if 'root' in witness else host.vault.root.parent)
                        request = request() if callable(request) else request
                        pair(host, request, host.vault.root)
                except Exception:
                    FAILURES.append({'episode': 'provider:' + operation, 'detail': traceback.format_exc()})
                    event({'phase': 'provider-failed', 'operation': operation, 'detail': FAILURES[-1]['detail']})
        if UNIT == 'transfer:files':
            export = module(NAME, 'export_fixture')
            with tempfile.TemporaryDirectory(prefix='cal-all34-files-0242-') as temporary:
                root = Path(temporary)
                root.chmod(448)
                track(root)
                selected = export.selection(view)
                key, path, pin = export.provision(root, selected)
                channel = A.ReaderChannel(path, pin, schemas)
                channel.authenticate(F.proof(key, channel.challenge))
                key = None
                host = S.Service(view, channel, schemas)
                try:
                    pair(host, export.call(host, selected), host.vault.root)
                finally:
                    host.close()
                    channel.close()
        if UNIT == 'transfer:import':
            package = module(NAME, 'package_fixture')
            with tempfile.TemporaryDirectory(prefix='cal-all34-import-0242-') as temporary:
                root = Path(temporary)
                root.chmod(448)
                track(root)
                key, path, pin, message, proposal, plan, archive = package.provision(root, view)
                channel = A.ReaderChannel(path, pin, schemas)
                channel.authenticate(F.proof(key, channel.challenge))
                key = None
                host = S.Service(view, channel, schemas)
                try:
                    pair(host, op_call(host, 'package.import', message, package.KEY), host.vault.root)
                finally:
                    host.close()
                    channel.close()
        if UNIT == 'transfer:typed':
            typedname = install('_cal_all34_typed_fixture', BASE / 'api50-typed-checks-v4')
            typed = module(typedname, 'fixture')
            with typed.example(NAME, view, schemas) as (host, request, witness):
                track(witness['root'])
                pair(host, request, host.vault.root)

def action_governance_episode():
 members=json.loads((API/'integration-members.json').read_bytes())['members'];an=install('_cal_all34_actions',BASE/members['actions']['directory']);gn=install('_cal_all34_governance',BASE/members['governance']['directory']);AF=module(an,'fixture');AS=module(an,'service');GF=module(gn,'fixture');GS=module(gn,'service')
 class SharedGovernance(GF.Fixture):
  def open(self):
   self.host=GF.GovernanceHost(self.root,self.policy_pin,self.schemas,members['governance']['source_sha256'],members['governance']['profile_sha256'],integration_profile_binding=self.schemas.profile_binding);self.channel=GF.GovernanceChannel(self.host);self.channel.authenticate({'challenge':self.channel.challenge,'signature_base64':base64.b64encode(self.reader.sign(GF.encoded(self.channel.challenge))).decode()});self.service=GS.GovernanceService(self.host,self.channel)
 with P.source.replay_source('custody-participation') as view,base_fixture(view) as (host,target,base_root),tempfile.TemporaryDirectory(prefix='cal-all34-branches-0242-') as temporary:
  owned=Path(temporary);owned.chmod(0o700);track(owned);action=AF.OwnedActor(owned/'actions',schemas,integration_profile_binding=schemas.profile_binding);gr=owned/'governance';gr.mkdir(mode=0o700);gov=SharedGovernance(gr,schemas);actions=AS.ActionService(action.runtime,action.channel,schemas,source_sha256=members['actions']['source_sha256'],profile_sha256=members['actions']['profile_sha256'],integration_profile_binding=schemas.profile_binding)
  try:
   surface=common(host,action_service=actions,governance_service=gov.service)
   def action_call(operation,message,key=None):return {'schema_version':'lab-api-call/v2-candidate','call_id':'call:all34-action:'+uuid.uuid4().hex,'operation':operation,'caller_context_ref':action.channel.context['context_ref'],'expected_source_cut':copy.deepcopy(action.cut),'deadline':action.deadline,'max_response_bytes':1048576,'idempotency_key':key,'message':copy.deepcopy(message),'expected_contract_profile_binding':schemas.profile_binding}
   request=action.request(increment=3);pair(actions,action_call('action.evaluate',request),action.root,surface);dispatched=pair(actions,action_call('action.dispatch',request,request['idempotency_key']),action.root,surface);recovery=action.recovery(dispatched['message'],key='all34:reconcile');pair(actions,action_call('action.reconcile',recovery,'all34:reconcile'),action.root,surface)
   checkpoint=pair(gov.service,gov.checkpoint_call('all34:checkpoint'),gr,surface);pair(gov.service,gov.capability_call('all34:capability'),gr,surface);pair(gov.service,gov.admission_call(checkpoint['message']['subject_binding'],'all34:admission'),gr,surface)
  finally:gov.service.close();gov.channel.close();action.close()
def resolution_episode():
 package=BASE/'current-participation-v8/packages/0001';plan=json.loads((package/'resolution-qualification-plan.json').read_bytes());period=json.loads((package/'period.json').read_bytes())
 with P.source.replay_source('integrated-participation') as view,tempfile.TemporaryDirectory(prefix='cal-all34-resolution-0242-') as temporary:
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
     key,policy_path,pin=F.provision(owned,'reference-corrected',principal=principal,max_actions=8)
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
     policy.update(schema_version='lab-local-ontology-projection-policy/v1-candidate',source_name='custody-participation',session_control=None,
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
def source8_lifecycle(stack,H,M,D,selected,parent,selection,events,roots):
 P=M['protocol'];A=M['auth'];view=selected.view;sid=selection['session_ref'];resource=parent.sessions.live[sid]
 item=next(item for item in selection['items'] if item['posture']=='selected');lesson=item['lesson']
 selection_binding=parent.vault.object(P.compact(selection));instruction=selection['instruction_precedence_binding'];applicability=item['applicability_check_binding']
 root=Path(stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-Source8-application-action-0148-')));root.chmod(0o700);roots.append(str(root))
 body=P.source.parse((P.ROOT/'authority/artifact-types/lesson-application/v1/fixtures/valid/record.json').read_bytes())
 body.update(node_id='lesson-application:Source8-'+__import__('uuid').uuid4().hex,owner_ref=D.records.PRINCIPAL,scope_ref=selected.sources.scope_ref,
             evidence_refs=[lesson['version_ref']],claim_ceiling='Controlled unadmitted application candidate; no Tool dispatch or effectiveness claim.')
 body['payload'].update(lesson_revision_ref=lesson['version_ref'],session_ref=sid,applicability_assessment_ref=applicability['ref'],
                        intended_influence='Record the exact reviewed fixture Lesson in this actual Session candidate.',conflict_refs=[],override_refs=[],application_posture='candidate-attributed-no-tool-dispatch')
 body['relation_refs']=[{'relation_kind_ref':'relation.applies-lesson','direction':'source','counterpart_kind':'operational-lesson','counterpart_ref':lesson['version_ref']}]
 materials,metadata,target=H.candidate_materials(M,view,body,'fixture:application')
 key,path,_=H.provision(M,root,D,selected,'source8-lesson-fixture-participation',materials,kind='lab-local-lesson-application-policy/v2-candidate',metadata=metadata)
 policy=P.frame_parse(path.read_bytes());operation_key='Source8:actual-application';proposal=H.proposal_before_auth(M,view,policy,target,operation_key)
 proposal_binding=H.object_before_auth(M,root,policy,P.compact(proposal));method=P.ROOT/'product/lab/release-candidates/v1/interface/lesson-application-v3-action-0148/preparation.py';method_binding=P.binding(str(method.relative_to(P.ROOT)),method.read_bytes())
 routing={'schema_version':'lab-lesson-application-routing/v1-candidate','source_cut':selected.source_cut,'scope_ref':selected.sources.scope_ref,
          'proposal_binding':proposal_binding,'method_binding':method_binding,'selection_binding':selection_binding,'applicability_binding':applicability,
          'instruction_precedence_binding':instruction,'intended_influence':body['payload']['intended_influence'],'action_bound_refs':[],
          'override_bindings':[],'authorization_basis_binding':policy['development_authorization_binding'],'authority_effect':'none','actual_owner_outcome':None}
 routing_binding=H.object_before_auth(M,root,policy,P.compact(routing))
 policy['application_control']={'routing_binding':routing_binding,'method_binding':method_binding,
                               'runtime_identities':{'session_ref':sid,'agent_instance_ref':resource.agent['node_id']}}
 path.write_bytes(P.compact(policy));pin=P.source.sha(path.read_bytes());channel=A.ReaderChannel(path,pin,parent.schemas);channel.authenticate(M['fixtures'].proof(key,channel.challenge))
 manifest=P.source.parse((root/'workspace/workspace.json').read_bytes());row=parent.sessions.selected(sid)
 attachment={'schema_version':'lab-private-Source8-Session-attachment/v1-candidate','parent_source_binding':bind(API/'source-manifest.json'),
   'session_ref':sid,'agent_instance_ref':resource.agent['node_id'],'assignment':row['assignment'],'session_state_binding':row['session_state_binding'],
   'source_cut':selected.source_cut,'principal_ref':D.records.PRINCIPAL,'parent_policy_sha256':parent.channel.expected_sha,'operator_policy_sha256':pin,
   'parent_workspace_binding':parent.vault.control_binding,'operator_workspace_binding':{'ref':'workspace:'+manifest['workspace_ref'],'sha256':policy['workspace']['manifest_sha256']},
   'selection_binding':selection_binding,'applicability_binding':applicability,'instruction_precedence_binding':instruction,'authority_effect':'none'}
 bad=copy.deepcopy(attachment);bad['session_ref']='agent-session:R03-live:'+'f'*32
 before=len(list((root/'workspace/journal').glob('*.claim.json')))
 try:M['service'].Service(view,channel,parent.schemas,parent_host=parent,session_attachment_binding=bad)
 except (ValueError,KeyError):pass
 else:raise AssertionError('foreign private resource attachment unexpectedly accepted')
 assert before==len(list((root/'workspace/journal').glob('*.claim.json')))
 events.append({'case':'foreign-Session-attachment','result':'actual-refusal'})
 application=M['service'].Service(view,channel,parent.schemas,parent_host=parent,session_attachment_binding=attachment);stack.callback(application.close)
 app_api=importlib.import_module(M['service'].__package__+'.integration_dispatch').IntegrationService(application)
 actor={k:channel.context[k] for k in ('principal_ref','agent_instance_ref','session_ref','assignment_ref')};actor['role_assignment_refs']=[]
 message={'schema_version':'lab-lesson-application-request/v1-candidate','request_ref':'request:Source8-application','actor':actor,
   'source_cut':selected.source_cut,'lesson':lesson,'session_ref':sid,'selection_binding':selection_binding,'applicability_binding':applicability,
   'conflict_refs':[],'override_basis':[],'application_candidate_binding':P.binding('fixture:application:body',materials['fixture:application:body']),
   'authority_effect':'none'}
 call=H.call(M,application,'lesson.apply',message,key=operation_key);raw=P.compact(call);reply=pair(application,call,application.vault.root,app_api)
 events.append({'operation':'lesson.apply','raw_sha256':P.source.sha(raw),'reply':reply});assert reply.get('kind')=='result',reply
 claims=len(list((application.vault.root/'journal').glob('*.claim.json')));retry_call=copy.deepcopy(call);retry_call['call_id']+='-retry';require(retry_call['message']==call['message'] and retry_call['idempotency_key']==call['idempotency_key'],'exact operation retry must retain original message and key');retry=invoke(app_api,retry_call,'actual-completed-application-exact-retry','result',root=application.vault.root)
 assert retry.get('kind')=='result' and retry['message']==reply['message'];assert claims==len(list((application.vault.root/'journal').glob('*.claim.json')))
 events.append({'operation':'lesson.apply','case':'exact-retry','reply':retry})
 lookup=M['fixtures'].call(channel.context,'operation.inspect',None,lookup={'operation':'lesson.apply','idempotency_key':operation_key})
 inspected=invoke(app_api,lookup,'actual-completed-application-inspection','result',root=application.vault.root);events.append({'operation':'operation.inspect','reply':inspected});assert inspected.get('kind')=='result',inspected
 # Current independent observer records what these actual calls returned.
 evidence={'schema_version':'lab-controlled-application-observation/v1-candidate','source_cut':selected.source_cut,
           'application_result_sha256':P.source.sha(P.compact(reply['message'])),'inspection_result_sha256':P.source.sha(P.compact(inspected['message'])),
           'completed_claim_count':claims,'Tool_dispatches':0,'canonical_admission':False,'authority_effect':'none','actual_owner_outcome':None}
 app_header={k:target['artifact'][k] for k in ('scope_ref','identity_ref','version_ref','carrier_ref','byte_sha256')}
 assess_root=Path(stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-Source8-assessment-action-0148-')));assess_root.chmod(0o700);roots.append(str(assess_root))
 ceiling='Exact recorded application outcome only; no general or causal effectiveness inferred.'
 eb=P.binding('fixture:observed-application',P.compact(evidence));predicted='Prepare one exact unadmitted application candidate.';observed='Actual authenticated application result and separate scoped inspection were returned; no admission or Tool effect.'
 assessment=P.source.parse((P.ROOT/'authority/artifact-types/lesson-outcome-assessment/v1/fixtures/valid/record.json').read_bytes())
 assessment.update(node_id='lesson-outcome-assessment:Source8-'+__import__('uuid').uuid4().hex,owner_ref=D.records.PRINCIPAL,scope_ref=selected.sources.scope_ref,evidence_refs=[eb['ref']],claim_ceiling=ceiling)
 assessment['payload'].update(lesson_application_ref=app_header['version_ref'],predicted_outcome=predicted,observed_outcome=observed,
    disposition='recorded-outcome-only',evidence_refs=[eb['ref']],counterevidence_refs=[],causal_claim_ceiling=ceiling)
 assessment['relation_refs']=[{'relation_kind_ref':'relation.derives-from','direction':'source','counterpart_kind':'lesson-application','counterpart_ref':app_header['version_ref']}]
 mats,meta,ass_target=H.candidate_materials(M,view,assessment,'fixture:assessment');mats[eb['ref']]=P.compact(evidence)
 observation={'schema_version':'lab-recorded-application-outcome/v1-candidate','method_ref':'recorded-application-outcome/v1-candidate',
   'scope_ref':selected.sources.scope_ref,'source_cut':selected.source_cut,'application':app_header,'predicted_outcome':predicted,
   'observed_outcome':observed,'evidence_bindings':[eb],'counterevidence_bindings':[],'causal_claim_ceiling':ceiling,'authority_effect':'none'}
 mats['fixture:outcome-observation']=P.compact(observation)
 ak,ap,_=H.provision(M,assess_root,D,selected,'source8-lesson-fixture-participation',mats,kind='lab-local-lesson-assessment-policy/v1-candidate',metadata=meta)
 pol=P.frame_parse(ap.read_bytes());ass_key='Source8:actual-assessment';prop=H.proposal_before_auth(M,view,pol,ass_target,ass_key)
 pb=H.object_before_auth(M,assess_root,pol,P.compact(prop));method=method.parent.parent/'lesson-assessment-v2-action-0148/preparation.py';mb=P.binding(str(method.relative_to(P.ROOT)),method.read_bytes())
 route={'schema_version':'lab-lesson-assessment-routing/v1-candidate','scope_ref':selected.sources.scope_ref,'source_cut':selected.source_cut,
    'proposal_binding':pb,'method_binding':mb,'observation_binding':P.binding('fixture:outcome-observation',mats['fixture:outcome-observation']),
    'authorization_basis_binding':pol['development_authorization_binding'],'authority_effect':'none','actual_owner_outcome':None}
 rb=H.object_before_auth(M,assess_root,pol,P.compact(route));pol['assessment_control']={'routing_binding':rb,'method_binding':mb}
 pol['source8_control']['application_journal_scope']={'root':str(application.vault.root),'workspace_binding':application.vault.control_binding,'manifest_sha256':policy['workspace']['manifest_sha256']}
 ap.write_bytes(P.compact(pol));ac=A.ReaderChannel(ap,P.source.sha(ap.read_bytes()),parent.schemas);ac.authenticate(M['fixtures'].proof(ak,ac.challenge))
 assessor=M['service'].Service(view,ac,parent.schemas);stack.callback(assessor.close)
 actor={k:ac.context[k] for k in ('principal_ref','agent_instance_ref','session_ref','assignment_ref')};actor['role_assignment_refs']=[]
 msg={'schema_version':'lab-lesson-assessment-request/v1-candidate','request_ref':'request:Source8-assessment','actor':actor,'source_cut':selected.source_cut,
   'application':app_header,'assessment_candidate_binding':P.binding('fixture:assessment:body',mats['fixture:assessment:body']),
   'evidence_bindings':[eb],'counterevidence_bindings':[],'causal_claim_ceiling':ceiling,'authority_effect':'none'}
 assess_api=importlib.import_module(M['service'].__package__+'.integration_dispatch').IntegrationService(assessor)
 reply=pair(assessor,H.call(M,assessor,'lesson.assess',msg,key=ass_key),assessor.vault.root,assess_api)
 events.append({'operation':'lesson.assess','reply':reply});assert reply.get('kind')=='result',reply
 application.close();assert resource.closed is False and parent.sessions.live.get(sid) is resource
 return ['foreign-Session-attachment','actual-late-application-attachment','completed-application-exact-retry','completed-application-inspection','actual-journal-candidate-assessment','attached-close-preserves-parent']

class OwnedRoots:
 def append(self,value):track(Path(value))

def source8_episode():
 runtime_name=install('_cal_all34_source8_runtime_provider',BASE/'source8-session-runtime-v1-action-0148');provider=module(runtime_name,'provider');mods=provider.modules(NAME)
 with ExitStack() as stack:
  source_name='source8-lesson-fixture-participation';D=P.source.source8_delivery_for(source_name);selected=stack.enter_context(D.reader.open_signed(D.SOURCE_PIN,D.SOURCE_PACKAGE));view=selected.view;view.custody_signed_sources=selected;view.integrated_reader=D.reader;view.source8_context_producer=D
  materials,plan=provider.lesson_materials(mods,D,selected);root=Path(stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-all34-source8-0242-')));root.chmod(0o700);track(root)
  key,path,pin=provider.provision(mods,root,D,selected,source_name,materials);channel=A.ReaderChannel(path,pin,schemas);channel.authenticate(F.proof(key,channel.challenge));key=None;host=S.Service(view,channel,schemas);stack.callback(host.close);stack.callback(channel.close);surface=common(host)
  context=D.query(selected,host.sessions.bridge);delivery=pair(host,provider.call(mods,host,'context.get',context),root,surface)
  ref=lambda identity:copy.deepcopy(selected.sources.resolve(identity+'@'+D.records.VERSION)[0].artifact);budget=copy.deepcopy(context['budget']);budget['max_actions']=1;runtime=importlib.import_module(type(host.sessions).__module__)
  opening={'schema_version':'lab-agent-session-open/v1-candidate','request_ref':'request:all34-source8-open:'+uuid.uuid4().hex,'actor':host.sessions.bridge.actor(),'assignment':ref(D.records.ASSIGNMENT),'profile':ref(D.records.PROFILE),'implementation':ref(D.records.IMPLEMENTATION),'capabilities':[ref(D.records.CAPABILITY)],'context_delivery_binding':P.binding('context-delivery:'+result_message(delivery,'context.get')['context_view']['version_ref'],P.compact(result_message(delivery,'context.get'))),'authority_envelope_binding':runtime.stable_policy(host.channel),'source_cut':selected.source_cut,'budget':budget,'memory_policy':{'persistence_allowed':False,'expires_with_session':True},'authority_effect':'none'}
  opened=pair(host,provider.call(mods,host,'session.open',opening,key='all34:source8-open'),root,surface);opened_message=result_message(opened,'session.open');sid=opened_message['session_ref'];resource=host.sessions.live[sid]
  scope_kernel=runtime.D.FACT_SCOPE
  callbacks=(selected.guard,selected.sources.current_guard,D.verify_source,D.generate,host.channel.guard,host.channel.policy_guard,host.channel.termination_guard,scope_kernel.policy_scope,scope_kernel.parent_guard,scope_kernel.package_guard)
  started=A.now();machine=mods['machine_transport'].select(host,sid,bind(API/'source-manifest.json'));stack.callback(machine.close)
  require(scope_kernel.active_scope() is None,'Machine select retained source scope');event({'phase':'actual-Machine-select-completed','started_at':started.isoformat(),'ended_at':A.now().isoformat(),'elapsed_seconds':(A.now()-started).total_seconds(),'original_Session_expires_at':resource.expires.isoformat(),'source_scope_absent':True})
  started=A.now();proof=machine.proof();require(scope_kernel.active_scope() is None,'Machine proof retained source scope');event({'phase':'actual-Machine-proof-completed','started_at':started.isoformat(),'ended_at':A.now().isoformat(),'elapsed_seconds':(A.now()-started).total_seconds(),'source_scope_absent':True})
  started=A.now();machine.authenticate(proof);require(scope_kernel.active_scope() is None,'Machine authentication retained source scope');require(machine.used and machine.context is not None and machine._private_key is not None,'actual proof nonce must be consumed and live signer retained until disposal')
  require(type(machine) is mods['machine_transport'].MachinePeer and type(machine.service) is S.Service and machine.service.borrowed_custody is False,'actual selected Machine/Service required')
  require((selected.guard,selected.sources.current_guard,D.verify_source,D.generate,host.channel.guard,host.channel.policy_guard,host.channel.termination_guard,scope_kernel.policy_scope,scope_kernel.parent_guard,scope_kernel.package_guard)==callbacks,'Machine setup replaced original callback')
  event({'phase':'actual-Machine-authentication-completed','started_at':started.isoformat(),'ended_at':A.now().isoformat(),'elapsed_seconds':(A.now()-started).total_seconds(),'original_Session_expires_at':resource.expires.isoformat(),'source_scope_absent':True,'nonce_consumed':True})
  machine_api=common(machine.service);query=D.query(selected,machine.service.sessions.bridge);selection=pair(machine.service,provider.call(mods,machine.service,'lesson.select',query),root,machine_api)
  selection_message=result_message(selection,'lesson.select');require(len(selection_message['items'])==len(plan['lessons']) and len([item for item in selection_message['items'] if item['posture']=='selected'])==1,'exact actual fixture Lesson selection required');original=[item for item in selection_message['items'] if item['lesson']['identity_ref']=='operational-lesson:R03-Machine-policy-custody'];require(len(original)==1 and original[0]['posture']!='selected','original Source8 Lesson may not inherit fixture applicability')
  source8_lifecycle(stack,provider,mods,D,selected,host,selection_message,[],OwnedRoots())
  inspect_message={'schema_version':'lab-session-inspect-request/v1-candidate','request_ref':'request:all34-source8-inspect:'+uuid.uuid4().hex,'actor':host.sessions.bridge.actor(),'session_ref':sid,'budget':budget,'authority_effect':'none'};inspected=pair(host,provider.call(mods,host,'session.inspect',inspect_message),root,surface)
  closing={'schema_version':'lab-agent-session-close/v1-candidate','request_ref':'request:all34-source8-close:'+uuid.uuid4().hex,'session_ref':sid,'agent_instance_ref':opened_message['agent_instance_ref'],'expected_session_binding':result_message(inspected,'session.inspect')['last_receipt_binding'],'requested_at':A.now().isoformat(),'reason':'completed','eligible_audit_bindings':[],'authority_effect':'none'};pair(host,provider.call(mods,host,'session.close',closing,key='all34:source8-close'),root,surface);require(resource.closed and machine.closed and machine._private_key is None and machine.context is None,'actual parent Session and Machine signer/context disposal required');require(scope_kernel.active_scope() is None,'publiclifecycle retained source scope');event({'phase':'actual-Machine-disposal-completed','private_key_erased':True,'source_scope_absent':True,'original_source_and_policy_callbacks_retained':(selected.guard,selected.sources.current_guard,D.verify_source,D.generate,host.channel.guard,host.channel.policy_guard,host.channel.termination_guard,scope_kernel.policy_scope,scope_kernel.parent_guard,scope_kernel.package_guard)==callbacks})

def source8_failed_auth_episode():
 runtime_name=install('_cal_all34_source8_runtime_provider',BASE/'source8-session-runtime-v1-action-0148');provider=module(runtime_name,'provider');mods=provider.modules(NAME)
 with ExitStack() as stack:
  source_name='source8-lesson-fixture-participation';D=P.source.source8_delivery_for(source_name);selected=stack.enter_context(D.reader.open_signed(D.SOURCE_PIN,D.SOURCE_PACKAGE));view=selected.view;view.custody_signed_sources=selected;view.integrated_reader=D.reader;view.source8_context_producer=D
  materials,plan=provider.lesson_materials(mods,D,selected);root=Path(stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-all34-source8-0242-')));root.chmod(0o700);track(root)
  key,path,pin=provider.provision(mods,root,D,selected,source_name,materials);channel=A.ReaderChannel(path,pin,schemas);channel.authenticate(F.proof(key,channel.challenge));key=None;host=S.Service(view,channel,schemas);stack.callback(host.close);stack.callback(channel.close);surface=common(host)
  context=D.query(selected,host.sessions.bridge);delivery=pair(host,provider.call(mods,host,'context.get',context),root,surface)
  ref=lambda identity:copy.deepcopy(selected.sources.resolve(identity+'@'+D.records.VERSION)[0].artifact);budget=copy.deepcopy(context['budget']);budget['max_actions']=1;runtime=importlib.import_module(type(host.sessions).__module__)
  opening={'schema_version':'lab-agent-session-open/v1-candidate','request_ref':'request:all34-source8-open:'+uuid.uuid4().hex,'actor':host.sessions.bridge.actor(),'assignment':ref(D.records.ASSIGNMENT),'profile':ref(D.records.PROFILE),'implementation':ref(D.records.IMPLEMENTATION),'capabilities':[ref(D.records.CAPABILITY)],'context_delivery_binding':P.binding('context-delivery:'+result_message(delivery,'context.get')['context_view']['version_ref'],P.compact(result_message(delivery,'context.get'))),'authority_envelope_binding':runtime.stable_policy(host.channel),'source_cut':selected.source_cut,'budget':budget,'memory_policy':{'persistence_allowed':False,'expires_with_session':True},'authority_effect':'none'}
  opened=pair(host,provider.call(mods,host,'session.open',opening,key='all34:source8-open'),root,surface);opened_message=result_message(opened,'session.open');sid=opened_message['session_ref'];resource=host.sessions.live[sid]
  from cryptography.exceptions import InvalidSignature
  scope_kernel=runtime.D.FACT_SCOPE;callbacks=(selected.guard,selected.sources.current_guard,D.verify_source,D.generate,host.channel.guard,host.channel.policy_guard,host.channel.termination_guard,scope_kernel.policy_scope,scope_kernel.parent_guard,scope_kernel.package_guard)
  machine=mods['machine_transport'].select(host,sid,bind(API/'source-manifest.json'));stack.callback(machine.close);proof=machine.proof()
  require(scope_kernel.active_scope() is None,'failed-auth setup retained source scope');original_policy=path.read_bytes();reason=UNIT.split(':',1)[1]
  try:
   if reason=='Source8-failed-signature':
    malformed=P.frame_parse(proof);signature=bytearray(base64.b64decode(malformed['signature'],validate=True));signature[0]^=1;malformed['signature']=base64.b64encode(signature).decode();wire=P.compact(malformed)
   elif reason=='Source8-real-revocation':
    revoked=P.frame_parse(original_policy);revoked['revoked']=True;path.write_bytes(P.compact(revoked));wire=proof
   else:raise ValueError('undeclared failed-auth case')
   before=snapshot(root);started=A.now()
   try:machine.authenticate(wire)
   except BaseException as error:
    if reason=='Source8-failed-signature':require(type(error) is InvalidSignature,'signature case did not reach actual original cryptographic verifier')
    else:require(isinstance(error,ValueError) and 'reader policy revoked or changed' in str(error),'actual owned grant-byte revocation did not reach original private policy guard')
    require(scope_kernel.active_scope() is None and machine.closed and machine._private_key is None and machine.context is None and machine.service is None,'failed auth retained scope/signer/context/service')
    require(snapshot(root)==before,'failed authentication wrote durable owned state')
    require((selected.guard,selected.sources.current_guard,D.verify_source,D.generate,host.channel.guard,host.channel.policy_guard,host.channel.termination_guard,scope_kernel.policy_scope,scope_kernel.parent_guard,scope_kernel.package_guard)==callbacks,'failed auth replaced original callback')
    event({'phase':'actual-failed-authentication-verified','case':reason,'error_type':type(error).__name__,'started_at':started.isoformat(),'ended_at':A.now().isoformat(),'source_scope_absent':True,'private_key_erased':True,'private_grant_or_key_exported':False,'original_callbacks_retained':True,'durable_state_unchanged':True})
   else:raise ValueError('invalid signature or actual revoked grant authenticated')
  finally:
   path.write_bytes(original_policy)
   require(scope_kernel.active_scope() is None,'failed-auth cleanup retained source scope')



def main():
 global EVENTS,CASES,FAILURES,ROOTS,NAME,P,G,schemas,A,F,H,S,I,W,M,EF,PR,CS,PLAN,UNIT,API
 parser=argparse.ArgumentParser()
 for key in ('source','profile','caller-sha256','plan-sha256','api-directory','plan','unit'):parser.add_argument('--'+key,required=True)
 args=parser.parse_args();UNIT=args.unit;API=Path(args.api_directory).resolve();require(API.is_relative_to(BASE),'explicit selected API directory required');plan_path=Path(args.plan).resolve();require(plan_path.is_relative_to(TASK),'owned exact plan required');output=TASK/'units';output.mkdir(exist_ok=True);name=UNIT.replace(':','--').replace('.','-');EVENTS=output/(name+'.events.jsonl');out=output/(name+'.json');are=None;CASES=[];FAILURES=[];ROOTS=set();entry_guard=False
 require(not EVENTS.exists() and not out.exists(),'new exclusive actual all34 evidence required');require(Path(__file__).resolve().is_relative_to(Path('/tmp/cal-runtime-completion-T04')),'actual untrusted external client origin required');require(Path(__file__).read_bytes()==RETAINED.read_bytes() and bind(RETAINED)['sha256']==args.caller_sha256 and bind(plan_path)['sha256']==args.plan_sha256,'retained/runtime exact independent caller and plan bytes required');plan=json.loads(plan_path.read_bytes());PLAN=plan;are=ROOT/plan['are_boundary_binding']['path'];require(bind(are)==plan['are_boundary_binding'],'exact new run ARE evidence binding differs');adapter_guard();retention_guard();require(plan['source_sha256']==args.source and plan['profile_sha256']==args.profile and plan['api_directory']==str(API.relative_to(ROOT)) and UNIT in plan['units'],'independent API/source/profile/unit selection required');require(json.loads(are.read_bytes())['authority_effect']=='none','ARE boundary grants no API authority')
 event({'phase':'starting','pid':os.getpid(),'runtime_caller_binding':bind(Path(__file__)),'retained_caller_binding':bind(RETAINED),'plan_binding':bind(plan_path),'source_sha256':args.source,'profile_sha256':args.profile,'unit':UNIT,'api_directory':str(API.relative_to(ROOT))});fd=os.open(RUN/'final-api-regression-0173-0190.execution.lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600);event({'phase':'waiting-real-SH0190-execution-lock'});fcntl.flock(fd,fcntl.LOCK_SH)
 try:
  NAME=install('_cal_selected_api_all34_0242',API);P=module(NAME,'protocol');G=module(NAME,'guard');G.verify(args.source);schemas=P.Schemas(args.profile);A=module(NAME,'auth');F=module(NAME,'fixtures');H=module(NAME,'handlers');S=module(NAME,'service');I=module(NAME,'integration_dispatch');W=module(NAME,'workspace');M=module(NAME,'artifact_model');EF=module(NAME,'example_fixture');PR=module(NAME,'projection_refresh');CS=module(NAME,'custody_context_sessions');require(set(plan['operations'])==set(schemas.operations) and len(schemas.operations)==34,'exact all34 plan/catalog required');[require(bind(ROOT/x['path'])==x,'independent fixture/provider input changed at full entry') for x in plan['provider_bindings']];entry_guard=True;event({'phase':'full-history-entry-guard-passed'})
  provider=base_episode if UNIT.startswith('base:') else fixtures_episode if UNIT.startswith(('fixture:','transfer:')) else {'member:action-governance':action_governance_episode,'member:resolution':resolution_episode,'member:workflow':workflow_episode,'member:ontology':ontology_episode,'member:Source8-lifecycle':source8_episode,'member:Source8-failed-signature':source8_failed_auth_episode,'member:Source8-real-revocation':source8_failed_auth_episode}[UNIT]
  event({'phase':'episode-starting','episode':UNIT})
  try:provider()
  except CallerBoundaryError as error:FAILURES.append({'episode':UNIT,'boundary':error.decision.record(),'operation':error.operation,'detail':str(error)});event({'phase':'episode-failed','episode':UNIT,**FAILURES[-1]})
  except Exception:FAILURES.append({'episode':UNIT,'detail':traceback.format_exc()});event({'phase':'episode-failed','episode':UNIT,'detail':FAILURES[-1]['detail']})
  event({'phase':'episode-terminal','episode':UNIT,'owned_fixture_roots_remaining':[str(x) for x in ROOTS if x.exists()]})
  G.verify(args.source);adapter_guard();retention_guard();require(bind(are)==plan['are_boundary_binding'],'ARE evidence drift');[require(bind(ROOT/x['path'])==x,'independent fixture/provider input changed at full exit') for x in plan['provider_bindings']];require(bind(RETAINED)['sha256']==args.caller_sha256 and Path(__file__).read_bytes()==RETAINED.read_bytes() and bind(plan_path)['sha256']==args.plan_sha256,'actual final caller/plan drift');exit_guard=True
 except Exception:FAILURES.append({'episode':'full-history-boundary','detail':traceback.format_exc()});exit_guard=False
 finally:fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
 coverage={op:{'positive':sum(x['operation']==op and x['expected_kind']=='result' and x['result']=='PASS' for x in CASES),'negative':sum(x['operation']==op and x['expected_kind']=='error' and x['result']=='PASS' for x in CASES)} for op in plan['units'][UNIT]['operations']};missing={op:x for op,x in coverage.items() if not(x['positive'] and x['negative'])};cleanup=all(not x.exists() for x in ROOTS);passed=entry_guard and exit_guard and cleanup and not missing and not FAILURES and all(x['result']=='PASS' for x in CASES)
 event({'phase':'terminal','result':'PASS' if passed else 'FAIL','actual_calls':len(CASES),'missing_operation_paths':missing,'full_history_exit_guard_passed':exit_guard,'owned_fixtures_removed':cleanup})
 value={'schema_version':'lab-same-producer-common-all-operation-wire-qualification/v1-candidate','result':'PASS' if passed else 'FAIL','source_sha256':args.source,'profile_sha256':args.profile,'unit':UNIT,'api_directory':str(API.relative_to(ROOT)),'unit_operations':plan['units'][UNIT]['operations'],'actual_calls':CASES,'coverage':coverage,'missing_operation_paths':missing,'failures':FAILURES,'source_guarded_entry_exit_completed':entry_guard and exit_guard,'owned_fixture_cleanup':[{'root':str(x),'removed':not x.exists()} for x in sorted(ROOTS)],'owned_fixture_removed':cleanup,'files':[bind(API/'source-manifest.json'),bind(API/'contract-profile.json'),bind(RETAINED),bind(TASK/'caller_adapter.py'),bind(plan_path)],'runtime_caller_binding':bind(Path(__file__)),'events_binding':bind(EVENTS),'are_boundary_binding':bind(are),'actual_all_calls_through_selected-API_common_dispatcher':True,'original345_regression_replaced':False,'original_clocks_or_callbacks_changed':False,'production_or_fixture_monkeypatches':False,'new_caller_owned_source8_lifecycle':True,'prior_API14_0250_diagnostic_qualification_transferred':False,'observed_Machine_setup_events_recorded':True,'private_keys_or_policy_exported':False,'actual_owner_outcome':None,'authority_effect':'none','unit_terminal_completed':True,'whole_API_qualified':False,'task_complete':False,'goal_complete':False,'claim_ceiling':'Only actual recorded same frozen selected-API common-dispatcher wire calls and causal refusals. Missing positive paths and genuine provider/origin/material failures stay failures. Original345, human pilot, R08 and whole Lab acceptance remain separate.'}
 with out.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
 print(json.dumps({'result':value['result'],'actual_calls':len(CASES),'missing':missing,'report_binding':bind(out)}),flush=True);return 0 if passed else 1

if __name__=="__main__":raise SystemExit(main())
