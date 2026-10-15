"""Independent owned fixture helpers for the actual common operator.

Construction declares fixture inputs; every operation still uses the selected
real Service, nonce channel, current signed source and actual live resource.
"""
import base64,copy,importlib,json,os,uuid
from datetime import timedelta
from pathlib import Path

def modules(package):
    return {n:importlib.import_module(package+'.'+n) for n in ('protocol','auth','fixtures','service','handlers','machine_transport')}

def lesson_materials(M,D,selected):
    P=M['protocol'];R=D.records;ref=lambda i:copy.deepcopy(selected.sources.resolve(i+'@'+R.VERSION)[0].artifact)
    mats={};put=lambda label,value:(mats.__setitem__(label,P.compact(value)) or P.binding(label,mats[label]))
    code=D.HERE/'implementation-binding.json';mats[str(code.relative_to(P.ROOT))]=code.read_bytes()
    source_binding=P.binding(str(code.relative_to(P.ROOT)),code.read_bytes())
    instruction={'schema_version':'lab-lesson-instruction-policy/v1-candidate','source_cut':selected.source_cut,
        'assignment':ref(R.ASSIGNMENT),'work':ref(R.WORK),'coordination_context':ref(R.COORDINATION),
        'instruction_refs':['instruction:controlled-Source8-fixture-read'],'tags':[],
        'veto_lesson_influence':False,'authority_effect':'none','actual_owner_outcome':None}
    instructions=put('fixture:lesson-instructions',instruction)
    lessons=sorted([s for s in selected.view.subjects.values() if s['kind']=='operational-lesson'
                    and s['effective_state'] in D.reader.adapter.CURRENT],key=lambda s:s['version_ref'])
    declared_path=D.reader.HERE/'packages/0001/fixture-applicability.json'
    declaration=P.source.parse(declared_path.read_bytes()) if declared_path.exists() else None
    family=D.HERE.name
    if declaration is not None:
        P.source.require(declaration['required_generator_ref']==str((D.HERE/'build.py').relative_to(P.ROOT))+'#generate'
                         and declaration['required_scope_ref']==selected.sources.scope_ref,'actual fixture generator/scope differs')
        family=selected.view.subjects[declaration['lesson']]['record']['payload']['applicability']
    rows=[]
    for s in lessons:
        body=s['record'];payload=body['payload'];artifact=D.reader.adapter.model.artifact_ref(selected.view,s)
        is_fixture=declaration is not None and declaration['lesson']==s['version_ref']
        review=None;rule=None;retention=None
        if is_fixture:
            # Independently selected controlled declaration, with no human claim.
            original=P.source.parse((D.reader.HERE/'packages/0001/fixture-runtime-review.json').read_bytes())
            P.source.require(original['lesson']==s['version_ref'] and original['fixture_only'] is True
                             and original['actual_human_review'] is False,'controlled fixture review differs')
            review=put('fixture:lesson-review',{'lesson':artifact,'source_cut':selected.source_cut,
                'domain_scope_ref':body['scope_ref'],'disposition':original['disposition'],
                'effective_state':s['effective_state'],'fixture_only':True,'authority_effect':'none'})
            retention=put('fixture:lesson-retention',{'policy_ref':payload['retention_policy_ref'],
                'retain_project_evidence':True,'exclude_session_memory':True,'authority_effect':'none'})
            rule=put('fixture:lesson-applicability',{'schema_version':'lab-lesson-applicability/v1-candidate',
                'lesson':artifact,'source_cut':selected.source_cut,'project_ref':selected.sources.scope_ref,
                'family':family,'source_binding':source_binding,'required_instruction_refs':instruction['instruction_refs'],
                'excluded_tags':[],'influence_ref':'fixture:scoped-Source8-context-use','counterevidence':[],'authority_effect':'none'})
        excluded=[]
        for index,text in enumerate(payload['exclusions']):
            verdict=False if is_fixture else True if text=='another generator or scope version' else None
            assessment=None if verdict is None else put('fixture:exclusion:'+s['identity']+':'+str(index),
                {'lesson':artifact,'source_cut':selected.source_cut,'exclusion_text':text,'excluded':verdict,'authority_effect':'none'})
            excluded.append({'text':text,'excluded':verdict,'assessment_binding':assessment})
        rows.append({'lesson':artifact,'review_binding':review,'review_disposition':None if review is None else original['disposition'],
            'fixture_only':None if review is None else True,'applicability_rule_binding':rule,'retention_binding':retention,'exclusions':excluded})
    plan={'schema_version':'lab-lesson-host-plan/v1-candidate','source_cut':selected.source_cut,
        'assignment':ref(R.ASSIGNMENT),'work':ref(R.WORK),'coordination_context':ref(R.COORDINATION),'profile':ref(R.PROFILE),
        'project_ref':selected.sources.scope_ref,'family':family,'source_binding':source_binding,'instruction_policy_binding':instructions,
        'domain_profile':{'supported_lesson_statuses':sorted(set(s['record']['payload']['status'] for s in lessons)),
            'supported_retention_policy_refs':sorted(set(s['record']['payload']['retention_policy_ref'] for s in lessons)),
            'reviewed_use_postures':[{'disposition':'reviewed-for-controlled-use','effective_state':'local-admitted-current','fixture_only':True}]},
        'lessons':rows,'authority_effect':'none','actual_owner_outcome':None}
    put('fixture:lesson-plan',plan);return mats,plan

def provision(M,root,D,selected,source_name,materials,*,kind='lab-local-lesson-read-policy/v1-candidate',metadata=None):
    P=M['protocol'];F=M['fixtures'];A=M['auth']
    key,path,_=F.provision(root,materials=materials,target_metadata=metadata,principal=D.records.PRINCIPAL)
    policy=P.frame_parse(path.read_bytes());period=D.load(D.reader.HERE/'packages/0001/period.json')
    P.source.require(A.instant(period['not_before'])<=A.now()<A.instant(period['expires_at']),'actual Source8 period is not current')
    policy.update(schema_version=kind,source_name=source_name,principal_ref=D.records.PRINCIPAL,
        expires_at=min(A.now()+timedelta(minutes=30),A.instant(period['expires_at'])).isoformat(),
        max_request_bytes=1048576,max_response_bytes=4194304,
        source8_control={**P.source.source8_bindings(source_name),'application_journal_scope':None},
        session_control={'period_binding':P.source.source8_bindings(source_name)['period_binding'],'max_session_seconds':900})
    authority=P.ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
    policy['development_authorization_binding']=P.binding(str(authority.relative_to(P.ROOT)),authority.read_bytes())
    if kind=='lab-local-lesson-read-policy/v1-candidate':
        policy['allowed_operations']=list(P.LESSON_SUPPORTED)
        policy['lesson_control']={'plan_binding':P.binding('fixture:lesson-plan',materials['fixture:lesson-plan'])}
    elif kind=='lab-local-lesson-application-policy/v2-candidate':
        policy['allowed_operations']=list(P.APPLICATION_SESSION_SUPPORTED)
        policy['purpose']='current-participation-and-exact-lesson-application'
        policy['application_control']=None
    elif kind=='lab-local-lesson-assessment-policy/v1-candidate':
        policy['allowed_operations']=list(P.ASSESSMENT_SUPPORTED)
        policy['purpose']='durable-metadata-and-exact-lesson-assessment'
        policy['session_control']=None;policy['scope_control']=None;policy['assessment_control']=None
    path.write_bytes(P.compact(policy));return key,path,P.source.sha(path.read_bytes())

def call(M,service,operation,message,*,key=None,seconds=900):
    P=M['protocol'];A=M['auth'];deadline=(A.now()+timedelta(seconds=seconds)).isoformat()
    value={'schema_version':'lab-api-call/v2-candidate','expected_contract_profile_binding':service.schemas.profile_binding,
        'call_id':'call:Source8:'+uuid.uuid4().hex,'operation':operation,'caller_context_ref':service.channel.context['context_ref'],
        'expected_source_cut':M['handlers'].cut(service.handlers.view),'deadline':deadline,'max_response_bytes':4194304,
        'idempotency_key':key,'message':copy.deepcopy(message)}
    if 'budget' in value['message']:value['message']['budget'].update(deadline=deadline,max_input_bytes=1048576,max_output_bytes=4194304)
    return value

def opening(M,service,D,dispatcher=None):
    P=M['protocol'];selected=service.handlers.view.custody_signed_sources
    dispatcher=service if dispatcher is None else dispatcher
    message=D.query(selected,service.sessions.bridge)
    response=dispatcher.call(P.compact(call(M,service,'context.get',message)))
    P.source.require(response.get('kind')=='result','actual fresh Context generation did not succeed')
    delivery=response['message'];ref=lambda i:copy.deepcopy(selected.sources.resolve(i+'@'+D.records.VERSION)[0].artifact)
    budget=copy.deepcopy(message['budget']);budget['max_actions']=1
    runtime=importlib.import_module(type(service.sessions).__module__)
    message={'schema_version':'lab-agent-session-open/v1-candidate','request_ref':'request:Source8-open:'+uuid.uuid4().hex,
        'actor':service.sessions.bridge.actor(),'assignment':ref(D.records.ASSIGNMENT),'profile':ref(D.records.PROFILE),
        'implementation':ref(D.records.IMPLEMENTATION),'capabilities':[ref(D.records.CAPABILITY)],
        'context_delivery_binding':P.binding('context-delivery:'+delivery['context_view']['version_ref'],P.compact(delivery)),
        'authority_envelope_binding':runtime.stable_policy(service.channel),'source_cut':selected.source_cut,'budget':budget,
        'memory_policy':{'persistence_allowed':False,'expires_with_session':True},'authority_effect':'none'}
    raw=P.compact(call(M,service,'session.open',message,key='Source8:open:'+uuid.uuid4().hex))
    opened=dispatcher.call(raw);P.source.require(opened.get('kind')=='result','actual Source8 Session opening did not succeed')
    return response,opened,raw

def candidate_materials(M,view,body,label):
    P=M['protocol'];carrier='cal.artifact-type.'+body['kind']+'/v1';identity=body['node_id'];version=identity+'@controlled-candidate.1'
    raw=(json.dumps(body,indent=3,ensure_ascii=False)+'\n').encode()
    target={'category':'artifact-instance','operation':'admit','version_ref':version,'carrier_ref':carrier,
        'record':body,'predecessor_ref':None,'decision_ref':'decision:'+label,'contract':None,
        'content':view.handle.custody.content_entry(raw)}
    core={'decision_ref':target['decision_ref'],'category':'artifact-instance','operation':'admit',
        'version_ref':version,'target_digest':view.handle.common.digest(target)}
    meta={'schema_version':'lab-candidate-target-metadata/v1-candidate','category':'artifact-instance',
        'decision_ref':target['decision_ref'],'contract':None}
    mats={label+':body':raw,label+':core':view.handle.common.encoded(core),label+':metadata':P.source.encoded(meta)}
    contract=view.data['projection']['contracts'][carrier]
    header={'scope_ref':body['scope_ref'],'identity_ref':identity,'version_ref':version,'carrier_ref':carrier,
        'byte_sha256':P.source.sha(raw),'candidate_contract_binding':{'ref':contract['schema_path'],'sha256':contract['schema_sha256']}}
    api_target={'operation':'admit','artifact':header,'predecessor':None,
        'content':{'content_ref':label+':body','byte_sha256':P.source.sha(raw),'size_bytes':len(raw),'media_type':'application/json'},
        'candidate_binding':P.binding(label+':metadata',mats[label+':metadata']),
        'requested_effect':'Prepare one scoped unadmitted '+body['kind']+' candidate only',
        'decision_core_binding':P.binding(label+':core',mats[label+':core'])}
    return mats,{version:api_target['candidate_binding']},api_target

def proposal(M,service,target,key):
    P=M['protocol'];view=service.handlers.view;ctx=service.channel.context
    actor={k:ctx[k] for k in ('principal_ref','agent_instance_ref','session_ref','assignment_ref')};actor['role_assignment_refs']=ctx['role_assignment_bindings']
    return {'schema_version':'lab-change-proposal/v1-candidate','proposal_ref':'proposal:Source8:'+uuid.uuid4().hex,
        'actor':actor,'scope_ref':view.data['config']['scope_ref'],'base_cut':M['handlers'].cut(view),
        'source_profile_binding':{'ref':view.handle.manifest['profile_binding']['path'],'sha256':view.handle.manifest['profile_binding']['sha256']},
        'workspace_binding':service.vault.control_binding,'targets':[target],'schema_bindings':[],
        'connection_proposals':[],'evidence_bindings':[],'idempotency_key':key,
        'challenge_route':view.data['config']['challenge_route'],'authority_effect':'none'}

def proposal_before_auth(M,view,policy,target,key):
    P=M['protocol'];manifest=P.source.parse((Path(policy['workspace']['root'])/'workspace.json').read_bytes())
    actor={'principal_ref':policy['principal_ref'],'role_assignment_refs':[],
           'agent_instance_ref':None,'session_ref':None,'assignment_ref':None}
    return {'schema_version':'lab-change-proposal/v1-candidate','proposal_ref':'proposal:Source8:'+uuid.uuid4().hex,
        'actor':actor,'scope_ref':view.data['config']['scope_ref'],'base_cut':M['handlers'].cut(view),
        'source_profile_binding':{'ref':view.handle.manifest['profile_binding']['path'],'sha256':view.handle.manifest['profile_binding']['sha256']},
        'workspace_binding':{'ref':'workspace:'+manifest['workspace_ref'],'sha256':policy['workspace']['manifest_sha256']},
        'targets':[target],'schema_bindings':[],'connection_proposals':[],'evidence_bindings':[],
        'idempotency_key':key,'challenge_route':view.data['config']['challenge_route'],'authority_effect':'none'}

def object_before_auth(M,root,policy,raw):
    """Owned input provisioning before its private immutable grant is selected."""
    P=M['protocol'];workspace=Path(policy['workspace']['root']);manifest=P.source.parse((workspace/'workspace.json').read_bytes())
    sha=P.source.sha(raw);path=workspace/'objects'/(sha+'.json')
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as f:f.write(raw)
    return {'ref':'workspace-object:'+manifest['workspace_ref']+':'+sha,'sha256':sha}
