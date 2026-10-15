"""Freeze prospective endpoint successor, retaining all78 original method ASTs."""
import ast
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
PARENT = BASE / 'typed-extension-preparation-v6'
TARGET = BASE / 'typed-extension-preparation-v7'

def sha(raw): return hashlib.sha256(raw).hexdigest()
def bind(p): return {'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p.read_bytes())}
def put(p, value):
    with p.open('x') as f: json.dump(value, f, sort_keys=True, indent=2); f.write('\n')
def methods(p):
    return {n.name: ast.dump(n, include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes()))
            if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}

def main():
    raw = (PARENT / 'source-manifest.json').read_bytes()
    assert sha(raw) == '9e8d107b7aa1d2fec78d230521dcfba2b0334235e8d335046c56d67f5be7bc9a'
    proof = PARENT / 'receipts/checks-0001.json'
    assert sha(proof.read_bytes()) == '773fb3d913fe95b2a6d9b0afe2a234e8a40695efe356e4412ded93e9a3271cc6'
    assert json.loads(proof.read_bytes())['result'] == 'PASS'
    parent = json.loads(raw); rows = {r['path']: r for r in parent['files']}
    for p in PARENT.glob('test_*.py'): assert methods(p) == methods(TARGET / p.name)
    assert len(methods(TARGET / 'test_prospective.py')) == 20
    for name in ['adapter.py', 'source_selection.py', 'kernel-inputs.json']:
        assert (PARENT / name).read_bytes() == (TARGET / name).read_bytes()
    context = RUN / 'context-R03-typed-extension-prospective-v7.json'
    put(context, {'schema_version': 'lab-bounded-context/v1-candidate',
        'task': 'R03 exact prospective carrier targets with complete original postimage',
        'strict_coverage': 'PASS', 'blockers': [],
        'source_bindings': [bind(RUN / 'authorization.json'), bind(PARENT / 'source-manifest.json'), bind(proof)],
        'write_scope': TARGET.relative_to(ROOT).as_posix(),
        'decisions': [{'selection': 'Same exact type-target body, separate contract and schema bindings; unchanged original engine for complete preparation.', 'mode': 'existing-authorized-implementation'}],
        'validation_surface': 'All78 predecessor cases plus20 prospective admit/revise and refusal cases.',
        'constraints': ['Original78 method ASTs and original callbacks remain unchanged.',
            'Prospective endpoints remain candidate-for-R08; simulated backend states grant no admission.',
            'Independent current projection/configuration/HEAD, every stable core and complete original engine closure remain required.',
            'No new public operation, Actor authority, signature, store, global pair or relation instance.',
            'No canonical mutation, private/live key use, activation, publication or new owner decision.'],
        'remaining_obligations': ['Authenticated actual current host/source/Actor and permission integration.',
            'Durable public handler journal and full original operation cases.',
            'Governed internal and specialized authority resolvers.',
            'All original qualifications and genuine R05/R06/R07/S02/R08.'],
        'actual_owner_outcome': None, 'authority_effect': 'none', 'task_complete': False})
    for p in [PARENT / 'source-manifest.json', proof, context, RUN / 'authorization.json',
              RUN / 'check-typed-prospective-authoring-0001.py',
              RUN / 'typed-prospective-authoring-0001.log', RUN / 'typed-prospective-authoring-0002.log',
              RUN / 'typed-prospective-authoring-terminal-0001.json',
              RUN / 'typed-prospective-authoring-terminal-0002.json', Path(__file__).resolve()]:
        r = bind(p); rows[r['path']] = r
    for p in TARGET.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts and 'receipts' not in p.parts:
            r = bind(p); rows[r['path']] = r
    for r in rows.values(): assert sha((ROOT / r['path']).read_bytes()) == r['sha256']
    value = {**parent, 'files': [rows[k] for k in sorted(rows)], 'expected_cases': 98,
             'parent_source_binding': bind(PARENT / 'source-manifest.json'), 'context_binding': bind(context),
             'retained_predecessor_case_count': 78, 'new_prospective_endpoint_case_count': 20,
             'pure_postimage_only': True, 'public_handler_qualified': False,
             'actual_owner_outcome': None, 'authority_effect': 'none'}
    put(TARGET / 'source-manifest.json', value)
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(TARGET / 'source-manifest.json'),
                      'source_files': len(rows), 'expected_cases': 98}), flush=True)

if __name__ == '__main__': main()
