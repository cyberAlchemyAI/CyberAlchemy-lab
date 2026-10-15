"""Actual common Source8 host proof; execution requires independently frozen pins."""
import argparse,copy,fcntl,hashlib,importlib,importlib.util,json,os,sys,tempfile,time,traceback
from contextlib import ExitStack
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v13'
RUNTIME=API.parent/'source8-session-runtime-v1-action-0148'

def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def bootstrap(name,path):
 spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
 module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)

def lifecycle(stack,H,M,D,selected,parent,selection,events,roots):
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
 call=H.call(M,application,'lesson.apply',message,key=operation_key);raw=P.compact(call);reply=app_api.call(raw)
 events.append({'operation':'lesson.apply','raw_sha256':P.source.sha(raw),'reply':reply});assert reply.get('kind')=='result',reply
 claims=len(list((application.vault.root/'journal').glob('*.claim.json')))
 retry_call=copy.deepcopy(call);retry_call['call_id']+='-retry';retry=app_api.call(P.compact(retry_call))
 assert retry.get('kind')=='result' and retry['message']==reply['message'];assert claims==len(list((application.vault.root/'journal').glob('*.claim.json')))
 events.append({'operation':'lesson.apply','case':'exact-retry','reply':retry})
 # Revocation changes only this independently owned private grant. The current
 # channel must reject the changed bytes before any additional journal claim.
 original_grant=path.read_bytes();revoked=copy.deepcopy(policy);revoked['allowed_operations']=[]
 try:
  path.write_bytes(P.compact(revoked))
  revoked_reply=app_api.call(raw)
  assert revoked_reply.get('schema_version')=='lab-api-transport-error/v1-candidate' and revoked_reply.get('code')=='unauthenticated-channel',revoked_reply
  assert claims==len(list((application.vault.root/'journal').glob('*.claim.json')))
  events.append({'operation':'lesson.apply','case':'actual-private-grant-byte-revocation','reply':revoked_reply})
 finally:path.write_bytes(original_grant)
 # Use the actual UTC clock for a separate expired request. This does not alter
 # the source period, Session lease, private grant or original operation clock.
 expired=copy.deepcopy(call);expired['call_id']+='-expired'
 from datetime import timedelta
 expired['deadline']=(A.now()-timedelta(seconds=1)).isoformat()
 expired_reply=app_api.call(P.compact(expired))
 assert expired_reply.get('kind')=='error' and expired_reply['message']['code']=='deadline-exceeded',expired_reply
 assert claims==len(list((application.vault.root/'journal').glob('*.claim.json')))
 events.append({'operation':'lesson.apply','case':'actual-expired-request','reply':expired_reply})
 lookup=M['fixtures'].call(channel.context,'operation.inspect',None,lookup={'operation':'lesson.apply','idempotency_key':operation_key})
 inspected=app_api.call(P.compact(lookup));events.append({'operation':'operation.inspect','reply':inspected});assert inspected.get('kind')=='result',inspected
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
 reply=assess_api.call(P.compact(H.call(M,assessor,'lesson.assess',msg,key=ass_key)))
 events.append({'operation':'lesson.assess','reply':reply});assert reply.get('kind')=='result',reply
 application.close();assert resource.closed is False and parent.sessions.live.get(sid) is resource
 return ['foreign-Session-attachment','actual-late-application-attachment','completed-application-exact-retry','actual-private-grant-byte-revocation','actual-expired-request','completed-application-inspection','actual-journal-candidate-assessment','attached-close-preserves-parent']

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--source-sha256',required=True);parser.add_argument('--profile-sha256',required=True)
 args=parser.parse_args();fd=os.open(RUN/'final-api-regression-0173-0190.execution.lock',os.O_RDONLY|os.O_NOFOLLOW)
 events=[];cases=[];roots=[];started=time.monotonic();full_exit=False
 report_path=RUN/'Source8-common-api13-action-0148.json'
 assert not report_path.exists(),'immutable existing report cannot be replaced'
 fcntl.flock(fd,fcntl.LOCK_SH)
 try:
  assert bind(API/'source-manifest.json')['sha256']==args.source_sha256
  assert bind(API/'contract-profile.json')['sha256']==args.profile_sha256
  name='_cal_Source8_common_API13_action_0148';bootstrap(name,API)
  G=importlib.import_module(name+'.guard');G.verify(args.source_sha256)
  pn='_cal_Source8_independent_provider_action_0148';bootstrap(pn,RUNTIME)
  H=importlib.import_module(pn+'.provider');M=H.modules(name);P=M['protocol'];schemas=P.Schemas(args.profile_sha256)
  for source_name in ('source8-session-participation','source8-lesson-fixture-participation'):
   with ExitStack() as stack:
    D=P.source.source8_delivery_for(source_name)
    selected=stack.enter_context(D.reader.open_signed(D.SOURCE_PIN,D.SOURCE_PACKAGE))
    view=selected.view;view.custody_signed_sources=selected;view.integrated_reader=D.reader;view.source8_context_producer=D
    materials,plan=H.lesson_materials(M,D,selected)
    root=Path(stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-Source8-common-action-0148-')));root.chmod(0o700);roots.append(str(root))
    key,policy,pin=H.provision(M,root,D,selected,source_name,materials)
    channel=M['auth'].ReaderChannel(policy,pin,schemas);channel.authenticate(M['fixtures'].proof(key,channel.challenge))
    service=M['service'].Service(view,channel,schemas);stack.callback(service.close)
    from_api=importlib.import_module(name+'.integration_dispatch').IntegrationService(service)
    # Parent native source remains the actual reader object; no mocked callback.
    delivery,opened,raw=H.opening(M,service,D,from_api)
    events.append({'operation':'context.get','source_name':source_name,'reply':delivery})
    events.append({'operation':'session.open','source_name':source_name,'raw_sha256':P.source.sha(raw),'reply':opened})
    sid=opened['message']['session_ref'];resource=service.sessions.live[sid]
    parent_binding=bind(API/'source-manifest.json');peer=M['machine_transport'].select(service,sid,parent_binding)
    stack.callback(peer.close);peer.authenticate(peer.proof())
    machine_api=importlib.import_module(name+'.integration_dispatch').IntegrationService(peer.service)
    query=D.query(selected,peer.service.sessions.bridge)
    call=H.call(M,peer.service,'lesson.select',query);wire=P.compact(call);reply=machine_api.call(wire)
    events.append({'operation':'lesson.select','source_name':source_name,'raw_sha256':P.source.sha(wire),'reply':reply})
    assert reply.get('kind')=='result',reply
    assert len(reply['message']['items'])==len(plan['lessons'])
    original=[item for item in reply['message']['items'] if item['lesson']['identity_ref']=='operational-lesson:R03-Machine-policy-custody']
    assert len(original)==1 and original[0]['posture']!='selected'
    assert peer.context['limits']['max_actions']==0 and peer.context['role_assignment_bindings']==[]
    if source_name=='source8-lesson-fixture-participation':
     assert len([item for item in reply['message']['items'] if item['posture']=='selected'])==1
     for case in lifecycle(stack,H,M,D,selected,service,reply['message'],events,roots):cases.append({'case':case,'result':'PASS'})
    cases.append({'case':source_name+':actual-context-session-machine-selection','result':'PASS'})
    # Original caller bytes are authenticated by the actual common dispatcher.
    denied=copy.deepcopy(call);denied['call_id']+='-foreign';denied['message']['actor']['principal_ref']='principal:foreign'
    refused=machine_api.call(P.compact(denied));assert refused.get('kind')=='error'
    events.append({'operation':'lesson.select','case':'foreign-Actor','reply':refused})
    cases.append({'case':source_name+':foreign-Actor','result':'PASS'})
    service.sessions.dispose_all();assert resource.closed and peer.closed and peer._private_key is None
    disposed=peer.call(wire);assert disposed['schema_version']=='lab-api-transport-error/v1-candidate'
    cases.append({'case':source_name+':actual-disposal','result':'PASS'})
    key=None
   assert not root.exists()
  success=True
 except BaseException as error:
  cases.append({'case':'qualification-completion','result':'FAIL','error_type':type(error).__name__,'message':str(error)[:1000]})
 finally:
  try:
   if 'G' in locals():G.verify(args.source_sha256);full_exit=True
  finally:
   report={'schema_version':'lab-actual-Source8-common-qualification/v1-candidate','result':'PASS' if locals().get('success',False) and full_exit and all(not Path(p).exists() for p in roots) else 'FAIL',
    'source_binding':bind(API/'source-manifest.json') if (API/'source-manifest.json').exists() else None,
    'expected_source_sha256':args.source_sha256,'expected_profile_sha256':args.profile_sha256,
    'qualification_driver_binding':bind(Path(__file__).resolve()),
    'independent_provider_source_binding':bind(RUNTIME/'source-manifest.json'),
    'cases':cases,'actual_case_count':len(cases),'actual_public_calls':len(events),
    'full_exit_guard':full_exit,'owned_roots_absent':all(not Path(p).exists() for p in roots),
    'duration_seconds':time.monotonic()-started,'fixture_only':True,'actual_owner_outcome':None,
    'canonical_admission':False,'actual_human_review':False,'whole_API_qualified':False,'task_complete':False}
   with report_path.open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
   event_path=RUN/'Source8-common-api13-action-0148.events.jsonl'
   with event_path.open('x') as f:
    for event in events:f.write(json.dumps(event,sort_keys=True)+'\n')
   fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
 print(json.dumps({'result':report['result'],'report_binding':bind(report_path)}),flush=True)
 return 0 if report['result']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
