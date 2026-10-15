"""Freeze the carrier-aware successor before its owned runtime effects."""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
INTERFACE = ROOT / 'product/lab/release-candidates/v1/interface'
PARENT = INTERFACE / 'api-v38'
API = INTERFACE / 'api-v39'
COMPOSITION = INTERFACE / 'classification-preparation-v4'
FAILURE = INTERFACE / 'failure-preparation-v1'
FAILURE_RULES = INTERFACE / 'failure-assessment-rules-v8'
RULES = INTERFACE / 'classification-rules-v3'
CONTEXT = INTERFACE / 'current-context-delivery-v8'
PARENT_PIN = '7a7803987956c8935926b0ea608c3e114f92405e418adccbf72dfc5e2467ab7c'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def load(path):
    return json.loads(path.read_bytes())


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def methods(path):
    return {node.name: ast.dump(node, include_attributes=False)
            for node in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')}


def main():
    assert not (API / 'source-manifest.json').exists()
    assert not (API / 'contract-profile.json').exists()
    spec = importlib.util.spec_from_file_location('_cal_API39_parent_guard', PARENT / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    parent = guard.verify(PARENT_PIN)
    checks_path = RUN / 'API39-failure-fixture-authoring-checks-0002.json'
    checks = load(checks_path)
    assert checks['result'] == 'PASS' and checks['actual_checks'] == 278
    assert len(checks['checks']) == 278 and all(row['result'] == 'PASS' for row in checks['checks'])
    inputs_path = ROOT / checks['input_binding']['path']
    assert bind(inputs_path) == checks['input_binding']
    for row in load(inputs_path)['files']:
        assert bind(ROOT / row['path']) == row, row['path']
    proof_path = RULES / 'receipts/proof-0001.json'
    proof = load(proof_path)
    assert proof['result'] == 'PASS' and proof['actual_cases'] == 35
    assert proof['actual_terminal_exit_code'] == 0
    context_proof = CONTEXT / 'receipts/qualification-0001.json'
    qualified = load(context_proof)
    assert bind(context_proof)['sha256'] == '4f9cd4c33f01dc81eae22c105c223ecda7fa7f159862772c7184482552ec8890'
    assert qualified['result'] == 'PASS' and qualified['selected_methods'] == 50
    retained, revised = [], []
    for path in PARENT.rglob('*.py'):
        if 'receipts' in path.parts or '__pycache__' in path.parts:
            continue
        old = methods(path)
        new = methods(API / path.relative_to(PARENT))
        assert old.keys() == new.keys(), path.name
        for name in old:
            key = str(path.relative_to(PARENT)) + ':' + name
            (retained if old[name] == new[name] else revised).append(key)
    assert len(retained) == 275
    assert revised == []
    added=methods(API/'test_failure_api.py')
    assert len(added)==18
    failure_proof_path=FAILURE_RULES/'receipts/proof-0001.json'
    fp=load(failure_proof_path)
    assert fp['result']=='PASS' and fp['actual_cases']==63 and fp['actual_terminal_exit_code']==0
    for name in ('guard.py',):
        assert (API / name).read_bytes() == (PARENT / name).read_bytes()
    selected = [PARENT / 'source-manifest.json', context_proof,
                RULES / 'source-manifest.json', proof_path,
                checks_path, inputs_path,
                RUN / 'API38-classification-exception-diagnostic-0001.json',
                RUN / 'API38-classification-exception-terminal-0001.json',
                RUN / 'API39-failure-fixture-authoring-terminal-0002.json',
                failure_proof_path, FAILURE_RULES/'source-manifest.json',
                RUN/'failure-rules63-terminal-0008.json',
                RUN / 'classification-rules35-terminal-0003.json',
                RUN / 'API37-classification-exception-diagnostic-0001.json',
                RUN / 'API37-classification-exception-terminal-0001.json',
                RUN / 'authorization.json', Path(__file__).resolve()]
    context_path = RUN / 'context-R03-failure-API-0039.json'
    put(context_path, {'schema_version': 'lab-bounded-context/v1-candidate',
                      'task': 'R03 scoped classification and full public failure preparation',
                      'strict_coverage': 'PASS', 'blockers': [],
                      'source_bindings': [bind(path) for path in selected],
                      'constraints': [
                          'Original Product bytes, domain scope and inline version remain distinct from authority header axes.',
                          'Retain all275 inherited method ASTs and add all18 failure cases without replacing an original obligation.',
                          'Each failure fixture has8 baseline nodes and5 separate Typed Relation targets with exact proposals. Scope exclusions remain explicit.',
                          'Full source and permission guards and original900second policy remain mandatory.',
                          'Complete146/134/review11/controls11/termination6/Machine14/classification16/failure18 plus independent integrated audit remain.',
                          'All21 remaining public qualifications and completeS02 precede sole actualR08.'],
                      'authority_effect': 'none', 'actual_owner_outcome': None})
    profile = copy.deepcopy(load(PARENT / 'contract-profile.json'))
    files = []
    for row in profile['files']:
        path = ROOT / row['path']
        if path.is_relative_to(PARENT):
            files.append(bind(API / path.relative_to(PARENT)))
        elif path.is_relative_to(INTERFACE / 'classification-preparation-v3'):
            files.append(bind(COMPOSITION / path.relative_to(INTERFACE / 'classification-preparation-v3')))
        else:
            files.append(row)
    profile['files'] = files
    profile['files'] += [bind(path) for path in FAILURE.iterdir() if path.is_file()]
    profile['files'] += [bind(API/'failure_preparation.py')]
    profile['implemented_operations'] = profile['implemented_operations'] + ['failure.assess']
    assert len(profile['implemented_operations'])==16
    profile['failure_rule_source_binding']=bind(FAILURE_RULES/'source-manifest.json')
    profile['failure_rule_proof_binding']=bind(failure_proof_path)
    profile['carrier_classification_context_binding'] = bind(context_path)
    profile['classification_rule_source_binding'] = bind(RULES / 'source-manifest.json')
    profile['classification_rule_proof_binding'] = bind(proof_path)
    profile['claim_ceiling'] = 'Sixteen authored candidate handlers with278 fixture authoring checks and63 failure kernel cases. All current public suites and independent audit remain; no wholeAPI/Agent/admission/release qualification.'
    put(API / 'contract-profile.json', profile)
    rows = {row['path']: row for row in parent['files']}

    def add(row):
        assert rows.get(row['path'], row) == row, row['path']
        assert bind(ROOT / row['path']) == row, row['path']
        rows[row['path']] = row

    for path in selected + [context_path]:
        add(bind(path))
    for row in load(inputs_path)['files'] + load(RULES / 'source-manifest.json')['files'] + fp['files']:
        add(row)
    for directory in (API, COMPOSITION, FAILURE):
        for path in directory.rglob('*'):
            if path.is_file() and 'receipts' not in path.parts and '__pycache__' not in path.parts:
                if path.suffix == '.py':
                    ast.parse(path.read_bytes())
                add(bind(path))
    manifest = {'schema_version': 'lab-failure-preparation-API-source/v1-candidate',
                'files': [rows[key] for key in sorted(rows)], 'environment': parent['environment'],
                'parent_source_binding': bind(PARENT / 'source-manifest.json'),
                'context_binding': bind(context_path),
                'qualified_context_proof_binding': bind(context_proof),
                'classification_rule_source_binding': bind(RULES / 'source-manifest.json'),
                'classification_rule_proof_binding': bind(proof_path),
                'retained_inherited_methods': retained, 'explicit_revised_methods': revised,
                'unchanged_inherited_method_count': 275, 'original_obligations': 275,
                'additional_failure_methods': sorted(added), 'new_actual_failure_cases':18,
                'failure_rule_source_binding':bind(FAILURE_RULES/'source-manifest.json'),
                'failure_rule_proof_binding':bind(failure_proof_path),
                'static_checks_binding': bind(checks_path), 'authored_handler_count': 16,
                'qualified_public_handler_count': 13, 'remaining_qualified_operations': 21,
                'original_contracts_preserved': 34, 'expected_regression_cases': 146,
                'new_actual_classification_cases': 16, 'original_Machine_cases': 14,
                'original_public_reference_schema_widened': False,
                'freeze_precedes_new_owned_fixture_effects': True,
                'time_bounds_extended': False, 'permissions_cached': False,
                'whole_API_qualified': False, 'current_Agent_qualified': False,
                'task_complete': False, 'goal_complete': False,
                'authority_effect': 'none', 'actual_owner_outcome': None}
    put(API / 'source-manifest.json', manifest)
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(API / 'source-manifest.json'),
                      'profile_binding': bind(API / 'contract-profile.json'),
                      'files': len(rows), 'unchanged_methods': 275, 'explicit_revisions': revised}), flush=True)


if __name__ == '__main__':
    main()
