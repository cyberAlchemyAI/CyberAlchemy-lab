"""Freeze exact qualification inputs before any new controlled host effects."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
RUN = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'

def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')

def methods(path):
    return {n.name: ast.dump(n, include_attributes=False)
            for n in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}

def main():
    assert not (HERE / 'source-manifest.json').exists()
    parent = HERE.parent / 'fact-read-scope-v1/receipts/proof-0001.json'
    failed = RUN / 'current-Agent-development-observation-failed-proof-0005.json'
    current = HERE.parent / 'api-v33/source-manifest.json'
    rows = {}
    for path in [parent, failed, current]:
        value = json.loads(path.read_bytes())
        if path == parent:
            assert value['result'] == 'PASS'
        if path == failed:
            assert value['result'] == 'FAIL' and value['actual_terminal_exit_code'] == 1
        for row in value['files']:
            assert rows.get(row['path'], row) == row
            assert bind(ROOT / row['path']) == row, row['path']
            rows[row['path']] = row
        rows[bind(path)['path']] = bind(path)
    original = methods(HERE.parent / 'fact-read-scope-v1/checks.py')
    assert original == methods(HERE / 'checks.py') and len(original) == 18
    assert len(methods(HERE / 'current_checks.py')) == 4
    context = RUN / 'context-R03-fact-policy-boundaries-0002.json'
    put(context, {'schema_version': 'lab-bounded-context/v1-candidate',
                  'task': 'R03 compose full source guards and actual current policy checks',
                  'strict_coverage': 'PASS', 'blockers': [],
                  'source_bindings': [bind(p) for p in [parent, failed, current,
                                      RUN / 'authorization.json', HERE / 'DESIGN.md']],
                  'constraints': ['Reuse the original copy implementation and registry; replace no callbacks.',
                                  'Full source/package entry and exit checks; actual uncached policy checks.',
                                  'Explicit private coupling; no public scope activation or durable dispatch.',
                                  'All18original tests unchanged plus4actual API33 policy/dispatch cases.',
                                  'No period renewal, deadline extension, permission cache or Agent resurrection.',
                                  'Helper qualification alone cannot complete current Agent or R03.'],
                  'authority_effect': 'none', 'actual_owner_outcome': None})
    for p in [context, RUN / 'authorization.json']:
        rows[bind(p)['path']] = bind(p)
    for p in HERE.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:
            if p.suffix == '.py':
                ast.parse(p.read_bytes())
            rows[bind(p)['path']] = bind(p)
    for row in rows.values():
        assert bind(ROOT / row['path']) == row, row['path']
    output = HERE / 'source-manifest.json'
    put(output, {'schema_version': 'lab-source-policy-boundary-source/v1-candidate',
                 'files': [rows[k] for k in sorted(rows)], 'context_binding': bind(context),
                 'qualified_original_helper_binding': bind(parent),
                 'current_API_source_binding': bind(current), 'failed_lifecycle_binding': bind(failed),
                 'original18check_methods_preserved': True, 'actual_current_policy_cases': 4,
                 'expected_tests': 22, 'original_copy_registry_coupling_explicit': True,
                 'frozen_before_new_owned_host_nonce_or_workspace_effects': True,
                 'permissions_cached': False, 'time_bounds_extended': False,
                 'authority_effect': 'none', 'actual_owner_outcome': None,
                 'current_Agent_qualified': False, 'task_complete': False, 'goal_complete': False})
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(output),
                      'files': len(rows), 'original_methods': 18, 'current_cases': 4}), flush=True)

if __name__ == '__main__':
    main()
