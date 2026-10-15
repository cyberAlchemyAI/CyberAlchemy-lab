"""Author profile and freeze complete API/source closure before owned effects."""
import ast,hashlib,importlib.metadata,json,platform
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes())}
def put(p,v):p.open('x').write(json.dumps(v,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
def methods(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    assert not (HERE/'source-manifest.json').exists();parent=HERE.parent/'api-v16'
    original_profile=json.loads((parent/'contract-profile.json').read_bytes());profile={**original_profile,'files':[]}
    for row in original_profile['files']:
        p=ROOT/row['path'];p=HERE/p.relative_to(parent) if p.is_relative_to(parent) else p;profile['files'].append(bind(p))
    for p in [HERE/'custody_context_sessions.py',HERE/'guard.py']:profile['files'].append(bind(p))
    assert len(profile['implemented_operations'])==12
    profile['claim_ceiling']='Twelve existing candidate handlers with explicit original-byte source, complete disposable SQL projection and ephemeral Session integration. Remaining22public APIs and final operational acceptance are separate obligations.'
    put(HERE/'contract-profile.json',profile)
    rows={}
    def add(b):assert rows.get(b['path'],b)==b,b['path'];rows[b['path']]=b
    for root in [parent,HERE.parent/'custody-context-delivery-v1']:
        manifest=json.loads((root/'source-manifest.json').read_bytes());add(bind(root/'source-manifest.json'))
        for row in manifest['files']:add(row)
    for p in (HERE.parent/'custody-context-delivery-v1/packages/0001').rglob('*'):
        if p.is_file():add(bind(p))
    for p in [RUN/'context-R03-custody-api-0001.json',RUN/'CONTEXT-R03-custody-api-0001.md',RUN/'derive-R03-custody-api-0001.py']:add(bind(p))
    deltas={}
    for name in ['test_preparation.py','test_preparation_corrected.py','run_session_checks.py']:
        old=methods(parent/name);new=methods(HERE/name);assert set(old)==set(new),name
        changed=[n for n in old if old[n]!=new[n]]
        assert changed==(['test_30_current_handler_profile_retains_all_original_contracts'] if name=='run_session_checks.py' else []),(name,changed)
        deltas[name]={'methods':len(old),'changed_method_ASTs':changed,'reason':'Existing profile supports12operations; successor count assertion corrected from11to12 without narrowing any handler or contract.' if changed else 'All original test method ASTs unchanged.'}
    for p in HERE.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:
            if p.suffix=='.py':ast.parse(p.read_bytes())
            add(bind(p))
    for row in rows.values():assert sha((ROOT/row['path']).read_bytes())==row['sha256']
    env={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')}
    assert env=={'python':'3.14.4','jsonschema':'4.23.0','cryptography':'46.0.5'}
    m={'schema_version':'lab-original-source-API-source/v1-candidate','files':sorted(rows.values(),key=lambda r:r['path']),'environment':env,'parent_source_binding':bind(parent/'source-manifest.json'),'context_producer_binding':bind(HERE.parent/'custody-context-delivery-v1/source-manifest.json'),'profile_binding':bind(HERE/'contract-profile.json'),'original_test_method_derivation':deltas,'original_operations':34,'implemented_operations':12,'remaining_operations':22,'frozen_before_owned_API_effects':True,'authority_effect':'none','actual_owner_outcome':None,'task_complete':False}
    put(HERE/'source-manifest.json',m);print(json.dumps({'result':'FROZEN','files':len(rows),'source_binding':bind(HERE/'source-manifest.json'),'profile_binding':bind(HERE/'contract-profile.json'),'original_methods':deltas}),flush=True)
if __name__=='__main__':main()
