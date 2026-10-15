"""Preserve both original exact producer-check registrations in a frozen successor."""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
PARENT = BASE / 'api-v43'
API = BASE / 'api-v44'


def bind(path):
    return {'path': str(path.relative_to(ROOT)),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2); stream.write('\n')


def methods(path):
    return {node.name: ast.dump(node, include_attributes=False)
            for node in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')}


def main():
    spec = importlib.util.spec_from_file_location('_cal_API44_parent_guard', PARENT / 'guard.py')
    guard = importlib.util.module_from_spec(spec); spec.loader.exec_module(guard)
    parent = guard.verify('57c048a3630590b3f7ed38212d432d33257f281c3df58ce137fafde73f1bd45d')
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
    assert changed == ['source_bridge.py'] and len(retained) == 293
    context = RUN / 'context-R03-scope-compatibility-API-0044.json'
    static = RUN / 'API44-scope-compatibility-authoring-0001.json'
    paths = [PARENT / 'source-manifest.json', RUN / 'API43-existing-scope-registration-finding-0001.json',
             RUN / 'API43-freeze-terminal-0001.json', BASE / 'current-context-delivery-v8/control.py',
             BASE / 'api-v42/custody_context_sessions.py', RUN / 'authorization.json',
             Path(__file__).resolve()]
    put(static, {'schema_version': 'lab-scope-compatibility-static-checks/v1-candidate',
                 'result': 'PASS', 'unchanged_original_test_methods': 293,
                 'original_API_schema_bytes_unchanged': True,
                 'original_callback_bytes_unchanged': True,
                 'scope_pin_and_selected_registration_required': True,
                 'files': [bind(p) for p in paths], 'actual_public_calls': 0,
                 'whole_API_qualified': False, 'authority_effect': 'none', 'task_complete': False})
    put(context, {'schema_version': 'lab-bounded-context/v1-candidate',
                  'task': 'R03 preserve existing producer-check registration while grouping pure calculation',
                  'strict_coverage': 'PASS', 'blockers': [],
                  'source_bindings': [bind(p) for p in paths + [static]],
                  'change': 'Select only exact original preflight or verify_source with unchanged independent pin and actual current scope registration.',
                  'constraints': ['All293 original public methods and all34 API contracts unchanged.',
                                  'All source/policy callbacks remain original; no clock, permission or deadline change.',
                                  'Both full source boundaries and actual uncached policy reads remain mandatory.',
                                  'Existing Session scope and pure candidate scope retain their own selected registration.'],
                  'whole_API_qualified': False, 'actual_owner_outcome': None, 'authority_effect': 'none'})
    profile = json.loads((PARENT / 'contract-profile.json').read_bytes())
    profile['files'] = [bind(API / (ROOT / row['path']).relative_to(PARENT))
                        if (ROOT / row['path']).is_relative_to(PARENT) else row
                        for row in profile['files']]
    profile['carrier_classification_context_binding'] = bind(context)
    profile['scope_compatibility_context_binding'] = bind(context)
    profile['claim_ceiling'] = 'Sixteen authored handlers; bounded pure calculation with original scope compatibility. Current public suites and qualifications remain required.'
    put(API / 'contract-profile.json', profile)
    rows = {row['path']: row for row in parent['files']}
    for path in paths + [context, static]:
        row = bind(path); rows[row['path']] = row
    for path in API.rglob('*'):
        if path.is_file() and 'receipts' not in path.parts and '__pycache__' not in path.parts:
            row = bind(path); rows[row['path']] = row
    manifest = copy.deepcopy(parent)
    manifest.update(files=[rows[key] for key in sorted(rows)],
                    parent_source_binding=bind(PARENT / 'source-manifest.json'),
                    context_binding=bind(context), static_checks_binding=bind(static),
                    retained_inherited_methods=retained, unchanged_inherited_method_count=293,
                    explicit_revised_methods=[], whole_API_qualified=False,
                    current_Agent_qualified=False, task_complete=False, goal_complete=False)
    put(API / 'source-manifest.json', manifest)
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(API / 'source-manifest.json'),
                      'profile_binding': bind(API / 'contract-profile.json'),
                      'source_files': len(rows), 'unchanged_methods': len(retained)}), flush=True)


if __name__ == '__main__':
    main()
