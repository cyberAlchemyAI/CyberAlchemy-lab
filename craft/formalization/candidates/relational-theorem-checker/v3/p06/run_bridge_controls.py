"""Full exact rich qualification and actual supervised refusal controls."""
from pathlib import Path
import copy
import json
import sys
import threading
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sys.path.insert(0,str(BASE.parent))
from v3.p06.api import SupervisedQualifier
from v3.p03.context import C,QualificationContext,check
from v3.p03.qualification import inspect_saved
sys.path.insert(0,str(BASE/'execution'));import support as s
request=s.read(BASE/'p01/request-fixture.json');raw=json.dumps(request,ensure_ascii=False).encode()
policy=request['resource_policy'];controls=[];runs=[]
def control(name,ok):
    s.require(ok,'P06 bridge control failed: '+name)
    controls.append({'name':name,'result':'pass'})
    s.write(HERE/'bridge-controls-progress.json',{'complete':False,'controls':controls,'runs':runs})
def save(name,answer):
    p=HERE/(name+'.json');s.write(p,answer);runs.append(s.binding(p));return answer
api=SupervisedQualifier(HERE/'qualified-runs',policy)
answer=save('supervised-rich-result',api.qualify(raw))
control('actual-full-rich-pipeline-fresh-qualified',answer['status']=='qualified-candidate')
result=answer['qualified_result'];control('actual-live-event-after-supervisor-completion',api.live_event(result))
control('original-unchanged-request-and-resource-policy',result['request_identity']==C.identity(request) and result['resource_report']['policy_identity']==C.identity(policy))
control('all-twenty-fixed-obligations',result['manifest']['obligations']==[o['id'] for o in C.required_inventory('rule-only')])
payload=s.read(check(result['payload']));expected=s.read(check(s.read(BASE/'p03/shadow-result.json')['payload']))
control('semantic-equality-to-accepted-rich-pipeline',all(payload[k]==expected[k] for k in ['normal_form','before_normal_form','closure','certificates','observations','supports']))
control('actual-backend-and-reason-recorded',result['resource_report']['enforcement']=='advisory' and result['resource_report']['outcome']=='completed' and answer['supervised_run']['events'])
ctx=QualificationContext(HERE/'saved-inspection',policy)
inspection=save('supervised-saved-inspection',inspect_saved(request,result,ctx))
control('saved-inspection-current-but-not-new-event',inspection['status']=='recorded-current' and not ctx.live_event(result) and not inspection['application_authorized'])
other=SupervisedQualifier(HERE/'other-session',policy)
control('new-session-does-not-rehydrate-event',not other.live_event(result))
mutated=copy.deepcopy(result);mutated['resource_report']['events'][0]['detail']='changed'
control('modified-result-does-not-reuse-event',not api.live_event(mutated))
def negative(name,data,selected_policy=policy,cancel=None):
    r=save(name,SupervisedQualifier(HERE/'refusal-runs',selected_policy).qualify(data,cancel=cancel))
    control(name+'-has-no-qualified-receipt',r['qualified_result'] is None and not r['claims'] and not r['complete_closure'] and not r['application_authorized'])
    run=r['supervised_run']
    if run and 'job' in run:control(name+'-has-no-issued-file',not (Path(run['job'])/'result.json').exists() and not (Path(run['job'])/'completion.json').exists())
    return r
duplicate=negative('duplicate-key-result',b'{"x":1,"x":2}');control('duplicate-key-invalid',duplicate['status']=='invalid')
nonfinite=negative('nonfinite-result',b'{"x":NaN}');control('nonfinite-invalid',nonfinite['status']=='invalid')
large=negative('large-input-result',b' '* (policy['work_limits']['input_bytes']+1));control('byte-ceiling-before-launch',large['status']=='unknown-resource' and large['supervised_run'] is None)
required=copy.deepcopy(policy);required['memory_mode']='required'
r=negative('required-unavailable-result',raw,required);control('host-required-backend-unavailable-refuses-before-worker',r['status']=='unsupported-policy' and 'job' not in r['supervised_run'])
tiny=copy.deepcopy(policy);tiny['run_seconds']=.01
r=negative('whole-timeout-result',raw,tiny);control('whole-deadline-includes-decoding-and-construction',r['status']=='unknown-resource' and r['supervised_run']['outcome']=='timeout')
cancel=threading.Event();timer=threading.Timer(.15,cancel.set);timer.start()
try:r=negative('cancelled-pipeline-result',raw,policy,cancel)
finally:timer.cancel()
control('cancelled-pipeline-no-issued-result',r['status']=='cancelled')
low=copy.deepcopy(policy);low['output_bytes']=1
low_request=copy.deepcopy(request);low_request['resource_policy']=low
r=negative('tiny-output-result',json.dumps(low_request).encode(),low)
control('atomic-stream-output-exhaustion',r['status']=='unknown-resource')
mismatch=copy.deepcopy(policy);mismatch['stage_seconds']=59
r=negative('mismatched-policy-result',raw,mismatch)
control('operator-request-policy-mismatch-invalid',r['status']=='invalid' and 'policy' in r['reason'])
control('recipe-roundtrip-exact',s.read(HERE/'pipeline-recipe-review.json')['roundtrip_to_retained_recipe']=='exact')
control('supervisor-cleanup-before-issuance',answer['supervised_run']['complete'] and answer['supervised_run']['cleanup']['remaining_pids']==[])
report={'result':'pass','qualification_bridge_complete':True,'controls':controls,'runs':runs,
        'hard_cgroup_memory_tested':False,'enforcement_on_this_host':'advisory',
        'required_memory_on_this_host':'unsupported-policy before launch',
        'source_bindings':api.sources,'authority_effect':'none'}
s.write(HERE/'bridge-controls.json',report)
print('P06 full qualification bridge passed: '+str(len(controls))+' controls',flush=True)
