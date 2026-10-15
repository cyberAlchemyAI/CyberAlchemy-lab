"""Freeze exact integrated source/public policy before owned API qualification."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';OLD,API=BASE/'api-v86',BASE/'api-v87'


def bind(path):return {'path':path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def load(path):return json.loads(path.read_bytes())
def emit(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
def methods(text):return {node.name:ast.dump(node,include_attributes=False) for node in ast.walk(ast.parse(text)) if isinstance(node,ast.FunctionDef) and node.name.startswith('test_')}


def main():
    assert not (API/'source-manifest.json').exists() and not (API/'contract-profile.json').exists()
    spec=importlib.util.spec_from_file_location('_cal_API87_parent_guard',OLD/'guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    parent=guard.verify('03f8cbad5579f81d6ed6242ba0aee6e30b468e91b55c6984f73ab5a74064859f')
    qualified=RUN/'integrated-source-qualification-0008.json';q=load(qualified)
    assert q['result']=='PASS' and q['actual_cases']==23 and q['errors']==q['failures']==0
    unchanged,revised,local=[],[],[]
    for folder in (API,BASE/'challenge-resolution-v3',BASE/'lesson-host-composition-v37'):
        for path in sorted(folder.rglob('*')):
            if not path.is_file() or {'receipts','__pycache__'}&set(path.parts) or path.name in ('source-manifest.json','contract-profile.json'):continue
            if path.suffix=='.py':
                actual=methods(path.read_text());old=OLD/path.relative_to(API) if folder==API else None
                if old is not None and old.exists():
                    before=methods(old.read_text());expected=old.read_text()
                    if old.name=='test_current_controls.py':expected=expected.replace('product:cyberalchemy-lab@current-episode-0003.candidate.1','product:cyberalchemy-lab@current-episode-0004.candidate.1')
                    assert methods(expected)==actual,path
                    for name in before:(unchanged if before[name]==actual[name] else revised).append(path.relative_to(API).as_posix()+':'+name)
            local.append(bind(path))
    assert len(unchanged)==322 and len(revised)==1
    for name in ('machine_transport.py','machine_context_scope.py','custody_context_sessions.py','candidate.py'):
        assert (API/name).read_bytes()==(OLD/name).read_bytes(),name
    context=RUN/'context-R03-integrated-public-resolution-0087.json'
    sources=[qualified,RUN/'integrated-reader-qualification-0007.json',RUN/'authorization.json',Path(__file__).resolve(),
             BASE/'current-source-adapter-v7/source-manifest.json',BASE/'current-participation-v8/source-manifest.json',
             BASE/'current-participation-v8/packages/0001/manifest.json',OLD/'source-manifest.json']
    emit(context,{'schema_version':'lab-bounded-context/v1-candidate','task':'R03 actual integrated public challenge resolution',
        'source_bindings':[bind(path) for path in sources],
        'constraints':['Exact independently pinned Source8/Reader7 selection and closed integrated owner metadata policy; no Agent Session participation is added.',
                       'Actual policy/source/schema/vault guards and immutable source stamps run at pure calculation boundaries; original dispatch and atomic durable writes refuse active integrated pure scope.',
                       'New source calculation uses complete actual source checks. Source5 original Machine/fact-copy paths remain selected separately.',
                       'Independent selected signed gate object avoids circular input-manifest hashing and grants only exact candidate consequence preparation.',
                       'All323inherited methods retained;322ASTunchanged;1exact observed Product fixture reference correction with assertions retained.',
                       'Original transport, native prospective target validator, journal/retry/deadline and privacy remain. New public source and affected inherited qualification required.'],
        'public_runtime_qualified':False,'actual_owner_outcome':None,'authority_effect':'none'})
    profile=load(OLD/'contract-profile.json');assert len(profile['implemented_operations'])==24
    rows={row['path']:row for row in profile['files']}
    for row in list(rows.values()):
        path=ROOT/row['path']
        if path.is_relative_to(OLD):rows[bind(API/path.relative_to(OLD))['path']]=bind(API/path.relative_to(OLD))
    for row in [*local,*q['files'],*load(BASE/'current-source-adapter-v7/source-manifest.json')['files'],
                *[bind(path) for path in [*sources,context]]]:
        assert rows.get(row['path'],row)==row,row['path'];rows[row['path']]=row
    for row in rows.values():assert bind(ROOT/row['path'])==row,row['path']
    profile.update(files=[rows[key] for key in sorted(rows)],integrated_resolution_context_binding=bind(context),
        integrated_resolution_method_binding=bind(BASE/'challenge-resolution-v3/preparation.py'),
        claim_ceiling='24authored handlers; actual Source8 cold/native/gate and Reader7 catalog evidence only. Integrated public resolution and changed inherited qualification remain required.')
    emit(API/'contract-profile.json',profile)
    full={row['path']:row for row in parent['files']}
    for row in [*rows.values(),bind(API/'contract-profile.json'),bind(OLD/'source-manifest.json')]:
        assert full.get(row['path'],row)==row,row['path'];full[row['path']]=row
    for row in full.values():assert bind(ROOT/row['path'])==row,row['path']
    emit(API/'source-manifest.json',{**parent,'files':[full[key] for key in sorted(full)],
        'parent_source_binding':bind(OLD/'source-manifest.json'),'retained_inherited_methods':unchanged+revised,
        'unchanged_inherited_method_count':322,'explicit_revised_methods':1,'binding_only_revised_methods':revised,
        'integrated_resolution_context_binding':bind(context),'authored_handler_count':24,
        'integrated_public_resolution_qualified':False,'current_Agent_qualified':False,'whole_API_qualified':False,
        'runtime_qualification_transferred':False,'task_complete':False,'goal_complete':False})
    print(json.dumps({'result':'FROZEN','source_binding':bind(API/'source-manifest.json'),
        'profile_binding':bind(API/'contract-profile.json'),'retained_methods':323,'unchanged_methods':322,
        'authored_handlers':24,'remaining_handlers':10,'public_runtime_qualified':False}),flush=True)


if __name__=='__main__':main()
