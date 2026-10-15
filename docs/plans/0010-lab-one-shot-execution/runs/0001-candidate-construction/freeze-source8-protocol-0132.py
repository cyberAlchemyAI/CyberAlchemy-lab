"""Freeze negotiated protocol v4 and exact source/catalog eligibility before tests."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';OLD=BASE/'api-v91';API=BASE/'api-v92';PACKAGE=BASE/'source8-protocol-v1'
def bind(path):return {'path':path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def load(path):return json.loads(path.read_bytes())
def emit(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
def methods(path):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(path.read_text())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    assert not (API/'source-manifest.json').exists()
    spec=importlib.util.spec_from_file_location('_cal_API92_parent_guard',OLD/'guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    parent=guard.verify('b007a3251489936135b1dcdbb3c46657706bbb651678d11fcaf2280fb09fc92e')
    local=[];retained=[]
    for folder in (API,PACKAGE,BASE/'lesson-host-composition-v42'):
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
    for name in ('machine_transport.py','machine_context_scope.py','custody_context_sessions.py','candidate.py'):
        assert (API/name).read_bytes()==(OLD/name).read_bytes(),name
    context=RUN/'context-R03-versioned-source8-protocol-0132.json'
    evidence=[RUN/'authorization.json',RUN/'typed-relation-v4-public-header-gap-0131.json',RUN/'API91-integrated-resolution-0002.json',
        RUN/'build-source8-protocol-0132.py',Path(__file__).resolve(),OLD/'source-manifest.json']
    emit(context,{'schema_version':'lab-bounded-context/v1-candidate','task':'R03 versioned current-source protocol closure',
        'source_bindings':[bind(p) for p in evidence],
        'constraints':['Existing construction/isolated validation authorization; final R08 owner admission remains.',
            'Original protocol IDs and resources retain their original bytes/eligibility.97new resources have unique independent IDs.',
            'Exactly one additional carrier:v4.TypedRelation; exact domain schema and signed local catalog declaration.',
            'Negotiated operator profile v4; wire v2 retained with required independent exact profile hash.',
            'All323inherited method ASTs unchanged; no API91 runtime qualification transfer.'],
        'authority_effect':'none','actual_owner_outcome':None})
    profile=load(OLD/'contract-profile.json');rows={r['path']:r for r in profile['files']}
    for row in [*local,*[bind(p) for p in [*evidence,context]]]:
        assert rows.get(row['path'],row)==row,row['path'];rows[row['path']]=row
    for row in rows.values():assert bind(ROOT/row['path'])==row,row['path']
    profile.update(schema_version='lab-operator-contract-profile/v4-candidate',files=[rows[k] for k in sorted(rows)],
        protocol_resource_selection_binding=bind(PACKAGE/'selection.json'),protocol_context_binding=bind(context),
        claim_ceiling='24authored handlers and negotiated exact Source8 candidate carrier/catalog resource eligibility; affected current/inherited API qualification required.')
    emit(API/'contract-profile.json',profile)
    full={r['path']:r for r in parent['files']}
    for row in [*rows.values(),bind(API/'contract-profile.json'),bind(OLD/'source-manifest.json')]:
        assert full.get(row['path'],row)==row,row['path'];full[row['path']]=row
    for row in full.values():assert bind(ROOT/row['path'])==row,row['path']
    emit(API/'source-manifest.json',{**parent,'files':[full[k] for k in sorted(full)],
        'parent_source_binding':bind(OLD/'source-manifest.json'),'retained_inherited_methods':retained,
        'unchanged_inherited_method_count':323,'explicit_revised_methods':0,'binding_only_revised_methods':[],
        'protocol_context_binding':bind(context),'negotiated_protocol_profile_version':4,
        'current_protocol_query_inspection_qualified':False,'integrated_public_resolution_qualified':False,
        'whole_API_qualified':False,'runtime_qualification_transferred':False,'task_complete':False,'goal_complete':False})
    print(json.dumps({'result':'FROZEN','source_binding':bind(API/'source-manifest.json'),
        'profile_binding':bind(API/'contract-profile.json'),'retained_methods':len(retained),'protocol_resources':97}))
if __name__=='__main__':main()
