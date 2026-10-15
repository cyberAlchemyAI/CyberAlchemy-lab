"""Freeze the exact current governance schema successor without changing tests."""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
PARENT = BASE / 'api-v41'
API = BASE / 'api-v42'
RULES = BASE / 'failure-assessment-rules-v9'


def bind(path):
    return {'path': str(path.relative_to(ROOT)),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def methods(path):
    return {node.name: ast.dump(node, include_attributes=False)
            for node in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')}


def main():
    spec = importlib.util.spec_from_file_location('_cal_API42_parent_guard', PARENT / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    parent = guard.verify('d3fed5312abf115041e35ed22d6bc062386668cdebd5416a782d6703d372e7ab')
    proof_path = RULES / 'receipts/proof-0001.json'
    proof = json.loads(proof_path.read_bytes())
    assert proof['result'] == 'PASS' and proof['actual_cases'] == 75
    assert proof['actual_terminal_exit_code'] == 0
    for row in proof['files']:
        assert bind(ROOT / row['path']) == row
    for name in ['source_binding', 'report_binding', 'terminal_binding']:
        row = proof[name]
        assert bind(ROOT / row['path']) == row
    retained, changed = [], []
    for path in PARENT.rglob('*'):
        if not path.is_file() or 'receipts' in path.parts or '__pycache__' in path.parts:
            continue
        if path.name in ('source-manifest.json', 'contract-profile.json'):
            continue
        successor = API / path.relative_to(PARENT)
        if path.read_bytes() != successor.read_bytes():
            changed.append(str(path.relative_to(PARENT)))
        if path.suffix == '.py':
            assert methods(path) == methods(successor)
            retained.extend(str(path.relative_to(PARENT)) + ':' + name for name in methods(path))
    assert changed == ['failure_preparation.py'] and len(retained) == 293
    assert (BASE / 'failure-assessment-rules-v8/engine.py').read_bytes() == (RULES / 'engine.py').read_bytes()
    # The adapter changes only independent rule selection and its required proof count.
    old_adapter = BASE / 'failure-preparation-v2/preparation.py'
    new_adapter = BASE / 'failure-preparation-v3/preparation.py'
    expected = old_adapter.read_text().replace("'failure-assessment-rules-v8'", "'failure-assessment-rules-v9'")
    expected = expected.replace('9daa2e2db409332eea242ab0e07d16ab92fdccbc02c9f2317c7768e842bb4554', proof['source_binding']['sha256'])
    expected = expected.replace('b0978c48119cdf7967158cae09a40cb37a9cde33a5620f63c2e50c7fa27f3cd1', bind(proof_path)['sha256'])
    expected = expected.replace("document['actual_cases']==63", "document['actual_cases']==75")
    expected = expected.replace('_cal_public_failure_preparation_rules_v8', '_cal_public_failure_preparation_rules_v9')
    assert new_adapter.read_text() == expected
    context = RUN / 'context-R03-failure-API-0042.json'
    static_path = RUN / 'API42-exact-governance-schema-authoring-0001.json'
    selected = [PARENT / 'source-manifest.json', RULES / 'source-manifest.json', proof_path,
                RUN / 'API41-failure-exception-diagnostic-0001.json', RUN / 'authorization.json',
                Path(__file__).resolve(), old_adapter, new_adapter]
    put(static_path, {'schema_version': 'lab-exact-schema-successor-static-checks/v1-candidate',
                     'result': 'PASS', 'unchanged_original_test_methods': 293,
                     'unchanged_primitive_method_ASTs': 63, 'new_primitive_cases': 12,
                     'original_API_schema_bytes_unchanged': True, 'engine_bytes_unchanged': True,
                     'files': [bind(p) for p in selected], 'authority_effect': 'none',
                     'whole_API_qualified': False, 'task_complete': False})
    put(context, {'schema_version': 'lab-bounded-context/v1-candidate',
                  'task': 'R03 exact current governance carrier schema successor',
                  'strict_coverage': 'PASS', 'blockers': [],
                  'source_bindings': [bind(p) for p in selected + [static_path]],
                  'change': 'Add six exact admitted v2 schemas to the independently selected failure evaluator table.',
                  'constraints': ['All293 public test methods and original34 API contracts unchanged.',
                                  'Preserve source guards, signed policy, real clocks and original ceilings.',
                                  'Complete current public suites and all original operation qualifications remain required.'],
                  'actual_owner_outcome': None, 'authority_effect': 'none'})
    profile = json.loads((PARENT / 'contract-profile.json').read_bytes())
    profile['files'] = [bind(API / (ROOT / row['path']).relative_to(PARENT))
                        if (ROOT / row['path']).is_relative_to(PARENT) else row
                        for row in profile['files']]
    old = BASE / 'failure-preparation-v2'
    new = BASE / 'failure-preparation-v3'
    profile['files'] = [bind(new / (ROOT / row['path']).relative_to(old))
                        if (ROOT / row['path']).is_relative_to(old) else row
                        for row in profile['files']]
    profile['failure_rule_source_binding'] = proof['source_binding']
    profile['failure_rule_proof_binding'] = bind(proof_path)
    profile['carrier_classification_context_binding'] = bind(context)
    profile['claim_ceiling'] = 'Sixteen authored handlers; exact current failure schema successor. Current public qualifications remain incomplete.'
    put(API / 'contract-profile.json', profile)
    rows = {row['path']: row for row in parent['files']}
    for row in proof['files']:
        rows[row['path']] = row
    for path in selected + [context, static_path, RULES / 'receipts/checks-0001.json', ROOT / proof['terminal_binding']['path']]:
        row = bind(path); rows[row['path']] = row
    for directory in [API, new]:
        for path in directory.rglob('*'):
            if path.is_file() and 'receipts' not in path.parts and '__pycache__' not in path.parts:
                row = bind(path); rows[row['path']] = row
    manifest = copy.deepcopy(parent)
    manifest.update(files=[rows[key] for key in sorted(rows)],
                    parent_source_binding=bind(PARENT / 'source-manifest.json'),
                    context_binding=bind(context), static_checks_binding=bind(static_path),
                    retained_inherited_methods=retained, unchanged_inherited_method_count=293,
                    explicit_revised_methods=[], failure_rule_source_binding=proof['source_binding'],
                    failure_rule_proof_binding=bind(proof_path), whole_API_qualified=False,
                    current_Agent_qualified=False, task_complete=False, goal_complete=False)
    put(API / 'source-manifest.json', manifest)
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(API / 'source-manifest.json'),
                      'profile_binding': bind(API / 'contract-profile.json'),
                      'source_files': len(rows), 'unchanged_methods': len(retained)}), flush=True)


if __name__ == '__main__':
    main()
