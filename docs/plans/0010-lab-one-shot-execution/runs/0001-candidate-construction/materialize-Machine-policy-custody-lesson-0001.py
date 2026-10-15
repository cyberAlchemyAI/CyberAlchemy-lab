"""Materialize a scoped learning candidate from an actual original refusal.

This creates reviewable records and closed declared relations only. No record
is admitted, no live resource is restored, and no application is inferred.
"""
import base64
import copy
from datetime import datetime,timezone,timedelta
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
OUT=RUN/'Machine-policy-custody-lesson-0001'
VERSION='1.0.0-candidate.1'
CLAIM='Candidate learning records derived from an actual current controlled diagnostic only; no admission, applied lesson, general effectiveness or restored Agent memory.'


def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def load(path):return json.loads(path.read_bytes())


def emit(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')


def main():
    assert not OUT.exists()
    diagnostic_path=RUN/'API83-original-Machine-generation-diagnosis-0001.json'
    diagnostic=load(diagnostic_path)
    assert diagnostic['result']=='PASS' and diagnostic['actual_cases']==1
    observed=diagnostic['observed']
    assert observed['peer_closed'] and not observed['resource_closed'] and not observed['actual_Session_expired']
    assert any(item.get('known_original_refusal')=='fact scope selects another host channel'
               for item in observed['exception_chain'])
    records_dir=ROOT/'product/lab/release-candidates/v1/interface/api-v83/receipts/per-call-observations'
    openings=[]
    for path in records_dir.glob('*.json'):
        record=load(path)
        if not record['test_ref'].endswith('.test_original_generation_refuses_parent_policy_host_in_Machine_scope'):continue
        reply=record['actual_public_reply']
        if reply.get('operation')=='session.open' and reply.get('kind')=='result':openings.append((path,record))
    assert len(openings)==1
    opening_path,opening=openings[0]
    session=opening['actual_public_reply']['message']
    assert session['posture']=='active' and session['memory_persistence_allowed'] is False
    owners=[]
    for snapshot in opening['durable_journal_snapshots']:
        if not snapshot['path'].startswith('journal/session-'):continue
        original=base64.b64decode(snapshot['base64_original_bytes'],validate=True)
        assert hashlib.sha256(original).hexdigest()==snapshot['sha256']
        row=json.loads(original)
        if row.get('session_ref')==session['session_ref']:
            assert row['short_memory_persisted'] is False and row['authority_effect']=='none'
            owners.append(row['principal_ref'])
    assert len(set(owners))==1
    owner=owners[0];scope=session['assignment']['scope_ref']
    evidence=diagnostic_path.relative_to(ROOT).as_posix()
    authorization=RUN/'authorization.json'
    counter_path=RUN/'API83-live-application-composition-0002.json'
    assert load(counter_path)['result']=='PASS'
    counter=counter_path.relative_to(ROOT).as_posix()
    kinds=['agent-action','operational-observation','agent-reflection','operational-lesson']
    bodies={}
    schemas={}
    sources=[diagnostic_path,opening_path,authorization,counter_path,Path(__file__).resolve()]
    for kind in kinds:
        folder=ROOT/'authority/artifact-types'/kind/'v1'
        schema_path=folder/'schema.json';fixture_path=folder/'fixtures/valid/record.json'
        schema=load(schema_path);body=load(fixture_path)
        body.update(node_id=kind+':R03-Machine-policy-custody',owner_ref=owner,scope_ref=scope,
                    lifecycle_state='candidate',authority_effect='none',evidence_refs=[evidence],successor_refs=[],
                    relation_refs=[],claim_ceiling=CLAIM,challenge_route='protocol:R03-candidate-learning-review')
        bodies[kind]=body;schemas[kind]=schema;sources.extend([schema_path,fixture_path])
    ref=lambda kind:bodies[kind]['node_id']+'@'+VERSION
    relation=lambda kind,target:{'relation_kind_ref':kind,'direction':'source','counterpart_kind':target,'counterpart_ref':ref(target)}
    action=bodies['agent-action']
    action['payload'].update(agent_instance_ref=session['agent_instance_ref']+'@ephemeral.1',
        session_ref=session['session_ref']+'@ephemeral.1',assignment_ref=session['assignment']['version_ref'],
        action_kind='controlled-original-Machine-context-generation-diagnosis',posture='observed-original-policy-host-refusal',
        input_refs=[session['assignment']['version_ref']],output_refs=[evidence],tool_refs=[],
        implementation_refs=['docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/diagnose-API83-original-Machine-generation-0001.py'],
        authority_evidence_refs=[authorization.relative_to(ROOT).as_posix()],receipt_refs=[evidence],
        residue_refs=['protocol:R03-no-full-Machine-or-API-qualification'])
    action['relation_refs']=[relation('relation.produces','operational-observation')]
    observation=bodies['operational-observation']
    observation['payload'].update(project_ref=scope,action_ref=ref('agent-action'),
        observed_at='not-exported:exact-original-diagnostic-report:'+bind(diagnostic_path)['sha256'],
        datum='Original generator rejected the parent policy channel because its fact scope registered the Machine channel. Peer closed; parent Session stayed live and unexpired.',
        method_ref='protocol:R03-direct-original-generator-and-safe-refusal-chain',evidence_refs=[evidence],
        interpretation_posture='observed-known-original-refusal; no expiry cause or broader outcome inferred')
    observation['relation_refs']=[{'relation_kind_ref':'relation.produces','direction':'target',
                                   'counterpart_kind':'agent-action','counterpart_ref':ref('agent-action')}]
    reflection=bodies['agent-reflection']
    reflection['payload'].update(source_session_ref=session['session_ref']+'@ephemeral.1',
        source_action_refs=[ref('agent-action')],observation_refs=[ref('operational-observation')],
        interpretation='The actual Machine supplies Actor attribution; its actual parent supplies the independent policy. Registering the peer as the sole policy host collapses these distinct responsibilities.',
        repair_hypothesis='Declare exact actual-parent policy custody for the Machine fact scope, retaining the original generator, Actor, permission, clocks and source guards.',
        counterevidence_refs=[counter],disposition='candidate-scoped-reflection')
    reflection['relation_refs']=[relation('relation.derives-from','operational-observation')]
    retention_ref='protocol:R03-Machine-policy-custody-lesson-retention/v1-candidate'
    lesson=bodies['operational-lesson']
    lesson['payload'].update(
        lesson_statement='For this Machine Context implementation, bind borrowed source facts to the peer actual parent policy custodian while retaining the peer as the authenticated Actor.',
        scope_refs=[scope],applicability='Exact original current-context-delivery-v9 and fact-read-scope-v1 Machine-to-parent composition; source/API selections remain independently bound.',
        exclusions=['another generator or scope version','expired or revoked source/permission','sibling host or reconstructed resource',
                    'role inheritance','tool or external action authority','canonical admission','general effectiveness'],
        predicted_benefit='The original seven-read Machine case returns all seven domain results without disposing a live unexpired peer because of this policy-host mismatch.',
        falsifier='The exact repaired case still loses authentication, breaks any original source/Actor/permission guard, disposes a live unexpired peer, or extends roles, operations or lifetime.',
        evidence_refs=[ref('agent-reflection'),ref('operational-observation'),evidence],counterevidence_refs=[counter],
        retention_policy_ref=retention_ref,expires_at=(datetime.now(timezone.utc)+timedelta(hours=24)).isoformat(),
        classification_assignment_refs=[],status='candidate-scoped-not-applied')
    lesson['relation_refs']=[relation('relation.derives-from','agent-reflection')]
    for kind,body in bodies.items():Draft202012Validator(schemas[kind]).validate(body)
    registry_path=ROOT/'authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json'
    registry=load(registry_path)
    carrier_registry_path=ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json'
    carrier_registry=load(carrier_registry_path)
    typed_contract=next(row for row in carrier_registry['admitted_contracts'] if row['artifact_type_ref']=='cal.artifact-type.typed-relation/v3')
    typed_schema_path=ROOT/typed_contract['schema_path']
    assert bind(typed_schema_path)['sha256']==typed_contract['schema_sha256']
    template_path=typed_schema_path.parent/'fixtures/valid/record.json'
    typed=[]
    for kind,left,right,qualifiers in [
        ('relation.produces','agent-action','operational-observation',{'action_receipt_ref':evidence,'production_role':'actual-diagnostic-observation','output_posture':'candidate-unadmitted'}),
        ('relation.derives-from','agent-reflection','operational-observation',{'derivation_role':'actual-known-original-refusal'}),
        ('relation.derives-from','operational-lesson','agent-reflection',{'derivation_role':'scoped-falsifiable-repair-hypothesis'})]:
        declared=next(row for row in registry['entries'] if row['relation_kind_id']==kind)
        signature_path=ROOT/declared['instance_path'];signature=load(signature_path)
        assert declared['lifecycle_state']=='admitted-current' and bind(signature_path)['sha256']==declared['instance_sha256']
        payload=signature['payload'];assert {'source_kind':left,'target_kind':right} in payload['allowed_endpoint_pairs']
        qc=payload['qualifier_contract']
        Draft202012Validator({'type':'object','additionalProperties':False,'properties':qc['properties'],'required':qc['required_axes']}).validate(qualifiers)
        body=load(template_path)
        body.update(node_id='typed-relation:R03-Machine-policy-custody:'+left+'-'+right,
                    owner_ref=owner,scope_ref=scope,lifecycle_state='candidate',evidence_refs=[evidence],
                    successor_refs=[],claim_ceiling=CLAIM,authority_effect='none')
        body['payload'].update(relation_kind_ref=kind,
            source={'kind':left,'ref':bodies[left]['node_id'],'version_ref':ref(left)},
            target={'kind':right,'ref':bodies[right]['node_id'],'version_ref':ref(right)},
            qualifiers=qualifiers,relation_lifecycle_state='candidate',relation_evidence_refs=[evidence])
        Draft202012Validator(load(typed_schema_path)).validate(body)
        typed.append(body);sources.append(signature_path)
    sources.extend([registry_path,carrier_registry_path,typed_schema_path,template_path])
    OUT.mkdir(mode=0o700)
    rows=[]
    for body in [*bodies.values(),*typed]:
        path=OUT/(body['node_id'].replace(':','_')+'.json');emit(path,body)
        rows.append({'kind':body['kind'],'version_ref':body['node_id']+'@'+VERSION,'binding':bind(path),'posture':'candidate-unadmitted'})
    retention_path=OUT/'retention-policy.json'
    emit(retention_path,{'schema_version':'lab-candidate-learning-retention/v1-candidate','policy_ref':retention_ref,
                        'retain':['immutable scoped lesson/reflection/observation revisions','exact original public/controlled diagnostic evidence','counterevidence and refusal history'],
                        'exclude':['Session RAM and notes','private keys and credentials','unselected private archives'],
                        'at_expiry':'exclude from current selection; retain evidence without automatic deletion',
                        'authority_effect':'none','actual_owner_outcome':None})
    index={'schema_version':'lab-actual-diagnostic-learning-candidate/v1-candidate','result':'PASS',
           'actual_diagnostic_binding':bind(diagnostic_path),'actual_opening_binding':bind(opening_path),
           'files':[bind(path) for path in sorted(set(sources))]+[bind(retention_path)]+[row['binding'] for row in rows],
           'records':rows,'body_count':4,'declared_typed_relation_count':3,
           'current_source_imported':False,'application_created':False,'outcome_assessed':False,
           'short_memory_exported':False,'private_keys_exported':False,'canonical_admission':False,
           'actual_owner_outcome':None,'authority_effect':'none','task_complete':False,'goal_complete':False,
           'claim_ceiling':CLAIM}
    emit(OUT/'index.json',index)
    print(json.dumps({'result':'PASS','binding':bind(OUT/'index.json'),'candidate_bodies':4,'declared_typed_relations':3,
                      'applied':False,'admitted':False}),flush=True)


if __name__=='__main__':main()
