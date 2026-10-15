"""Freeze actual complete failures, owner core proof and explicit metadata adapter."""
import ast,hashlib,importlib.metadata,json,platform
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5];RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
def bind(p):return {'path':p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def put(p,v):p.open('x').write(json.dumps(v,indent=2,sort_keys=True)+'\n')
def methods(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    old=HERE.parent/'api-v21';context=RUN/'context-R03-metadata-scope-api-0002.json';ctx=json.loads(context.read_bytes());assert ctx['strict_coverage']=='PASS' and not ctx['blockers'];previous=json.loads((old/'contract-profile.json').read_bytes());profile={**previous,'files':[]}
    for row in previous['files']:
        path=ROOT/row['path'];profile['files'].append(bind(HERE/path.relative_to(old) if path.is_relative_to(old) else path))
    profile['files'] += [bind(HERE/n) for n in ['scope_preparation.py','scope-preparation-profile.json'] if bind(HERE/n)['path'] not in {r['path'] for r in profile['files']}];assert len({r['path'] for r in profile['files']})==len(profile['files']);profile['claim_ceiling']='Twelve existing handlers; explicit eight-operation metadata grants and closed42target/21domain candidate preparation. No current Agent participation or owner admission from metadata; full84verification/independentaudit pending.';put(HERE/'contract-profile.json',profile)
    rows={}
    def add(r):assert rows.get(r['path'],r)==r,r['path'];rows[r['path']]=r
    for p in [RUN/'custody-api-failed-proof-0003.json',HERE.parent/'owner-core-preparation-v1/receipts/proof-0001.json',old/'source-manifest.json']:
        for r in json.loads(p.read_bytes())['files']:add(r)
        add(bind(p))
    for r in ctx['source_bindings']:add(r)
    add(bind(context))
    for path in HERE.rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts:add(bind(path))
    for n in ['test_preparation.py','test_preparation_corrected.py','run_session_checks.py','test_custody_sessions.py','test_custody_api.py','test_guarded_reads.py']:assert methods(HERE/n)==methods(old/n),n
    for path in HERE.glob('*.py'):ast.parse(path.read_bytes())
    for r in rows.values():assert bind(ROOT/r['path'])==r,r['path']
    env={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')};assert env=={'python':'3.14.4','jsonschema':'4.23.0','cryptography':'46.0.5'}
    source={'schema_version':'lab-exact-metadata-scope-source/v1-candidate','files':sorted(rows.values(),key=lambda r:r['path']),'environment':env,'frozen_before_owned_effects':True,'original146methodASTs_retained':True,'new_metadata_scope_tests':20,'current_suite_cases':84,'original_Assignment_renewed':False,'authority_effect':'none','actual_owner_outcome':None,'task_complete':False};put(HERE/'source-manifest.json',source);print(json.dumps({'result':'FROZEN','files':len(rows),'source_binding':bind(HERE/'source-manifest.json'),'profile_binding':bind(HERE/'contract-profile.json')}))
if __name__=='__main__':main()
