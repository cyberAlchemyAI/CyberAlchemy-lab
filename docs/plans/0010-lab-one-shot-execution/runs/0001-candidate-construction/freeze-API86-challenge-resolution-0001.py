"""Freeze exact authored resolution candidate without transferring runtime proof."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';OLD,API=BASE/'api-v85',BASE/'api-v86'
COMPONENT=BASE/'challenge-resolution-v1'


def bind(path):return {'path':path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def load(path):return json.loads(path.read_bytes())
def emit(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
def methods(text):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(text)) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}


def main():
    assert not (API/'source-manifest.json').exists() and not (API/'contract-profile.json').exists()
    spec=importlib.util.spec_from_file_location('_cal_API86_parent_guard',OLD/'guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    parent=guard.verify('adb265d1ef7d8762e9fae1a1f984d19b8605d0a40ef43fffe89ba04728d53fae')
    qualified=RUN/'challenge-resolution-contracts-0001.json';q=load(qualified)
    assert q['result']=='PASS' and q['actual_cases']==15 and q['failures']==q['errors']==0
    for row in q['files']:assert bind(ROOT/row['path'])==row
    unchanged,revised,local=[],[],[]
    for folder in (API,COMPONENT,BASE/'lesson-host-composition-v36'):
        for path in sorted(folder.rglob('*')):
            if not path.is_file() or {'receipts','__pycache__'}&set(path.parts) or path.name in ('source-manifest.json','contract-profile.json'):continue
            if path.suffix=='.py':
                actual=methods(path.read_text());old=OLD/path.relative_to(API) if folder==API else None
                if old is not None and old.exists():
                    before=methods(old.read_text())
                    expected=methods(old.read_text().replace('self.assertEqual(len(SUPPORTED),23)','self.assertEqual(len(SUPPORTED),24)'))
                    assert actual==expected,path
                    for name in before:
                        (unchanged if before[name]==actual[name] else revised).append(path.relative_to(API).as_posix()+':'+name)
            local.append(bind(path))
    assert len(unchanged)+len(revised)==323 and len(revised)==3
    for name in ('machine_transport.py','guarded_reads.py','guarded_candidate.py','workspace.py','custody_context_sessions.py'):
        assert (API/name).read_bytes()==(OLD/name).read_bytes(),name
    catalog=ROOT/'docs/proposals/0008-lab-api-contracts/operations/challenge.resolve.json'
    source_paths=[OLD/'source-manifest.json',catalog,
        ROOT/'docs/proposals/0007-lab-integrated-schema-package/schemas/challenge-resolution.schema.json',
        qualified,RUN/'authorization.json',RUN/'author-API86-challenge-resolution-0001.py',
        RUN/'API86-authoring-attempt-0001.json',RUN/'complete-API86-authoring-0002.py',
        RUN/'API86-authoring-completion-0002.json',RUN/'qualify-challenge-contracts-0001.py',Path(__file__).resolve()]
    context=RUN/'context-R03-challenge-resolution-0086.json'
    emit(context,{'schema_version':'lab-bounded-context/v1-candidate','task':'R03 challenge.resolve candidate preparation',
        'source_bindings':[bind(path) for path in source_paths],
        'constraints':['Independent exact signed development owner gate, recognized current Principal/key and real clock required; declarations alone supply no permission.',
                       'Original Contract response mode, evidence kinds, owner/policy/gate/residue routes and response period must close.',
                       'Semantic and governance bindings remain distinct; compose complete exact targets, connections, schemas and evidence; preserve original proposal bytes.',
                       'Declared Effects, target versions and Decision Scopes remain separate exact types; proposed successor cannot overwrite existing challenged bytes.',
                       'Actual transport, journal, clocks, privacy and guarded candidate validation remain; no admission, dispatch, activation or publication.',
                       'All323 inherited methods retained:320AST unchanged;3exact registry count expectations23to24 only. Original API remains34operations.',
                       '15actual isolated component cases passed; positive current-source and public handler qualification remain pending.'],
        'runtime_qualified':False,'actual_owner_outcome':None,'authority_effect':'none'})
    profile=load(OLD/'contract-profile.json');profile['implemented_operations'].append('challenge.resolve')
    assert len(profile['implemented_operations'])==24
    rows={row['path']:row for row in profile['files']}
    for row in list(rows.values()):
        path=ROOT/row['path']
        if path.is_relative_to(OLD):rows[bind(API/path.relative_to(OLD))['path']]=bind(API/path.relative_to(OLD))
    for row in [*local,*q['files'],*[bind(path) for path in [*source_paths,context]]]:
        assert rows.get(row['path'],row)==row,row['path'];rows[row['path']]=row
    for row in rows.values():assert bind(ROOT/row['path'])==row,row['path']
    profile.update(files=[rows[key] for key in sorted(rows)],challenge_resolution_context_binding=bind(context),
        challenge_resolution_method_binding=bind(COMPONENT/'preparation.py'),
        claim_ceiling='24 authored handlers;15 actual isolated resolution contract cases only. Public/current-source resolution, inherited Machine and wholeAPI qualification remain pending.')
    emit(API/'contract-profile.json',profile)
    full={row['path']:row for row in parent['files']}
    for row in [*rows.values(),bind(API/'contract-profile.json'),bind(OLD/'source-manifest.json')]:
        assert full.get(row['path'],row)==row,row['path'];full[row['path']]=row
    for row in full.values():assert bind(ROOT/row['path'])==row,row['path']
    emit(API/'source-manifest.json',{**parent,'files':[full[key] for key in sorted(full)],
        'parent_source_binding':bind(OLD/'source-manifest.json'),'retained_inherited_methods':unchanged+revised,
        'unchanged_inherited_method_count':len(unchanged),'explicit_revised_methods':len(revised),
        'binding_only_revised_methods':revised,'authored_handler_count':24,'challenge_resolution_context_binding':bind(context),
        'challenge_resolution_method_binding':bind(COMPONENT/'preparation.py'),
        'challenge_resolution_actual_runtime_qualified':False,'current_Agent_qualified':False,'whole_API_qualified':False,
        'runtime_qualification_transferred':False,'task_complete':False,'goal_complete':False})
    print(json.dumps({'result':'FROZEN','source_binding':bind(API/'source-manifest.json'),
        'profile_binding':bind(API/'contract-profile.json'),'retained_methods':323,'unchanged_methods':320,
        'authored_handlers':24,'missing_operations':10,'actual_isolated_cases':15,'runtime_qualified':False}),flush=True)


if __name__=='__main__':main()
