"""Private local coordination profile with original transition semantics.

The strict source-current kernel remains unchanged. This selected variant accepts
proofs for scoped owned outputs/coordination, without promoting them to admission.
Every other original plan predicate is retained verbatim and hash checked.
"""
import copy
from datetime import datetime
import hashlib
from pathlib import Path
from currentness import S
from host_headers import HostHeaders

ORIGINAL = S.ROOT / 'product/lab/release-candidates/v1/interface/workflow-transition-v1/kernel.py'
ORIGINAL_SHA = 'ac9a773cf7ab6c3c9383c3697a12a7e703fb2a53c8266a46b83bd4bf2ace52d9'
if hashlib.sha256(ORIGINAL.read_bytes()).hexdigest() != ORIGINAL_SHA:
    raise ValueError('selected original workflow kernel differs')
require, encoded, digest, instant, exact, validate_shapes = (
    getattr(S.J.K, name) for name in ('require', 'encoded', 'digest', 'instant', 'exact', 'validate_shapes'))

def plan(message,*,definition_raw,run_raw,authority_raw,satisfaction_raw,host_grant,
         authenticated_actor,current_cut,selected_headers,selected_obligations,now):
    """Compute one candidate next run after independently bound obligations.

All keyword inputs are supplied by the independently selected host. Neither
authority_raw nor satisfaction_raw is accepted as a replacement for host_grant.
The host must guard/retrieve originals before and after this calculation.
"""
    require(type(selected_headers) is HostHeaders, 'private owned workflow profile required')
    selected_headers.guard()
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
        require(type(selected_headers) is HostHeaders, 'private host-selected currentness resolver required')
        row=selected_headers.resolve(header)
        require(row['artifact']==header and header['scope_ref']==host_grant['scope_ref'],
            'workflow exact owned or signed input/reference differs')
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
    selected_headers.guard()
    return {'schema_version':'lab-workflow-transition-plan/v1-candidate','event':event,'next_run':next_run,
        'allowed_output_carriers':copy.deepcopy(transition['output_carriers']),
        'expected_before_sha256':message['run_binding']['sha256'],'next_run_structural_sha256':digest(next_run),
        'actual_apply_completed':False,'work_satisfaction_asserted':False,'authority_effect':'none'}
