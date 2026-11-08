"""Positive recursive candidate qualification; fixed independent theorem bundle and actual witnesses."""
from pathlib import Path
import sys,json,os,copy,time,itertools,tempfile,subprocess
sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parents[1];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'s03'));import extension as ext
sys.path.insert(0,str(BASE/'s05'));import adapter as projection
s=ext.s;resource=projection.resource;render=projection.render

def module_list():
 return s.core_modules({n for n,_ in s.V1_MODULES})+[(n,BASE/f's00/{n}.lean') for n in ['RequirementSemantics','RequiredStatements']]+[(n,BASE/f's02/{n}.lean') for n in ['ContextProjection','ProjectionProofs']]+[('BaselineContract',BASE/'s15/BaselineContract.lean')]+[(n,BASE/f's16/{n}.lean') for n in ['ProducerPolicy','SupportedObservations','SupportLineage']]+[(n,BASE/f's04/{n}.lean') for n in ['ConditionSemantics','InterpretationSemantics','MappingStatements']]+[(n,BASE/f's18/{n}.lean') for n in ['SourceInterpretation','BaselineTransition']]+[(n,BASE/f's03/{n}.lean') for n in ['RecursiveExtension','RecursiveConservativity','RecursiveSaturation']]+[(n,HERE/(n+'.lean')) for n in ['RuntimeCatalog','RuntimeProofs','RuntimeVerifier']]

def prepare(build):
 build=Path(build);build.mkdir(parents=True,exist_ok=True);path=build/'dependencies.json';mods=module_list()
 if path.exists():
  old=s.read(path);s.require([x['source'] for x in old['modules']]==[s.binding(p) for _,p in mods],'stale runtime imports')
  for m in old['modules']:s.check(m['source']);s.check(m['olean'])
 else:s.write(path,{'modules':s.compile_modules(build,mods)})
 return s.read(path)

def replay_general(build,weak=False):
 build=Path(build);name='Submitted';path=build/(name+'.lean')
 path.write_text('import RuntimeCatalog\nimport RuntimeProofs\nnamespace V2Submission\ntheorem required : '+('True := by trivial' if weak else 'Successor.Runtime.Catalog.RequiredGeneralBundle := Successor.Runtime.Proofs.general_bundle')+'\nend V2Submission\n')
 compile_logs=s.compile_modules(build,[(name,path)])
 lean=s.lean_path();r=subprocess.run([str(lean),'--run',str(build/'RuntimeVerifier.lean'),'RuntimeCatalog','Successor.Runtime.Catalog.RequiredGeneralBundle','definition-value','V2Submission.required'],cwd=build,env={**os.environ,'LEAN_PATH':str(build),'PATH':str(lean.parent)+os.pathsep+os.environ.get('PATH','')},capture_output=True,text=True,timeout=60)
 if weak:
  s.require(r.returncode!=0,'weakened independent target accepted');return {'result':'rejected','diagnostic':r.stderr,'submission_sha256':s.digest(path)}
 s.require(r.returncode==0,'fresh general bundle replay failed: '+r.stdout+r.stderr);audit=json.loads(r.stdout)
 s.require(audit['accepted'] and audit['fresh_kernel_replay'],'incomplete general replay')
 return {'audit':audit,'modules':compile_logs,'stderr':r.stderr,'claim_ceiling':'fresh replay by the same pinned Lean kernel; no independent second kernel'}

def normal_with_observations(b,p):
 n=ext.normalize(b['inference']);n['facts']=copy.deepcopy(p['facts'])+n['facts'];n.pop('normal_form_identity',None);n['normal_form_identity']=s.identity(n);return n

def instantiate(pattern,values):return {'predicate':pattern['predicate'],'values':[values[t['slot']] if 'slot' in t else t['constant'] for t in pattern['terms']]}
def evaluate(n):
 counters={'candidate_products':0,'typed_instances':0,'saturation_comparisons':0,'derived_steps':0};start=time.monotonic();instances=[]
 cap=s.read(BASE/'s17/preflight-bounds.json')['limits']
 def budget():
  if time.monotonic()-start>cap['lean_stage_seconds']:raise resource.Exhausted('unknown-resource: finite evaluator elapsed ceiling')
 for r in n['rules']:
  for vs in itertools.product(n['domain'],repeat=len(r['variables'])):
   counters['candidate_products']+=1;budget()
   if counters['candidate_products']>cap['ground_candidates']:raise resource.Exhausted('unknown-resource: ground candidate ceiling')
   if [v['kind'] for v in vs]!=[v['sort'] for v in r['variables']]:continue
   instances.append({'rule':{k:r[k] for k in ['id','version','hash']},'substitution':list(vs),'head':instantiate(r['head'],vs),'body':[instantiate(p,vs) for p in r['body']]})
 counters['typed_instances']=len(instances)
 facts=copy.deepcopy(n['facts']);steps=[{'kind':'base','conclusion':a} for a in facts];positions={s.identity(a):i for i,a in enumerate(facts)}
 while True:
  budget();active=None
  for i in instances:
   counters['saturation_comparisons']+=1
   if i['head'] not in facts and all(a in facts for a in i['body']):active=i;break
  if active is None:break
  if len(steps)>=cap['certificate_steps'] or counters['derived_steps']>=cap['saturation_steps']:raise resource.Exhausted('unknown-resource: certificate/saturation ceiling')
  indices=[positions[s.identity(a)] for a in active['body']];steps.append({'kind':'apply','conclusion':active['head'],'instance':active,'indices':indices});positions[s.identity(active['head'])]=len(facts);facts.append(active['head']);counters['derived_steps']+=1
 counters['seconds']=time.monotonic()-start
 return {'closure':facts,'steps':steps,'instances':instances,'counters':counters,'computation':'reference untyped products filtered by declared sorts; positive least closure'}

def witness_source(old,new,evaluation,graph):
 d=projection.c.f.d;oldLen=len(old['predicates']);rulesLen=len(old['rules'])
 keys=[{k:next(p for p in new['predicates'] if p['id']==id)[k] for k in ['id','version','hash']} for id in ['ConformsTo','TargetKind','Conforms']]
 source='import RuntimeProofs\nset_option maxRecDepth 8192\nset_option maxHeartbeats 4000000\nnamespace Successor.Runtime.Actual\nopen Inference Inference.Extension\n'
 source+='def before : Theory := '+render.theory_lean(old)+'\ndef after : Theory := '+render.theory_lean(new)+'\ndef facts : List Atom := '+d.rows(new['facts'],render.atom_lean)+'\ndef C : List Atom := '+d.rows(evaluation['closure'],render.atom_lean)+'\ndef steps : List Step := '+d.rows(evaluation['steps'],render.step_lean)+'\ndef sealed : List Key := '+d.rows(keys,render.key_lean)+'\n'
 source+='theorem before_valid : TheoryValid before := by decide\ntheorem after_valid : TheoryValid after := by decide\ntheorem initial_valid : InitialValid after facts := by decide\ntheorem lineage_valid : checkLineage after facts = true := by decide\ntheorem sealed_heads : Producer.checkHeads after sealed = true := by decide\ntheorem complete_closure : checkClosure after facts C [steps] = true := by decide\n'
 source+='def added := (groundInstances after).filter fun i => decide (¬ Old before i.head)\ndef extension : Recursive.CheckedExtension before after := {\n'
 source+='fresh := after.predicates.drop '+str(oldLen)+', addedRules := after.rules.drop '+str(rulesLen)+', added := added,domain_same := by decide,predicates_append := by decide,rules_append := by decide,roots_same := by decide,epoch_same := by decide,fresh_keys := by decide,fresh_ordinary := by decide,cover := by decide,old_bodies := by decide,fresh_heads := by decide,head_typed := by decide,head_roots := by decide,added_valid := by decide,producer_safe := by decide }\n'
 source+='theorem actual_expansion : ∀ F M, SemanticModel before F M → ∃ N, SemanticModel after F N ∧ ∀ a, Old before a → (N a ↔ M a) := Recursive.every_old_model_expands before after extension\n'
 source+='theorem closure_exact : ∀ a, a ∈ C ↔ Derivable after facts a := checked_closure_exact complete_closure\n'
 for t in ['before_valid','after_valid','initial_valid','lineage_valid','sealed_heads','complete_closure','actual_expansion','closure_exact']:source+='#print axioms '+t+'\n'
 return source+'end Successor.Runtime.Actual\n'

def qualify(proposal,build=None):
 import jsonschema
 jsonschema.Draft202012Validator(s.read(HERE/'rule-bundle.schema.json')).validate(proposal)
 before,after=proposal['before'],proposal['after'];s.require(proposal['baseline_identity']==s.identity(before),'stale/wrong baseline identity')
 resource.preflight(before);bounds=resource.preflight(after);classified=ext.classify(before,after)
 s.require(not projection.predict(before)['unhandled_kinds'] and not projection.predict(after)['unhandled_kinds'],'unselected source meanings need separately composed stress qualification')
 if build is None:build=Path(tempfile.mkdtemp(prefix='v2-recursive-',dir=HERE/'runs'))
 build=Path(build);prepare(build)
 # The actual source projection recompiles for each exact snapshot.
 p=projection.project(projection.request(before),build/'projection');old=normal_with_observations(before,p);new=normal_with_observations(after,p);result=evaluate(new)
 stem='ActualRecursive_'+s.identity(proposal)[:20];source=build/(stem+'.lean');source.write_text(witness_source(old,new,result,projection.predict(before)['graph']))
 actual=s.compile_modules(build,[(stem,source)])
 # Copy general submission to an immutable proposal-specific archive after replay.
 general=replay_general(build);archive=build/(stem+'_Submission.lean');archive.write_bytes((build/'Submitted.lean').read_bytes());general['submission_source']=s.binding(archive)
 expected=ext.c.obligations('rule-only');proofEvidence={'actual':actual,'general':general,'projection':p['kernel_evidence'],'dependencies':s.binding(build/'dependencies.json')}
 evidencePath=build/(stem+'_evidence.json');s.write(evidencePath,proofEvidence)
 obligations=[{'id':o['id'],'method':o['method'],'target':o['target'],'status':'discharged','proposal_identity':s.identity(proposal),'baseline_identity':s.identity(before),'profile_identity':before['profile_identity'],'catalog_identity':before['catalog_identity'],'evidence':[s.binding(evidencePath)]} for o in expected]
 return {'schema':'relational.recursive-result/v2','status':'qualified-candidate','proposal_identity':s.identity(proposal),'before_identity':s.identity(before),'after_identity':s.identity(after),'profile_identity':before['profile_identity'],'catalog_identity':before['catalog_identity'],'obligations':obligations,'closure':result['closure'],'certificates':result['steps'],'observations':p['facts'],'supports':p['supports'],'normal_form':new,'before_normal_form':old,'evidence':proofEvidence,'counters':result['counters'],'bounds':bounds,'closure_scope':'complete selected finite positive Horn profile','model_class':'generic-root-constrained-horn; optional source-faithful subclass preserved when old sealed interpretation is exact','human_review':'pending','readiness':'candidate-shadow-only; fresh application replay still required','authority_effect':'none'}

def validate_receipt(proposal,result):
 expected=ext.c.obligations('rule-only');s.require(result['proposal_identity']==s.identity(proposal),'stale proposal receipt')
 s.require(result['before_identity']==s.identity(proposal['before']) and result['after_identity']==s.identity(proposal['after']),'stale snapshot receipt')
 s.require(result['catalog_identity']==ext.c.profile()['catalog_identity'] and result['profile_identity']==s.identity(ext.c.profile()),'profile/catalog drift')
 s.require([o['id'] for o in result['obligations']]==[o['id'] for o in expected],'missing/shrunken/wrong obligation inventory')
 for o,e in zip(result['obligations'],expected):
  s.require(o['method']==e['method'] and o['target']==e['target'] and o['status']=='discharged' and bool(o['evidence']),'missing/wrong obligation evidence')
  for b in o['evidence']:s.check(b)
 for m in result['evidence']['actual']+result['evidence']['projection']:s.check(m['source']);s.check(m['olean'])
 general=result['evidence']['general'];s.check(general['submission_source']);deps=s.read(s.check(result['evidence']['dependencies']))
 s.require([x['source'] for x in deps['modules']]==[s.binding(p) for _,p in module_list()],'stale runtime proof/policy closure')
 for m in deps['modules']:s.check(m['source']);s.check(m['olean'])
 return {'status':'structurally-current-evidence','readiness':'requires-fresh-qualification-replay; metadata flags cannot authorize application'}

def proposal(before,after,id='recursive-candidate'):return {'schema':'relational.recursive-proposal/v2','proposal_id':id,'baseline_identity':s.identity(before),'before':before,'after':after}
def main():
 import argparse
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('proposal',type=Path);p.add_argument('--output',type=Path);args=p.parse_args()
 try:out=qualify(projection.decode(args.proposal.read_bytes()));code=0
 except (resource.Exhausted,subprocess.TimeoutExpired) as e:out={'status':'unknown-resource','reason':str(e),'complete_closure':False,'readiness':'blocked','authority_effect':'none'};code=3
 except ext.Unsupported as e:out={'status':'unsupported','reason':str(e),'readiness':'blocked','authority_effect':'none'};code=4
 except Exception as e:out={'status':'invalid','reason':str(e).splitlines()[0],'readiness':'blocked','authority_effect':'none'};code=2
 if args.output:s.write(args.output,out)
 print(json.dumps(out,indent=2));return code
if __name__=='__main__':sys.exit(main())
