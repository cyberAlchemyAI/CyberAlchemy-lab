"""Full instrumented rich cold/warm qualification and one primary stress dimension."""
from pathlib import Path
import copy
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

run_id=uuid.uuid4().hex;root=HERE/'evidence'/run_id;root.mkdir(parents=True)
source=C.decode((BASE/'p09/rich-combined-request.json').read_bytes());source['layout']='staged'
samples=[];controls=[];read_timings=[]
def test(name,ok):require(ok,name);controls.append({'name':name,'result':'pass'});print(name,'PASS',flush=True)
def save(name,value):
    p=root/(name+'.json');require(not p.exists(),'benchmark evidence overwrite refused');p.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n');return binding(p)
def progress():
    (HERE/'benchmark-progress.json').write_text(json.dumps({'status':'in-progress','run_id':run_id,'samples':samples,'controls':controls,'read_timings':read_timings,'authority_effect':'none'},indent=2)+'\n')
def semantic(answer):
    q=answer['qualification']['qualified_result'];p=C.decode(check(q['payload']).read_bytes())
    return {k:p[k] for k in ['normal_form','closure','certificates','supports','observations','model_class','closure_scope']}
def measure(name,request):
    input_ref=save(name+'-request',request);data=check(input_ref).read_bytes()
    client=Client(request['resource_policy'],BASE/'p07/consumer-runs'/('P10-'+name+'-'+run_id))
    started=time.monotonic();answer=client.qualify(data);elapsed=time.monotonic()-started
    output=save(name+'-result',answer);owned=answer['qualification'];run=owned['supervised_run'] or {};job=Path(run['job']) if run.get('job') else None
    trace=C.decode((job/'timings.json').read_bytes())['stages'] if job and (job/'timings.json').exists() else []
    validate_tree(trace)
    qualified=answer['status']=='qualified-candidate';payload=None;info=None
    if qualified:
        test(name+'-actual-live-complete',client.live_event(answer));q=owned['qualified_result'];payload=C.decode(check(q['payload']).read_bytes())
        test(name+'-fixed-twenty-obligations',q['manifest']['obligations']==[o['id'] for o in C.required_inventory('rule-only')])
        info=payload
    else:
        test(name+'-explicit-safe-refusal',answer['status']=='unknown-resource' and not client.live_event(answer) and not owned['claims'])
        typed=list(job.glob('builds/*/typed-input.json')) if job else []
        if typed:info=C.decode(typed[0].read_bytes())
    test(name+'-policy-unchanged',owned['policy_identity']==C.identity(source['resource_policy']))
    bounds=info['bounds'] if info else None
    inference=request['proposal']['after']['inference'];variables=[]
    for rule in inference['rules']:
        variables.append(len({t['variable'] for atom in [rule['head'],*rule['body']] for t in atom['terms'] if 'variable' in t}))
    grounding=sum(len(inference['domain'])**n for n in variables)
    if bounds:test(name+'-preflight-within-envelope',bounds['outcome']=='within-envelope' and bounds['upper_bounds']['ground_candidates']==grounding)
    cache=job/'builds' if job else None;cache_files=list(cache.glob('*/cache-check.json')) if cache and cache.exists() else []
    sample={'name':name,'input':input_ref,'output':output,'build_mode':request['build_mode'],'layout':request['layout'],
        'workload':{'domain':len(inference['domain']),'predicates':len(inference['predicates']),'rules':len(inference['rules']),
                    'maximum_rule_variables':max(variables),'ground_candidates':grounding,'typed_instances':payload['counters']['typed_instances'] if payload else None},
        'resource_policy':request['resource_policy'],'status':answer['status'],'actual_kernel_completion':qualified,
        'supervised_seconds':run.get('seconds'),'client_seconds':elapsed,
        'memory':{'backend':run.get('enforcement','unavailable'),'peak_aggregate_rss_observed':run.get('aggregate_rss_peak_observed'),
                  'hard_aggregate_cap':run.get('enforcement')=='cgroup-v2','policy_bytes':request['resource_policy']['memory_bytes']},
        'output_bytes_observed':run.get('output_bytes_observed'),'stage_tree':trace,'required_ids':owned['qualified_result']['manifest']['obligations'] if qualified else [],
        'cache_check':binding(cache_files[0]) if cache_files else None,
        'measurement_scope':'Actual full supervised invocation under unchanged policy. Cold means recompiled local dependencies; OS page-cache state and other host load are not controlled. Timed context delegates all checking to accepted implementation.',
        'authority_effect':'none'}
    samples.append(sample);progress();print(name,answer['status'],'client seconds',round(elapsed,3),flush=True)
    return client,answer

cold=copy.deepcopy(source);cold['build_mode']='cold';cold_client,cold_answer=measure('rich-cold',cold)
warm=copy.deepcopy(source);warm['build_mode']='warm';warm_client,warm_answer=measure('rich-warm',warm)
if cold_answer['status']=='qualified-candidate' and warm_answer['status']=='qualified-candidate':
    test('cold-warm-exact-semantic-agreement',semantic(cold_answer)==semantic(warm_answer))
test('warm-full-proof-completion',warm_answer['status']=='qualified-candidate')
q=warm_answer['qualification']['qualified_result'];payload=C.decode(check(q['payload']).read_bytes());atom=next(a for a in payload['closure'] if a['predicate']['id']=='ContractReady')
for name,operation in [('saved-inspection',lambda:warm_client.inspect(warm,warm_answer)),('positive-explanation',lambda:warm_client.describe(warm,warm_answer,atom))]:
    started=time.monotonic();value=operation();seconds=time.monotonic()-started;ref=save(name,value)
    read_timings.append({'name':name,'seconds':seconds,'output':ref,'scope':'Read-only parent operation; no new kernel invocation/application event or aggregate memory cap.'});progress()
    test(name+'-correct',value.get('status',value.get('outcome')) in ['recorded-current','present'])
stress=copy.deepcopy(warm);rule=next(r for r in stress['proposal']['after']['inference']['rules'] if r['id']=='review-exact-contract-scope')
rule['version']='v3-performance-three-variables'
rule['body'] += [{'predicate':'Conforms','terms':[{'variable':v}]} for v in ['y','z']]
test('stress-keeps-primary-other-dimensions',stress['proposal']['before']==warm['proposal']['before'] and stress['proposal']['after']['inference']['domain']==warm['proposal']['after']['inference']['domain'] and stress['proposal']['after']['inference']['predicates']==warm['proposal']['after']['inference']['predicates'] and len(stress['proposal']['after']['inference']['rules'])==len(warm['proposal']['after']['inference']['rules']))
C.validate('request',stress);stress_client,stress_answer=measure('rich-three-variables',stress)
test('stress-actual-normalization-completed',samples[-1]['cache_check'] is not None and samples[-1]['workload']['ground_candidates']==4144)
report={'result':'pass','run_id':run_id,'samples':samples,'read_timings':read_timings,'controls':controls,
    'source':binding(BASE/'p09/rich-combined-request.json'),'runtime_roots':[str((BASE/'p07/consumer-runs'/('P10-'+s['name']+'-'+run_id)).relative_to(ROOT)) for s in samples],
    'scope':'Measured rich cold/warm/stress invocations, not general latency/throughput. Any refusal remains nonqualified.','authority_effect':'none'}
(HERE/'benchmark-results.json').write_text(json.dumps(report,indent=2)+'\n');print('Benchmark run complete:',len(samples),'samples',flush=True)
