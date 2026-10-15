"""Freeze the full v37 successor before any of its owned runtime fixtures."""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
INTERFACE = ROOT / 'product/lab/release-candidates/v1/interface'
PARENT = INTERFACE / 'api-v36'
API = INTERFACE / 'api-v37'
COMPOSITION = INTERFACE / 'classification-preparation-v2'
CONTEXT = INTERFACE / 'current-context-delivery-v8'
PARENT_PIN = '1c32032bf01bf9327f8bf2efb731ac30a0970734cd408307ddbe97c6b7a5b1fa'
CONTEXT_PROOF = '4f9cd4c33f01dc81eae22c105c223ecda7fa7f159862772c7184482552ec8890'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def load(path):
    return json.loads(path.read_bytes())


def put(path, body):
    with path.open('x') as stream:
        json.dump(body, stream, indent=2, sort_keys=True)
        stream.write('\n')


def methods(path):
    return {node.name: ast.dump(node, include_attributes=False)
            for node in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')}


def main():
    source_path = API / 'source-manifest.json'
    profile_path = API / 'contract-profile.json'
    assert not source_path.exists() and not profile_path.exists()
    parent_source = PARENT / 'source-manifest.json'
    assert bind(parent_source)['sha256'] == PARENT_PIN
    spec = importlib.util.spec_from_file_location('_cal_API37_freezer_parent_guard', PARENT / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    parent = guard.verify(PARENT_PIN)
    context_proof = CONTEXT / 'receipts/qualification-0001.json'
    assert bind(context_proof)['sha256'] == CONTEXT_PROOF
    proof = load(context_proof)
    assert proof['result'] == 'PASS' and proof['selected_methods'] == 50
    assert proof['actual_build_exit_code'] == proof['actual_check_exit_code'] == proof['actual_audit_exit_code'] == 0
    checks_path = RUN / 'API37-public-reference-checks-0001.json'
    checks_terminal_path = RUN / 'API37-public-reference-terminal-0001.json'
    checks = load(checks_path)
    checks_terminal = load(checks_terminal_path)
    assert checks['result'] == 'PASS' and checks['tests_run'] == checks['expected_tests'] == 12
    assert len(checks['cases']) == 12 and all(row['result'] == 'PASS' for row in checks['cases'])
    assert checks_terminal['terminal_observed'] and checks_terminal['actual_exit_code'] == 0
    assert checks_terminal['report_binding'] == bind(checks_path)
    check_inputs_path = ROOT / checks['input_binding']['path']
    assert bind(check_inputs_path) == checks['input_binding']
    for row in load(check_inputs_path)['files']:
        assert bind(ROOT / row['path']) == row
    diagnostic_path = RUN / 'API36-classification-transport-diagnostic-0001.json'
    diagnostic_terminal_path = RUN / 'API36-classification-transport-terminal-0001.json'
    diagnostic = load(diagnostic_path)
    diagnostic_terminal = load(diagnostic_terminal_path)
    assert diagnostic['public_reply_fields'] == {'schema_version': 'lab-api-transport-error/v1-candidate', 'code': 'invalid-envelope'}
    assert diagnostic['original_api_call_schema_valid'] is False and diagnostic['owned_workspace_removed'] is True
    assert diagnostic_terminal['terminal_observed'] and diagnostic_terminal['actual_exit_code'] == 0
    assert diagnostic_terminal['report_binding'] == bind(diagnostic_path)
    assert (API / 'guard.py').read_bytes() == (PARENT / 'guard.py').read_bytes()
    retained = []
    for path in PARENT.rglob('*.py'):
        if 'receipts' in path.parts or '__pycache__' in path.parts or path.name == 'freeze_classification.py':
            continue
        current = API / path.relative_to(PARENT)
        assert methods(path) == methods(current), path.name
        retained.extend(str(path.relative_to(PARENT)) + ':' + name for name in methods(path))
    assert len(retained) == 275
    current_reference_checks = load(RUN / 'current-source-anchor-checks-0003.json')
    assert current_reference_checks['result'] == 'PASS'
    assert current_reference_checks['tests_run'] == current_reference_checks['expected_tests'] == 18
    assert current_reference_checks['whole_original_file_set_measurement']['file_selection_reduced'] is False
    context_path = RUN / 'context-R03-public-reference-API-0037.json'
    selected_inputs = [parent_source, context_proof, checks_path, check_inputs_path, checks_terminal_path,
                       diagnostic_path, diagnostic_terminal_path,
                       RUN / 'current-source-anchor-checks-0003.json',
                       RUN / 'current-source-anchor-terminal-0003.json',
                       RUN / 'API37-public-reference-construction-0001.json',
                       RUN / 'authorization.json', Path(__file__).resolve()]
    put(context_path, {'schema_version': 'lab-bounded-context/v1-candidate',
                       'task': 'R03 exact public reference and current termination successor',
                       'strict_coverage': 'PASS', 'blockers': [],
                       'source_bindings': [bind(path) for path in selected_inputs],
                       'constraints': ['Retain all275 inherited method ASTs and full34contracts/46tasks.',
                                       'Original public five-field reference schema remains closed; contract binding stays on validated proposal targets.',
                                       'Full current file/source/permission guards, fixed Source4 period and900second Session ceiling remain.',
                                       'Complete original146/134/review11/controls11/termination6/Machine14/classification16 and independent integrated audit remain required.',
                                       'All21 remaining original operation qualifications and completeS02 precede sole actualR08.'],
                       'authority_effect': 'none', 'actual_owner_outcome': None})
    profile = copy.deepcopy(load(PARENT / 'contract-profile.json'))
    replaced_files = []
    for row in profile['files']:
        path = ROOT / row['path']
        if path.is_relative_to(PARENT):
            replaced_files.append(bind(API / path.relative_to(PARENT)))
        elif path.is_relative_to(INTERFACE / 'classification-preparation-v1'):
            replaced_files.append(bind(COMPOSITION / path.relative_to(INTERFACE / 'classification-preparation-v1')))
        else:
            replaced_files.append(row)
    profile['files'] = replaced_files
    profile['public_reference_context_binding'] = bind(context_path)
    profile['claim_ceiling'] = 'Fifteen authored handlers, public-reference corrections and exact current termination period; no successor full-suite/API/Agent qualification, owner outcome or release.'
    put(profile_path, profile)
    rows = {row['path']: row for row in parent['files']}
    def add(row):
        assert rows.get(row['path'], row) == row
        assert bind(ROOT / row['path']) == row
        rows[row['path']] = row
    for path in selected_inputs + [context_path]:
        add(bind(path))
    for row in load(check_inputs_path)['files']:
        add(row)
    for directory in (API, COMPOSITION):
        for path in directory.rglob('*'):
            if path.is_file() and 'receipts' not in path.parts and '__pycache__' not in path.parts:
                if path.suffix == '.py':
                    ast.parse(path.read_bytes())
                add(bind(path))
    manifest = {'schema_version': 'lab-public-reference-API-source/v1-candidate',
                'files': [rows[key] for key in sorted(rows)], 'environment': parent['environment'],
                'parent_source_binding': bind(parent_source), 'context_binding': bind(context_path),
                'qualified_context_proof_binding': bind(context_proof), 'retained_inherited_methods': retained,
                'unchanged_inherited_method_count': 275, 'authored_handler_count': 15,
                'qualified_public_handler_count': 13, 'remaining_qualified_operations': 21,
                'original_contracts_preserved': 34, 'expected_regression_cases': 146,
                'new_actual_classification_cases': 16, 'original_Machine_cases': 14,
                'public_reference_checks_binding': bind(checks_path),
                'current_source_guard_checks_binding': bind(RUN / 'current-source-anchor-checks-0003.json'),
                'current_source_guard_terminal_binding': bind(RUN / 'current-source-anchor-terminal-0003.json'),
                'original_public_reference_schema_widened': False,
                'freeze_precedes_new_owned_fixture_effects': True,
                'time_bounds_extended': False, 'permissions_cached': False,
                'whole_API_qualified': False, 'current_Agent_qualified': False,
                'task_complete': False, 'goal_complete': False,
                'authority_effect': 'none', 'actual_owner_outcome': None}
    put(source_path, manifest)
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(source_path),
                      'profile_binding': bind(profile_path), 'files': len(rows),
                      'inherited_method_ASTs_unchanged': 275}), flush=True)


if __name__ == '__main__':
    main()
