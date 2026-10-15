"""Check every declared ordered pair and exact eight-branch candidate change."""
import copy
import hashlib
import json
from pathlib import Path
from jsonschema import Draft202012Validator

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
OLD=ROOT/'authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/typed-relation/v3'
NEW=ROOT/'product/lab/release-candidates/v1/interface/typed-relation-schema-v4'
REGISTRY=ROOT/'authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json'


def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def load(path):return json.loads(path.read_bytes())
def value(schema):
    if 'const' in schema:return schema['const']
    if 'enum' in schema:return schema['enum'][0]
    kind=schema.get('type','string')
    if kind in ('integer','number'):return schema.get('minimum',0)
    if kind=='boolean':return False
    if kind=='array':return [value(schema.get('items',{})) for _ in range(schema.get('minItems',0))]
    if kind=='object':return {key:value(schema.get('properties',{}).get(key,{})) for key in schema.get('required',[])}
    return 'qualification-value'


def main():
    report=RUN/'typed-schema-successor-qualification-0128.json';assert not report.exists()
    old,new=load(OLD/'schema.json'),load(NEW/'schema.json')
    validator=Draft202012Validator(new);Draft202012Validator.check_schema(new)
    template=load(OLD/'fixtures/valid/record.json');template['schema_version']='cyberalchemy-lab-typed-relation/v4'
    cases=[];files=[REGISTRY,OLD/'schema.json',NEW/'schema.json',NEW/'artifact.json',NEW/'change.json',Path(__file__).resolve()]
    added=[];shape_checks=0
    for row in load(REGISTRY)['entries']:
        kind=row['relation_kind_ref'];path=ROOT/row['instance_path'];files.append(path)
        contract=load(path)['payload'];qc=contract['qualifier_contract']
        def branch(schema):
            return next(branch for branch in schema['allOf'] if branch.get('if',{}).get('properties',{}).get('payload',{}).get('properties',{}).get('relation_kind_ref',{}).get('const')==kind)
        old_branch,new_branch=copy.deepcopy(branch(old)),copy.deepcopy(branch(new))
        pairs=new_branch['then']['properties']['payload']['oneOf']
        actual={(pair['properties']['source']['properties']['kind']['const'],pair['properties']['target']['properties']['kind']['const']) for pair in pairs}
        declared={(pair['source_kind'],pair['target_kind']) for pair in contract['allowed_endpoint_pairs']}
        assert actual==declared and len(actual)==len(pairs),kind
        old_pairs=old_branch['then']['properties']['payload']['oneOf']
        extras=[pair for pair in pairs if pair not in old_pairs]
        added.extend({'relation_kind_ref':kind,'source_kind':pair['properties']['source']['properties']['kind']['const'],
                      'target_kind':pair['properties']['target']['properties']['kind']['const']} for pair in extras)
        new_branch['then']['properties']['payload']['oneOf']=old_pairs
        assert new_branch==old_branch,'an endpoint or qualifier contract changed beyond declared additions'
        shape_checks+=1
        for pair in contract['allowed_endpoint_pairs']:
            body=copy.deepcopy(template)
            body['payload'].update(relation_kind_ref=kind,
                source={'kind':pair['source_kind'],'ref':'source:qualification','version_ref':'source:qualification@1'},
                target={'kind':pair['target_kind'],'ref':'target:qualification','version_ref':'target:qualification@1'},
                qualifiers={axis:value(qc['properties'][axis]) for axis in qc['required_axes']})
            validator.validate(body);cases.append({'relation_kind_ref':kind,**pair,'result':'PASS'})
    assert len(cases)==550 and len(added)==8 and shape_checks==41
    # Closed authority/scope relation must still reject undeclared endpoint kinds.
    body=copy.deepcopy(template)
    body['payload'].update(relation_kind_ref='relation.scopes-authority-over',
        source={'kind':'principal','ref':'source:qualification','version_ref':'source:qualification@1'},
        target={'kind':'decision-scope','ref':'target:qualification','version_ref':'target:qualification@1'},
        qualifiers={'authority_role':'candidate-only','scope_ref':'scope:qualification'})
    assert not validator.is_valid(body)
    body=copy.deepcopy(template);body['authority_effect']='grant-permission';assert not validator.is_valid(body)
    body=copy.deepcopy(template);body['payload']['qualifiers']['undeclared-axis']='permission';assert not validator.is_valid(body)
    result={'schema_version':'lab-typed-schema-successor-qualification/v1-candidate','result':'PASS',
        'actual_schema_cases':550,'exact_pair_and_qualifier_contract_checks':41,'explicit_negative_cases':3,
        'added_schema_endpoint_branches':added,'files':[bind(path) for path in files],
        'native_registration_qualified':False,'actual_endpoint_sources_qualified':False,'semantic_pairs_added':0,
        'canonical_admissions':0,'authority_effect':'none','task_complete':False,'goal_complete':False,
        'claim_ceiling':'Actual complete550synthetic shape cases and41exact declared pair/qualifier comparisons only; native registration, source endpoints, public API and final owner admission remain unqualified.'}
    with report.open('x') as stream:json.dump(result,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':'PASS','schema_cases':550,'exact_contract_checks':41,'negative_cases':3,'report_binding':bind(report)}),flush=True)


if __name__=='__main__':main()
