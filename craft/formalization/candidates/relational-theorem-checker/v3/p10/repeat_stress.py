"""Repeat the exact preflight-valid proof-deadline case without changing policy/code."""
from pathlib import Path
import json
import sys
import time
import uuid
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sys.path.insert(0,str(BASE.parent))
from v3.p03.context import C,ROOT,binding,check,require
from v3.p10.api import Client
from v3.p10.timing import validate_tree

prior=C.decode((HERE/'benchmark-results.json').read_bytes());original=prior['samples'][-1]
require(original['name']=='rich-three-variables' and original['status']=='unknown-resource','repeat requires observed original boundary')
request=C.decode(check(original['input']).read_bytes());run_id=uuid.uuid4().hex
root=BASE/'p07/consumer-runs'/('P10-stress-repeat-'+run_id);client=Client(request['resource_policy'],root)
started=time.monotonic();answer=client.qualify(check(original['input']).read_bytes());seconds=time.monotonic()-started
require(answer['status'] in ['qualified-candidate','unknown-resource'],'unexpected stress repeat outcome')
qualified=answer['status']=='qualified-candidate';owned=answer['qualification'];run=owned['supervised_run'];job=Path(run['job'])
require(client.live_event(answer)==qualified,'repeat live event disagrees with actual outcome')
trace=C.decode((job/'timings.json').read_bytes())['stages'];validate_tree(trace)
typed=C.decode(next(job.glob('builds/*/typed-input.json')).read_bytes())
require(typed['bounds']['outcome']=='within-envelope' and typed['bounds']['upper_bounds']['ground_candidates']==4144,'repeat preflight changed')
path=HERE/'evidence'/prior['run_id']/('rich-three-variables-repeat-'+run_id+'.json');path.write_text(json.dumps(answer,indent=2)+'\n')
sample={**original,'name':'rich-three-variables-repeat','output':binding(path),'status':answer['status'],'actual_kernel_completion':qualified,
    'client_seconds':seconds,'supervised_seconds':run['seconds'],'memory':{'backend':run['enforcement'],'peak_aggregate_rss_observed':run['aggregate_rss_peak_observed'],
        'hard_aggregate_cap':run['enforcement']=='cgroup-v2','policy_bytes':request['resource_policy']['memory_bytes']},
    'output_bytes_observed':run['output_bytes_observed'],'stage_tree':trace,'cache_check':binding(next(job.glob('builds/*/cache-check.json'))),
    'required_ids':owned['qualified_result']['manifest']['obligations'] if qualified else []}
if qualified:
    payload=C.decode(check(owned['qualified_result']['payload']).read_bytes());sample['workload']={**original['workload'],'typed_instances':payload['counters']['typed_instances']}
else:require(not owned['claims'] and not owned['complete_closure'],'repeat refusal acquired a closure claim')
(HERE/'benchmark-results-initial.json').write_bytes((HERE/'benchmark-results.json').read_bytes())
prior['samples'].append(sample);prior['runtime_roots'].append(str(root.relative_to(ROOT)))
prior['controls'] += [{'name':n,'result':'pass'} for n in ['stress-repeat-exact-input-and-policy','stress-repeat-actual-preflight-within-envelope','stress-repeat-completion-or-explicit-no-claim-refusal']]
(HERE/'benchmark-results.json').write_text(json.dumps(prior,indent=2)+'\n')
report={'result':'pass','original_sample':binding(HERE/'benchmark-results-initial.json'),'repeat_input':original['input'],'repeat_output':binding(path),
    'outcome':answer['status'],'seconds':seconds,'scope':'One actual exact-input repeat. A different outcome is retained as observed variation, not concealed or extrapolated.','authority_effect':'none'}
(HERE/'stress-repeat.json').write_text(json.dumps(report,indent=2)+'\n');print('Stress repeat:',answer['status'],'seconds',round(seconds,3),flush=True)
