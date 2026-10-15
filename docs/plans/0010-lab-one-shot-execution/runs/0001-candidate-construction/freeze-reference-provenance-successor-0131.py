"""Freeze the explicit reference-role successor before actual qualification."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';OLD=BASE/'api-v88';API=BASE/'api-v89'

def bind(path):return {'path':path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def load(path):return json.loads(path.read_bytes())
def emit(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
def methods(path):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(path.read_text())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}

def main():
    assert not (API/'source-manifest.json').exists()
    spec=importlib.util.spec_from_file_location('_cal_API89_parent_guard',OLD/'guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    parent=guard.verify('585343c67bad6484df5a43f7ba772619e66b5e49f56ebe227dabf55296a1d06f')
    local=[];retained=[]
    for folder in (API,BASE/'challenge-resolution-v4',BASE/'lesson-host-composition-v39'):
        for path in sorted(folder.rglob('*')):
            if not path.is_file() or {'receipts','__pycache__'}&set(path.parts) or path.name in ('source-manifest.json','contract-profile.json'):continue
            if path.suffix=='.py':
                ast.parse(path.read_text())
                if folder==API:
                    old=OLD/path.relative_to(API)
                    if old.exists():
                        assert methods(old)==methods(path),path
                        retained.extend(path.relative_to(API).as_posix()+':'+name for name in methods(path))
            local.append(bind(path))
    assert len(retained)==323
    for name in ('machine_transport.py','machine_context_scope.py','custody_context_sessions.py'):
        assert (API/name).read_bytes()==(OLD/name).read_bytes(),name
    context=RUN/'context-R03-exact-reference-provenance-0131.json'
    evidence=[RUN/'authorization.json',RUN/'API87-integrated-resolution-diagnosis-0002.json',
              RUN/'build-reference-successors-0131.py',Path(__file__).resolve(),OLD/'source-manifest.json']
    emit(context,{'schema_version':'lab-bounded-context/v1-candidate','task':'R03 exact scoped reference closure',
        'source_bindings':[bind(p) for p in evidence],
        'constraints':['Existing candidate construction authorization; one final R08 owner checkpoint.',
            'Source8 signed originals, exact gate and proposals remain unchanged.',
            'Explicit expected-output protocol declaration under pending Work; no produced output or Work satisfaction.',
            'Historical eligibility applies only to the independently bound exact challenged Work revision.',
            'Full Challenge reference inventory, response transition and evidence closure remain required.',
            'All323inherited methods unchanged; new public qualification does not transfer full API or Machine validation.'],
        'authority_effect':'none','actual_owner_outcome':None})
    profile=load(OLD/'contract-profile.json');rows={r['path']:r for r in profile['files']}
    for row in [*local,*[bind(p) for p in [*evidence,context]]]:
        assert rows.get(row['path'],row)==row;rows[row['path']]=row
    for row in rows.values():assert bind(ROOT/row['path'])==row,row['path']
    profile.update(files=[rows[k] for k in sorted(rows)],exact_reference_context_binding=bind(context),
        integrated_resolution_method_binding=bind(BASE/'challenge-resolution-v4/preparation.py'),
        claim_ceiling='24authored handlers and explicit scoped reference roles only; actual public resolution and full inherited qualification required.')
    emit(API/'contract-profile.json',profile)
    full={r['path']:r for r in parent['files']}
    for row in [*rows.values(),bind(API/'contract-profile.json'),bind(OLD/'source-manifest.json')]:
        assert full.get(row['path'],row)==row;full[row['path']]=row
    for row in full.values():assert bind(ROOT/row['path'])==row,row['path']
    emit(API/'source-manifest.json',{**parent,'files':[full[k] for k in sorted(full)],
        'parent_source_binding':bind(OLD/'source-manifest.json'),'retained_inherited_methods':retained,
        'unchanged_inherited_method_count':323,'explicit_revised_methods':0,'binding_only_revised_methods':[],
        'exact_reference_context_binding':bind(context),'authored_handler_count':24,
        'integrated_public_resolution_qualified':False,'current_Agent_qualified':False,'whole_API_qualified':False,
        'runtime_qualification_transferred':False,'task_complete':False,'goal_complete':False})
    print(json.dumps({'result':'FROZEN','source_binding':bind(API/'source-manifest.json'),
        'profile_binding':bind(API/'contract-profile.json'),'retained_methods':len(retained)}))

if __name__=='__main__':main()
