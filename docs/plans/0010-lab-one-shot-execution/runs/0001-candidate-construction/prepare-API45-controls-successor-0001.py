"""Preserve original tests; freeze a separate exact-count control successor."""
import ast
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
API = BASE / 'api-v45'
PARENT = BASE / 'api44-control-checks-v1'
TARGET = BASE / 'api45-control-checks-v1'
SOURCE = '8931c159d933d0144791542d0357bdf8ba532a3b12bd68f35ab3d5a347a0624d'
PROFILE = '81fd3ed4feb462b23888dfe0edc98787cb18e24c2b7342e23dc230c6b2c54b31'

def sha(raw): return hashlib.sha256(raw).hexdigest()
def bind(p): return {'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p.read_bytes())}
def put(p, value):
    with p.open('x') as f: json.dump(value, f, indent=2, sort_keys=True); f.write('\n')
def methods(raw):
    return {n.name: n for n in ast.walk(ast.parse(raw))
            if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}

def main():
    manifest = API / 'source-manifest.json'
    assert sha(manifest.read_bytes()) == SOURCE
    assert sha((API / 'contract-profile.json').read_bytes()) == PROFILE
    rows = {r['path']: r for r in json.loads(manifest.read_bytes())['files']}
    for r in rows.values(): assert sha((ROOT / r['path']).read_bytes()) == r['sha256']
    assert sha((PARENT / 'source-manifest.json').read_bytes()) == '9221f9fff475d4ff7f97187a620b9ee68ecd539233450e1a2055b576ad25b356'
    parent = json.loads((PARENT / 'source-manifest.json').read_bytes())
    for r in parent['files']: assert sha((ROOT / r['path']).read_bytes()) == r['sha256']
    original = (API / 'test_current_controls.py').read_bytes()
    revised = (PARENT / 'test_current_controls.py').read_bytes()
    old = methods(original); new = methods(revised)
    assert set(old) == set(new) and len(old) == 11
    changed = 'test_03_exact_current_profile_and_protocol_controls'
    for key in old:
        if key != changed: assert ast.dump(old[key]) == ast.dump(new[key])
    replaced = 0
    class OnlyCount(ast.NodeTransformer):
        def visit_Call(self, node):
            nonlocal replaced
            self.generic_visit(node)
            if (isinstance(node.func, ast.Attribute) and node.func.attr == 'assertEqual'
                and len(node.args) == 2 and isinstance(node.args[0], ast.Call)
                and isinstance(node.args[0].func, ast.Name) and node.args[0].func.id == 'len'
                and ast.unparse(node.args[0].args[0]) == "declared['implemented_operations']"
                and isinstance(node.args[1], ast.Constant) and node.args[1].value == 15):
                node.args[1].value = 16; replaced += 1
            return node
    expected = OnlyCount().visit(old[changed])
    assert replaced == 1 and ast.dump(expected) == ast.dump(new[changed])
    TARGET.mkdir()
    with (TARGET / 'test_current_controls.py').open('xb') as f: f.write(revised)
    runner = (PARENT / 'checks.py').read_text()
    for previous, successor in [('API44', 'API45'), ('api-v44', 'api-v45'),
                                ('9f56fbe2c874f2f9f5f7965998e033b5a51ebb75b19d5c19c3733b6b02345f0f', SOURCE),
                                ('afb0373d8857ae0ee11b67efd356d2652091aab8e6953fe4ddbc5deee4bd1578', PROFILE)]:
        assert previous in runner; runner = runner.replace(previous, successor)
    with (TARGET / 'checks.py').open('x') as f: f.write(runner)
    disposition = {'schema_version': 'lab-control-count-successor-disposition/v1-candidate',
        'result': 'AUTHORING-CHECKED', 'actual_API_source_binding': bind(manifest),
        'actual_API_profile_binding': bind(API / 'contract-profile.json'),
        'original_test_binding': bind(API / 'test_current_controls.py'),
        'successor_test_binding': bind(TARGET / 'test_current_controls.py'),
        'predecessor_control_proof_binding': bind(PARENT / 'receipts/checks-0001.json'),
        'unchanged_method_ASTs': 10, 'explicit_revised_methods': [changed],
        'exact_revision': 'Only stale supported-handler count15 is corrected to16; all other assertions remain.',
        'original_API45_suite_executed': False, 'successor_suite_executed': False,
        'task_complete': False, 'whole_API_qualified': False, 'authority_effect': 'none', 'actual_owner_outcome': None}
    put(TARGET / 'disposition.json', disposition)
    for p in [manifest, API / 'contract-profile.json', API / 'test_current_controls.py',
              PARENT / 'source-manifest.json', PARENT / 'receipts/checks-0001.json', RUN / 'authorization.json',
              Path(__file__).resolve(), *TARGET.iterdir()]:
        r = bind(p); rows[r['path']] = r
    for r in rows.values(): assert sha((ROOT / r['path']).read_bytes()) == r['sha256']
    put(TARGET / 'source-manifest.json', {'schema_version': 'lab-versioned-control-source/v1-candidate',
        'files': [rows[k] for k in sorted(rows)], 'API_source_binding': bind(manifest),
        'API_profile_binding': bind(API / 'contract-profile.json'), 'expected_cases': 11,
        'actual_owner_outcome': None, 'authority_effect': 'none'})
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(TARGET / 'source-manifest.json'),
                      'full_cases_to_run': 11, 'unchanged_method_ASTs': 10}), flush=True)

if __name__ == '__main__': main()
