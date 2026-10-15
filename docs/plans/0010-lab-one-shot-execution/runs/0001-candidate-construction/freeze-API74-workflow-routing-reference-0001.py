"""Freeze original-contract challenge adapter without inheriting runtime claims."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';OLD=BASE/'api-v73';API=BASE/'api-v74'
def load(p):return json.loads(p.read_bytes())
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def emit(p,v):
    with p.open('x') as stream:json.dump(v,stream,indent=2,sort_keys=True);stream.write('\n')
def files(folder):return sorted(p for p in folder.rglob('*') if p.is_file() and not {'receipts','__pycache__'}&set(p.parts) and p.name not in ('source-manifest.json','contract-profile.json'))
def tests(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    spec=importlib.util.spec_from_file_location('_cal_API74_parent_guard',OLD/'guard.py');guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    parent=guard.verify('e4c01c240b0d3030cae83bb822a4a1227478a84205337de8f528f4722c0fc8d9')
    inherited=[]
    for p in files(OLD):
        if p.suffix=='.py':
            before=tests(p);after=tests(API/p.relative_to(OLD))
            assert before==after,p
            inherited.extend(p.relative_to(OLD).as_posix()+':'+name for name in before)
    assert len(inherited)==320
    assert len(tests(API/'test_generated_candidate.py'))==5
    assert len(tests(API/'test_workflow_composition.py'))==3
    extra=[]
    for folder in (API,BASE/'lesson-host-composition-v24'):
        for p in files(folder):
            if p.suffix=='.py':ast.parse(p.read_bytes())
            extra.append(bind(p))
    extra.extend(bind(p) for p in (RUN/'author-API74-workflow-routing-reference-0001.py',OLD/'receipts/workflow-composition-focused-checks-0001.json',OLD/'receipts/workflow-composition-focused-0001.log',OLD/'receipts/workflow-composition-focused-wire-0001.json',RUN/'API73-workflow-focused-terminal-0001.json',BASE/'api-v71/receipts/generated-focused-checks-0001.json',BASE/'api-v71/receipts/generated-focused-0001.log',BASE/'api-v71/receipts/generated-focused-wire-0001.json',
        RUN/'author-API60-challenge-routing-schema-0001.py',Path(__file__).resolve(),RUN/'API69-generated_candidate.py',
        RUN/'API66-challenge-preflight-diagnosis-0001.json',RUN/'diagnose-API66-challenge-preflight-0001.py',
        RUN/'API64-challenge-preflight-diagnosis-0001.json',RUN/'diagnose-API64-challenge-preflight-0001.py',
        BASE/'checkpoint-owner-verification-v3/receipts/checks-0001.json',
        BASE/'checkpoint-owner-verification-v3/source-manifest.json'))
    profile=load(OLD/'contract-profile.json')
    assert profile['implemented_operations'][12]=='challenge.submit'
    assert len(profile['implemented_operations'])==21
    catalog=load(ROOT/profile['original_operation_catalog_binding']['path']);assert len(catalog['operations'])==34
    rows={r['path']:r for r in profile['files']}
    for row in list(rows.values()):
        p=ROOT/row['path']
        if p.is_relative_to(OLD):new=bind(API/p.relative_to(OLD));rows[new['path']]=new
    for row in extra:rows[row['path']]=row
    profile['files']=[rows[k] for k in sorted(rows)]
    profile['claim_ceiling']='Twenty-one authored handlers with original contracts; actual challenge and inherited current runtime qualification required. No complete API or actual owner authority.'
    emit(API/'contract-profile.json',profile)
    rows={r['path']:r for r in parent['files']}
    for row in extra+[bind(API/'contract-profile.json'),bind(OLD/'source-manifest.json')]:rows[row['path']]=row
    for row in rows.values():assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
    emit(API/'source-manifest.json',{**parent,'files':[rows[k] for k in sorted(rows)],'parent_source_binding':bind(OLD/'source-manifest.json'),
        'retained_inherited_methods':inherited,'unchanged_inherited_method_count':320,'whole_API_qualified':False,
        'challenge_submit_actual_runtime_qualified':False,'generated_candidate_actual_runtime_qualified':False,'package_export_actual_runtime_qualified':False,
        'readonly_lookup_actual_runtime_qualified':False,'task_complete':False,'goal_complete':False})
    print(json.dumps({'result':'FROZEN','source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),
        'unchanged_inherited_methods':320,'original_public_contracts':34,'authored_handlers':21,'missing_operations':13,'actual_runtime_qualified':False}),flush=True)
if __name__=='__main__':main()
