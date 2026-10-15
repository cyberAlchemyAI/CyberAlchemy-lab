"""Freeze the authenticated export successor with all original contracts/tests."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';OLD=BASE/'api-v57';API=BASE/'api-v58'
def load(path):return json.loads(path.read_bytes())
def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def emit(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
def files(folder):return sorted(p for p in folder.rglob('*') if p.is_file() and not {'receipts','__pycache__'}&set(p.parts)
    and p.name not in ('source-manifest.json','contract-profile.json'))
def tests(path):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(path.read_bytes()))
    if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    spec=importlib.util.spec_from_file_location('_cal_API58_parent_guard',OLD/'guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    parent=guard.verify('31028e938f21265f753f822ae6f9838cfa4f5b0aaf36596feafc482bccd36d21')
    inherited=[]
    for path in files(OLD):
        if path.suffix=='.py':
            assert tests(path)==tests(API/path.relative_to(OLD)),path
            inherited.extend(path.relative_to(OLD).as_posix()+':'+name for name in tests(path))
    assert len(inherited)==293 and len(tests(API/'test_package_export.py'))==12
    extra=[]
    for folder in (API,BASE/'lesson-host-composition-v8'):
        for path in files(folder):
            if path.suffix=='.py':ast.parse(path.read_bytes())
            extra.append(bind(path))
    extra.extend(bind(path) for path in (RUN/'author-API58-package-export-0001.py',
        RUN/'author-API58-export-plan-schema-0001.py',Path(__file__).resolve()))
    profile=load(OLD/'contract-profile.json');profile['implemented_operations'].append('package.export')
    assert len(profile['implemented_operations'])==20
    catalog=load(ROOT/profile['original_operation_catalog_binding']['path']);assert len(catalog['operations'])==34
    rows={row['path']:row for row in profile['files']}
    for row in list(rows.values()):
        path=ROOT/row['path']
        if path.is_relative_to(OLD):new=bind(API/path.relative_to(OLD));rows[new['path']]=new
    for row in extra:rows[row['path']]=row
    profile['files']=[rows[k] for k in sorted(rows)]
    profile['claim_ceiling']='Twenty authored handlers, including independently authorized original-source managed package export. Actual selected qualification required. Fourteen public operations and broader package/authority/carrier closure and complete plan remain unfinished.'
    emit(API/'contract-profile.json',profile)
    rows={row['path']:row for row in parent['files']}
    for row in extra+[bind(API/'contract-profile.json'),bind(OLD/'source-manifest.json')]:rows[row['path']]=row
    for row in rows.values():assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
    emit(API/'source-manifest.json',{**parent,'files':[rows[k] for k in sorted(rows)],
        'parent_source_binding':bind(OLD/'source-manifest.json'),'retained_inherited_methods':inherited,
        'unchanged_inherited_method_count':293,'added_export_methods':12,'whole_API_qualified':False,
        'pending_evidence_runtime_qualified':False,'classification_actual_runtime_qualified':False,
        'package_export_actual_runtime_qualified':False,'task_complete':False,'goal_complete':False})
    print(json.dumps({'result':'FROZEN','source_binding':bind(API/'source-manifest.json'),
        'profile_binding':bind(API/'contract-profile.json'),'retained_original_methods':293,
        'added_export_cases':12,'retained_original_contracts':34,'authored_handlers':20,
        'missing_operations':14,'actual_runtime_qualified':False}),flush=True)
if __name__=='__main__':main()
