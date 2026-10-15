"""Verify every independently declared source/mapper/Context selection in the API."""
import ast
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
API = BASE / 'api-v79'
CONTEXT = BASE / 'current-context-delivery-v9'
MAPPED = BASE / 'current-mapped-context-v4'
SOURCE = BASE / 'current-participation-v5'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def load(path):
    return json.loads(path.read_bytes())


def literal(path, name):
    for node in ast.walk(ast.parse(path.read_bytes())):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError((path, name))


def main():
    checks = []
    files = []
    def match(path, name, target):
        selected = literal(path, name)
        exact = bind(target)
        assert selected == exact['sha256'], (path, name, selected, exact)
        checks.append({'source_binding': bind(path), 'selector': name, 'selected_binding': exact})
        files.extend([path, target])
    match(API / 'custody_context_sessions.py', 'DELIVERY_PIN', CONTEXT / 'source-manifest.json')
    match(API / 'custody_context_sessions.py', 'MAPPING_PIN', MAPPED / 'packages/0001/manifest.json')
    match(CONTEXT / 'base.py', 'MAPPED_PIN', MAPPED / 'source-manifest.json')
    match(CONTEXT / 'base.py', 'MAPPED_PACKAGE_PIN', MAPPED / 'packages/0001/manifest.json')
    match(CONTEXT / 'generation.py', 'MAPPED_SOURCE_SHA', MAPPED / 'source-manifest.json')
    match(CONTEXT / 'build.py', 'SOURCE_PIN', SOURCE / 'source-manifest.json')
    match(CONTEXT / 'build.py', 'SOURCE_PACKAGE', SOURCE / 'packages/0001/manifest.json')
    profile_path = API / 'contract-profile.json'
    profile = load(profile_path)
    proof_path = CONTEXT / 'receipts/qualification-0001.json'
    proof = load(proof_path)
    assert proof['result'] == 'PASS' and proof['selected_methods'] == 50
    assert profile['qualified_context_proof_binding'] == bind(proof_path)
    assert profile['selected_current_context_source_binding'] == proof['source_binding'] == bind(CONTEXT / 'source-manifest.json')
    assert profile['selected_current_context_package_binding'] == proof['package_binding'] == bind(CONTEXT / 'packages/0001/manifest.json')
    assert profile['current_mapping_package_binding'] == bind(MAPPED / 'packages/0001/manifest.json')
    repository = profile['files']
    assert all(not Path(row['path']).is_absolute() for row in repository)
    external = profile['external_execution_dependency_bindings']
    assert external == load(CONTEXT / 'EXECUTION-DEPENDENCIES.json')['external_dependency_bindings']
    selected = load(API / 'source-manifest.json')
    assert all(row in selected['files'] for row in external)
    rows = {row['path']: row for row in selected['files']}
    for row in external:
        assert hashlib.sha256(Path(row['path']).read_bytes()).hexdigest() == row['sha256']
    files.extend([profile_path, proof_path, API / 'source-manifest.json', CONTEXT / 'EXECUTION-DEPENDENCIES.json', Path(__file__).resolve()])
    bindings = {bind(path)['path']: bind(path) for path in files}
    for path in files:
        if path != Path(__file__).resolve():
            assert rows.get(bind(path)['path'], bind(path)) == bind(path)
    out = RUN / 'API79-component-binding-checks-0001.json'
    value = {'schema_version': 'lab-current-component-binding-checks/v1-candidate',
             'result': 'PASS', 'files': [bindings[key] for key in sorted(bindings)],
             'actual_literal_binding_joins': checks, 'qualified_Context_binding': bind(proof_path),
             'repository_and_external_guards_preserved': True,
             'scope': 'Exact declared component identities only; actual original API/Machine/lifecycle qualification remains required.',
             'current_Machine_qualified': False, 'whole_API_qualified': False,
             'authority_effect': 'none', 'actual_owner_outcome': None, 'task_complete': False}
    with out.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': 'PASS', 'actual_literal_joins': len(checks), 'report_binding': bind(out)}), flush=True)


if __name__ == '__main__':
    main()
