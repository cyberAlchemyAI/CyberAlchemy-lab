"""Freeze the review successor after actual parent controls and Context qualification."""
import ast
import copy
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
RUN = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
PARENT = HERE.parent / 'api-v31'

def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

def load(path):
    return json.loads(path.read_bytes())

def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')

def methods(path):
    return {node.name: node for node in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')}

def main():
    assert not (HERE / 'source-manifest.json').exists()
    assert not (HERE / 'contract-profile.json').exists()
    rows = {}
    def add(row):
        assert rows.get(row['path'], row) == row, row['path']
        assert bind(ROOT / row['path']) == row, row['path']
        rows[row['path']] = row
    parents = [PARENT / 'receipts/R03-0041.json',
               HERE.parent / 'review-package-v2/receipts/independent-proof-0001.json']
    for path in parents:
        receipt = load(path)
        assert receipt['result'] == 'PASS'
        for row in receipt['files']:
            add(row)
        add(bind(path))
    controls_path = PARENT / 'receipts/current-controls.json'
    controls = load(controls_path)
    terminal_path = RUN / 'current-Agent-controls-terminal-0006.json'
    terminal = load(terminal_path)
    assert controls['result'] == 'PASS' and controls['tests_run'] == controls['expected_tests'] == 11
    assert len(controls['cases']) == len({case['test'] for case in controls['cases']}) == 11
    assert all(case['result'] == 'PASS' for case in controls['cases'])
    assert terminal['exit_code'] == 0 and terminal['terminal_observed'] is True
    assert controls['source_sha256'] == bind(PARENT / 'source-manifest.json')['sha256']
    assert controls['profile_sha256'] == bind(PARENT / 'contract-profile.json')['sha256']
    context = RUN / 'context-R03-review-integration-0001.json'
    scoped = load(context)
    assert scoped['strict_coverage'] == 'PASS' and scoped['blockers'] == []
    for row in scoped['source_bindings']:
        add(row)
    for path in [controls_path, terminal_path, context]:
        add(bind(path))
    cardinality_updates = {'run_session_checks.py', 'test_custody_sessions.py', 'test_current_controls.py'}
    retained, changed = [], []
    for path in PARENT.glob('*.py'):
        previous = methods(path)
        if not previous:
            continue
        current = methods(HERE / path.name)
        assert set(previous) == set(current), path.name
        for name, old in previous.items():
            new = current[name]
            if ast.dump(old, include_attributes=False) == ast.dump(new, include_attributes=False):
                retained.append(path.name + ':' + name)
                continue
            assert path.name in cardinality_updates
            old_text = ast.get_source_segment(path.read_text(), old)
            assert old_text.count('self.assertEqual(len(SUPPORTED),13)') == 1
            expected = ast.parse(old_text.replace('self.assertEqual(len(SUPPORTED),13)',
                                                  'self.assertEqual(len(SUPPORTED),14)')).body[0]
            assert ast.dump(expected, include_attributes=False) == ast.dump(new, include_attributes=False)
            changed.append(path.name + ':' + name)
    assert len(retained) + len(changed) == 228 and len(changed) == 3
    assert len(methods(HERE / 'test_review_api.py')) == 11
    # The new private review grant leaves every old grant branch unchanged.
    previous_auth = load(PARENT / 'authentication.schema.json')['oneOf']
    current_auth = load(HERE / 'authentication.schema.json')['oneOf']
    assert current_auth[:len(previous_auth)] == previous_auth and len(current_auth) == len(previous_auth) + 1
    protocol_ast = ast.parse((HERE / 'protocol.py').read_bytes())
    constants = {node.targets[0].id: ast.literal_eval(node.value) for node in protocol_ast.body
                 if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
                 and node.targets[0].id in ('METADATA_SUPPORTED', 'LEGACY_SUPPORTED')}
    assert len(constants['METADATA_SUPPORTED']) == 8 and len(constants['LEGACY_SUPPORTED']) == 12
    profile = copy.deepcopy(load(PARENT / 'contract-profile.json'))
    profile['files'] = [bind(HERE / (ROOT / row['path']).relative_to(PARENT)
                             if (ROOT / row['path']).is_relative_to(PARENT) else ROOT / row['path'])
                        for row in profile['files']]
    for name in ['review_preparation.py', 'review-routing.schema.json', 'review_fixture.py']:
        row = bind(HERE / name)
        assert row['path'] not in {r['path'] for r in profile['files']}
        profile['files'].append(row)
    profile['implemented_operations'].append('proposal.review')
    assert len(profile['implemented_operations']) == len(set(profile['implemented_operations'])) == 14
    profile['new_review_grant_operations'] = 9
    profile['qualified_parent_controls_binding'] = bind(controls_path)
    profile['review_context_binding'] = bind(context)
    profile['claim_ceiling'] = 'Fourteen authored candidate handlers, including exact multi-member review. Actual review11, regression146/134, controls11 and independent current integration qualification remain pending. No governing owner authority or admission.'
    environment = {'python': platform.python_version(),
                   'jsonschema': importlib.metadata.version('jsonschema'),
                   'cryptography': importlib.metadata.version('cryptography')}
    assert environment == {'python': '3.14.4', 'jsonschema': '4.23.0', 'cryptography': '46.0.5'}
    put(HERE / 'contract-profile.json', profile)
    for path in HERE.rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts:
            if path.suffix == '.py':
                ast.parse(path.read_bytes())
            add(bind(path))
    manifest = {'schema_version': 'lab-current-review-API-source/v1-candidate',
                'files': [rows[key] for key in sorted(rows)], 'environment': environment,
                'parent_partial_receipt_binding': bind(parents[0]),
                'parent_controls_binding': bind(controls_path),
                'parent_controls_terminal_binding': bind(terminal_path),
                'context_binding': bind(context), 'original_contracts_preserved': 34,
                'unchanged_inherited_methods': retained, 'documented_cardinality_updates': changed,
                'additional_review_methods': 11, 'authored_handler_count': 14,
                'remaining_declared_operations': 20,
                'expected_regression_cases': {'review': 11, 'integration': 146,
                                              'metadata_and_export': 134, 'current_controls': 11},
                'qualified_public_handler_count': 13, 'current_Agent_qualified': False,
                'freeze_precedes_new_owned_fixture_effects': True,
                'actual_owner_outcome': None, 'authority_effect': 'none',
                'task_complete': False, 'goal_complete': False}
    put(HERE / 'source-manifest.json', manifest)
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(HERE / 'source-manifest.json'),
                      'profile_binding': bind(HERE / 'contract-profile.json'), 'files': len(rows),
                      'unchanged_methods': len(retained), 'cardinality_updates': len(changed)}), flush=True)

if __name__ == '__main__':
    main()
