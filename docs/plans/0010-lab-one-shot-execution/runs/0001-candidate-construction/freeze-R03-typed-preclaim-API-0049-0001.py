"""Select qualified pure preclaim joins without changing original public contracts."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
PARENT, API = BASE / 'api-v48', BASE / 'api-v49'
HOST = BASE / 'typed-host-composition-v4'
SOURCE = 'a7329574c52004e476fd822da9177375a484ffc380e27c84f437ffc8f66d08e6'
HOST_SOURCE = '76d5226e365b6f71b5e220f00e12c5758298033781ae1a2dcd730d61b5239ebd'


def binding(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def emit(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')


def files(path):
    return [p for p in path.rglob('*') if p.is_file() and not {'receipts', '__pycache__'} & set(p.parts)
            and p.name not in ('source-manifest.json', 'contract-profile.json')]


def tests(path):
    return {node.name: ast.dump(node, include_attributes=False) for node in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')}


def main():
    assert not API.exists()
    assert binding(HOST / 'source-manifest.json')['sha256'] == HOST_SOURCE
    check = json.loads((RUN / 'typed-preclaim-join-checks-0001.json').read_bytes())
    assert check['result'] == 'PASS' and check['actual_cases'] == 41 and check['actual_public_calls'] == 0
    proof = json.loads((RUN / 'API48-typed-binding-join-checks-0001.json').read_bytes())
    assert proof['result'] == 'PASS' and proof['actual_cases'] == 6
    spec = importlib.util.spec_from_file_location('_cal_API49_parent_guard', PARENT / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    previous = guard.verify(SOURCE)
    API.mkdir()
    (API / 'receipts').mkdir()
    for path in files(PARENT):
        target = API / path.relative_to(PARENT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
    path = API / 'typed_preparation.py'
    text = path.read_text()
    assert text.count("'typed-host-composition-v3'") == 1
    path.write_text(text.replace("'typed-host-composition-v3'", "'typed-host-composition-v4'")
                   .replace('_typed_preparation_v3', '_typed_preparation_v4'))
    changed, retained = [], []
    for path in files(PARENT):
        target = API / path.relative_to(PARENT)
        if path.read_bytes() != target.read_bytes():
            changed.append(path.relative_to(PARENT).as_posix())
        if path.suffix == '.py':
            assert tests(path) == tests(target)
            retained.extend(path.relative_to(PARENT).as_posix() + ':' + name for name in tests(path))
    assert changed == ['typed_preparation.py'] and len(retained) == 293
    context = RUN / 'context-R03-typed-preclaim-API-0049.json'
    emit(context, {'schema_version': 'lab-bounded-context/v1-candidate', 'strict_coverage': 'PASS',
        'task': 'R03 refuse exact typed identity contradictions before candidate claim',
        'source_bindings': [binding(PARENT / 'source-manifest.json'), binding(HOST / 'source-manifest.json'),
                           binding(RUN / 'typed-preclaim-join-checks-0001.json'),
                           binding(RUN / 'API48-typed-binding-join-checks-0001.json'), binding(RUN / 'authorization.json')],
        'write_scope': API.relative_to(ROOT).as_posix(),
        'constraints': ['Original34 public schemas and293 original test methods remain unchanged.',
            'Only typed composition loader selection changes in the API source.',
            'Keep every original wire/noncollapse/schema/core/postimage/source predicate after the early join.',
            'Actor, actual permission, real clocks, incomplete core uncertainty and original journal remain.',
            'Assigned Agent, operational grants and genuine owner outcomes remain unqualified.'],
        'actual_owner_outcome': None, 'authority_effect': 'none', 'task_complete': False})
    profile = json.loads((PARENT / 'contract-profile.json').read_bytes())
    profile['files'] = [binding(API / (ROOT / row['path']).relative_to(PARENT)) if (ROOT / row['path']).is_relative_to(PARENT) else row
                        for row in profile['files']]
    assert len(profile['implemented_operations']) == 17
    profile['typed_composition_context_binding'] = binding(context)
    profile['typed_composition_source_binding'] = binding(HOST / 'source-manifest.json')
    profile['claim_ceiling'] = 'Seventeen authored handlers. Pure preclaim identity joins qualified; actual full runtime and assigned Agent typed participation remain unqualified.'
    emit(API / 'contract-profile.json', profile)
    host = json.loads((HOST / 'source-manifest.json').read_bytes())
    rows = {row['path']: row for row in previous['files'] + host['files'] + host['input_bindings']}
    for path in files(API) + [PARENT / 'source-manifest.json', HOST / 'source-manifest.json', context,
        API / 'contract-profile.json', RUN / 'typed-preclaim-join-checks-0001.json',
        RUN / 'typed-preclaim-join-checks-0001.log', RUN / 'API48-typed-binding-join-checks-0001.json',
        RUN / 'API48-typed-binding-join-checks-0001.log', Path(__file__).resolve()]:
        row = binding(path)
        rows[row['path']] = row
    for row in rows.values():
        assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256']
    emit(API / 'source-manifest.json', {**previous, 'files': [rows[key] for key in sorted(rows)],
        'parent_source_binding': binding(PARENT / 'source-manifest.json'), 'context_binding': binding(context),
        'typed_composition_source_binding': binding(HOST / 'source-manifest.json'),
        'retained_inherited_methods': retained, 'unchanged_inherited_method_count': 293,
        'whole_API_qualified': False, 'current_Agent_qualified': False, 'task_complete': False, 'goal_complete': False})
    print(json.dumps({'result': 'FROZEN', 'source_binding': binding(API / 'source-manifest.json'),
        'profile_binding': binding(API / 'contract-profile.json'), 'authored_handlers': 17,
        'original_methods_retained': 293, 'only_API_file_changed': 'typed_preparation.py'}), flush=True)


if __name__ == '__main__':
    main()
