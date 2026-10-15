"""Specific prospective interpretation profile models; code selection stays proof."""
import copy
import hashlib
import json
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[6];HERE=Path(__file__).resolve().parent
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
    schema=json.loads((HERE/'prospective-model-proposal/schema.json').read_text())
    selected=[(16,'governed-subject-representation-profile','implementation/lab-ontology/candidates/v1/profiles/lab-ontology-profile.json',
        'Exact prospective domain-carrier and represented-subject mapping design; source/native/history/authority axes remain separate.'),
        (19,'rich-domain-translation','implementation/lab-ontology/candidates/v1/adapters/lifecycle/profiles/translation-profile.json',
        'Exact prospective source/Definition/semantic/governance interpretation, challenge join, closure and withdrawal obligations. The original selected code remains independently bound technical implementation selection, not instantiated Model authority.'),
        (23,'legacy-local-vocabulary','implementation/lab-ontology/candidates/v1/migration/adapters/translation-profile.json',
        'Exact source-local twenty-predicate interpretation profile; directed/symmetric edges and private source-qualified metadata remain distinct from global Typed Relations, source admission, body import and ontology adoption.')]
    options=[];folder=HERE/'prospective-model-proposal/profile-options-0001';folder.mkdir(exist_ok=True)
    for index,name,profile_path,meaning in selected:
        d=json.loads((HERE/'dispositions'/f'{index:02d}.json').read_text());profile=json.loads((ROOT/profile_path).read_text());assert profile['authority_effect']=='none'
        original=json.loads((ROOT/d['original_body_binding']['path']).read_text());body=copy.deepcopy(original)
        body['schema_version']=schema['properties']['schema_version']['const'];body['payload']['model_disposition']='prospective-design'
        body['payload']['version_ref']=body['node_id']+'@prospective.profile.T10-candidate.1'
        # The Model denotes the interpretation rules, not the property schemas
        # or execution code which are independently retained original inputs.
        body['payload']['contract_ref']=profile_path
        body['payload']['model_kind']='prospective-interpretation-profile:'+name
        body['payload']['rule_refs']=list(dict.fromkeys(original['payload']['rule_refs']+[profile_path+'#']))
        body['claim_ceiling']+=' '+meaning+' Accountable exact type/meaning approval is required before use; no code realization, namespace alias, current owner or permission inferred.'
        Draft202012Validator(schema).validate(body)
        out=folder/(name+'.json')
        if out.exists():raise RuntimeError('retain prior profile option')
        out.write_text(json.dumps(body,indent=2,sort_keys=True)+'\n')
        options.append({'member_ref':d['member_ref'],'original_wrapper_binding':d['original_body_binding'],'candidate_binding':bind(out),
            'exact_profile_binding':bind(ROOT/profile_path),'meaning':meaning,'original_control_bindings':d['original_axes']['original_control_bindings'],
            'original_preparation_member':d['original_member_semantics'],'full_original_member_scope_still_required':True,
            'source_local_or_private_provenance_not_global_authority':True,'original_code_or_schema_inputs_not_promoted_to_models':True,
            'original_owner_and_scope_preserved':body['owner_ref']==original['owner_ref']and body['scope_ref']==original['scope_ref'],
            'meaning_and_type_approval_required':True,'native_use_allowed':False,'actual_owner_outcome':None,'authority_effect':'none'})
    report={'schema_version':'lab-T10-exact-prospective-profile-options/v1','schema_binding':bind(HERE/'prospective-model-proposal/schema.json'),
        'options':options,'all29_complete':False,'task_complete':False,'authority_effect':'none'}
    (folder/'options.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'specific_profile_model_options':3,'code_and_schema_selection_not_replaced':True,'native_use_allowed':False}))
if __name__=='__main__':main()
