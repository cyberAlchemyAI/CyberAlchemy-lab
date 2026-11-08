"""Freeze Session boundary composition after actual helper qualification."""
import ast
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
PARENT = HERE.parent / 'api-v33'
HELPER = HERE.parent / 'fact-read-scope-v2'
RUN = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def load(path):
    return json.loads(path.read_bytes())


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')


def methods(path):
    return {node.name: ast.dump(node, include_attributes=False)
            for node in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')}


def main():
    assert not (HERE / 'source-manifest.json').exists()
    assert not (HERE / 'contract-profile.json').exists()
    helper_source = HELPER / 'source-manifest.json'
    assert bind(helper_source)['sha256'] == '89175b84cf29a4baef6a42194d6d753ff49d73a4855e0f011441408d12a7f446'
    helper_proof = HELPER / 'receipts/proof-0001.json'
    helper_report = HELPER / 'receipts/checks-0001.json'
    proof = load(helper_proof)
    report = load(helper_report)
    assert proof['result'] == 'PASS' and proof['actual_terminal_exit_code'] == 0
    assert report['result'] == 'PASS' and report['tests_run'] == report['expected_tests'] == 22
    assert len(report['cases']) == 22 and all(row['result'] == 'PASS' for row in report['cases'])
    parent_source = PARENT / 'source-manifest.json'
    parent_controls = PARENT / 'receipts/current-controls.json'
    controls_terminal = RUN / 'current-Agent-controls-terminal-0007.json'
    assert bind(parent_source)['sha256'] == 'd240d0d47f83b2dfeb9b5cccdba824d22986b37a690cb2318f8a77782e09487a'
    controls = load(parent_controls)
    assert controls['result'] == 'PASS' and controls['tests_run'] == controls['expected_tests'] == 11
    assert load(controls_terminal)['exit_code'] == 0
    rows = {}

    def add(row):
        assert rows.get(row['path'], row) == row, row['path']
        assert bind(ROOT / row['path']) == row, row['path']
        rows[row['path']] = row

    for document in [load(parent_source), load(helper_source), proof]:
        for row in document['files']:
            add(row)
    inherited = []
    changed = {'auth.py', 'custody_context_sessions.py'}
    excluded = {'source-manifest.json', 'contract-profile.json', 'freeze_review.py'}
    for old in PARENT.rglob('*'):
        if not old.is_file() or any(name in old.parts for name in ('receipts', '__pycache__')):
            continue
        relative = old.relative_to(PARENT)
        if relative.as_posix() in excluded:
            continue
        current = HERE / relative
        assert current.is_file(), str(relative)
        if relative.as_posix() not in changed:
            assert current.read_bytes() == old.read_bytes(), str(relative)
        if current.suffix == '.py':
            assert methods(old) == methods(current), str(relative)
            inherited.extend(str(relative) + ':' + name for name in methods(old))
    assert len(inherited) == 239
    assert len(methods(HERE / 'test_termination_boundaries.py')) == 6
    context = RUN / 'context-R03-session-boundaries-0003.json'
    inputs = [parent_source, helper_source, helper_proof, helper_report,
              parent_controls, controls_terminal, RUN / 'authorization.json',
              RUN / 'current-Agent-development-observation-failed-proof-0005.json',
              HERE / 'SESSION-BOUNDARIES.md', HERE / 'session-boundary-derivation.json']
    put(context, {'schema_version': 'lab-bounded-context/v1-candidate',
                  'task': 'R03 Session opening and termination boundary composition',
                  'strict_coverage': 'PASS', 'blockers': [],
                  'source_bindings': [bind(path) for path in inputs],
                  'constraints': ['Original 34 public contracts and 239 inherited test methods preserved.',
                                  'Only auth.py and custody_context_sessions.py production bytes change.',
                                  'Helper has actual 22 case PASS and observed successful terminal.',
                                  'Initial source identity captures no permission; termination rereads policy, exact period and real clock.',
                                  'No Assignment renewal, deadline extension, callback replacement or durable dispatch inside scope.',
                                  'Six actual termination cases and original full regression/lifecycle obligations remain.',
                                  'No Machine Agent transport qualification follows from this change.',
                                  'Candidate only; sole real owner checkpoint remains R08 after complete S02.'],
                  'actual_owner_outcome': None, 'authority_effect': 'none'})
    for path in inputs + [context]:
        add(bind(path))
    profile = copy.deepcopy(load(PARENT / 'contract-profile.json'))
    profile['files'] = [bind(HERE / (ROOT / row['path']).relative_to(PARENT)
                             if (ROOT / row['path']).is_relative_to(PARENT) else ROOT / row['path'])
                        for row in profile['files']]
    profile['session_boundary_context_binding'] = bind(context)
    profile['qualified_boundary_helper_binding'] = bind(helper_proof)
    profile['claim_ceiling'] = 'Fourteen authored handlers with proposed Session boundary composition. Parent controls11 and helper22 passed; successor six termination checks, full146/134 regression, review11 and lifecycle remain pending. No Machine Agent transport qualification, admission or governing authority.'
    assert len(profile['implemented_operations']) == 14
    put(HERE / 'contract-profile.json', profile)
    for path in HERE.rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts:
            if path.suffix == '.py':
                ast.parse(path.read_bytes())
            add(bind(path))
    manifest = {'schema_version': 'lab-Session-boundary-composition-source/v1-candidate',
                'files': [rows[key] for key in sorted(rows)],
                'environment': load(parent_source)['environment'],
                'parent_source_binding': bind(parent_source), 'context_binding': bind(context),
                'qualified_boundary_helper_binding': bind(helper_proof),
                'parent_controls_terminal_binding': bind(controls_terminal),
                'unchanged_inherited_methods': inherited,
                'new_actual_termination_cases': 6, 'original_contracts_preserved': 34,
                'expected_regression_cases': load(parent_source)['expected_regression_cases'],
                'changed_production_files': sorted(changed), 'authored_handler_count': 14,
                'qualified_public_handler_count': 13, 'remaining_qualified_operations': 21,
                'parent_full_regression_qualified': False, 'current_Agent_qualified': False,
                'freeze_precedes_new_owned_fixture_effects': True,
                'time_bounds_extended': False, 'permissions_cached': False,
                'actual_owner_outcome': None, 'authority_effect': 'none',
                'task_complete': False, 'goal_complete': False}
    put(HERE / 'source-manifest.json', manifest)
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(HERE / 'source-manifest.json'),
                      'profile_binding': bind(HERE / 'contract-profile.json'),
                      'inherited_methods': len(inherited), 'new_cases': 6,
                      'files': len(rows)}), flush=True)


if __name__ == '__main__':
    main()
