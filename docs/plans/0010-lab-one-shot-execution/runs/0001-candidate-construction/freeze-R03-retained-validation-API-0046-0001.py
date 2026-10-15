"""Preserve known failed validation evidence after complete exact core verification.

The successor retains every inherited test and contract, original timing/source/
permission/journal predicates, and uncertain incomplete-core handling.
"""
import ast,copy,hashlib,importlib.util,json,shutil
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';PARENT=BASE/'api-v45';API=BASE/'api-v46'
PARENT_PIN='8931c159d933d0144791542d0357bdf8ba532a3b12bd68f35ab3d5a347a0624d'
PAIRS=[('failure-preparation-v4','failure-preparation-v5','failure_preparation.py'),('classification-preparation-v6','classification-preparation-v7','classification_preparation.py')]
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def put(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def methods(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def files(p):return [x for x in p.rglob('*') if x.is_file() and not {'receipts','__pycache__'} & set(x.parts) and x.name not in ('source-manifest.json','contract-profile.json')]
def main():
 assert not API.exists() and all(not (BASE/new).exists() for old,new,loader in PAIRS)
 spec=importlib.util.spec_from_file_location('_cal_API46_parent_guard',PARENT/'guard.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
 parent=g.verify(PARENT_PIN)
 failure=json.loads((PARENT/'receipts/failure-checks.json').read_bytes());assert failure['tests_run']==18 and failure['result']=='FAIL'
 assert sum(c['result']=='FAIL' for c in failure['cases'])==2
 for old,new,loader in PAIRS:
  src=BASE/old;dest=BASE/new;dest.mkdir()
  for p in files(src):
   target=dest/p.relative_to(src);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())
  p=dest/'preparation.py';s=p.read_text()
  anchor="        require(validation['result']!='fail' and len(details['cores'])==len(proposal['targets']),"
  assert s.count(anchor)==1
  branch="""        # Complete exact cores establish a known structural refusal. Let the
        # original calculation exit guards run and commit its failed report
        # before delivering the known error. Incomplete-core failures retain
        # their original uncertain/pending handling.
        if validation['result']=='fail' and len(details['cores'])==len(proposal['targets']):
            raise RuleFailure('invalid-contract',
                'Exact prospective structural validation did not pass; inspect retained evidence.',
                details['evidence'])
"""
  p.write_text(s.replace(anchor,branch+anchor))
  old_ast=ast.parse((src/'preparation.py').read_bytes());new_ast=ast.parse(p.read_bytes())
  funcs=[n for n in ast.walk(new_ast) if isinstance(n,ast.FunctionDef) and n.name=='_prepare'];assert len(funcs)==1
  f=funcs[0];indices=[i for i,n in enumerate(f.body) if isinstance(n,ast.If) and ast.unparse(n.test)=="validation['result'] == 'fail' and len(details['cores']) == len(proposal['targets'])"]
  assert len(indices)==1;f.body.pop(indices[0]);assert ast.dump(old_ast,include_attributes=False)==ast.dump(new_ast,include_attributes=False)
  with (dest/'DESIGN.md').open('a') as out:out.write('\n## Retained known structural refusal\n\nA failed structural validation with every exact stable Decision core verified is\na known invalid-contract outcome. The original source exit guards run before\nstaged failed-report evidence commits. Incomplete cores retain the original\nuncertain outcome; this change does not qualify deadline delivery.\n')
 API.mkdir();(API/'receipts').mkdir()
 for p in files(PARENT):
  target=API/p.relative_to(PARENT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())
 for old,new,loader in PAIRS:
  p=API/loader;s=p.read_text().replace(old,new).replace(old.replace('-','_'),new.replace('-','_'));p.write_text(s)
 retained=[];changed=[]
 for p in files(PARENT):
  target=API/p.relative_to(PARENT)
  if p.read_bytes()!=target.read_bytes():changed.append(p.relative_to(PARENT).as_posix())
  if p.suffix=='.py':
   assert methods(p)==methods(target);retained.extend(p.relative_to(PARENT).as_posix()+':'+n for n in methods(p))
 assert sorted(changed)==['classification_preparation.py','failure_preparation.py'] and len(retained)==293
 context=RUN/'context-R03-retained-validation-API-0046.json';static=RUN/'API46-retained-validation-static-0001.json'
 put(context,{'schema_version':'lab-bounded-context/v1-candidate','task':'R03 retain known failed structural validation evidence','strict_coverage':'PASS','blockers':[],
  'source_bindings':[bind(p) for p in [PARENT/'source-manifest.json',PARENT/'receipts/failure-checks.json',RUN/'API45-failure15-validation-finding-0001.json',RUN/'authorization.json']],
  'write_scope':[API.relative_to(ROOT).as_posix()]+[(BASE/new).relative_to(ROOT).as_posix() for old,new,loader in PAIRS],
  'constraints':['All293 inherited methods and34 public contracts unchanged.','Only known failed structural validation with complete exact cores becomes retained RuleFailure.','Incomplete cores still take original generic refusal and uncertain journal path.','Original900-second limit, clocks, source/policy callbacks and journal bodies unchanged.','Candidate source only; no public qualification or owner outcome.'],
  'validation_surface':'Static full AST retention plus unchanged original case14/case15 and subsequent full original suites.', 'actual_owner_outcome':None,'authority_effect':'none','task_complete':False})
 put(static,{'schema_version':'lab-known-validation-retention-static/v1-candidate','result':'PASS','unchanged_original_test_methods':293,'unchanged_public_contracts':34,'changed_API_files':sorted(changed),'sole_preparation_AST_change':'If known failed validation and complete exact cores, raise existing RuleFailure with staged evidence before original require.','original_other_preparation_ASTs_unchanged':True,'deadline_delivery_qualified':False,'actual_public_calls':0,'whole_API_qualified':False,'actual_owner_outcome':None,'authority_effect':'none','task_complete':False})
 profile=json.loads((PARENT/'contract-profile.json').read_bytes());profile_rows=[]
 for row in profile['files']:
  p=ROOT/row['path']
  if p.is_relative_to(PARENT):p=API/p.relative_to(PARENT)
  else:
   for old,new,loader in PAIRS:
    if p.is_relative_to(BASE/old):p=BASE/new/p.relative_to(BASE/old);break
  profile_rows.append(bind(p))
 profile['files']=profile_rows;profile['known_validation_retention_context_binding']=bind(context)
 profile['claim_ceiling']='Sixteen authored handlers; known failed validation retained after complete exact core verification. Original runtime suites and deadline qualification remain outstanding.'
 put(API/'contract-profile.json',profile)
 rows={r['path']:r for r in parent['files']}
 for p in [PARENT/'source-manifest.json',PARENT/'receipts/failure-checks.json',RUN/'API45-failure18-terminal-0001.json',RUN/'API45-failure15-validation-finding-0001.json',context,static,Path(__file__).resolve()]+files(API)+[API/'contract-profile.json']:
  r=bind(p);rows[r['path']]=r
 for old,new,loader in PAIRS:
  for p in files(BASE/new):r=bind(p);rows[r['path']]=r
 for r in rows.values():assert hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256']
 manifest={**parent,'files':[rows[k] for k in sorted(rows)],'parent_source_binding':bind(PARENT/'source-manifest.json'),'context_binding':bind(context),'static_checks_binding':bind(static),'retained_inherited_methods':retained,'unchanged_inherited_method_count':293,'whole_API_qualified':False,'current_Agent_qualified':False,'task_complete':False,'goal_complete':False}
 put(API/'source-manifest.json',manifest)
 print(json.dumps({'result':'FROZEN','source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),'source_files':len(rows),'unchanged_methods':293,'runtime_qualified':False}),flush=True)
if __name__=='__main__':main()
