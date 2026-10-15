"""Freeze a successor that preserves every test and fixes JSON fixture evidence."""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
INTERFACE = ROOT / 'product/lab/release-candidates/v1/interface'
PARENT = INTERFACE / 'api-v39'
API = INTERFACE / 'api-v40'


def bind(path):
    return {'path': str(path.relative_to(ROOT)),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def methods(path):
    return {n.name: ast.dump(n, include_attributes=False)
            for n in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}


def main():
    spec = importlib.util.spec_from_file_location('_cal_API40_parent_guard', PARENT / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    parent = guard.verify('9da5ddbe2f6e6d1f9edd6d4f1ff83df9ab894804ab93bcf5e11379a7226cdf35')
    checks_path = RUN / 'API40-failure-fixture-authoring-checks-0002.json'
    checks = json.loads(checks_path.read_bytes())
    assert checks['result'] == 'PASS' and checks['actual_checks'] == 278
    inputs_path = ROOT / checks['input_binding']['path']
    assert bind(inputs_path) == checks['input_binding']
    for row in json.loads(inputs_path.read_bytes())['files']:
        assert bind(ROOT / row['path']) == row
    retained = []
    changed = []
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
            retained.extend(str(path.relative_to(PARENT)) + ':' + n for n in methods(path))
    assert changed == ['failure_fixture.py']
    assert len(retained) == 293
    terminal = RUN / 'API39-failure18-terminal-0001.json'
    failed = json.loads(terminal.read_bytes())
    assert failed['actual_terminal_exit_code'] == 1 and failed['errors'] == 18
    context = RUN / 'context-R03-failure-API-0040.json'
    selected = [PARENT / 'source-manifest.json', checks_path, inputs_path,
                terminal, RUN / 'authorization.json', Path(__file__).resolve()]
    put(context, {'schema_version': 'lab-bounded-context/v1-candidate',
                  'task': 'R03 failure fixture evidence JSON successor',
                  'strict_coverage': 'PASS', 'blockers': [],
                  'source_bindings': [bind(p) for p in selected],
                  'change': 'Encode synthetic evidence as a JSON object before signed workspace provisioning.',
                  'constraints': ['All293 test methods unchanged; all34 API schemas unchanged.',
                                  'Preserve all source guards, signed policy checks, real clocks and900second ceiling.',
                                  'All current suites and operation qualifications still required before R08.'],
                  'actual_owner_outcome': None, 'authority_effect': 'none'})
    profile = json.loads((PARENT / 'contract-profile.json').read_bytes())
    profile['files'] = [bind(API / (ROOT / r['path']).relative_to(PARENT))
                        if (ROOT / r['path']).is_relative_to(PARENT) else r
                        for r in profile['files']]
    profile['carrier_classification_context_binding'] = bind(context)
    profile['claim_ceiling'] = 'Sixteen authored handlers; synthetic evidence JSON fixture correction. Current public operation qualification remains incomplete.'
    put(API / 'contract-profile.json', profile)
    rows = {r['path']: r for r in parent['files']}
    for p in selected + [context]:
        rows[bind(p)['path']] = bind(p)
    for r in json.loads(inputs_path.read_bytes())['files']:
        rows[r['path']] = r
    for p in API.rglob('*'):
        if p.is_file() and 'receipts' not in p.parts and '__pycache__' not in p.parts:
            rows[bind(p)['path']] = bind(p)
    manifest = copy.deepcopy(parent)
    manifest.update(files=[rows[k] for k in sorted(rows)],
                    parent_source_binding=bind(PARENT / 'source-manifest.json'),
                    context_binding=bind(context), static_checks_binding=bind(checks_path),
                    retained_inherited_methods=retained, unchanged_inherited_method_count=293,
                    explicit_revised_methods=[], fixture_evidence_encoding='JSON object with explicit synthetic claim',
                    original_obligations=275, whole_API_qualified=False,
                    current_Agent_qualified=False, task_complete=False, goal_complete=False)
    put(API / 'source-manifest.json', manifest)
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(API / 'source-manifest.json'),
                      'profile_binding': bind(API / 'contract-profile.json'),
                      'source_files': len(rows), 'unchanged_methods': len(retained)}), flush=True)


if __name__ == '__main__':
    main()
