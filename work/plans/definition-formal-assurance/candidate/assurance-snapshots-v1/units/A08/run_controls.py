"""Retain actual searches, including incomplete/unresolved control outcomes."""
import importlib.util
import json
import sys
from pathlib import Path
UNIT=Path(__file__).resolve().parent;ROOT=UNIT.parents[6];IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1';sys.path.insert(0,str(IMPL))
loader=importlib.util.spec_from_file_location('governance_v2',IMPL/'pilot-v2.py');v=importlib.util.module_from_spec(loader);loader.loader.exec_module(v)


def put(name,value):
    path=UNIT/name
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True,allow_nan=False);stream.write('\n')
    return {'path':path.relative_to(ROOT).as_posix(),'sha256':v.r.digest(path.read_bytes())}


def main():
    refs=[]
    cases=[('positive',{}),('collapse',{'constraints':['trace-implies-position'],'mode':'exhaustive','stop':240}),('contradiction',{'constraints':['no-position','some-position'],'mode':'exhaustive','stop':90}),('missing-population',{'constraints':['no-right'],'mode':'exhaustive','stop':240}),('full-range-budget-stop',{'mode':'exhaustive'}),('one-configuration-limit',{'mode':'exhaustive','budgets':{'max_interpretations':1}}),('step-limit',{'budgets':{'max_evaluation_steps':1}}),('output-limit',{'budgets':{'max_output_bytes':8192}}),('deadline',{'budgets':{'timeout_seconds':0.000000001}}),('cancellation',{'cancelled':lambda:True})]
    for name,request in cases:
        result=v.search(**request);ref=put(name+'-search.json',result);refs.append({'case_id':name,'request':{key:value for key,value in request.items() if key!='cancelled'},'cancel_policy':'immediate user callback' if name=='cancellation' else None,'result_ref':ref,'status':result['status'],'counts':result['counts']})
        print(json.dumps({'case':name,'status':result['status'],'counts':result['counts']}),flush=True)
    prepared=v.prepare();records=[]
    for name,index,path,permit,duty,claim in [('ungranted-assertion',0,'complete',False,False,'right'),('unclaimed-grant',0,'complete',True,False,'none'),('duty-without-permission',0,'complete',False,True,'responsibility'),('right-duty-overlap',0,'complete',True,True,'both'),('incomplete-claim-with-grant',0,'complete',True,False,'incomplete-right'),('unknown-origin-with-grant',0,'unknown',True,False,'right'),('local-trace-with-grant',0,'source-local',True,False,'right')]:
        state=v.make_state(index,path,permit,duty,claim);records.append({'case_id':name,'state':state,'actual':v.record_values(state,v.Control(v.f.load_limits()))})
    transitions=[]
    for name,rank in [('provenance-only',0),('silent-status',1),('explicit-status',2),('unrelated-subject',0)]:
        world=v.point(rank)
        if name=='unrelated-subject':world['transition']['move']['subject_id']=v.SUBJECTS[1]
        transitions.append({'case_id':name,'model':world,'transition_holds':v.transition_holds(world['transition'],world['records'],v.Control(v.f.load_limits()))})
    values_ref=put('record-transition-controls.json',{'authority_effect':'none','semantic_ready':False,'record_cases':records,'transition_cases':transitions,'claim_ceiling':'Hypothetical records; independently implemented A08 predicates, not independent A09 verification or actual owner acts.'})
    put('worked-controls.json',{'schema_version':'definition-assurance-worked-controls/v1-candidate','authority_effect':'none','searches':refs,'record_transition_ref':values_ref,'next_unit':'A09.1','independent_replay':'pending','full_definition_fidelity':'pending','full_project_completion':'not-established'})


if __name__=='__main__':main()
