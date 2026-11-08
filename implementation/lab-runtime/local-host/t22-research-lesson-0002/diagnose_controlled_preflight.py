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

HERE=Path(__file__).resolve().parent
ROOT=Path(__file__).resolve().parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v73-t15-learning-selector-0001'
APPLICATION_METHOD=API.parent/'lesson-application-v7-t03-derived-effect-0001/preparation.py'
ASSESSMENT_METHOD=API.parent/'lesson-assessment-v4-t03-independent-effect-0001/preparation.py'
ASSESSOR='principal:T03-independent-assessor'


def require(value,reason):
    if not value:raise ValueError(reason)


def execute(stack,M,D,H,selected,parent,selection,provider,margin,control,stage,call):
    P=M['protocol'];A=M['auth'];F=M['fixtures'];view=selected.view
    sid=selection['session_ref'];resource=parent.sessions.live[sid]
    item=next(item for item in selection['items'] if item['posture']=='selected')
    lesson=item['lesson'];applicability=item['applicability_check_binding']
    producer=importlib.import_module(M['service'].__package__+'.later_lesson_inspection')
    report,counterevidence=stage('lesson-influenced-inspection',lambda:producer.execute(P,parent,selection,episode_pin='a3aac58fe32f2921a014a15fca95549f96bc0d2ad269021cea23925e1e5c08ea'))
    inspection_binding=P.binding('fixture:t03-live-inspection-output',P.compact(report))
    counter_binding=P.binding('fixture:t03-live-inspection-counterevidence',P.compact(counterevidence))
    # Retain bounded public output bodies for independent cold readback. These
    # contain source pins/discrepancies, no private Session memory or grant.
    for leaf,value in (('controlled-inspection-output.json',report),
                       ('controlled-inspection-counterevidence.json',counterevidence)):
        raw=P.compact(value)
        descriptor=os.open(HERE/leaf,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(descriptor,'wb') as output:
            output.write(raw);output.flush();os.fsync(output.fileno())

    selection_binding=parent.vault.object(P.compact(selection))
    instruction=selection['instruction_precedence_binding']
    root=Path(stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-T03-later-application-')))
    root.chmod(0o700)
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
        'action_bound_refs':[],'override_bindings':[],
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
    application_margin=stage('application-margin-binding',lambda:margin.compose(M['service'].__package__,
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
    import traceback
    baseline_journal={p.name:P.source.sha(p.read_bytes()) for p in (application.vault.root/'journal').iterdir() if p.is_file()}
    try:
        stage('original-application-selector',lambda:application.select_application(message,selected.source_cut,operation_key))
        OM=importlib.import_module(M['service'].__package__+'.observed_margin')
        wire=provider.call(M,application,'lesson.apply',message,key=operation_key)
        context=application.channel.guard();deadline=min(A.instant(wire['deadline']),A.instant(context['limits']['deadline']))
        def observe():
            with application.vault.lock():return OM.before_claim(application.vault,wire,context,deadline)
        stage('original-pure-before-claim',observe)
        result={'result':'PASS-original-selector-and-pure-margin','durable_claim':False}
    except Exception as error:
        trace=traceback.format_exc();path=HERE/'controlled-preflight-trace.log'
        descriptor=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(descriptor,'w') as output:output.write(trace)
        result={'result':'REFUSED-original-pure-preflight','exception_class':type(error).__name__,'message':str(error)[:500],'trace_path':str(path.relative_to(ROOT)),'durable_claim':False}
    after={p.name:P.source.sha(p.read_bytes()) for p in (application.vault.root/'journal').iterdir() if p.is_file()}
    require(after==baseline_journal,'pure diagnostic allocated an operation journal')
    application.close()
    return result
