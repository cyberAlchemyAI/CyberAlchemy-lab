"""Freeze actual candidate import dispatch with all original contracts/methods retained."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD, API = BASE / 'api-v52', BASE / 'api-v53'
CHECK = BASE / 'api53-package-checks-v1'
LESSON = BASE / 'lesson-host-composition-v3'
PUB = BASE / 'package-publication-v2'


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
    spec = importlib.util.spec_from_file_location('_cal_API53_parent_guard', OLD / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    parent = guard.verify('b28af91a974d3039aec4dae206d4dc8dc2007835f69adaee66b800e067da4c93')
    inherited = []
    for path in files(OLD):
        if path.suffix == '.py':
            assert tests(path) == tests(API / path.relative_to(OLD)), path
            inherited.extend(path.relative_to(OLD).as_posix() + ':' + name for name in tests(path))
    assert len(inherited) == 293
    assert len(tests(CHECK / 'test_host.py')) == 3
    for path in files(API) + files(CHECK) + files(LESSON):
        if path.suffix == '.py':
            ast.parse(path.read_bytes())
    assert load(PUB / 'receipts/checks-0001.json')['result'] == 'PASS'
    assert load(PUB / 'receipts/checks-0001.json')['real_filesystem_fixture_cases'] == 53
    readme = API / 'PACKAGE-IMPORT.md'
    with readme.open('x') as stream:
        stream.write('''# Candidate package import implementation

The actual authenticated operator dispatcher adds package.import with a distinct
independent policy. Its managed generation, source/target proposals, mapping,
disposition and provenance are selected before channel authentication. No caller
path or uploaded archive selects storage or grants permission. Package bytes stay
in managed storage; public controls and candidate evidence retain the original
1 MiB limits. Original source callbacks, clocks and prospective validators remain.

Preflight performs pure full original source/target validation in a discardable
buffer before a durable claim. Required resolved Work references and original
carrier schemas must be in the archive's declared graph. Retained artifacts must
match current signed-source original bytes. Complete accounting must agree with
exact target bytes and independent stable cores. After the claim, evaluation is
repeated and evidence commits only after original source exit checks. The returned
ChangeProposal retains exact package/mapping/disposition provenance and remains
unadmitted. Exact retries verify managed readback and use no writes or repair.

The implemented lane supports fully resolved Work candidates in the same current
target cut, with retained current dependency originals. Foreign/admitted-source
authority resolution and broader source/carrier portability remain explicit
unfinished obligations. Unsupported source posture/cut is refused. Public export
is still unimplemented. Candidate fixtures supply synthetic publication permission;
actual import uses the real one-use channel and signed target replay. Runtime
qualification requires this successor's own complete actual checks. General
import, all inherited journeys and the whole API are not qualified by authoring.

All 34 original public operation contracts and 293 inherited test methods remain.
The package policy allows eight metadata operations plus package.import; it grants
no Agent participation, Machine write authority, owner decision or activation.
Within this policy only, native candidate validation can read its immutable owned
workspace evidence objects, allowing exact import provenance to be retained.
The lesson host is separately rebound to API53 without changing its calculation.
''')
    static = RUN / 'API53-package-import-static-0001.json'
    emit(static, {'schema_version': 'lab-package-import-static/v1-candidate', 'result': 'PASS',
        'retained_original_operation_contracts': 34, 'retained_inherited_methods': 293,
        'selected_new_actual_cases': 3, 'authored_handlers': 19, 'missing_operations': 15,
        'actual_public_calls': 0, 'actual_runtime_qualified': False, 'whole_API_qualified': False,
        'scope': 'Actual candidate import policy/dispatcher/host authored; same-cut fully resolved Work lane only. General foreign/admitted-source import and export remain unfinished.',
        'authority_effect': 'none', 'actual_owner_outcome': None, 'task_complete': False})
    profile = load(OLD / 'contract-profile.json')
    profile['implemented_operations'].append('package.import')
    profile['files'] = [bind(API / (ROOT / row['path']).relative_to(OLD))
        if (ROOT / row['path']).is_relative_to(OLD) else row for row in profile['files']]
    extra = [bind(p) for p in files(API) if not (OLD / p.relative_to(API)).exists()]
    extra.extend(bind(p) for p in files(CHECK) + files(LESSON))
    publication = load(PUB / 'source-manifest.json')
    extra.extend(publication['files'] + publication['input_bindings'])
    extra.extend([bind(PUB / 'source-manifest.json'), bind(PUB / 'receipts/checks-0001.json'), bind(static)])
    profile_rows = {r['path']: r for r in profile['files'] + extra}
    profile['files'] = [profile_rows[k] for k in sorted(profile_rows)]
    profile['claim_ceiling'] = 'Nineteen authored handlers; same-cut candidate Work import authored with actual runtime checks pending. Fifteen operations, general package import/portable source export and whole API qualification remain incomplete.'
    emit(API / 'contract-profile.json', profile)
    rows = {r['path']: r for r in parent['files']}
    for row in extra:
        rows[row['path']] = row
    for path in files(API) + files(CHECK) + files(LESSON) + [OLD / 'source-manifest.json',
            API / 'contract-profile.json', RUN / 'authorization.json', Path(__file__).resolve()]:
        row = bind(path)
        rows[row['path']] = row
    for row in rows.values():
        assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
    emit(API / 'source-manifest.json', {**parent, 'files': [rows[k] for k in sorted(rows)],
        'parent_source_binding': bind(OLD / 'source-manifest.json'), 'retained_inherited_methods': inherited,
        'unchanged_inherited_method_count': 293, 'whole_API_qualified': False,
        'package_import_actual_runtime_qualified': False, 'package_general_import_qualified': False,
        'public_export_qualified': False, 'task_complete': False, 'goal_complete': False})
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(API / 'source-manifest.json'),
        'profile_binding': bind(API / 'contract-profile.json'), 'retained_original_methods': 293,
        'authored_handlers': 19, 'missing_operations': 15, 'actual_runtime_qualified': False}), flush=True)


if __name__ == '__main__':
    main()
