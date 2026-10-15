"""Exact workflow transition planning, independent host authority, no admission.

Public message data cannot create the independent host grant or choose evidence
producers. A host adapter must verify these selected originals and authenticate
the actor before calling this pure kernel. Persistence and observed recovery are
separate operations; this function never labels a planned transition applied.
"""
import copy
from datetime import datetime,timezone
import hashlib
import json
import importlib.util
from pathlib import Path
from jsonschema import Draft202012Validator,FormatChecker

CURRENT=('admitted-current','local-admitted-current')
def require(value,reason):
    if not value:raise ValueError(reason)
def encoded(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def digest(value):return hashlib.sha256(encoded(value)).hexdigest()
def instant(value):
    result=datetime.fromisoformat(value.replace('Z','+00:00'));require(result.tzinfo is not None,'explicit workflow clock timezone required')
    return result.astimezone(timezone.utc)
def exact(binding,raw):
    require(type(raw) is bytes and hashlib.sha256(raw).hexdigest()==binding['sha256'],'original workflow material differs')
    return json.loads(raw)

def validate_shapes(message,definition,run,authority,satisfaction):
    root=Path(__file__).resolve().parents[6]
    path=root/'docs/proposals/0007-lab-integrated-schema-package/resources.py'
    spec=importlib.util.spec_from_file_location('_cal_workflow_original_resources_v1',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    registry=module.build_registry()
    for name,value in [('workflow-transition',message),('workflow-definition',definition),('workflow-run',run),
        ('authority-evaluation',authority),('validation-report',satisfaction)]:
        Draft202012Validator({'$ref':'urn:cyberalchemy-lab:protocol:'+name+':v1-candidate'},
            registry=registry,format_checker=FormatChecker()).validate(value)

def plan(message,*,definition_raw,run_raw,authority_raw,satisfaction_raw,host_grant,
         authenticated_actor,current_cut,selected_headers,selected_obligations,now):
    """Compute one candidate next run after independently bound obligations.

All keyword inputs are supplied by the independently selected host. Neither
authority_raw nor satisfaction_raw is accepted as a replacement for host_grant.
The host must guard/retrieve originals before and after this calculation.
"""
    fields={'schema_version','request_ref','run_binding','definition_binding','transition_ref','expected_state','actor',
        'input_artifacts','action_receipt_bindings','authority_evaluation_binding','satisfaction_report_binding','source_cut',
        'idempotency_key','authority_effect'}
    require(set(message)==fields and message['schema_version']=='lab-workflow-transition/v1-candidate'
        and message['authority_effect']=='none','closed workflow transition request required')
    grant_fields={'schema_version','principal_ref','actor_role_refs','scope_ref','source_cut','run_binding',
        'definition_binding','permitted_transitions','authority_evaluation_binding','satisfaction_report_binding',
        'action_receipt_bindings','obligation_bindings','not_before','expires_at','permitted_effects','authority_effect'}
    require(set(host_grant)==grant_fields and host_grant['schema_version']=='lab-independent-workflow-grant/v1-candidate'
        and host_grant['authority_effect']=='none','independently provisioned closed workflow grant required')
    require(type(now) is datetime and now.tzinfo is not None,'actual host clock required')
    require(instant(host_grant['not_before'])<=now<instant(host_grant['expires_at']),'workflow host grant outside actual period')
    require(host_grant['permitted_effects']==['candidate-workflow-transition'],'workflow grant cannot authorize admission or external effects')
    require(authenticated_actor==message['actor'] and authenticated_actor['principal_ref']==host_grant['principal_ref'],
        'workflow Actor differs from actual authenticated grant')
    require(message['source_cut']==current_cut==host_grant['source_cut'],'workflow exact current cut differs')
    for key in ('run_binding','definition_binding','authority_evaluation_binding','satisfaction_report_binding','action_receipt_bindings'):
        require(message[key]==host_grant[key],'workflow material not independently selected: '+key)
    definition=exact(message['definition_binding'],definition_raw);run=exact(message['run_binding'],run_raw)
    authority=exact(message['authority_evaluation_binding'],authority_raw)
    satisfaction=exact(message['satisfaction_report_binding'],satisfaction_raw)
    validate_shapes(message,definition,run,authority,satisfaction)
    require(definition['schema_version']=='lab-workflow-definition/v1-candidate' and definition['authority_effect']=='none'
        and definition['single_goal_coordination'] is True,'one-goal workflow definition required')
    require(run['schema_version']=='lab-workflow-run/v1-candidate' and run['authority_effect']=='none'
        and run['definition_binding']==message['definition_binding'] and run['source_cut']==current_cut
        and run['actor']==authenticated_actor and run['state']==message['expected_state'],'exact current run preimage differs')
    states=definition['states'];require(len(states)==len(set(states)) and run['state'] in states
        and set(definition['terminal_states'])<=set(states) and definition['initial_state'] in states,'workflow state closure differs')
    require(run['state'] not in definition['terminal_states'],'terminal workflow cannot transition')
    matches=[t for t in definition['transitions'] if t['transition_ref']==message['transition_ref']]
    require(len(matches)==1 and message['transition_ref'] in host_grant['permitted_transitions'],'transition undeclared or not permitted')
    transition=matches[0]
    require(transition['from_state']==run['state'] and all(transition[k] in states for k in ('to_state','failure_state','indeterminate_state')),
        'workflow transition state mapping differs')
    require(set(transition['actor_role_refs'])&set(host_grant['actor_role_refs']),'actual host grant lacks required Actor role')
    # A supplied permitted report is necessary evidence, never permission.
    require(authority['schema_version']=='lab-authority-evaluation/v1-candidate' and authority['authority_effect']=='none'
        and authority['source_cut']==current_cut and authority['posture']=='permitted'
        and instant(authority['evaluated_at'])<=now<instant(authority['expires_at'])
        and authority['gaps']==[] and authority['evidence_bindings'],'actual current authority evidence incomplete')
    require(satisfaction['schema_version']=='lab-validation-report/v1-candidate' and satisfaction['authority_effect']=='none'
        and satisfaction['source_cut']==current_cut and satisfaction['result']=='pass' and satisfaction['gaps']==[],
        'actual satisfaction evidence incomplete')
    # Obligation identities must match every declared role. Successful generic
    # schemas or an unrelated report cannot substitute for these named checks.
    required=[*transition['authority_requirement_refs'],*transition['precondition_refs'],
        *transition['satisfaction_check_refs'],*transition['relation_requirement_refs']]
    require(len(required)==len(set(required)),'workflow obligation roles collapsed or duplicated')
    actual={}
    for report in (authority,satisfaction):
        for check in report['checks']:
            ref=check['obligation_ref'];require(ref not in actual,'ambiguous workflow check obligation')
            actual[ref]=check
    require(set(host_grant['obligation_bindings'])==set(required)==set(selected_obligations),'workflow obligation selection incomplete')
    for obligation in required:
        check=actual.get(obligation)
        require(check is not None and check['result']=='pass' and check['evidence_bindings'],
            'workflow obligation unobserved or not passed: '+obligation)
        require(check['evidence_bindings']==host_grant['obligation_bindings'][obligation]==selected_obligations[obligation],
            'workflow obligation original evidence differs')
    require(len(message['input_artifacts'])==len({h['version_ref'] for h in message['input_artifacts']}),'duplicate workflow input')
    require({h['carrier_ref'] for h in message['input_artifacts']}==set(transition['input_carriers']),
        'workflow input carrier closure differs')
    for header in [run[k] for k in ('intent','intent_resolution','work','coordination_context')]+message['input_artifacts']:
        row=selected_headers.get(header['version_ref'])
        require(row is not None and set(row)=={'artifact','posture','semantic_kind'} and row['artifact']==header
            and row['posture'] in CURRENT and header['scope_ref']==host_grant['scope_ref'],'workflow exact current input/reference differs')
    require(run['coordination_context']['carrier_ref']=='cal.artifact-type.coordination-context/v2',
        'workflow must select actual Coordination Context/v2')
    next_run=copy.deepcopy(run);next_run['state']=transition['to_state'];next_run['gaps']=[]
    event={'schema_version':'lab-candidate-workflow-event/v1-candidate','run_ref':run['run_ref'],
        'definition_binding':message['definition_binding'],'transition_ref':transition['transition_ref'],
        'from_state':run['state'],'to_state':transition['to_state'],'source_cut':current_cut,
        'request_ref':message['request_ref'],'idempotency_key':message['idempotency_key'],
        'before_run_binding':message['run_binding'],'actor':copy.deepcopy(authenticated_actor),
        'authority_evaluation_binding':message['authority_evaluation_binding'],
        'satisfaction_report_binding':message['satisfaction_report_binding'],
        'action_receipt_bindings':copy.deepcopy(message['action_receipt_bindings']),
        'observed_obligation_refs':required,'output_artifact_refs':[],
        'completed_work_asserted':False,'canonical_admission_granted':False,'authority_effect':'none'}
    event_sha=digest(event)
    next_run['event_bindings']=[*run['event_bindings'],{'ref':'workflow-event:'+event_sha,'sha256':event_sha}]
    return {'schema_version':'lab-workflow-transition-plan/v1-candidate','event':event,'next_run':next_run,
        'allowed_output_carriers':copy.deepcopy(transition['output_carriers']),
        'expected_before_sha256':message['run_binding']['sha256'],'next_run_structural_sha256':digest(next_run),
        'actual_apply_completed':False,'work_satisfaction_asserted':False,'authority_effect':'none'}
