"""Freeze exact pending-evidence successor without inheriting qualification."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
OLD,API=BASE/'api-v56',BASE/'api-v57'
CHECK=BASE/'api57-classification-checks-v1'

def load(path):return json.loads(path.read_bytes())
def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def files(folder):
    return sorted(p for p in folder.rglob('*') if p.is_file()
        and not {'receipts','__pycache__'}&set(p.parts)
        and p.name not in ('source-manifest.json','contract-profile.json'))
def emit(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
def tests(path):
    return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(path.read_bytes()))
        if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}

def main():
    spec=importlib.util.spec_from_file_location('_cal_API57_parent_guard',OLD/'guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    parent=guard.verify('160eff199de756b0212bb9b3c8f180dd6c13037a77385319a1e4fad4dc818361')
    inherited=[]
    for path in files(OLD):
        if path.suffix=='.py':
            assert tests(path)==tests(API/path.relative_to(OLD)),path
            inherited.extend(path.relative_to(OLD).as_posix()+':'+n for n in tests(path))
    assert len(inherited)==293
    previous=tests(BASE/'api56-classification-checks-v1/test_classification_api.py')
    current=tests(CHECK/'test_classification_api.py')
    assert len(previous)==16 and len(current)==17
    assert all(current[name]==body for name,body in previous.items())
    extra=[]
    for folder in (API,CHECK,BASE/'classification-preparation-v9',BASE/'lesson-host-composition-v7'):
        for path in files(folder):
            if path.suffix=='.py':ast.parse(path.read_bytes())
            extra.append(bind(path))
    author=RUN/'author-API57-pending-evidence-0001.py'
    extra.extend([bind(author),bind(Path(__file__).resolve())])
    profile=load(OLD/'contract-profile.json')
    rows={row['path']:row for row in profile['files']}
    for row in list(rows.values()):
        path=ROOT/row['path']
        if path.is_relative_to(OLD):
            new=bind(API/path.relative_to(OLD));rows[new['path']]=new
    for row in extra:rows[row['path']]=row
    profile['files']=[rows[key] for key in sorted(rows)]
    profile['claim_ceiling']='Nineteen authored handlers, pending native verification evidence visible through authenticated operation inspection; exact qualification required. Fifteen public operations and complete plan remain outstanding.'
    assert len(profile['implemented_operations'])==19
    emit(API/'contract-profile.json',profile)
    rows={row['path']:row for row in parent['files']}
    for row in extra+[bind(API/'contract-profile.json'),bind(OLD/'source-manifest.json')]:rows[row['path']]=row
    for row in rows.values():assert bind(ROOT/row['path'])==row,row['path']
    emit(API/'source-manifest.json',{**parent,'files':[rows[k] for k in sorted(rows)],
        'parent_source_binding':bind(OLD/'source-manifest.json'),'retained_inherited_methods':inherited,
        'unchanged_inherited_method_count':293,'whole_API_qualified':False,
        'classification_actual_runtime_qualified':False,'pending_evidence_runtime_qualified':False,
        'task_complete':False,'goal_complete':False})
    selection=[bind(p) for p in files(CHECK)]+[bind(API/'source-manifest.json'),
        bind(API/'contract-profile.json'),bind(API/'test_classification_api.py')]
    emit(CHECK/'source-manifest.json',{'schema_version':'lab-separate-classification-check-source/v1-candidate',
        'files':selection,'original_classification_methods':16,
        'previous16_successor_methods_unchanged':True,'added_method':'test_17_pending_native_evidence_is_inspectable_and_tamper_refused',
        'actual_runtime_qualified':False,'authority_effect':'none','actual_owner_outcome':None})
    print(json.dumps({'result':'FROZEN','source_binding':bind(API/'source-manifest.json'),
        'profile_binding':bind(API/'contract-profile.json'),'check_source_binding':bind(CHECK/'source-manifest.json'),
        'inherited_original_methods':293,'retained_classification_cases':16,'added_cases':1,
        'actual_runtime_qualified':False}),flush=True)

if __name__=='__main__':main()
