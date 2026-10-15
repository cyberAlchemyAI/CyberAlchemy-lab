"""Refresh authored successor once before final exact qualification; preserve parent bytes."""
from pathlib import Path
import json,hashlib,ast
R=Path('/home/vlad_/projects/CyberAlchemy-lab');RUN=Path(__file__).parent;N=R/'product/lab/release-candidates/v1/interface/api-installation-release-v1';O=N.parent/'api-integration-v6'
def bind(p):return {'path':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def load(p):return json.loads(p.read_bytes())
def emit(p,v):p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
assert bind(O/'source-manifest.json')['sha256']=='7ab054776a5fa8fd310f60e126a29c98686d159f989fb3a721cb6dcd1f1f119f'
assert bind(O/'contract-profile.json')['sha256']=='d832f9c20e487261d9987906408dfbd54c7f6cf624890f9144d750d7eb8a053f'
old_methods=0
for old in O.glob('*.py'):
 def tests(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
 assert tests(old)==tests(N/old.name),old.name
 old_methods+=len(tests(old))
assert old_methods==323
selection=N/'SCHEMA-EXECUTION-DEPENDENCIES.json';selected=load(selection)
for row in selected['files']:row['sha256']=bind(R/row['path'])['sha256']
selected['files'].sort(key=lambda r:r['path']);emit(selection,selected)
profile=load(N/'contract-profile.json');rows={r['path']:r for r in profile['files']}
for row in [*selected['files'],bind(selection)]:rows[row['path']]=row
profile.update(files=list(sorted(rows.values(),key=lambda r:r['path'])),schema_execution_dependency_binding=bind(selection));emit(N/'contract-profile.json',profile)
manifest=load(N/'source-manifest.json');rows={r['path']:r for r in manifest['files']}
for p in N.rglob('*'):
 if p.is_file() and p.name!='source-manifest.json' and 'receipts' not in p.parts and '__pycache__' not in p.parts:rows[bind(p)['path']]=bind(p)
for p in [RUN/'qualify-installation-release-0148.py',Path(__file__),RUN/'INSTALLATION-RELEASE-0148.md']:rows[bind(p)['path']]=bind(p)
manifest.update(files=list(sorted(rows.values(),key=lambda r:r['path'])),schema_execution_dependency_binding=bind(selection),original_test_method_ASTs_retained=old_methods,new_installation_release_test_methods=15,runtime_qualification_transferred=False,whole_API_qualified=False,goal_complete=False);emit(N/'source-manifest.json',manifest)
print(json.dumps({'source':bind(N/'source-manifest.json'),'profile':bind(N/'contract-profile.json'),'selected_schema_execution_files':len(selected['files']),'original_methods_retained':old_methods}))
