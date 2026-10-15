"""Group existing pure known-outcome predicates; preserve every original method.

CPU evidence identifies repeated source checks but does not qualify normal timing.
All original predicates remain; durable finish and delivery stay outside scope.
"""
import ast,hashlib,importlib.util,json
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';PARENT=BASE/'api-v46';API=BASE/'api-v47'
PIN='db77ca7aa91fe4d8b5e25f2f23b4b32610a40f83dfd20ab6bcf50fcd06326118'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def put(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def files(p):return [x for x in p.rglob('*') if x.is_file() and not {'receipts','__pycache__'} & set(x.parts) and x.name not in ('source-manifest.json','contract-profile.json')]
def tests(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
 assert not API.exists()
 spec=importlib.util.spec_from_file_location('_cal_API47_parent_guard',PARENT/'guard.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
 parent=g.verify(PIN)
 finding=json.loads((RUN/'API45-known-outcome-source-cost-finding-0001.json').read_bytes());assert finding['result']=='MEASURED' and not finding['normal_runtime_qualified']
 API.mkdir();(API/'receipts').mkdir()
 for p in files(PARENT):
  target=API/p.relative_to(PARENT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())
 p=API/'service.py';s=p.read_text()
 for exception in ['RuleFailure','FailureRuleFailure']:
  start='                    except '+exception+' as error:\n';end='                        self.vault.finish(namespace,domain,error.evidence,posture=\'failed\')\n'
  assert s.count(start)==1
  a=s.index(start)+len(start);b=s.index(end,a);original=s[a:b]
  assert original.startswith('                        self.channel.guard();self.schemas.guard()\n')
  grouped='                        from .guarded_candidate import selection\n                        with selection(self):\n'+''.join('    '+line if line.strip() else line for line in original.splitlines(keepends=True))
  s=s[:a]+grouped+s[b:]
 p.write_text(s)
 old=ast.parse((PARENT/'service.py').read_bytes());new=ast.parse(p.read_bytes());groups=0
 for n in ast.walk(new):
  if isinstance(n,ast.ExceptHandler) and isinstance(n.type,ast.Name) and n.type.id in ['RuleFailure','FailureRuleFailure']:
   assert isinstance(n.body[0],ast.ImportFrom) and n.body[0].module=='guarded_candidate'
   assert [a.name for a in n.body[0].names]==['selection']
   group=n.body[1];assert isinstance(group,ast.With) and len(group.items)==1 and ast.unparse(group.items[0].context_expr)=='selection(self)'
   assert len(group.body)==5
   assert ast.unparse(n.body[2]).startswith('self.vault.finish(') and isinstance(n.body[3],ast.Return)
   n.body=group.body+n.body[2:];groups+=1
 assert groups==2 and ast.dump(old,include_attributes=False)==ast.dump(new,include_attributes=False)
 retained=[];changed=[]
 for p in files(PARENT):
  target=API/p.relative_to(PARENT)
  if p.read_bytes()!=target.read_bytes():changed.append(p.relative_to(PARENT).as_posix())
  if p.suffix=='.py':assert tests(p)==tests(target);retained.extend(p.relative_to(PARENT).as_posix()+':'+n for n in tests(p))
 assert changed==['service.py'] and len(retained)==293
 context=RUN/'context-R03-known-outcome-read-scope-API-0047.json';static=RUN/'API47-known-outcome-static-0001.json'
 put(context,{'schema_version':'lab-bounded-context/v1-candidate','task':'R03 group known-rule-failure pure predicates through existing read composition','strict_coverage':'PASS','blockers':[],
 'source_bindings':[bind(p) for p in [PARENT/'source-manifest.json',RUN/'authorization.json',RUN/'API45-known-outcome-source-cost-finding-0001.json',RUN/'API45-failure12-cpu-measurement-0001.json',RUN/'API45-failure12-cpu-measurement-terminal-0001.json',PARENT/'guarded_candidate.py',BASE/'fact-read-scope-v2/scope.py']],
 'write_scope':API.relative_to(ROOT).as_posix(),'constraints':['All293 original tests and34 public schemas remain unchanged.','Both known-outcome predicate sequences are AST-identical after flattening the added context/import.','Actual permission bytes and real clocks remain read at each original callback.','Original source/producer checks run on scope entry and exit.','No journal finish or reply delivery runs within the pure scope.','Original900-second deadline and all original refusal/cleanup expectations remain.','Normal deadline improvement must be established by original successor cases, not profiling.'],
 'validation_surface':'Full original AST retention plus all original public failure/classification/control/source/permission/expiry/refusal/cleanup suites; successor verification remains sequential.', 'actual_owner_outcome':None,'authority_effect':'none','task_complete':False})
 put(static,{'schema_version':'lab-known-outcome-read-scope-static/v1-candidate','result':'PASS','changed_API_files':changed,'unchanged_original_test_methods':293,'unchanged_original_public_contracts':34,'known_outcome_groups':2,'original_predicate_ASTs_unchanged':True,'every_other_original_Service_AST_unchanged':True,'durable_finish_and_delivery_outside_scope':True,'original_permission_callbacks_and_clocks_unchanged':True,'actual_public_calls':0,'normal_runtime_qualified':False,'whole_API_qualified':False,'actual_owner_outcome':None,'authority_effect':'none','task_complete':False})
 profile=json.loads((PARENT/'contract-profile.json').read_bytes());profile['files']=[bind(API/(ROOT/r['path']).relative_to(PARENT)) if (ROOT/r['path']).is_relative_to(PARENT) else r for r in profile['files']]
 profile['known_outcome_read_scope_context_binding']=bind(context);profile['claim_ceiling']='Sixteen authored handlers; all original known-outcome predicates preserved within existing pure source composition. Actual deadline and complete original runtime qualification remain outstanding.'
 put(API/'contract-profile.json',profile)
 rows={r['path']:r for r in parent['files']}
 for p in [PARENT/'source-manifest.json',context,static,Path(__file__).resolve(),RUN/'API45-known-outcome-source-cost-finding-0001.json',RUN/'API45-failure12-cpu-measurement-0001.json',RUN/'API45-failure12-cpu-measurement-terminal-0001.json',RUN/'API45-failure12-cpu-measurement-0001.log']+files(API)+[API/'contract-profile.json']:
  r=bind(p);rows[r['path']]=r
 for r in rows.values():assert hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256']
 manifest={**parent,'files':[rows[k] for k in sorted(rows)],'parent_source_binding':bind(PARENT/'source-manifest.json'),'context_binding':bind(context),'static_checks_binding':bind(static),'retained_inherited_methods':retained,'unchanged_inherited_method_count':293,'whole_API_qualified':False,'current_Agent_qualified':False,'task_complete':False,'goal_complete':False}
 put(API/'source-manifest.json',manifest)
 print(json.dumps({'result':'FROZEN','source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),'source_files':len(rows),'unchanged_methods':293,'normal_runtime_qualified':False}),flush=True)
if __name__=='__main__':main()
