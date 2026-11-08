from pathlib import Path
import sys,copy,time,subprocess,json,resource as usage
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'s06'));import runtime as r
s=r.s;HERE=Path(__file__).resolve().parent
s.context('S11',[(s.BASE/'s10/qualification-audit.json','qualified source/proof/runtime envelope'),(s.BASE/'s09/application-qualification.json','actual application cost evidence'),(s.BASE/'s17/preflight-bounds.json','early envelope ceilings'),(s.BASE/'s06/recursive-proposal.json','fixed complete benchmark proposal'),(s.BASE/'s06/runtime.py','ground/closure/proof stage boundaries')],[{'decision':'Separate full cold/warm qualification from evaluator-only growth probes; inclusive timers cannot be summed','basis':'S11 measurement scope'},{'decision':'Record observed worker/child peak RSS and exact resource classifications; no scale/latency promise','basis':'bounded profile budget'}])
p=s.read(s.BASE/'s06/recursive-proposal.json');s.write(HERE/'benchmark-proposal.json',p)
full=[]
for mode in ['cold','warm']:
 output=HERE/(mode+'-measurement.json');proc=subprocess.run([sys.executable,str(HERE/'worker.py'),str(HERE/'benchmark-proposal.json'),str(HERE/'build'),str(output)],capture_output=True,text=True,timeout=600)
 s.require(proc.returncode==0,'benchmark failed '+mode+' '+proc.stdout+proc.stderr);data=s.read(output);s.require(data['status']=='qualified-candidate','unqualified benchmark');data['mode']=mode;full.append(data);print(mode+' qualification '+str(round(data['seconds'],3))+' seconds',flush=True)
 if mode=='cold':
  # The warm replay uses the same cache and rewrites its timing/evidence report.
  # Preserve cold evidence before that run; proof source/binary bytes are still
  # checked after both runs, and a warm result cannot substitute for this one.
  archive=HERE/'cold-evidence';archive.mkdir(exist_ok=True);captured={}
  for obligation in data['result']['obligations']:
   updated=[]
   for binding in obligation['evidence']:
    if binding['path'] not in captured:
     path=s.check(binding);target=archive/path.name;target.write_bytes(path.read_bytes());captured[binding['path']]=s.binding(target)
    updated.append(captured[binding['path']])
   obligation['evidence']=updated
  data['cold_evidence_policy']='Original cold evidence bytes retained before warm replay; source/binary identities rechecked after both runs.';s.write(output,data)
# Stage-only workload variation does not claim that these larger cases completed kernel qualification.
probes=[]
for domainSize,variables,depth in [(15,1,1),(20,2,2),(30,3,3)]:
 b=r.ext.c.fixture()
 while len(b['inference']['domain'])<domainSize:b['inference']['domain'].append({'kind':'text','value':'unused-'+str(len(b['inference']['domain']))})
 after=copy.deepcopy(b);head='Probe'+str(variables);after['inference']['predicates'].append({'id':head,'version':'v2','sorts':['reference']*variables,'role':'ordinary'});after['producers'].append({'predicate':head,'class':'derived-information','meaning':'derived-positive-horn'})
 after['inference']['rules'].append({'id':'probe-'+str(variables),'version':'v2','head':{'predicate':head,'terms':[{'variable':'x'+str(k)} for k in range(variables)]},'body':[{'predicate':'Conforms','terms':[{'variable':'x'+str(k)}]} for k in range(variables)]})
 for step in range(depth):
  name='Chain'+str(step);prev=head if step==0 else 'Chain'+str(step-1);after['inference']['predicates'].append({'id':name,'version':'v2','sorts':['reference']*variables,'role':'ordinary'});after['producers'].append({'predicate':name,'class':'derived-information','meaning':'derived-positive-horn'});after['inference']['rules'].append({'id':name,'version':'v2','head':{'predicate':name,'terms':[{'variable':'x'+str(k)} for k in range(variables)]},'body':[{'predicate':prev,'terms':[{'variable':'x'+str(k)} for k in range(variables)]}]})
 start=time.monotonic()
 try:
  bounds=r.resource.preflight(after);normal=r.normal_with_observations(after,r.projection.predict(b));ev=r.evaluate(normal);probes.append({'domain':domainSize,'variables':variables,'arity':variables,'chain_depth':depth,'status':'evaluator-complete-kernel-not-run','seconds':time.monotonic()-start,'bounds':bounds,'counters':ev['counters'],'facts':len(ev['closure'])})
 except r.resource.Exhausted as ex:probes.append({'domain':domainSize,'variables':variables,'arity':variables,'chain_depth':depth,'status':'unknown-resource','seconds':time.monotonic()-start,'reason':str(ex),'complete_readiness':False})
# Required hostile envelope path: unknown cannot supply complete readiness.
huge=copy.deepcopy(p['after']);huge['inference']['domain'].extend([{'kind':'text','value':str(k)} for k in range(1000)])
try:r.resource.preflight(huge);raise ValueError('exhaustion case accepted')
except r.resource.Exhausted as ex:exhausted={'status':'unknown-resource','reason':str(ex),'complete_closure':False,'absence':False,'readiness':False,'products_allocated':0}
cliProposal=copy.deepcopy(p);cliProposal['after']=huge;s.write(HERE/'exhausted-proposal.json',cliProposal)
proc=subprocess.run([sys.executable,str(s.BASE/'s06/recursive-runtime.py'),str(HERE/'exhausted-proposal.json'),'--output',str(HERE/'exhausted-result.json')],capture_output=True,text=True,timeout=60)
s.require(proc.returncode==3,'exhausted CLI did not return resource outcome');cliOut=s.read(HERE/'exhausted-result.json');s.require(cliOut['status']=='unknown-resource' and cliOut['complete_closure'] is False and cliOut['readiness']=='blocked','exhausted CLI issued complete readiness');exhausted['actual_cli_result']=s.binding(HERE/'exhausted-result.json')
registry=s.read(s.BASE/'s10/qualification-audit.json')['registry_regression_modules'];registryCost=sum(x['seconds'] for x in registry)
sys.path.insert(0,str(s.BASE/'s10'));import audit
audit.binding_closure([HERE/'cold-measurement.json',HERE/'warm-measurement.json'])
dominance=[{'mode':m['mode'],'grounding_and_saturation_seconds':m['inclusive_stages']['grounding_and_saturation']['seconds'],'largest_measured_proof_stage_seconds':max(m['inclusive_stages']['compile_and_actual_witness_checks']['seconds'],m['inclusive_stages']['fresh_general_kernel_replay']['seconds'])} for m in full]
s.require(all(m['largest_measured_proof_stage_seconds']>m['grounding_and_saturation_seconds'] for m in dominance),'measurement does not support reference selection rationale')
selection={'selected_evaluator':'qualified-reference','new_optimization':'none','reason':'Fresh pure proof/witness replay and immutable source preparation dominate qualified workload; evaluator-only probes are bounded. Removing required replay would change the guarantee. No additional optimization is needed to finish this bounded pilot.','optional_S12':'not-needed; keep reference and do not issue a speedup claim','observed_cost_comparison':dominance}
s.write(HERE/'benchmark-profile.json',{'schema':'relational.benchmark-profile/v2','full_workload':s.binding(HERE/'benchmark-proposal.json'),'full_modes':['cold','warm'],'stage_probes':probes,'limits':s.binding(s.BASE/'s17/preflight-bounds.json'),'selection':selection,'authority_effect':'none'})
s.write(HERE/'stage-measurements.json',{'result':'pass','full_qualification':full,'evaluator_only_probes':probes,'registry_dependency_compile_seconds':registryCost,'registry_module_count':len(registry),'exhaustion':exhausted,'counter_semantics':'estimates distinct from observed candidates/comparisons; inclusive timers not additive; worker RSS units KiB on Linux','selection':selection,'authority_effect':'none'})
lines=['# Observed qualified reference performance','',*[m['mode']+': '+str(round(m['seconds'],3))+' seconds; child peak '+str(m['child_max_rss_kib'])+' KiB; '+str(m['work']['candidate_products'])+' observed ground products.' for m in full],'','These are finite local observations. Inclusive stage timers overlap and must not be added. Larger domain/arity/chain probes measure only the evaluator and are explicitly not whole-workflow/kernel qualification. Resource refusal happens before product allocation and supplies no closure, absence or readiness.','',selection['reason'],'','The qualified reference remains selected. No optimization speedup or throughput/latency promise is issued.']
(HERE/'performance-baseline.md').write_text('\n'.join(lines)+'\n')
s.accept('S11',['Full cold/warm qualification records inclusive stage costs, ground/saturation counters and per-worker/child RSS; larger probes are evaluator-only.','Measurements are local finite observations; resource exhaustion remains unknown with no readiness or scale promise.','Measured cost review selects the qualified reference; optional optimization is not needed for this envelope.'],controls=[{'name':'cold-complete-qualified','result':'pass'},{'name':'warm-complete-fresh-proof-replay','result':'pass'},{'name':'preallocation-exhaustion-no-complete-verdict','result':'pass'}],extra_dependencies=[HERE/'worker.py',HERE/'benchmark-proposal.json',HERE/'cold-measurement.json',HERE/'warm-measurement.json'])
print('S11 accepted: cold/warm full measurements and '+str(len(probes))+' scoped growth probes; reference selected.')
