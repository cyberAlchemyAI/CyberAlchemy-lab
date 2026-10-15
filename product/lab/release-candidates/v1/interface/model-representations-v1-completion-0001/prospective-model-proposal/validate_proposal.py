"""Exact proposal delta; no admitted-v1 or native implementation PASS."""
import copy
import hashlib
import json
from pathlib import Path
from jsonschema import Draft202012Validator

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[6]
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T10'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    proposal=json.loads((HERE/'proposal.json').read_text())
    for key in ('definition_binding','original_schema_binding','original_descriptor_binding','candidate_schema_binding','candidate_descriptor_binding'):
        row=proposal[key];assert sha(ROOT/row['path'])==row['sha256']
    original=json.loads((ROOT/proposal['original_schema_binding']['path']).read_text());new=json.loads((HERE/'schema.json').read_text())
    expected=copy.deepcopy(original);expected['$id']=new['$id']
    expected['properties']['schema_version']['const']=new['properties']['schema_version']['const']
    expected['properties']['relation_refs']['minItems']=0
    expected['properties']['payload']['properties']['model_disposition']={'const':'prospective-design'}
    expected['properties']['payload']['required'].append('model_disposition')
    assert expected==new,'undeclared original constraint change'
    original_descriptor=json.loads((ROOT/proposal['original_descriptor_binding']['path']).read_text());new_descriptor=json.loads((HERE/'artifact.json').read_text())
    for key in ('relation_roles','allowed_relation_kinds','semantic_definition_refs','semantic_definition_bindings','orthogonality_rules','hostile_non_collapse'):
        assert original_descriptor[key]==new_descriptor[key]
    checks=[]
    for item in proposal['candidate_members']:
        original_body=json.loads((ROOT/item['original_body_binding']['path']).read_text());body=json.loads((ROOT/item['candidate_binding']['path']).read_text())
        assert sha(ROOT/item['candidate_binding']['path'])==item['candidate_binding']['sha256']
        Draft202012Validator(new).validate(body)
        errors=list(Draft202012Validator(original).iter_errors(original_body))
        assert len(errors)==1 and errors[0].validator=='minItems'and list(errors[0].path)==['relation_refs']
        assert body['relation_refs']==[]and body['scope_ref']==original_body['scope_ref']and body['owner_ref']==original_body['owner_ref']
        for key in ('contract_ref','rule_refs','extension_policy_ref','model_kind'):assert body['payload'][key]==original_body['payload'][key]
        for row in item['original_control_bindings']:assert sha(ROOT/row['path'])==row['sha256']
        wrong=copy.deepcopy(body);wrong['payload']['model_disposition']='implemented'
        assert not Draft202012Validator(new).is_valid(wrong)
        wrong=copy.deepcopy(body);wrong['relation_refs']=[{'relation_kind_ref':'relation.instance-of','direction':'target','counterpart_kind':'decision','counterpart_ref':'unrelated'}]
        relation=wrong['relation_refs'][0]
        assert not any(r['relation_kind_ref']==relation['relation_kind_ref']and r['direction']==relation['direction']and relation['counterpart_kind']in r['counterpart_kinds']for r in new_descriptor['relation_roles'])
        wrong=copy.deepcopy(body);wrong['derived_authority']=True
        assert not Draft202012Validator(new).is_valid(wrong)
        checks.append({'member_ref':item['member_ref'],'new_candidate_schema_valid':True,'original_v1_still_refused':True,'owner_scope_and_original_rule_bindings_preserved':True,'nonprospective_wrong_counterpart_and_authority_negatives_refused':True})
    assert len(checks)==10 and not proposal['admission_or_use_allowed']and proposal['actual_owner_outcome']is None
    # Exact native registered-declaration shape only. A future namespace/source
    # selection and accountable type approval remain unfulfilled prerequisites.
    entry={'artifact_type_ref':new_descriptor['artifact_type_ref'],'semantic_kind':'governed-model',
        'semantic_definition_refs':new_descriptor['semantic_definition_refs'],
        'schema_path':(HERE/'schema.json').relative_to(ROOT).as_posix(),'schema_selector':None,
        'schema_sha256':sha(HERE/'schema.json'),'distinct_validation_purpose':new_descriptor['distinct_validation_purpose']}
    fragment=json.loads((ROOT/'authority/artifact-types/artifact-type/v3/schema.json').read_text())['properties']['registered_types']['items']
    Draft202012Validator(fragment).validate(entry)
    out=HERE/'registered-declaration-proposal.json'
    if out.exists():raise RuntimeError('preserve previous proposal verification')
    out.write_text(json.dumps(entry,indent=2)+'\n')
    report={'schema_version':'lab-T10-prospective-carrier-proposal-check/v1','result':'EXPLICIT-GATED-PROPOSAL-SHAPE-PASS','checks':checks,'exact_declared_schema_delta_only':True,
        'original_v1_unchanged':True,'original_role_kind_definition_constraints_preserved':True,'registered_declaration_shape_valid':True,
        'actual_native_namespace_or_prepare_qualified':False,'actual_meaning_or_type_approval':None,'runtime_selected':False,
        'all29_complete':False,'task_complete':False,'authority_effect':'none'}
    (RUN/'prospective-proposal-qualification-0001.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'proposal_models':10,'explicit_delta_checked':True,'original_v1_refusals_retained':True,'runtime_use_allowed':False}))

if __name__=='__main__':main()
