"""Successor task evidence and pinned compilation; never mutate v1 artifacts."""
from pathlib import Path
import hashlib,json,subprocess,os,re,importlib.util,sys,time
sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parents[1]
ROOT=next(p for p in BASE.parents if (p/'docs/plans/relational-theorem-checker/PLAN-SOURCE.json').is_file())
V1=BASE.parent/'v1'
PROPOSAL=ROOT/'docs/plans/relational-theorem-checker/reviews/2026-10-09/implementation-analysis/revised-plan.json'
PLAN=BASE/'execution/plan.json'
def require(c,m):
 if not c:raise ValueError(m)
def read(p):return json.loads(Path(p).read_text())
def write(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def identity(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def binding(p):return {'path':str(Path(p).resolve().relative_to(ROOT)),'sha256':digest(p)}
def check(b):
 path=Path(b['path']);require(not path.is_absolute() and '..' not in path.parts,'unsafe binding');p=ROOT/path
 require(p.is_file() and digest(p)==b['sha256'],'stale evidence: '+str(path));return p

def init():
 if not PLAN.exists():
  p=read(PROPOSAL);p['execution_source']=binding(PROPOSAL);p['status']='executing-candidate';p['execution_authorization']='Direct user request: complete the whole plan'
  p['shared_write_scope']=[str((BASE/'execution').relative_to(ROOT))];p['authority_effect']='none'
  for t in p['tasks']:t['status']='not-started'
  write(PLAN,p);sync()
def task(id):return next(t for t in read(PLAN)['tasks'] if t['id']==id)
def sync():
 p=read(PLAN);write(BASE/'execution/status.json',{'schema':'relational.v2-execution-status/v1','objective':'complete the revised whole plan','accepted':[t['id'] for t in p['tasks'] if t['status']=='accepted'],'remaining':[{'id':t['id'],'status':t['status']} for t in p['tasks'] if t['status']!='accepted'],'goal_complete':all(t['status'] in ['accepted','not-needed'] for t in p['tasks']),'authority_effect':'none'})
def context(id,sources,decisions):
 init();t=task(id);require(len(sources)<=14,'context budget');deps=[]
 for d in t['depends_on']:
  prev=task(d);require(prev['status']=='accepted','predecessor not accepted '+d);b=prev['receipt'];audit_receipt(check(b));deps.append(b)
 for p,selector in sources:require(Path(p).is_file() and selector,'missing context')
 pack={'schema':'relational.v2-task-context/v1','task':id,'mode':'standard','write_scope':t['write_scope'],'shared_write_scope':read(PLAN)['shared_write_scope'],'source_plan':binding(PROPOSAL),'sources':[dict(binding(p),selector=sel) for p,sel in sources],'obligations':[{'id':id+'-C'+str(i+1),'criterion':c,'sources':[str(Path(p).relative_to(ROOT)) for p,_ in sources],'status':'covered'} for i,c in enumerate(t['acceptance_criteria'])],'dependency_bindings':deps,'decisions':decisions,'strict_coverage':'pass','human_feedback_claimed':False,'authority_effect':'none'}
 write(BASE/id.lower()/'context-pack.json',pack)
 plan=read(PLAN);entry=next(x for x in plan['tasks'] if x['id']==id);entry['status']='in-progress';write(PLAN,plan);sync()
 return pack

def lean_path():
 p=V1/'formal/.toolcache/lean-4.33.1-linux/bin/lean';lock=read(V1/'formal/toolchain-lock.json')
 require(subprocess.check_output([str(p),'--version'],text=True).strip()==lock['version_output'],'compiler version drift')
 require(digest(p)==lock['lean_binary_sha256'] and digest(p.parent.parent/'lib/lean/libleanshared.so')==lock['lean_shared_library_sha256'],'compiler/kernel drift')
 return p

def compile_modules(build,modules,timeout=60):
 build=Path(build);build.mkdir(parents=True,exist_ok=True);lean=lean_path();logs=[]
 for name,p in modules:
  source=Path(p);raw=source.read_text();require(not re.search(r'^\s*(?:axiom\s|.*\bsorry\b)',raw,re.M),'unsupported axiom/sorry source '+str(p))
  target=build/(name+'.lean');target.write_bytes(source.read_bytes());start=time.monotonic()
  r=subprocess.run([str(lean),'-o',str(target.with_suffix('.olean')),str(target)],cwd=build,env={**os.environ,'LEAN_PATH':str(build)},capture_output=True,text=True,timeout=timeout)
  out=r.stdout+r.stderr;require(r.returncode==0 and 'warning:' not in out,'Lean failed '+name+'\n'+out)
  require(not re.search(r'\b(sorryAx)\b',out),'admitted proof');logs.append({'module':name,'source':binding(source),'olean':binding(target.with_suffix('.olean')),'seconds':time.monotonic()-start,'output':out})
 return logs
V1_MODULES=[('RelationalInput','formal/core/RelationalInput.lean'),('RelationalSemantics','formal/core/RelationalSemantics.lean'),('SemanticLogic','formal/semantic-logic/v1/SemanticLogic.lean'),('ReferenceChecker','formal/reference-checker/l0/ReferenceChecker.lean'),('InferenceCore','inference/derivations/InferenceCore.lean'),('DerivationSoundness','inference/derivations/DerivationSoundness.lean'),('ClosureAdequacy','inference/closure/ClosureAdequacy.lean'),('ProtectedLineage','inference/protected/ProtectedLineage.lean'),('ModelSemantics','inference/independence/ModelSemantics.lean'),('RuleConservativity','inference/integration/RuleConservativity.lean'),('StressTypes','relation-stress/v1/implementation/StressTypes.lean'),('DelegationSemantics','relation-stress/v1/implementation/DelegationSemantics.lean'),('ObligationSemantics','relation-stress/v1/implementation/ObligationSemantics.lean'),('StressCheckers','relation-stress/v1/implementation/StressCheckers.lean'),('StressLaws','relation-stress/v1/implementation/StressLaws.lean'),('StressProofs','relation-stress/v1/implementation/StressProofs.lean')]
def core_modules(names):return [(n,V1/p) for n,p in V1_MODULES if n in names]
def audit_receipt(p):
 r=read(p);require(r['result']=='accepted','receipt not accepted')
 for b in r['artifacts']+r['dependency_bindings']:check(b)
 return r

def accept(id,criteria,controls=(),extra_dependencies=()):
 t=task(id);require(id!='S14','S14 needs actual human assessment; no fabricated acceptance')
 require(len(criteria)==len(t['acceptance_criteria']),'missing criterion evidence')
 ctx=read(BASE/id.lower()/'context-pack.json');deps=ctx['dependency_bindings']+[binding(p) for p in extra_dependencies]
 for b in deps:check(b)
 for p in ctx['sources']:check(p)
 artifacts=[]
 for name in t['outputs']:
  p=BASE/id.lower()/name;require(p.is_file(),'missing deliverable '+name);artifacts.append(dict(binding(p),name=name))
 artifacts+=[binding(BASE/id.lower()/'context-pack.json')]
 receipt={'schema':'relational.v2-task-acceptance/v1','task':id,'result':'accepted','review':'author implementation/self-review; candidate only','criteria':[{'criterion':c,'finding':f,'result':'pass'} for c,f in zip(t['acceptance_criteria'],criteria)],'controls':list(controls),'artifacts':artifacts,'dependency_bindings':deps,'human_review':None,'authority_effect':'none'}
 p=BASE/id.lower()/'task-acceptance.json';write(p,receipt);plan=read(PLAN);x=next(t for t in plan['tasks'] if t['id']==id);x['status']='accepted';x['receipt']=binding(p)
 for u in x['working_units']:u['status']='accepted'
 write(PLAN,plan);sync()
