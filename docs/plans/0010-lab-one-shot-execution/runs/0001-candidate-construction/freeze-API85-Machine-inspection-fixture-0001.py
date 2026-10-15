"""Freeze exact private Machine/owner policy composition and original evidence."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
OLD,API=BASE/'api-v84',BASE/'api-v85'
COMPONENT=BASE/'machine-context-scope-v1'


def bind(path):return {'path':path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def load(path):return json.loads(path.read_bytes())


def emit(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')


def methods(path):
    return {node.name:ast.dump(node,include_attributes=False) for node in ast.walk(ast.parse(path.read_text()))
            if isinstance(node,ast.FunctionDef) and node.name.startswith('test_')}


def main():
    spec=importlib.util.spec_from_file_location('_cal_API84_parent_guard',OLD/'guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    parent=guard.verify('4e18e4f15f154312939a442822d487df7e7b2f6ab492d0d98239cfe6160f1690')
    diagnosis=RUN/'API83-original-Machine-generation-diagnosis-0001.json'
    checked=load(diagnosis)
    assert checked['result']=='PASS' and checked['actual_cases']==1
    assert checked['observed']['peer_closed'] and not checked['observed']['resource_closed']
    assert not checked['observed']['actual_Session_expired']
    retained,local=[],[]
    for folder in [API,COMPONENT,BASE/'lesson-host-composition-v35']:
        for path in sorted(folder.rglob('*')):
            if not path.is_file() or {'receipts','__pycache__'}&set(path.parts):continue
            if path.name in ('source-manifest.json','contract-profile.json'):continue
            if path.suffix=='.py':
                ast.parse(path.read_text())
                old_path=OLD/path.relative_to(API) if folder==API else None
                if old_path is not None and old_path.exists():
                    expected=old_path.read_text()
                    if old_path.name=='test_machine_transport.py':expected=expected.replace("        request=self.inspection(context['session_ref'])","        request=self.inspection(context['session_ref'])\n        request['caller_context_ref']=context['context_ref']",1)
                    expected_methods={node.name:ast.dump(node,include_attributes=False) for node in ast.walk(ast.parse(expected)) if isinstance(node,ast.FunctionDef) and node.name.startswith('test_')}
                    assert expected_methods==methods(path),path
                    retained.extend(path.relative_to(API).as_posix()+':'+name for name in methods(path))
            local.append(bind(path))
    assert len(retained)==323
    for name in ('machine_transport.py','auth.py','guarded_reads.py','guarded_candidate.py','workspace.py'):
        assert (OLD/name).read_bytes()==(API/name).read_bytes(),name
    context=RUN/'context-R03-Machine-inspection-fixture-0085.json'
    source_paths=[OLD/'source-manifest.json',diagnosis,
                  RUN/'API84-Machine-seven-read-observation-0002.json',
                  API/'test_machine_transport.py',
                  RUN/'API83-Machine-seven-read-observation-0001.json',
                  RUN/'diagnose-API83-original-Machine-generation-0001.py',
                  BASE/'fact-read-scope-v1/scope.py',BASE/'current-context-delivery-v9/generation.py',
                  BASE/'current-context-delivery-v9/source-manifest.json',COMPONENT/'DESIGN.md',
                  RUN/'authorization.json',RUN/'author-API85-Machine-inspection-fixture-0001.py',Path(__file__).resolve()]
    emit(context,{'schema_version':'lab-bounded-context/v1-candidate','task':'R03 exact Machine inspection fixture connection binding',
                  'source_bindings':[bind(path) for path in source_paths],
                  'constraints':['Actual original generator refuses its actual parent policy channel while the scope registers the Machine channel; no Session expiry occurred.',
                                 'Compose exact actual owner policy custody and retain original Machine Actor, source, permission, clock, scope-copy and generator functions.',
                                 'Permit no sibling owner/source, lost resource, new roles/operations or extended lifetime; dispatch/writes stay outside facts.',
                                 'All323 test methods retained:322ASTs unchanged; one fixture adds the actual Machine opaque caller context reference. Original assertions/production transport/auth/guards remain.',
                                 'Ordinary operator Context generation stays on original path. New affected Machine and full API qualification remain pending.',
                                 'All34 public operations and46 plan tasks remain in scope;23authored/11missing unchanged.'],
                  'runtime_qualified':False,'actual_owner_outcome':None,'authority_effect':'none'})
    profile=load(OLD/'contract-profile.json');assert len(profile['implemented_operations'])==23
    rows={row['path']:row for row in profile['files']}
    for row in list(rows.values()):
        path=ROOT/row['path']
        if path.is_relative_to(OLD):rows[bind(API/path.relative_to(OLD))['path']]=bind(API/path.relative_to(OLD))
    for row in local+[bind(path) for path in [*source_paths,context]]:
        assert rows.get(row['path'],row)==row,row['path'];rows[row['path']]=row
    for row in rows.values():assert not Path(row['path']).is_absolute() and bind(ROOT/row['path'])==row,row['path']
    profile.update(files=[rows[key] for key in sorted(rows)],Machine_context_scope_context_binding=bind(context),
                   Machine_context_scope_method_binding=bind(COMPONENT/'generation.py'),
                   claim_ceiling='23authored handlers; exact Machine/owner source-fact custody repair. Actual affected Machine and fullAPI qualification remain pending.')
    emit(API/'contract-profile.json',profile)
    full={row['path']:row for row in parent['files']}
    for row in [*rows.values(),bind(API/'contract-profile.json'),bind(OLD/'source-manifest.json')]:
        assert full.get(row['path'],row)==row,row['path'];full[row['path']]=row
    for row in full.values():assert bind(ROOT/row['path'])==row,row['path']
    value={**parent,'files':[full[key] for key in sorted(full)],'parent_source_binding':bind(OLD/'source-manifest.json'),
           'retained_inherited_methods':retained,'unchanged_inherited_method_count':322,
           'explicit_revised_methods':1,'binding_only_revised_methods':['test_machine_transport.py:test_02_all_seven_public_read_operations_with_actual_Actor'],
           'Machine_context_scope_context_binding':bind(context),'Machine_context_scope_method_binding':bind(COMPONENT/'generation.py'),
           'authored_handler_count':23,'current_Agent_qualified':False,'whole_API_qualified':False,
           'runtime_qualification_transferred':False,'task_complete':False,'goal_complete':False}
    emit(API/'source-manifest.json',value)
    print(json.dumps({'result':'FROZEN','source_binding':bind(API/'source-manifest.json'),
                      'profile_binding':bind(API/'contract-profile.json'),'retained_methods':323,'unchanged_methods':322,'explicit_fixture_binding_revisions':1,
                      'authored_handlers':23,'remaining_handlers':11,'runtime_qualified':False}),flush=True)


if __name__=='__main__':main()
