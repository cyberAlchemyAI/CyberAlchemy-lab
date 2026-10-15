"""Freeze readiness successor independently; preserve the running v1 parent."""
from pathlib import Path
import json,hashlib,ast
R=Path('/home/vlad_/projects/CyberAlchemy-lab');RUN=Path(__file__).parent;I=R/'product/lab/release-candidates/v1/interface';N=I/'api-installation-release-v3';O=I/'api-installation-release-v2';V6=I/'api-integration-v6'
def bind(p):return {'path':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def load(p):return json.loads(p.read_bytes())
def emit(p,v):p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
assert bind(O/'source-manifest.json')['sha256']=='6cf76392309e7d2ee1c47ec6d3d979a893e4610264fac044af6a30ffdecf4ce4'
assert bind(O/'contract-profile.json')['sha256']=='ccb2cf9222d228bbffe9870057debb3423c3a3336e2570682f145eab007b6476'
count=0
for old in V6.glob('*.py'):
 def tests(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
 assert tests(old)==tests(N/old.name),old.name;count+=len(tests(old))
assert count==323
oldprefix=O.relative_to(R).as_posix()+'/';newprefix=N.relative_to(R).as_posix()+'/'
selected=load(O/'SCHEMA-EXECUTION-DEPENDENCIES.json');rows={};reasons={}
for row in selected['files']:
 path=row['path'];path=newprefix+path[len(oldprefix):] if path.startswith(oldprefix) else path
 rows[path]=bind(R/path);reasons[path]=selected['selection_reasons'][row['path']]
for p in N.rglob('*'):
 if p.is_file() and p.suffix in ('.py','.json','.whl') and p.name not in ('source-manifest.json','contract-profile.json','SCHEMA-EXECUTION-DEPENDENCIES.json'):
  row=bind(p);rows[row['path']]=row;reasons.setdefault(row['path'],[]).append('Complete conservative local readiness/code/schema/control/dependency selection. Actual original callbacks remain unchanged.')
for path in ['product/lab/release-candidates/v1/release-scope.json','product/lab/release-candidates/v1/pilot/preparation-v1/PILOT-PROTOCOL.md']:
 rows[path]=bind(R/path);reasons[path]=['Actual predeclared Product acceptance and genuine human pilot source, never a completion claim.']
selected.update(files=[rows[k] for k in sorted(rows)],selection_reasons=reasons,parent_source_binding=bind(O/'source-manifest.json'),parent_profile_binding=bind(O/'contract-profile.json'))
selection=N/'SCHEMA-EXECUTION-DEPENDENCIES.json';emit(selection,selected)
profile=load(O/'contract-profile.json');full={r['path']:r for r in profile['files']}
for row in [*rows.values(),bind(selection)]:full[row['path']]=row
profile.update(files=[full[k] for k in sorted(full)],schema_execution_dependency_binding=bind(selection));emit(N/'contract-profile.json',profile)
manifest=load(O/'source-manifest.json');full={r['path']:r for r in manifest['files']}
for p in N.rglob('*'):
 if p.is_file() and p.name!='source-manifest.json' and '__pycache__' not in p.parts and 'receipts' not in p.parts:full[bind(p)['path']]=bind(p)
for p in [Path(__file__),RUN/'qualify-installation-release-readiness-v3-0148.py',RUN/'ARE-transport-evidence-boundary-0158.json']:full[bind(p)['path']]=bind(p)
manifest.update(files=[full[k] for k in sorted(full)],parent_source_binding=bind(O/'source-manifest.json'),schema_execution_dependency_binding=bind(selection),original_test_method_ASTs_retained=count,new_installation_release_test_methods=21,readiness_can_become_ready_with_actual_signed_complete_inputs=True,current_whole_Lab_readiness_qualified=False,whole_API_qualified=False,goal_complete=False);emit(N/'source-manifest.json',manifest)
print(json.dumps({'source':bind(N/'source-manifest.json'),'profile':bind(N/'contract-profile.json'),'selected_schema_execution_files':len(rows),'original_methods_retained':count}))
