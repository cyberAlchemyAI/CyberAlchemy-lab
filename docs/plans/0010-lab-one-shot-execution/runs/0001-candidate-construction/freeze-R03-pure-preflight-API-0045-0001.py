"""Freeze read-only preflight grouping; preserve all293 inherited tests."""
import ast,copy,hashlib,importlib.util,json
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';PARENT=BASE/'api-v44';API=BASE/'api-v45'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def put(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def methods(p):
 return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes()))
         if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def functions(p):
 return {n.name:n for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef)}
def main():
 spec=importlib.util.spec_from_file_location('_cal_API45_parent_guard',PARENT/'guard.py')
 g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
 parent=g.verify('9f56fbe2c874f2f9f5f7965998e033b5a51ebb75b19d5c19c3733b6b02345f0f')
 retained=[];changed=[]
 for p in PARENT.rglob('*'):
  if not p.is_file() or 'receipts' in p.parts or '__pycache__' in p.parts or p.name in ('source-manifest.json','contract-profile.json'):continue
  s=API/p.relative_to(PARENT)
  if p.read_bytes()!=s.read_bytes():changed.append(p.relative_to(PARENT).as_posix())
  if p.suffix=='.py':
   assert methods(p)==methods(s)
   retained += [p.relative_to(PARENT).as_posix()+':'+name for name in methods(p)]
 assert sorted(changed)==['guarded_candidate.py','service.py'] and len(retained)==293
 old,new=functions(PARENT/'service.py'),functions(API/'service.py')
 for name in ['select_classification','select_failure']:
  n=copy.deepcopy(new['_'+name]);n.name=name
  assert ast.dump(old[name],include_attributes=False)==ast.dump(n,include_attributes=False)
 for name in old:
  if name not in ['select_classification','select_failure']:
   assert ast.dump(old[name],include_attributes=False)==ast.dump(new[name],include_attributes=False)
 assert ast.dump(functions(PARENT/'guarded_candidate.py')['calculation'],include_attributes=False)==ast.dump(functions(API/'guarded_candidate.py')['calculation'],include_attributes=False)
 paths=[PARENT/'source-manifest.json',RUN/'authorization.json',RUN/'API45-sequential-verification-choice-0001.json',
        RUN/'API44-deadline-observations-0001.json',BASE/'fact-read-scope-v2/scope.py',BASE/'fact-read-scope-v1/scope.py',
        BASE/'failure-preparation-v4/preparation.py',BASE/'classification-preparation-v6/preparation.py',Path(__file__).resolve()]
 context=RUN/'context-R03-pure-preflight-API-0045.json';static=RUN/'API45-pure-preflight-authoring-0001.json'
 put(context,{'schema_version':'lab-bounded-context/v1-candidate','task':'R03 group pure metadata handler selection before durable candidate claim',
  'strict_coverage':'PASS','blockers':[],'source_bindings':[bind(p) for p in paths],
  'write_scope':API.relative_to(ROOT).as_posix(),'choice':'Explicit original read-only source/policy composition for selection/preflight; sequential successor verification.',
  'constraints':['All293 inherited test methods and all34 public contract schemas remain unchanged.',
   'Original selection function bodies are retained verbatim under private method names; no Actor/key/routing/source-cut check is removed.',
   'Original source/policy callbacks,900second limit, real clocks and uncached actual permission-file reads remain.',
   'Original journal claim, calculation, evidence commit, finish, delivery and reply bodies remain unchanged.',
   'No durable writes or nested dispatcher may run inside read-only selection; full original source/producer boundaries run before returning.',
   'Test resource pressure is observed, not established as deadline failure or exit143 causality.'],
  'validation_surface':'Static full original AST/body comparison, full original current public suites and separately versioned controls; bounded unchanged positive-call timing diagnostic.',
  'remaining_obligations':['Actual deadline delivery and every original public suite.','All21 original remaining qualifications.','Typed public integration/resolvers and genuine R05/R06/R07/S02/R08.'],
  'actual_owner_outcome':None,'authority_effect':'none','task_complete':False})
 put(static,{'schema_version':'lab-pure-preflight-static-checks/v1-candidate','result':'PASS',
  'unchanged_original_test_methods':293,'changed_files':sorted(changed),
  'original_selection_bodies_unchanged':True,'original_calculation_body_unchanged':True,
  'original_service_dispatch_journal_finish_and_reply_bodies_unchanged':True,
  'all_original_preflight_predicates_retained':True,'original_authentication_and_source_callbacks_unchanged':True,
  'actual_public_calls':0,'whole_API_qualified':False,'actual_owner_outcome':None,'authority_effect':'none','task_complete':False})
 profile=json.loads((PARENT/'contract-profile.json').read_bytes())
 profile['files']=[bind(API/(ROOT/row['path']).relative_to(PARENT)) if (ROOT/row['path']).is_relative_to(PARENT) else row for row in profile['files']]
 profile['pure_preflight_context_binding']=bind(context)
 profile['claim_ceiling']='Sixteen authored handlers; pure selection/preflight grouping with unchanged original predicate bodies and callbacks. Sequential original qualification remains required.'
 put(API/'contract-profile.json',profile)
 rows={x['path']:x for x in parent['files']}
 for p in paths+[context,static]:b=bind(p);rows[b['path']]=b
 for p in API.rglob('*'):
  if p.is_file() and 'receipts' not in p.parts and '__pycache__' not in p.parts:b=bind(p);rows[b['path']]=b
 manifest={**parent,'files':[rows[k] for k in sorted(rows)],'parent_source_binding':bind(PARENT/'source-manifest.json'),
  'context_binding':bind(context),'static_checks_binding':bind(static),'retained_inherited_methods':retained,
  'unchanged_inherited_method_count':293,'whole_API_qualified':False,'current_Agent_qualified':False,'task_complete':False,'goal_complete':False}
 put(API/'source-manifest.json',manifest)
 print(json.dumps({'result':'FROZEN','source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),'source_files':len(rows),'unchanged_methods':293}),flush=True)
if __name__=='__main__':main()
