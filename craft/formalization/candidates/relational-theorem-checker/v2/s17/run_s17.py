from pathlib import Path
import sys,copy,time,itertools,subprocess,os
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'s15'));import contracts as c
sys.path.insert(0,str(Path(__file__).resolve().parent));import resources as r
s=c.s;HERE=Path(__file__).resolve().parent
s.context('S17',[(s.BASE/'s15/baseline-example.json','declared rich finite workload'),(s.BASE/'s15/selected-profile.json','selected profile'),(s.BASE/'s02/projection-audit.json','contextual projection bounds'),(s.BASE/'s16/sealed-producer-controls.json','sealed facts and rule policy'),(s.V1/'inference/closure/ClosureAdequacy.lean','reference choices/enumeration/termination')],[{'decision':'Bound reference untyped enumeration conservatively; reject before products; retain unknown-resource distinct','basis':'finite universe and measured selected workload'}])
s.write(HERE/'preflight-bounds.json',{'schema':'relational.resource-budget/v2','limits':{'input_bytes':4194304,'json_depth':64,'nodes':128,'assertions':256,'assessments':256,'domain':32,'rules':16,'predicates':16,'variables':4,'arity':4,'ground_candidates':50000,'atom_candidates':3000000,'stress_candidates':256,'conflict_pairs':65536,'saturation_steps':50000,'certificate_steps':50000,'lean_stage_seconds':60},'implementation':'pre-allocation conservative capped-power counters; process timeout for Lean; final complete checks required','scope':'local bounded reference profile, no throughput/latency guarantee','authority_effect':'none'})
b=c.fixture();controls=[]
def test(name,fn,positive=False):
 try:
  value=fn();s.require(positive,'accepted hostile '+name);controls.append({'name':name,'result':'pass','outcome':'within-envelope','bounds':value})
 except r.Exhausted as e:
  s.require(not positive,'positive exhausted');controls.append({'name':name,'result':'pass','outcome':'unknown-resource','reason':str(e),'products_allocated':0})
def mutate(fn):
 q=copy.deepcopy(b);fn(q);return r.preflight(q)
test('selected-rich-nonempty-baseline',lambda:r.preflight(b),True)
test('huge-variable-list-small-graph',lambda:mutate(lambda q:q['inference']['rules'][0]['body'].append({'predicate':'Conforms','terms':[{'variable':'x'+str(n)} for n in range(1000)]})))
test('large-domain-small-graph',lambda:mutate(lambda q:q['inference']['domain'].extend([{'kind':'text','value':'new'+str(n)} for n in range(10000)])))
test('huge-arity-small-domain',lambda:mutate(lambda q:q['inference']['predicates'][-1].update(sorts=['reference']*1000)))
test('grounding-envelope',lambda:mutate(lambda q:q['inference']['rules'].extend([{'head':{'terms':[]},'body':[{'terms':[{'variable':f'v{x}'} for x in range(4)]}]}]*5)))
test('conflict-pair-preallocation',lambda:r.preflight(b,{'inheritances':[1]*20,'norms':[1]*20}))
s.require(r.capped_pow(2,10**100,50000)==50001,'capped exponent guard failed')
controls.append({'name':'enormous-exponent-capped-before-integer-growth','result':'pass','outcome':'rejected-bound','products_allocated':0})
# Fresh small reference probe measures actual products separately from estimates.
probe=[]
for size,vars in [(2,1),(8,2),(16,3)]:
 start=time.monotonic();count=sum(1 for _ in itertools.product(range(size),repeat=vars));elapsed=time.monotonic()-start
 s.require(count==size**vars,'reference bound mismatch');probe.append({'domain':size,'variables':vars,'upper_bound':size**vars,'observed_candidates':count,'seconds':elapsed})
# A controlled subprocess timeout checks the operational path. It is not a
# prediction of proof replay duration; the runtime will use the same timeout classification.
try:subprocess.run([sys.executable,'-c','while True: pass'],timeout=0.05,capture_output=True);raise ValueError('timeout control did not time out')
except subprocess.TimeoutExpired:controls.append({'name':'proof-process-timeout-classification','result':'pass','outcome':'unknown-resource','complete_closure':False,'absence':False,'readiness':False})
logs=s.compile_modules(HERE/'build',s.core_modules({'InferenceCore','DerivationSoundness','ClosureAdequacy'})+[('ResourceContract',HERE/'ResourceContract.lean')])
s.write(HERE/'feasibility-probe.json',{'result':'pass','reference_probes':probe,'selected_bounds':r.preflight(b),'formal_modules':logs,'observations':'Small finite reference enumeration only; broader end-to-end costs S11','authority_effect':'none'})
s.write(HERE/'budget-controls.json',{'result':'pass','controls':controls,'resource_contract':'exhaustion cannot discharge closure/absence/readiness','authority_effect':'none'})
s.accept('S17',['Resource contract and measured reference probes precede integration; separate bound/observed counters.','Hostile domain/variables/arity/ground/conflict cases reject before products; capped exponents avoid giant allocation.','Limits define a bounded profile and unknown-resource outcomes; no promised latency or scale.'],controls=controls,extra_dependencies=[HERE/'resources.py'])
print('S17 accepted: preallocation bounds and '+str(len(controls))+' resource controls.')
