"""Prospective endpoint interpretation options; no implemented alias inferred."""
import copy
import hashlib
import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[6];HERE=Path(__file__).resolve().parent
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
    schema=json.loads((HERE/'prospective-model-proposal/schema.json').read_text())
    declaration=json.loads((ROOT/'implementation/lab-runtime/candidates/repeatable-operation/design/contract-impact.json').read_text())
    preparation=ROOT/'implementation/lab-review/candidates/v1/packages/0001/preparation.json'
    prepared=json.loads(preparation.read_text());checks=[]
    for index,name in enumerate(('project','product','method')):
        original=json.loads((HERE/'dispositions'/f'{index:02d}.json').read_text());member=original['member_ref']
        selected=next(m for m in prepared['members']if m['member_id']==member)['selected_record']
        endpoint_index=next(i for i,e in enumerate(declaration['endpoint_proposals'])if e['endpoint_kind']==name)
        endpoint=declaration['endpoint_proposals'][endpoint_index]
        assert selected==endpoint
        body=json.loads((ROOT/original['original_body_binding']['path']).read_text());candidate=copy.deepcopy(body)
        candidate['schema_version']=schema['properties']['schema_version']['const']
        candidate['payload']['model_disposition']='prospective-design'
        candidate['payload']['version_ref']=candidate['node_id']+'@prospective.endpoint.T10-candidate.1'
        candidate['payload']['rule_refs']=list(dict.fromkeys(candidate['payload']['rule_refs']+[
            'implementation/lab-runtime/candidates/repeatable-operation/design/contract-impact.json#/endpoint_proposals/'+str(endpoint_index)]))
        candidate['claim_ceiling']+=' Prospective endpoint interpretation model option only. Exact original selected_record is not implemented endpoint aliasing, current instance eligibility, carrier admission, Method execution or owner approval. Type/meaning approval is required before use.'
        Draft202012Validator(schema).validate(candidate)
        folder=HERE/'prospective-model-proposal/endpoint-options-0001';folder.mkdir(exist_ok=True)
        out=folder/(name+'.json')
        if out.exists():raise RuntimeError('retain prior endpoint option')
        out.write_text(json.dumps(candidate,indent=2,sort_keys=True)+'\n')
        checks.append({'member_ref':member,'original_wrapper_binding':original['original_body_binding'],'candidate_binding':bind(out),
            'original_preparation_binding':bind(preparation),'original_endpoint_proposal':endpoint,
            'exact_endpoint_selector':'/endpoint_proposals/'+str(endpoint_index),'original_schema_binding':endpoint['schema_binding'],
            'candidate_model_is_prospective':True,'original_owner_and_scope_preserved':candidate['owner_ref']==body['owner_ref']and candidate['scope_ref']==body['scope_ref'],
            'no_implemented_alias_or_eligibility_inferred':True,'accountable_type_and_endpoint_meaning_approval_required':True,'runtime_selected':False,'authority_effect':'none'})
    result={'schema_version':'lab-T10-exact-prospective-endpoint-options/v1','candidate_schema_binding':bind(HERE/'prospective-model-proposal/schema.json'),
        'options':checks,'actual_owner_outcome':None,'native_proposal_or_runtime_use_allowed':False,'all29_complete':False,'task_complete':False,'authority_effect':'none'}
    (folder/'options.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'exact_endpoint_options':3,'schema_valid_prospective_only':True,'runtime_selected':False,'approval_required':True}))

if __name__=='__main__':main()
