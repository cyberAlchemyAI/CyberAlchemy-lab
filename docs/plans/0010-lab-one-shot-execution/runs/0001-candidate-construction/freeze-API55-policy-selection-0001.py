"""Freeze the Session opening successor and retain all inherited test ASTs."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD, API = BASE / 'api-v54', BASE / 'api-v55'
EXTRA = [BASE / 'api55-package-checks-v1', BASE / 'api55-session-checks-v1', BASE / 'lesson-host-composition-v5']


def load(path):
    return json.loads(path.read_bytes())


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def files(path):
    return sorted(p for p in path.rglob('*') if p.is_file() and not {'receipts', '__pycache__'} & set(p.parts)
                  and p.name not in ('source-manifest.json', 'contract-profile.json'))


def emit(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def tests(path):
    return {n.name: ast.dump(n, include_attributes=False) for n in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}


def main():
    spec = importlib.util.spec_from_file_location('_cal_API55_parent_guard', OLD / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    parent = guard.verify('c5706f746f40228b5fae94803c5d3eab6ac8297f184bfb0d14293ddd9986a15b')
    inherited = []
    for path in files(OLD):
        if path.suffix == '.py':
            assert tests(path) == tests(API / path.relative_to(OLD)), path
            inherited.extend(path.relative_to(OLD).as_posix() + ':' + name for name in tests(path))
    assert len(inherited) == 293
    for path in files(API) + [p for folder in EXTRA for p in files(folder)]:
        if path.suffix == '.py':
            ast.parse(path.read_bytes())
    doc = API / 'POLICY-VERIFYING.md'
    with doc.open('x') as stream:
        stream.write('''# Policy verification successor

API54 passed one original expiry case, but its second case expired during the
original note post-write guard. The failed report and actual terminal remain.
This successor also selects the original Context producer once per synchronous
policy check and reuses its verified module handle only within that invocation.
The same original preflight and reader selection execute, plus every actual
policy, period, revocation and clock check. No source bytes or grants are cached
between calls. The unused second preflight within that same policy check is
removed. Termination behavior retains its separate original source rules.

The original 70-second expiry tests failed in API50. A retained API53 profile
confirms that repeated original file checks dominate execution; profiling adds
overhead and does not qualify normal latency. All 293 inherited method ASTs and
34 public contracts remain unchanged in this successor.

Pre-claim eligibility retains its full original scope. After the durable claim,
eligibility, exact original delivery verification, classification, Agent/Session
descriptors and connection metadata share one synchronous pure source read scope.
The exact delivery consumed by eligibility is reused within that calculation.
Profile resolution uses its sealed copy. Original source/eligibility/channel
callbacks and the scope registry are unchanged. Every policy call rereads the
actual private policy, revocation and real clock. Full original source/package
exit checks precede live resource creation and journal writes outside the scope.

Short memory still belongs only to the live Session and is erased on disposal.
The original timer and absolute Assignment/deadline limits are retained. A final
real-clock check follows reply verification so an expired operation returns an
indeterminate outcome available through operation.inspect. Recorded exact retries
continue to return operation evidence without recreating a live resource.

Qualification requires this successor's own original expiry tests, affected
Session journeys, package import and full API regression. Authoring and static
AST retention alone do not qualify runtime latency, admit this implementation,
complete the plan or authorize activation. Nineteen handlers are authored and
fifteen original operations remain unimplemented.
''')
    static = RUN / 'API55-session-scope-static-0001.json'
    emit(static, {'schema_version': 'lab-session-scope-static/v1-candidate', 'result': 'PASS',
        'retained_original_operation_contracts': 34, 'retained_inherited_methods': 293,
        'selected_original_expiry_cases': 2, 'original_expiry_case_ASTs_unchanged': True,
        'authored_handlers': 19, 'missing_operations': 15, 'actual_public_calls': 0,
        'actual_runtime_qualified': False, 'whole_API_qualified': False,
        'authority_effect': 'none', 'actual_owner_outcome': None, 'task_complete': False, 'goal_complete': False})
    profile = load(OLD / 'contract-profile.json')
    profile['files'] = [bind(API / (ROOT / row['path']).relative_to(OLD))
        if (ROOT / row['path']).is_relative_to(OLD) else row for row in profile['files']]
    extra = [bind(p) for p in files(API) if not (OLD / p.relative_to(API)).exists()]
    extra += [bind(p) for folder in EXTRA for p in files(folder)] + [bind(static)]
    rows = {r['path']: r for r in profile['files'] + extra}
    profile['files'] = [rows[k] for k in sorted(rows)]
    profile['claim_ceiling'] = 'Nineteen authored handlers; Session opening pure read scope successor awaits unchanged original real-clock expiry and affected runtime checks. Fifteen operations and whole plan/API qualification remain incomplete.'
    emit(API / 'contract-profile.json', profile)
    rows = {r['path']: r for r in parent['files']}
    for row in extra:
        rows[row['path']] = row
    for path in files(API) + [p for folder in EXTRA for p in files(folder)] + [OLD / 'source-manifest.json',
            API / 'contract-profile.json', Path(__file__).resolve(), RUN / 'author-API55-policy-selection-0001.py',
            RUN / 'API53-original-expiry-profile-0001.json', RUN / 'API53-original-expiry-profile-0001.log',
            RUN / 'API54-expiry2-failed-terminal-0001.json',
            BASE / 'api54-session-checks-v1/receipts/checks-0001.json',
            BASE / 'api54-session-checks-v1/receipts/actual-0001.log',
            BASE / 'api54-session-checks-v1/receipts/wire-0001.json']:
        row = bind(path)
        rows[row['path']] = row
    for row in rows.values():
        assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
    emit(API / 'source-manifest.json', {**parent, 'files': [rows[k] for k in sorted(rows)],
        'parent_source_binding': bind(OLD / 'source-manifest.json'), 'retained_inherited_methods': inherited,
        'unchanged_inherited_method_count': 293, 'whole_API_qualified': False,
        'original_expiry_runtime_qualified': False, 'package_import_actual_runtime_qualified': False,
        'task_complete': False, 'goal_complete': False})
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(API / 'source-manifest.json'),
        'profile_binding': bind(API / 'contract-profile.json'), 'retained_original_methods': 293,
        'authored_handlers': 19, 'missing_operations': 15, 'actual_runtime_qualified': False}), flush=True)


if __name__ == '__main__':
    main()
