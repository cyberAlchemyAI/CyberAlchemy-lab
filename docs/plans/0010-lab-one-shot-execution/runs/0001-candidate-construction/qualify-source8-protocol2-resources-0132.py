"""Exact original/new resource isolation, closed carrier and schema checks."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from jsonschema import Draft202012Validator

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';API=BASE/'api-v93';PACKAGE=BASE/'source8-protocol-v2'
PIN='3860df6653827f4d51d586e39da71dbfe2154d7995fa397c6bba5b0f18bb4cd3'
PROFILE='cc1c9b0313b20a53ed8d860f595d9e34b458aa97a4df1bdfc2f73f0a9b39340a'
def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def main():
    output=RUN/'source8-protocol2-resource-qualification-0132.json';assert not output.exists()
    spec=importlib.util.spec_from_file_location('_cal_API93_resource_guard',API/'guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard);guard.verify(PIN)
    name='_cal_API93_resources_actual';spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    P=__import__(name+'.protocol',fromlist=['*']);schemas=P.Schemas(PROFILE)
    selection=json.loads((PACKAGE/'selection.json').read_bytes());checks=[]
    def check(name,value):assert value,name;checks.append({'check':name,'result':'PASS'})
    check('negotiated-profile-v4',schemas.profile['schema_version']=='lab-operator-contract-profile/v4-candidate')
    check('97-unique-versioned-resources',len(selection['resources'])==len(set(selection['uri_mapping'].values()))==97)
    for row in selection['resources']:
        doc=json.loads((ROOT/row['selected_binding']['path']).read_bytes());Draft202012Validator.check_schema(doc)
        check('closed-resource:'+row['original_uri'],doc['$id']==row['selected_uri']!=row['original_uri'])
    header=json.loads((BASE/'challenge-resolution-v6/reference-role-contract.json').read_bytes())['goal_scope']['membership']
    common='urn:cyberalchemy-lab:protocol:common:v1-candidate'
    old=Draft202012Validator({'$ref':common+'#/$defs/artifact_ref'},registry=schemas.registry)
    new=Draft202012Validator({'$ref':schemas.uri_mapping[common]+'#/$defs/artifact_ref'},registry=schemas.registry)
    check('original-resource-still-refuses-v4',not old.is_valid(header));check('selected-resource-accepts-exact-v4-header',new.is_valid(header))
    for field,value in [('carrier_ref','cal.artifact-type.typed-relation/v99'),('carrier_ref','cal.artifact-type.unselected/v1'),
        ('byte_sha256','unbound'),('identity_ref',''),('version_ref',''),('scope_ref','')]:
        changed=copy.deepcopy(header);changed[field]=value;check('refuse-'+field+'-'+value,not new.is_valid(changed))
    changed=copy.deepcopy(header);changed['implicit_authority']=True;check('closed-header-refuses-extra-field',not new.is_valid(changed))
    source=BASE/'current-participation-v8/packages/0001/artifacts/14.json';body=json.loads(source.read_bytes())
    domain='urn:cyberalchemy-lab:protocol:domain-artifact:v1-candidate'
    check('current-original-v4-body-conforms',schemas.protocol_valid(domain,{'carrier_ref':header['carrier_ref'],'body':body}))
    check('original-domain-does-not-admit-v4',not Draft202012Validator({'$ref':domain},registry=schemas.registry).is_valid({'carrier_ref':header['carrier_ref'],'body':body}))
    for label,mutate in [('unknown-qualifier',lambda x:x['payload']['qualifiers'].update(implicit_authority=True)),
        ('wrong-discriminator',lambda x:x.update(schema_version='cyberalchemy-lab-typed-relation/v3')),
        ('undeclared-relation',lambda x:x['payload'].update(relation_kind_ref='relation.unselected'))]:
        changed=copy.deepcopy(body);mutate(changed);check('refuse-v4-'+label,not schemas.protocol_valid(domain,{'carrier_ref':header['carrier_ref'],'body':changed}))
    schemas.guard();guard.verify(PIN)
    value={'schema_version':'lab-source8-resource-qualification/v1-candidate','result':'PASS','actual_checks':len(checks),'checks':checks,
        'files':[bind(p) for p in [API/'source-manifest.json',API/'contract-profile.json',PACKAGE/'selection.json',PACKAGE/'resources.py',source,Path(__file__).resolve()]],
        'source_guarded_exit_completed':True,'actual_public_query_inspection_qualified':False,'whole_API_qualified':False,
        'task_complete':False,'goal_complete':False,'authority_effect':'none','actual_owner_outcome':None,
        'claim_ceiling':'Selected negotiated resource schema/identity/closed carrier isolation only; current host query/inspection and full API require separate execution.'}
    with output.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':'PASS','actual_checks':len(checks),'report_binding':bind(output)}))
if __name__=='__main__':main()
