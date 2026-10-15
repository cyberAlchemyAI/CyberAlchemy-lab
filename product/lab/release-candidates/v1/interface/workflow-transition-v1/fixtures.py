"""Isolated schema-valid component witnesses; never current host/source authority."""
import copy
from datetime import datetime,timezone,timedelta
from pathlib import Path
import json
from .kernel import encoded,digest

ROOT=Path(__file__).resolve().parents[6]
def build():
    path=ROOT/'docs/proposals/0007-lab-integrated-schema-package/examples'
    definition=json.loads((path/'workflow-definition.json').read_bytes());run=json.loads((path/'workflow-run.json').read_bytes())
    now=datetime.now(timezone.utc);scope='project:isolated-workflow-source-review'
    actor={'principal_ref':'principal:isolated-workflow-owner','agent_instance_ref':None,'assignment_ref':None,'session_ref':None,'role_assignment_refs':[]}
    cut={'store_ref':'isolated-workflow-source','branch_ref':'branch:isolated-workflow-source','commit_sequence':0,
        'commit_sha256':'a'*64,'source_profile_sha256':'b'*64,'streams':[]}
    def header(name,carrier):return {'scope_ref':scope,'identity_ref':name,'version_ref':name+'@candidate.1','carrier_ref':carrier,'byte_sha256':'c'*64}
    definition.update(workflow_type_ref='workflow:inspect-source-integrity',version='1.0.0-candidate.1',
        states=['prepared','inspected','blocked','indeterminate'],initial_state='prepared',terminal_states=['inspected','blocked'],
        challenge_route='protocol:isolated-workflow-review',decision_profile=header('workflow-decision-profile:source-review','cal.artifact-type.workflow-decision-profile/v1'))
    t=definition['transitions'][0]
    t.update(transition_ref='transition:inspect-exact-source',from_state='prepared',to_state='inspected',
        actor_role_refs=['role:isolated-source-reviewer'],input_carriers=['cal.artifact-type.work/v1'],output_carriers=[],
        authority_requirement_refs=['obligation:independent-workflow-grant'],precondition_refs=['obligation:exact-current-run'],
        satisfaction_check_refs=['obligation:source-integrity-observed'],relation_requirement_refs=[],
        failure_state='blocked',indeterminate_state='indeterminate')
    def binding(ref,body):return {'ref':ref,'sha256':digest(body)}
    definition_binding=binding('workflow-definition:source-review',definition)
    run.update(run_ref='workflow-run:source-review',definition_binding=definition_binding,actor=actor,source_cut=cut,
        state='prepared',event_bindings=[],gaps=[],outcome_assessment=None,
        intent=header('intent:inspect-source','cal.artifact-type.intent/v1'),intent_resolution=None,
        work=header('work:inspect-source','cal.artifact-type.work/v1'),
        coordination_context=header('coordination:source-review','cal.artifact-type.coordination-context/v2'))
    # The public run protocol allows pending resolution. The component requires
    # an exact selected resolution before transitioning, so select one explicitly.
    run['intent_resolution']=header('intent-resolution:source-review','cal.artifact-type.intent-resolution/v1')
    obligations={ref:[{'ref':'evidence:'+ref,'sha256':'d'*64}] for ref in [*t['authority_requirement_refs'],*t['precondition_refs'],*t['satisfaction_check_refs']]}
    def check(ref):return {'check_ref':'check:'+ref,'obligation_ref':ref,'result':'pass','evidence_bindings':obligations[ref],
        'claim_ceiling':'Isolated component test witness only; no actual host, current source or owner grant is inferred.'}
    authority={'schema_version':'lab-authority-evaluation/v1-candidate','evaluation_ref':'evaluation:isolated-workflow',
        'request_binding':{'ref':'request:isolated-action','sha256':'e'*64},'authority_envelope_binding':{'ref':'grant:isolated-workflow','sha256':'f'*64},
        'source_cut':cut,'evaluated_at':(now-timedelta(seconds=1)).isoformat(),'expires_at':(now+timedelta(minutes=10)).isoformat(),
        'posture':'permitted','checks':[check(ref) for ref in t['authority_requirement_refs']],
        'evidence_bindings':obligations[t['authority_requirement_refs'][0]],'gaps':[],'authority_effect':'none'}
    satisfaction={'schema_version':'lab-validation-report/v1-candidate','report_ref':'validation:isolated-source-inspection',
        'subject_binding':binding('workflow-run:source-review:before',run),'source_cut':cut,
        'validator_binding':{'ref':'validator:isolated-source-check','sha256':'0'*64},
        'checks':[check(ref) for ref in [*t['precondition_refs'],*t['satisfaction_check_refs']]],'reference_checks':[],
        'gaps':[],'result':'pass','claim_ceiling':'Isolated component witness only.','authority_effect':'none'}
    message={'schema_version':'lab-workflow-transition/v1-candidate','request_ref':'request:inspect-source',
        'run_binding':binding('workflow-run:source-review:before',run),'definition_binding':definition_binding,
        'transition_ref':t['transition_ref'],'expected_state':'prepared','actor':actor,'input_artifacts':[run['work']],
        'action_receipt_bindings':[],'authority_evaluation_binding':binding('authority-evaluation:isolated-workflow',authority),
        'satisfaction_report_binding':binding('validation:isolated-source-inspection',satisfaction),'source_cut':cut,
        'idempotency_key':'workflow:inspect-source:1','authority_effect':'none'}
    grant={'schema_version':'lab-independent-workflow-grant/v1-candidate','principal_ref':actor['principal_ref'],
        'actor_role_refs':t['actor_role_refs'],'scope_ref':scope,'source_cut':cut,
        **{k:message[k] for k in ('run_binding','definition_binding','authority_evaluation_binding','satisfaction_report_binding','action_receipt_bindings')},
        'permitted_transitions':[t['transition_ref']],'obligation_bindings':obligations,
        'not_before':(now-timedelta(seconds=1)).isoformat(),'expires_at':(now+timedelta(minutes=10)).isoformat(),
        'permitted_effects':['candidate-workflow-transition'],'authority_effect':'none'}
    headers={h['version_ref']:{'artifact':h,'posture':'local-admitted-current','semantic_kind':'isolated-schema-witness'}
        for h in [run[k] for k in ('intent','intent_resolution','work','coordination_context')]}
    facts={'definition_raw':encoded(definition),'run_raw':encoded(run),'authority_raw':encoded(authority),
        'satisfaction_raw':encoded(satisfaction),'host_grant':grant,'authenticated_actor':actor,'current_cut':cut,
        'selected_headers':headers,'selected_obligations':obligations,'now':now}
    return copy.deepcopy(message),copy.deepcopy(facts)
