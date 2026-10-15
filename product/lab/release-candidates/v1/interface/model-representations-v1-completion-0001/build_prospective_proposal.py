"""Explicit new prospective carrier proposal; v1 and its refusals stay frozen."""
import copy
import hashlib
import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[6];HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def binding(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)}
def save(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():raise RuntimeError('retain prior proposal bytes')
    p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def main():
    original_schema=ROOT/'authority/artifact-types/governed-model/v1/schema.json'
    original_descriptor=ROOT/'authority/artifact-types/governed-model/v1/artifact.json'
    definition=ROOT/'authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/governed-model/v1/definition.json'
    original=json.loads(original_schema.read_text());descriptor=json.loads(original_descriptor.read_text())
    formal=json.loads(definition.read_text())['voices']['scientific_formal']
    assert sha(definition)==descriptor['semantic_definition_bindings'][0]['sha256']
    folder=HERE/'prospective-model-proposal';schema=copy.deepcopy(original)
    schema['$id']='https://lab.invalid/completion/prospective-governed-model/v1'
    schema['properties']['schema_version']['const']='cyberalchemy-lab-prospective-governed-model/v1-candidate'
    schema['properties']['relation_refs']['minItems']=0
    payload=schema['properties']['payload'];payload['properties']['model_disposition']={'const':'prospective-design'}
    payload['required'].append('model_disposition')
    Draft202012Validator.check_schema(schema);save(folder/'schema.json',schema)
    new_descriptor=copy.deepcopy(descriptor)
    new_descriptor.update(artifact_type_id='cal.artifact-type.prospective-governed-model',artifact_type_ref='cal.artifact-type.prospective-governed-model/v1',
        name='Prospective Governed Model proposal',schema_ref='cal.schema.prospective-governed-model/v1',schema_digest=sha(folder/'schema.json'),
        version='1.0.0-candidate.1',status='candidate-unadmitted',claim_ceiling='Separately identified prospective-only carrier proposal. Exact original GovernedModel Definition and relationship roles remain attributable. The explicit cardinality change requires accountable meaning/type approval before any selection, proposal, admission, runtime use or public release. Original v1 still refuses all original empty relations; this is not a v1 PASS or compatibility qualification.')
    new_descriptor['instance_contract']['instance_discriminator']['value']=schema['properties']['schema_version']['const']
    new_descriptor['instance_contract']['required_semantic_fields']=list(schema['required'])
    new_descriptor['distinct_validation_purpose']='Represent an explicit prospective non-executable rules/structures/behavior model where no legitimate instance, Decision, or predecessor exists. It is not a Schema, evidence result, implemented system or authority grant. Any supplied relationship must retain exact original permitted role/pair semantics.'
    new_descriptor['source_direction']={'canonical':'artifact.json','human_projection':'PROPOSAL.md','projection_policy':'proposal-only; no canonical promotion','shared_generator_path':str(Path(__file__).relative_to(ROOT)),'shared_generator_sha256':sha(Path(__file__))}
    new_descriptor['validation_contract']={'admission_effect':'none','assessment_scope':'prospective-candidate-shape-and-explicit-constraint-delta-only','validator_path':str((folder/'validate_proposal.py').relative_to(ROOT)),
        'required_checks':['original Definition and v1 schema/descriptor bytes unchanged','exact explicit schema delta only','all original v1 refusals retained','ten original non-executable blueprint model candidates schema-valid','original role and qualifier constraints retained','accountable meaning/type approval absent => no runtime use']}
    new_descriptor['typed_residue']=[{'residue_id':'PROSPECTIVE-MODEL-APPROVAL','missing':'Accountable artifact-type/Definition owner approval of exact prospective-only meaning and cardinality change.','owner_ref':'role:artifact-type-owner','consequence':'No native preparation/admission, runtime use or release.'},
        {'residue_id':'PROSPECTIVE-MODEL-SCOPES','missing':'Original model owner/source/domain scope and future per-run actor/evidence/authority qualifications.','owner_ref':'role:repository-owner','consequence':'No current roles, workflow execution or outcome satisfaction inferred.'}]
    save(folder/'artifact.json',new_descriptor)
    selected=[]
    ledger=json.loads((HERE/'disposition-ledger-initial.json').read_text())
    for member in ledger['members']:
        row=json.loads((ROOT/member['disposition_binding']['path']).read_text())
        if not row['member_ref'].startswith('protocol:W08:workflow:'):continue
        body=json.loads((ROOT/row['original_body_binding']['path']).read_text());control=json.loads((ROOT/row['original_axes']['original_control_bindings'][0]['path']).read_text())
        assert control['executable']is False and body['relation_refs']==[]
        candidate=copy.deepcopy(body);candidate['schema_version']=schema['properties']['schema_version']['const']
        candidate['payload']['model_disposition']='prospective-design'
        candidate['payload']['version_ref']=candidate['node_id']+'@prospective.T10-candidate.1'
        candidate['claim_ceiling']+=' Prospective carrier proposal only: the original blueprint is non-executable; no implementation/Decision/predecessor or current actor/permission/operational success is inferred. Exact meaning/type approval is required before use.'
        Draft202012Validator(schema).validate(candidate)
        name=row['member_ref'].split(':')[-1];out=folder/'candidates'/(name+'.json');save(out,candidate)
        selected.append({'member_ref':row['member_ref'],'original_body_binding':row['original_body_binding'],'candidate_binding':binding(out),
            'original_control_bindings':row['original_axes']['original_control_bindings'],'original_source_executable':False,'original_scope_changed':candidate['scope_ref']!=body['scope_ref'],
            'original_owner_changed':candidate['owner_ref']!=body['owner_ref'],'v1_status':'REFUSED relation_refs.minItems','new_candidate_schema_valid':True,'meaning_approval_required':True,'native_use_allowed':False})
    assert len(selected)==10
    proposal={'schema_version':'lab-T10-prospective-carrier-design-option/v1','definition_binding':binding(definition),'definition_normative_statement':formal['normative_statement'],
        'definition_testable_conditions':formal['testable_conditions'],'original_schema_binding':binding(original_schema),'original_descriptor_binding':binding(original_descriptor),
        'candidate_schema_binding':binding(folder/'schema.json'),'candidate_descriptor_binding':binding(folder/'artifact.json'),
        'explicit_schema_delta':[{'path':'/$id','purpose':'New candidate namespace, distinct from frozen v1.'},{'path':'/properties/schema_version/const','purpose':'New prospective-only discriminator.'},
            {'path':'/properties/relation_refs/minItems','before':1,'proposed':0,'meaning':'Allow a prospective model without inventing an instantiated relationship; accountable schema/meaning decision required.'},
            {'path':'/properties/payload/properties/model_disposition','purpose':'Restrict meaning to explicit prospective design.'},{'path':'/properties/payload/required','purpose':'Require the new prospective disposition.'}],
        'all_other_v1_constraints_preserved':True,'original_relation_roles_preserved':True,'candidate_members':selected,
        'scope_exclusions':['schema-only controls','test/evidence receipts','confidence vocabulary','private-source permission','source archive/provenance','endpoint alias approval','actual workflow execution'],
        'accountable_approver_roles':['role:artifact-type-owner','role:definition-owner'],'actual_answering_principal_ref':None,'actual_owner_outcome':None,
        'meaning_and_type_approval_required':True,'runtime_carrier_selected':False,'native_proposal_allowed':False,'admission_or_use_allowed':False,
        'original_v1_schema_weakened_or_changed':False,'original_v1_refusals_retained':True,'all29_complete':False,'task_complete':False,'authority_effect':'none'}
    save(folder/'proposal.json',proposal)
    print(json.dumps({'separately_identified_type_proposal':True,'prospective_blueprint_candidates':10,'original_v1_changed':False,'runtime_selected':False,'approval_required':True}))

if __name__=='__main__':main()
