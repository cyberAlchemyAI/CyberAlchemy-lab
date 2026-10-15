"""Actual selected resolver contract/control checks; no synthetic host episode."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from jsonschema import Draft202012Validator

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';API=BASE/'api-v90';COMPONENT=BASE/'challenge-resolution-v5'
PIN='fa54a5c2724d1ea065f30946f763ee8780f5588bc0abae35e484cae2520cd023'

def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def main():
    report=RUN/'reference-selection-qualification-0131.json';assert not report.exists()
    spec=importlib.util.spec_from_file_location('_cal_API90_contract_guard',API/'guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard);guard.verify(PIN)
    name='_cal_exact_reference_roles5'
    spec=importlib.util.spec_from_file_location(name,COMPONENT/'__init__.py',submodule_search_locations=[str(COMPONENT)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    selected=__import__(name+'.reference_roles',fromlist=['validate_control'])
    contract=json.loads((COMPONENT/'reference-role-contract.json').read_bytes())
    policy={'schema_version':selected.KIND,'scope_refs':[contract['scope_ref']],
        'resolution_control':{'routing_binding':contract['routing_binding']},
        'resolution_reference_control':{'resolver_binding':{'ref':bind(COMPONENT/'reference_roles.py')['path'],'sha256':bind(COMPONENT/'reference_roles.py')['sha256']},
            'contract_binding':{'ref':bind(COMPONENT/'reference-role-contract.json')['path'],'sha256':bind(COMPONENT/'reference-role-contract.json')['sha256']}}}
    checks=[]
    control,actual=selected.validate_control(policy);assert actual==contract
    checks.append({'check':'actual-selected-control-and-contract','result':'PASS'})
    mutations=[]
    for key in policy:
        v=copy.deepcopy(policy);del v[key];mutations.append(('missing-policy-'+key,v))
    for key in ('resolver_binding','contract_binding'):
        for field in ('ref','sha256'):
            v=copy.deepcopy(policy);v['resolution_reference_control'][key][field]='unselected';mutations.append(('changed-'+key+'-'+field,v))
    for key,value in [('schema_version','lab-local-integrated-challenge-resolution-policy/v2-candidate'),('scope_refs',['project:unselected'])]:
        v=copy.deepcopy(policy);v[key]=value;mutations.append(('unselected-'+key,v))
    v=copy.deepcopy(policy);v['resolution_control']['routing_binding']['sha256']='0'*64;mutations.append(('changed-signed-routing',v))
    v=copy.deepcopy(policy);v['resolution_reference_control']['extra']=True;mutations.append(('extra-control-field',v))
    for name,value in mutations:
        try:selected.validate_control(value)
        except (ValueError,KeyError):pass
        else:raise AssertionError('accepted '+name)
        checks.append({'check':name,'result':'PASS','unselected-control-refused':True})
    validator=Draft202012Validator(json.loads((COMPONENT/'reference-role-contract.schema.json').read_bytes()))
    validator.validate(contract)
    for key in contract:
        changed=copy.deepcopy(contract);del changed[key];assert not validator.is_valid(changed)
        checks.append({'check':'closed-contract-requires-'+key,'result':'PASS'})
    for name,selector,value in [
        ('produced-output',['expected_output','actual_output_asserted'],True),
        ('completed-work',['expected_output','eligible_completion_state'],'complete'),
        ('work-satisfaction',['expected_output','work_satisfaction_asserted'],True),
        ('historical-authority',['historical_subject','current_authority_asserted'],True),
        ('other-historical-relation',['historical_subject','eligible_relation_kind'],'relation.member-of'),
        ('other-historical-carrier',['historical_subject','eligible_carrier'],'cal.artifact-type.agent-assignment/v1'),
        ('changed-expected-protocol',['expected_output','requested_ref'],'protocol:unselected'),
        ('different-source-cut',['source_cut','commit_sha256'],'0'*64),
        ('canonical-admission',['canonical_admission_granted'],True),
        ('implicit-authority',['authority_effect'],'admission')]:
        changed=copy.deepcopy(contract);at=changed
        for key in selector[:-1]:at=at[key]
        at[selector[-1]]=value;assert not validator.is_valid(changed)
        checks.append({'check':'refuse-'+name,'result':'PASS'})
    guard.verify(PIN)
    value={'schema_version':'lab-exact-reference-selection-qualification/v1-candidate','result':'PASS','actual_checks':len(checks),'checks':checks,
        'files':[bind(p) for p in [API/'source-manifest.json',COMPONENT/'reference_roles.py',COMPONENT/'reference-role-contract.json',
            COMPONENT/'reference-role-contract.schema.json',ROOT/contract['definition_binding']['ref'],
            ROOT/contract['expected_output']['contract_binding']['ref'],Path(__file__).resolve()]],
        'actual_host_resolution_qualified':False,'source_guarded_exit_completed':True,'task_complete':False,'goal_complete':False,
        'authority_effect':'none','actual_owner_outcome':None,
        'claim_ceiling':'Actual selected reference code, exact contract schema and independently selected control refusals only. No host, source, native proposal, public resolution or full API qualification is inferred.'}
    with report.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':'PASS','actual_checks':len(checks),'report_binding':bind(report)}))

if __name__=='__main__':main()
