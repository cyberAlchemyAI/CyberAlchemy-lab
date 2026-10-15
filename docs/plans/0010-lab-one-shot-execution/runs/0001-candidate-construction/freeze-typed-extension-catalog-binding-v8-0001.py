"""Freeze complete catalog binding, retaining all98 predecessor method ASTs."""
import ast
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
PARENT = BASE / 'typed-extension-preparation-v7'
TARGET = BASE / 'typed-extension-preparation-v8'

def sha(raw): return hashlib.sha256(raw).hexdigest()
def bind(p): return {'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p.read_bytes())}
def put(p, value):
    with p.open('x') as f: json.dump(value, f, sort_keys=True, indent=2); f.write('\n')
def methods(p):
    return {n.name: ast.dump(n, include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes()))
            if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}

def main():
    raw = (PARENT / 'source-manifest.json').read_bytes()
    assert sha(raw) == '8ea42cdbf6cc457d29f4b825386ade66afba17509db530c8744f7bbd45d2fb0d'
    proof = PARENT / 'receipts/proof-0001.json'
    assert sha(proof.read_bytes()) == 'bbc49e9b52d19d2651439c67362b0fb959da121b7635ba0ac1e4ecc45b3a64a1'
    assert json.loads(proof.read_bytes())['result'] == 'PASS'
    parent = json.loads(raw); rows = {r['path']: r for r in parent['files']}
    for p in PARENT.glob('test_*.py'): assert methods(p) == methods(TARGET / p.name)
    assert len(methods(TARGET / 'test_catalog_binding.py')) == 16
    for name in ['adapter.py', 'source_selection.py', 'prospective.py', 'kernel-inputs.json']:
        assert (PARENT / name).read_bytes() == (TARGET / name).read_bytes()
    context = RUN / 'context-R03-typed-extension-catalog-binding-v8.json'
    put(context, {'schema_version': 'lab-bounded-context/v1-candidate',
        'task': 'R03 full independent catalog binding to exact runtime baseline and postimage',
        'strict_coverage': 'PASS', 'blockers': [],
        'source_bindings': [bind(RUN / 'authorization.json'), bind(PARENT / 'source-manifest.json'), bind(proof)],
        'write_scope': TARGET.relative_to(ROOT).as_posix(),
        'decisions': [{'selection': 'Complete catalog byte/predecessor closure bridges distinct independently selected envelopes; original executables and source guards remain separate.', 'mode': 'existing-authorized-implementation'}],
        'validation_surface': 'All98 predecessor cases plus16 complete catalog-binding and refusal cases.',
        'constraints': ['Original98 method ASTs and original callbacks remain unchanged.',
            'Catalog closure includes original complete schema bytes and Definition predecessors; source envelopes and executable closures stay distinct.',
            'Independent current projection/configuration/HEAD, every stable core and complete original engine closure remain required.',
            'No new public operation, Actor authority, signature, store, global pair or relation instance.',
            'No canonical mutation, private/live key use, activation, publication or new owner decision.'],
        'remaining_obligations': ['Authenticated actual current host/source/Actor and permission integration.',
            'Durable public handler journal and full original operation cases.',
            'Governed internal and specialized authority resolvers.',
            'All original qualifications and genuine R05/R06/R07/S02/R08.'],
        'actual_owner_outcome': None, 'authority_effect': 'none', 'task_complete': False})
    for p in [PARENT / 'source-manifest.json', proof, PARENT / 'receipts/checks-0001.json', context, RUN / 'authorization.json',
              RUN / 'check-typed-catalog-binding-authoring-0001.py',
              RUN / 'typed-catalog-binding-authoring-0001.log', RUN / 'typed-actual-source-comparison-0002.json', RUN / 'typed-actual-source-comparison-0002.log', RUN / 'inspect-typed-actual-source-0002.py', RUN / 'typed-actual-source-comparison-terminal-0002.json',
              RUN / 'typed-catalog-binding-authoring-terminal-0001.json', Path(__file__).resolve()]:
        r = bind(p); rows[r['path']] = r
    for p in TARGET.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts and 'receipts' not in p.parts:
            r = bind(p); rows[r['path']] = r
    for r in rows.values(): assert sha((ROOT / r['path']).read_bytes()) == r['sha256']
    value = {**parent, 'files': [rows[k] for k in sorted(rows)], 'expected_cases': 114,
             'parent_source_binding': bind(PARENT / 'source-manifest.json'), 'context_binding': bind(context),
             'retained_predecessor_case_count': 98, 'new_current_catalog_binding_case_count': 16,
             'pure_postimage_only': True, 'public_handler_qualified': False,
             'actual_owner_outcome': None, 'authority_effect': 'none'}
    put(TARGET / 'source-manifest.json', value)
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(TARGET / 'source-manifest.json'),
                      'source_files': len(rows), 'expected_cases': 114}), flush=True)

if __name__ == '__main__': main()
