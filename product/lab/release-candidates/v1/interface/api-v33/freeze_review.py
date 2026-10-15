"""Freeze one diagnosed fixture repair; all production code and checks retained."""
import ast
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
RUN = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
PARENT = HERE.parent / 'api-v32'

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
    return {n.name: ast.dump(n, include_attributes=False)
            for n in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}

def main():
    assert not (HERE / 'source-manifest.json').exists()
    assert not (HERE / 'contract-profile.json').exists()
    parent_source = PARENT / 'source-manifest.json'
    diagnostic = RUN / 'current-review-diagnostic-proof-0001.json'
    observed = load(diagnostic)
    assert observed['result'] == 'OBSERVED' and observed['actual_diagnostic_exit_code'] == 0
    assert observed['actual_error_code'] == 'invalid-contract'
    assert observed['actual_exception_function'] == 'ReviewPreparation.routing_guard'
    rows = {}
    def add(row):
        assert rows.get(row['path'], row) == row, row['path']
        assert bind(ROOT / row['path']) == row, row['path']
        rows[row['path']] = row
    for manifest in [load(parent_source), observed]:
        for row in manifest['files']:
            add(row)
    retained = []
    for old in PARENT.rglob('*'):
        if not old.is_file() or any(n in old.parts for n in ['receipts', '__pycache__']):
            continue
        relative = old.relative_to(PARENT)
        if relative.as_posix() in ('source-manifest.json', 'contract-profile.json', 'freeze_review.py'):
            continue
        current = HERE / relative
        assert current.is_file(), str(relative)
        if relative.as_posix() == 'review_fixture.py':
            before = old.read_text()
            needle = "'reference':'protocol:R03-current-review:'+uuid.uuid4().hex"
            assert before.count(needle) == 1
            assert current.read_text() == before.replace(needle, "'reference':'protocol:R03-review-workflow:'+uuid.uuid4().hex")
        else:
            assert current.read_bytes() == old.read_bytes(), str(relative)
        if current.suffix == '.py':
            assert methods(old) == methods(current), str(relative)
            retained.extend(str(relative) + ':' + name for name in methods(old))
    assert len(retained) == 239
    assert len(methods(HERE / 'test_review_api.py')) == 11
    context = RUN / 'context-R03-review-prefix-repair-0002.json'
    put(context, {'schema_version': 'lab-bounded-context/v1-candidate',
                  'task': 'R03 correct independently supplied workflow protocol reference',
                  'strict_coverage': 'PASS', 'blockers': [],
                  'source_bindings': [bind(parent_source), bind(diagnostic),
                                      bind(RUN / 'authorization.json'), bind(HERE / 'review-routing-repair.json')],
                  'constraints': ['Only the fixture reference prefix changes to match the existing closed schema.',
                                  'All239inherited check methods and production source bytes remain unchanged.',
                                  'No grant, deadline, public contract, callback or source period changes.',
                                  'Retain the original full11case run; it remains independently running and unqualified.',
                                  'Actual successor review11 and full integration qualification remain required.',
                                  'Candidate construction only; no owner outcome or canonical admission.'],
                  'authority_effect': 'none', 'actual_owner_outcome': None})
    for p in [parent_source, diagnostic, context]:
        add(bind(p))
    profile = copy.deepcopy(load(PARENT / 'contract-profile.json'))
    profile['files'] = [bind(HERE / (ROOT / row['path']).relative_to(PARENT)
                             if (ROOT / row['path']).is_relative_to(PARENT) else ROOT / row['path'])
                        for row in profile['files']]
    profile['review_context_binding'] = bind(context)
    profile['diagnosed_predecessor_binding'] = bind(diagnostic)
    profile['claim_ceiling'] = 'Fourteen authored handlers with one schema-compliant fixture reference repair. Actual review11, full regression146/134, current controls11 and independent qualification remain pending. No admission or governing owner authority.'
    assert len(profile['implemented_operations']) == 14
    put(HERE / 'contract-profile.json', profile)
    for p in HERE.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:
            if p.suffix == '.py':
                ast.parse(p.read_bytes())
            add(bind(p))
    previous = load(parent_source)
    manifest = {'schema_version': 'lab-current-review-prefix-repair-source/v1-candidate',
                'files': [rows[k] for k in sorted(rows)], 'environment': previous['environment'],
                'parent_source_binding': bind(parent_source), 'diagnostic_binding': bind(diagnostic),
                'context_binding': bind(context), 'original_contracts_preserved': 34,
                'unchanged_inherited_methods': retained, 'production_source_unchanged': True,
                'exact_fixture_reference_repair': True, 'authored_handler_count': 14,
                'qualified_public_handler_count': 13, 'remaining_qualified_operations': 21,
                'expected_regression_cases': previous['expected_regression_cases'],
                'parent_review_suite_terminal_observed': False,
                'parent_review_suite_session': 35878, 'current_Agent_qualified': False,
                'freeze_precedes_new_owned_fixture_effects': True,
                'authority_effect': 'none', 'actual_owner_outcome': None,
                'task_complete': False, 'goal_complete': False}
    put(HERE / 'source-manifest.json', manifest)
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(HERE / 'source-manifest.json'),
                      'profile_binding': bind(HERE / 'contract-profile.json'),
                      'unchanged_methods': len(retained), 'files': len(rows)}), flush=True)

if __name__ == '__main__':
    main()
