"""Scoped private coordination over unchanged original candidate Work inputs."""
import base64
import copy
import json
from pathlib import Path
import sys
import profiles as P
sys.path.insert(0,str(P.ROOT/'implementation/lab-runtime/local-host/t31-durable-output-0001'))
import owned_coordination_capsule as CC
from jsonschema import Draft202012Validator

def construct(profile,*,run_ref,principal,source_cut,project):
    P.guard(profile);m=profile['manifest'];headers=profile['headers'];scope=profile['scope_ref']
    P.need(project['identity_ref']==scope and project['scope_ref']==scope,'actual current Project differs from original candidate frame')
    old={k:headers[m[key]] for k,key in [('intent','intent_ref'),('work','work_ref'),('goal','goal_ref'),('coordination-context','coordination_ref')]}
    seed=P.sha(P.enc({'run':run_ref,'original_work':old['work'],'current_source_cut':source_cut}))[:24]
    ids={k:k+':retained-work-profile:'+seed for k in ('intent-resolution','decision','effect','declared-effect','goal-project')}
    refs={k:v+'@owned-coordination.1' for k,v in ids.items()};records={};schemas={}
    for kind,version in [('intent-resolution','v1'),('decision','v2'),('effect','v1')]:
        b,schema=CC.fixture(kind,version);b.update(node_id=ids[kind],owner_ref=principal,scope_ref=scope,lifecycle_state='candidate',
            successor_refs=[],evidence_refs=['retained-actual-original-Work:'+P.SPECS[profile['kind']]['run_sha256']],
            claim_ceiling='Private coordination of exact original candidate Work, not signed Source-current Work, original owner outcome, admission, satisfaction or source-cut retargeting.')
        records[kind]=b;schemas[kind]=schema
    records['intent-resolution']['payload'].update(intent_ref=old['intent']['version_ref'],selected_subject_refs=[old[k]['version_ref'] for k in ('work','goal','coordination-context')],
        excluded_subject_refs=['canonical-admission','live-stores','external-effects'],owner_decision_ref=refs['decision'],satisfaction_test_refs=['original-candidate-Work-profile:'+run_ref])
    records['decision']['payload'].update(decision_maker_ref=principal,subject_refs=[refs['intent-resolution']],selected_outcome='Coordinate unchanged original candidate Work evidence only.',
        declared_effect_refs=[refs['effect']],evidence_basis_refs=['retained-actual-original-Work:'+P.SPECS[profile['kind']]['run_sha256']])
    records['effect']['payload'].update(effect_kind='lifecycle-transition',subject_ref=refs['intent-resolution'],intended_state='owned-coordination-current',
        effective_when='Exact independently current Reader operator grant and candidate profile validate.',verification_refs=['original-candidate-Work-profile:'+run_ref])
    records['intent-resolution']['relation_refs']=[{'relation_kind_ref':'relation.declares-effect-on','direction':'target','counterpart_kind':'decision','counterpart_ref':refs['decision']}]
    records['decision']['relation_refs']=[{'relation_kind_ref':'relation.declares-effect-on','direction':'source','counterpart_kind':'intent-resolution','counterpart_ref':refs['intent-resolution']}]
    records['effect']['relation_refs']=[{'relation_kind_ref':'relation.declares-effect-on','direction':'target','counterpart_kind':'decision','counterpart_ref':refs['decision']}]
    for label,relation,source,target,qualifiers in [
       ('declared-effect','relation.declares-effect-on',{'kind':'decision','ref':ids['decision'],'version_ref':refs['decision']},{'kind':'intent-resolution','ref':ids['intent-resolution'],'version_ref':refs['intent-resolution']},{'effect_kind':'lifecycle-transition','exact_target_version_ref':refs['intent-resolution']}),
       ('goal-project','relation.member-of',{'kind':'goal','ref':old['goal']['identity_ref'],'version_ref':old['goal']['version_ref']},{'kind':'project','ref':project['identity_ref'],'version_ref':project['version_ref']},{'membership_role':'Retained candidate Goal framed by original Work/Coordination in this current Project scope'})]:
        b,schema=CC.fixture('typed-relation','v3');b.update(node_id=ids[label],owner_ref=principal,scope_ref=scope,evidence_refs=['original-candidate-Work-profile:'+run_ref],relation_refs=[],successor_refs=[],lifecycle_state='candidate',
            claim_ceiling='Private exact candidate relationship declaration only; no Source graph admission or endpoint authority.')
        b['payload'].update(relation_kind_ref=relation,source=source,target=target,qualifiers=qualifiers,relation_evidence_refs=['original-candidate-Work-profile:'+run_ref])
        records[label]=b;schemas[label]=schema
    artifacts={};raws={}
    for label,body in records.items():
        Draft202012Validator(json.loads(schemas[label].read_bytes())).validate(body);raw=P.enc(body)
        semantic='typed-relation' if label in ('declared-effect','goal-project') else label;version='v3' if semantic=='typed-relation' else ('v2' if semantic=='decision' else 'v1')
        artifacts[label]={'scope_ref':scope,'identity_ref':body['node_id'],'version_ref':refs[label],'carrier_ref':'cal.artifact-type.'+semantic+'/'+version,'byte_sha256':P.sha(raw)};raws[refs[label]]=raw
    capsule={'schema_version':'lab-private-retained-Work-coordination/v1','original_work':profile['original_work'],'original_input_manifest_sha256':P.SPECS[profile['kind']]['sha256'],
        'original_producer_source_cut':profile['original_producer_source_cut'],'current_coordinating_source_cut':source_cut,'current_project':project,
        'artifacts':artifacts,'records':records,'original_headers':headers,'original_record_byte_sha256s':{ref:P.sha(raw) for ref,raw in profile['raws'].items()},
        'actual_owner_outcome':None,'original_Work_bytes_and_meaning_unchanged':True,'original_Work_promoted_to_Source_current':False,'authority_effect':'none'}
    return capsule,raws
