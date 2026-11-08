"""Actual current-legacy one-Lesson application and outcome recording.

This is fixture-only later use of the Lesson selected in an earlier closed
Session. The Application and Assessment remain unadmitted candidates.
"""
import copy
import json
import os
import importlib
import sys
from pathlib import Path
import tempfile
import uuid

ASSESSOR='principal:T03-independent-assessor'


def require(value,reason):
    if not value:raise ValueError(reason)


def execute(stack,M,D,H,selected,parent,selection,provider,margin,control,stage,call,*,runtime,first_receipt):
    P=M['protocol'];A=M['auth'];F=M['fixtures'];view=selected.view
    ROOT=runtime.root;API=runtime.api;HERE=runtime.evidence
    APPLICATION_METHOD=ROOT/'product/lab/release-candidates/v1/interface/lesson-application-v8-t03-scope-custody-0001/preparation.py'
    ASSESSMENT_METHOD=ROOT/'product/lab/release-candidates/v1/interface/lesson-assessment-v4-t03-independent-effect-0001/preparation.py'
    episode_path='implementation/lab-runtime/local-host/t22-api30-episode-inspection-0002/episode.py'
    episode_rows=[row for row in runtime.provider.current().package['members'] if row['path']==episode_path]
    require(len(episode_rows)==1,'unique independently packaged inspection producer required')
    sid=selection['session_ref'];resource=parent.sessions.live[sid]
    item=next(item for item in selection['items'] if item['posture']=='selected')
    lesson=item['lesson'];applicability=item['applicability_check_binding']
    subject=parent.handlers.resolve_exact(lesson)
    model=importlib.import_module(M['service'].__package__+'.artifact_model')
    lesson_raw=model.record_bytes(view,subject)[0]
    require(P.source.sha(lesson_raw)==lesson['byte_sha256'],'actual selected Lesson original differs')
    from_runtime_write=os.open(HERE/'source-Lesson-original.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(from_runtime_write,'wb') as output:output.write(lesson_raw);output.flush();os.fsync(output.fileno())
    producer=importlib.import_module(M['service'].__package__+'.later_lesson_inspection')
    report,counterevidence=stage('lesson-influenced-inspection',lambda:producer.execute(P,parent,selection,episode_pin=episode_rows[0]['sha256']))
    inspection_binding=P.binding('fixture:t03-live-inspection-output',P.compact(report))
    counter_binding=P.binding('fixture:t03-live-inspection-counterevidence',P.compact(counterevidence))
    # Retain bounded public output bodies for independent cold readback. These
    # contain source pins/discrepancies, no private Session memory or grant.
    for leaf,value in (('later-inspection-output.json',report),
                       ('later-inspection-counterevidence.json',counterevidence)):
        raw=P.compact(value)
        descriptor=os.open(HERE/leaf,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(descriptor,'wb') as output:
            output.write(raw);output.flush();os.fsync(output.fileno())

    selection_binding=parent.vault.object(P.compact(selection))
    instruction=selection['instruction_precedence_binding']
    root=runtime.workspace('application')
    body=P.source.parse((ROOT/'authority/artifact-types/lesson-application/v1/fixtures/valid/record.json').read_bytes())
    body.update(node_id='lesson-application:T03-'+uuid.uuid4().hex,owner_ref=D.records.PRINCIPAL,
        scope_ref=selected.sources.scope_ref,evidence_refs=[lesson['version_ref']],
        claim_ceiling='Controlled local fixture application candidate; no Tool dispatch or effectiveness claim.')
    body['payload'].update(lesson_revision_ref=lesson['version_ref'],session_ref=sid,
        applicability_assessment_ref=applicability['ref'],
        intended_influence='Use the reviewed one-Lesson fixture during an API30 bounded Project State inspection.',
        conflict_refs=[],override_refs=[],application_posture='candidate-attributed-no-tool-dispatch')
    body['relation_refs']=[{'relation_kind_ref':'relation.applies-lesson','direction':'source',
        'counterpart_kind':'operational-lesson','counterpart_ref':lesson['version_ref']}]
    materials,metadata,target=provider.candidate_materials(M,view,body,'fixture:t03-application')
    descriptor=os.open(HERE/'application-candidate-original.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(descriptor,'wb') as output:output.write(materials['fixture:t03-application:body']);output.flush();os.fsync(output.fileno())
    key,path,_=provider.provision(M,root,D,selected,P.source.CURRENT_LEGACY_NAME,materials,
        kind='lab-local-lesson-application-policy/v2-candidate',metadata=metadata)
    policy=P.frame_parse(path.read_bytes());operation_key='T03:actual-later-application:'+uuid.uuid4().hex
    proposal=provider.proposal_before_auth(M,view,policy,target,operation_key)
    proposal_binding=provider.object_before_auth(M,root,policy,P.compact(proposal))
    method_binding=P.binding(str(APPLICATION_METHOD.relative_to(ROOT)),APPLICATION_METHOD.read_bytes())
    routing={'schema_version':'lab-lesson-application-routing/v1-candidate','source_cut':selected.source_cut,
        'scope_ref':selected.sources.scope_ref,'proposal_binding':proposal_binding,'method_binding':method_binding,
        'selection_binding':selection_binding,'applicability_binding':applicability,
        'instruction_precedence_binding':instruction,'intended_influence':body['payload']['intended_influence'],
        'action_bound_refs':['context.get'],'override_bindings':[],
        'authorization_basis_binding':policy['development_authorization_binding'],
        'authority_effect':'none','actual_owner_outcome':None}
    routing_binding=provider.object_before_auth(M,root,policy,P.compact(routing))
    policy['application_control']={'routing_binding':routing_binding,'method_binding':method_binding,
        'runtime_identities':{'session_ref':sid,'agent_instance_ref':resource.agent['node_id']}}
    path.write_bytes(P.compact(policy));pin=P.source.sha(path.read_bytes())
    channel=stage('application-channel',lambda:A.ReaderChannel(path,pin,parent.schemas));stack.callback(channel.close)
    stage('application-authenticate',lambda:channel.authenticate(F.proof(key,channel.challenge)))
    manifest=P.source.parse((root/'workspace/workspace.json').read_bytes());row=parent.sessions.selected(sid)
    attachment={'schema_version':'lab-private-Source8-Session-attachment/v1-candidate',
        'parent_source_binding':{'path':str((API/'source-manifest.json').relative_to(ROOT)),
                             'sha256':P.source.sha((API/'source-manifest.json').read_bytes())},
        'session_ref':sid,'agent_instance_ref':resource.agent['node_id'],'assignment':row['assignment'],
        'session_state_binding':row['session_state_binding'],'source_cut':selected.source_cut,
        'principal_ref':D.records.PRINCIPAL,'parent_policy_sha256':parent.channel.expected_sha,
        'operator_policy_sha256':pin,'parent_workspace_binding':parent.vault.control_binding,
        'operator_workspace_binding':{'ref':'workspace:'+manifest['workspace_ref'],
            'sha256':policy['workspace']['manifest_sha256']},
        'selection_binding':selection_binding,'applicability_binding':applicability,
        'instruction_precedence_binding':instruction,'authority_effect':'none'}
    application=stage('application-Service',lambda:M['service'].Service(view,channel,parent.schemas,
        parent_host=parent,session_attachment_binding=attachment));stack.callback(application.close)
    application_margin=stage('application-margin-binding',lambda:margin.compose(runtime,
        application,parent,attachment,control));stack.callback(application_margin.close)
    actor={k:channel.context[k] for k in ('principal_ref','agent_instance_ref','session_ref','assignment_ref')}
    actor['role_assignment_refs']=[]
    message={'schema_version':'lab-lesson-application-request/v1-candidate',
        'request_ref':'request:T03-later-application:'+uuid.uuid4().hex,'actor':actor,
        'source_cut':selected.source_cut,'lesson':lesson,'session_ref':sid,
        'selection_binding':selection_binding,'applicability_binding':applicability,
        'conflict_refs':[],'override_basis':[],
        'application_candidate_binding':P.binding('fixture:t03-application:body',materials['fixture:t03-application:body']),
        'authority_effect':'none'}
    # Observe the original pure margin/derived-boundary functions directly.
    # No journal allocation, claim, callback substitution or API change occurs.
    def margin_diagnostic():
        runtime=application.vault.observed_margin_runtime
        observed_module=importlib.import_module(M['service'].__package__+'.observed_margin')
        guarded=importlib.import_module(M['service'].__package__+'.guarded_candidate')
        effects=importlib.import_module(M['service'].__package__+'.derived_effects')
        diagnostic_call=provider.call(M,application,'lesson.apply',message,key=operation_key)
        context=channel.guard()
        deadline=min(A.instant(diagnostic_call['deadline']),A.instant(context['limits']['deadline']))
        with guarded.selection(application):
            bounds,cut=observed_module.observed(runtime,diagnostic_call,context,deadline,runtime.selection())
            write_guard=effects.selected_effect_guard(application,runtime.selection(),deadline=deadline)
        if write_guard is not None:write_guard()
        require(list((application.vault.root/'journal').glob('*'))==[], 'pure margin diagnostic wrote operation journal')
        return {'actual_pure_margin_and_effect_guard':True,'journal_entries':0,'direct_bounds':bounds}
    try:
        app_reply=stage('lesson.apply',lambda:call(application,'lesson.apply',message,operation_key))
    except BaseException:
        runtime.inspect_operation(application,'lesson.apply',operation_key,'failed-application')
        # Preserve an exact original pure inner diagnostic if the public
        # Service refusal hides a remaining preclaim integrity cause.
        try:
            stage('direct-original-margin-and-effect-preflight',margin_diagnostic)
        except BaseException:
            import traceback
            raw=traceback.format_exc().encode()
            descriptor=os.open(HERE/'later-direct-margin-trace.log',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
            with os.fdopen(descriptor,'wb') as output:output.write(raw);output.flush();os.fsync(output.fileno())
        raise
    app_result=P.source.sha(P.compact(app_reply))
    lookup=F.call(channel.context,'operation.inspect',None,
        lookup={'operation':'lesson.apply','idempotency_key':operation_key})
    inspected=stage('application.inspect',lambda:runtime.inspect_operation(application,'lesson.apply',operation_key,'completed-application'))
    require(inspected.get('kind')=='result','completed application inspection refused')
    inspected_result=P.source.sha(P.compact(inspected['message']))
    evidence={'schema_version':'lab-controlled-application-observation/v1-candidate',
        'source_cut':selected.source_cut,'application_result_sha256':app_result,
        'inspection_result_sha256':inspected_result,'completed_claim_count':len(list((application.vault.root/'journal').glob('*.claim.json'))),
        'inspection_output_binding':inspection_binding,'earlier_closed_session_receipt_sha256':P.source.sha(Path(first_receipt).read_bytes()),'Tool_dispatches':0,'canonical_admission':False,'authority_effect':'none','actual_owner_outcome':None}
    app_header={k:target['artifact'][k] for k in ('scope_ref','identity_ref','version_ref','carrier_ref','byte_sha256')}
    inspection={'schema_version':'lab-session-inspect-request/v1-candidate',
        'request_ref':'request:T03-close-before-assessment-inspect:'+uuid.uuid4().hex,
        'actor':parent.sessions.bridge.actor(),'session_ref':sid,
        'budget':{'max_input_bytes':1048576,'max_output_bytes':4194304,'max_actions':0,
                  'deadline':(M['auth'].now()+__import__('datetime').timedelta(seconds=3600)).isoformat()},
        'authority_effect':'none'}
    inspected_parent=stage('parent.inspect-before-assessment',lambda:call(parent,'session.inspect',inspection))
    closing={'schema_version':'lab-agent-session-close/v1-candidate',
        'request_ref':'request:T03-close-before-assessment:'+uuid.uuid4().hex,
        'session_ref':sid,'agent_instance_ref':resource.agent['node_id'],
        'expected_session_binding':inspected_parent['last_receipt_binding'],
        'requested_at':M['auth'].now().isoformat(),'reason':'completed',
        'eligible_audit_bindings':[],'authority_effect':'none'}
    closed_parent=stage('parent.close-before-assessment',lambda:call(parent,'session.close',closing,'T03:close-before-assessment:'+uuid.uuid4().hex))
    require(resource.closed and resource.memory==[] and resource.lesson_selections=={}
            and closed_parent['discarded_memory'] is True,'actual parent memory/registry survives close')
    application.close()
    assess_root=runtime.workspace('assessment')
    selected_assessment=runtime.load('current_lesson_assessment').selected
    ceiling=selected_assessment.CEILING
    eb=P.binding('fixture:t03-observed-application',P.compact(evidence))
    predicted='Consume an exact source-pinned API30 discrepancy report in the current Lesson Session.'
    observed='Native Session consumed inspection report '+inspection_binding['sha256']+' with '+str(len(report['observed_discrepancies']))+' source-selection discrepancies; authenticated application candidate and inspection returned.'
    assessment=P.source.parse((ROOT/'authority/artifact-types/lesson-outcome-assessment/v1/fixtures/valid/record.json').read_bytes())
    assessment.update(node_id='lesson-outcome-assessment:T03-'+uuid.uuid4().hex,owner_ref=ASSESSOR,
        scope_ref=selected.sources.scope_ref,evidence_refs=[eb['ref']],claim_ceiling=ceiling)
    assessment['payload'].update(lesson_application_ref=app_header['version_ref'],
        predicted_outcome=predicted,observed_outcome=observed,disposition='recorded-outcome-only',
        evidence_refs=[eb['ref'],inspection_binding['ref']],counterevidence_refs=[counter_binding['ref']],causal_claim_ceiling=ceiling)
    assessment['relation_refs']=[{'relation_kind_ref':'relation.derives-from','direction':'source',
        'counterpart_kind':'lesson-application','counterpart_ref':app_header['version_ref']}]
    mats,meta,ass_target=provider.candidate_materials(M,view,assessment,'fixture:t03-assessment')
    mats[eb['ref']]=P.compact(evidence)
    mats[inspection_binding['ref']]=P.compact(report)
    mats[counter_binding['ref']]=P.compact(counterevidence)
    observation={'schema_version':'lab-recorded-application-outcome/v1-candidate',
        'method_ref':selected_assessment.METHOD,'scope_ref':selected.sources.scope_ref,
        'source_cut':selected.source_cut,'application':app_header,'predicted_outcome':predicted,
        'observed_outcome':observed,'evidence_bindings':[eb,inspection_binding],'counterevidence_bindings':[counter_binding],
        'causal_claim_ceiling':ceiling,'authority_effect':'none'}
    mats['fixture:t03-outcome-observation']=P.compact(observation)
    assessment_key,assessment_path,_=provider.provision(M,assess_root,D,selected,P.source.CURRENT_LEGACY_NAME,mats,
        kind='lab-local-lesson-assessment-policy/v1-candidate',metadata=meta,principal=ASSESSOR)
    assess_policy=P.frame_parse(assessment_path.read_bytes())
    assess_operation_key='T03:actual-later-assessment:'+uuid.uuid4().hex
    assess_proposal=provider.proposal_before_auth(M,view,assess_policy,ass_target,assess_operation_key)
    assess_proposal_binding=provider.object_before_auth(M,assess_root,assess_policy,P.compact(assess_proposal))
    assess_method_binding=P.binding(str(ASSESSMENT_METHOD.relative_to(ROOT)),ASSESSMENT_METHOD.read_bytes())
    assess_route={'schema_version':'lab-lesson-assessment-routing/v1-candidate',
        'scope_ref':selected.sources.scope_ref,'source_cut':selected.source_cut,
        'proposal_binding':assess_proposal_binding,'method_binding':assess_method_binding,
        'observation_binding':P.binding('fixture:t03-outcome-observation',mats['fixture:t03-outcome-observation']),
        'authorization_basis_binding':assess_policy['development_authorization_binding'],
        'authority_effect':'none','actual_owner_outcome':None}
    assess_routing_binding=provider.object_before_auth(M,assess_root,assess_policy,P.compact(assess_route))
    assess_policy['assessment_control']={'routing_binding':assess_routing_binding,'method_binding':assess_method_binding}
    assess_policy['application_journal_scope']={'root':str(application.vault.root),
        'workspace_binding':application.vault.control_binding,
        'manifest_sha256':policy['workspace']['manifest_sha256']}
    assessment_path.write_bytes(P.compact(assess_policy));assessment_pin=P.source.sha(assessment_path.read_bytes())
    assessor_channel=stage('assessment-channel',lambda:A.ReaderChannel(assessment_path,assessment_pin,parent.schemas))
    stack.callback(assessor_channel.close)
    stage('assessment-authenticate',lambda:assessor_channel.authenticate(F.proof(assessment_key,assessor_channel.challenge)))
    assessor=stage('assessment-Service',lambda:M['service'].Service(view,assessor_channel,parent.schemas))
    stack.callback(assessor.close)
    assessment_attachment=None
    assessment_margin=stage('assessment-margin-binding',lambda:margin.compose(runtime,
        assessor,parent,assessment_attachment,control))
    stack.callback(assessment_margin.close)
    actor={k:assessor_channel.context[k] for k in ('principal_ref','agent_instance_ref','session_ref','assignment_ref')}
    actor['role_assignment_refs']=[]
    assess_message={'schema_version':'lab-lesson-assessment-request/v1-candidate',
        'request_ref':'request:T03-later-assessment:'+uuid.uuid4().hex,'actor':actor,
        'source_cut':selected.source_cut,'application':app_header,
        'assessment_candidate_binding':P.binding('fixture:t03-assessment:body',mats['fixture:t03-assessment:body']),
        'evidence_bindings':[eb,inspection_binding],'counterevidence_bindings':[counter_binding],
        'causal_claim_ceiling':ceiling,'authority_effect':'none'}
    try:
        assess_reply=stage('lesson.assess',lambda:call(assessor,'lesson.assess',assess_message,assess_operation_key))
    except BaseException:
        runtime.inspect_operation(assessor,'lesson.assess',assess_operation_key,'failed-assessment')
        raise
    runtime.inspect_operation(assessor,'lesson.assess',assess_operation_key,'completed-assessment')
    require(resource.closed and sid not in parent.sessions.live,
        'independent assessment borrowed or resurrected closed parent Session')
    for leaf,raw in (('later-assessment-candidate.json',mats['fixture:t03-assessment:body']),
                     ('later-assessment-result.json',P.compact(assess_reply)),
                     ('later-application-result.json',P.compact(app_reply))):
        descriptor=os.open(HERE/leaf,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(descriptor,'wb') as output:output.write(raw);output.flush();os.fsync(output.fileno())
    return {'parent_session_closed':True,'independent_assessment_after_parent_close':True,'assessment_candidate_sha256':P.source.sha(mats['fixture:t03-assessment:body']),'inspection_output_sha256':inspection_binding['sha256'],'counterevidence_sha256':counter_binding['sha256'],'actual_discrepancy_count':len(report['observed_discrepancies']),'application_reply_sha256':app_result,'application_inspection_sha256':inspected_result,
            'assessment_reply_sha256':P.source.sha(P.compact(assess_reply)),
            'fixture_only':True,'authority_effect':'none','actual_owner_outcome':None}
