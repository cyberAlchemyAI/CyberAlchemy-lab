"""Construct unfrozen successors; immutable predecessors and signed fixtures stay exact."""
import copy
import hashlib
import json
from pathlib import Path
import shutil

RUN=Path(__file__).resolve().parent; ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
API=BASE/'api-v88'; COMPONENT=BASE/'challenge-resolution-v4'

def binding(path):
    return {'ref':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def emit(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
def replace(path,before,after):
    text=path.read_text();assert before in text,(path,before);path.write_text(text.replace(before,after))

def main():
    for old,new in [('api-v87','api-v88'),('challenge-resolution-v3','challenge-resolution-v4'),('lesson-host-composition-v37','lesson-host-composition-v38')]:
        shutil.copytree(BASE/old,BASE/new,ignore=shutil.ignore_patterns('receipts','__pycache__','source-manifest.json','contract-profile.json'))
    old_kind='lab-local-integrated-challenge-resolution-policy/v2-candidate'
    new_kind='lab-local-integrated-challenge-resolution-policy/v3-candidate'
    replace(COMPONENT/'preparation.py',old_kind,new_kind)
    replace(API/'auth.py',"integrated=value['schema_version']=='"+old_kind+"'", "reference_resolution=value['schema_version']=='"+new_kind+"'\n        integrated=reference_resolution or value['schema_version']=='"+old_kind+"'")
    replace(API/'auth.py',"if integrated:fields+=['integrated_source_control']", "if integrated:fields+=['integrated_source_control']\n        if reference_resolution:fields+=['resolution_reference_control']")
    replace(API/'auth.py',"'"+old_kind+"')", "'"+old_kind+"','"+new_kind+"')")
    replace(API/'auth.py',"('challenge-resolution-v3' if integrated else 'challenge-resolution-v1')", "('challenge-resolution-v4' if reference_resolution else 'challenge-resolution-v3' if integrated else 'challenge-resolution-v1')")
    replace(API/'auth.py',"if failure:\n            from .workspace", "if reference_resolution:\n            from .challenge_resolution import implementation\n            method,_=implementation(value)\n            method.validate_reference_control(value)\n        if failure:\n            from .workspace")
    replace(API/'challenge_resolution.py',"version='v3' if policy", "version='v4' if policy['schema_version']=='"+new_kind+"' else 'v3' if policy")
    for path in API.glob('*.py'):
        if 'lesson-host-composition-v37' in path.read_text():replace(path,'lesson-host-composition-v37','lesson-host-composition-v38')
    for path in (BASE/'lesson-host-composition-v38').glob('*.py'):
        if 'api-v87' in path.read_text():replace(path,'api-v87','api-v88')
    schema_path=API/'authentication.schema.json';schema=json.loads(schema_path.read_bytes())
    branch=copy.deepcopy(schema['oneOf'][-1]);assert branch['properties']['schema_version']['const']==old_kind
    branch['properties']['schema_version']['const']=new_kind
    branch['properties']['resolution_reference_control']={'type':'object','additionalProperties':False,
        'properties':{name:{'$ref':'urn:cyberalchemy-lab:protocol:common:v1-candidate#/$defs/binding'} for name in ('resolver_binding','contract_binding')},
        'required':['resolver_binding','contract_binding']}
    branch['required'].append('resolution_reference_control');schema['oneOf'].append(branch)
    schema_path.write_text(json.dumps(schema,indent=2,sort_keys=True)+'\n')
    package=BASE/'current-participation-v8/packages/0001';plan=json.loads((package/'resolution-qualification-plan.json').read_bytes())
    routing=json.loads((package/'qualification-workspace/objects'/(plan['routing_binding']['sha256']+'.json')).read_bytes())
    definition=ROOT/'authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/work/v1/definition.json'
    delivery=ROOT/'docs/proposals/0007-lab-integrated-schema-package/schemas/context-delivery.schema.json'
    contract={'schema_version':'lab-exact-resolution-reference-roles/v1-candidate','source_cut':plan['source_cut'],
        'routing_binding':plan['routing_binding'],'scope_ref':routing['scope_ref'],
        'work':routing['subject'],'challenge':plan['message']['challenge'],'decision':plan['message']['resolution_decision'],
        'expected_output':{'selector':'/payload/output_refs/0','requested_ref':'protocol:R03-fresh-context-delivery',
            'role':'expected-output-protocol-declaration','contract_binding':binding(delivery),
            'contract_id':'urn:cyberalchemy-lab:protocol:context-delivery:v1-candidate','eligible_completion_state':'pending',
            'actual_output_asserted':False,'work_satisfaction_asserted':False},
        'historical_subject':{'role':'exact-challenged-version','eligible_relation_kind':'relation.challenges',
            'eligible_carrier':'cal.artifact-type.challenge-event/v1','current_authority_asserted':False},
        'definition_binding':binding(definition),'canonical_admission_granted':False,'authority_effect':'none'}
    emit(COMPONENT/'reference-role-contract.json',contract)
    print(json.dumps({'result':'CONSTRUCTED','api':str(API),'component':str(COMPONENT),'role_contract_binding':binding(COMPONENT/'reference-role-contract.json')}))

if __name__=='__main__':main()
