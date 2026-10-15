"""Report the exact missing operation inventory without changing API contracts."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
PARENT, API = BASE / 'api-v49', BASE / 'api-v50'
SOURCE = '70a59c0f1c5cd96bedd523a024827a41e2b8f54f3ca0f6a685599ff4d6fe14aa'


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
    spec = importlib.util.spec_from_file_location('_cal_API50_parent_guard', PARENT / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    previous = guard.verify(SOURCE)
    catalog = ROOT / 'docs/proposals/0008-lab-api-contracts/api-contracts.json'
    declared = [row['operation'] for row in json.loads(catalog.read_bytes())['operations']]
    profile = json.loads((PARENT / 'contract-profile.json').read_bytes())
    supported = profile['implemented_operations']
    assert len(declared) == len(set(declared)) == 34 and len(supported) == 17
    assert set(supported) <= set(declared)
    missing = sorted(set(declared) - set(supported))
    assert len(missing) == 17 and 'lesson.select' in missing
    API.mkdir()
    (API / 'receipts').mkdir()
    for path in files(PARENT):
        target = API / path.relative_to(PARENT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
    path = API / 'handlers.py'
    text = path.read_text()
    old = "                '20 declared API operations remain unimplemented in this handler package; complete transaction journeys, final owner review and broader ontology/workflow integration remain required.'),"
    new = "                f\"{len(set(self.schemas.operations) - set(SUPPORTED))} declared API operations remain unimplemented in this handler package: {', '.join(sorted(set(self.schemas.operations) - set(SUPPORTED)))}. Complete transaction journeys, final owner review and broader ontology/workflow integration remain required.\"),"
    assert text.count(old) == 1
    path.write_text(text.replace(old, new))
    retained, changed = [], []
    for path in files(PARENT):
        target = API / path.relative_to(PARENT)
        if path.read_bytes() != target.read_bytes():
            changed.append(path.relative_to(PARENT).as_posix())
        if path.suffix == '.py':
            assert tests(path) == tests(target)
            retained.extend(path.relative_to(PARENT).as_posix() + ':' + name for name in tests(path))
    assert changed == ['handlers.py'] and len(retained) == 293
    context = RUN / 'context-R03-current-status-API-0050.json'
    emit(context, {'schema_version': 'lab-bounded-context/v1-candidate', 'strict_coverage': 'PASS', 'task': 'R03',
        'source_bindings': [binding(PARENT / 'source-manifest.json'), binding(catalog), binding(RUN / 'authorization.json')],
        'write_scope': API.relative_to(ROOT).as_posix(),
        'constraints': ['Report the exact selected contract inventory minus registered handlers; this does not establish runtime qualification.',
            'Original34 public schemas and293 original test methods remain byte/AST identical.',
            'Permission, source replay, real clocks, typed joins, journal and incomplete plan criteria remain unchanged.',
            'No public handler, owner disposition, Agent permission or operational grant is added by this correction.'],
        'authority_effect': 'none', 'actual_owner_outcome': None, 'task_complete': False})
    profile['files'] = [binding(API / (ROOT / row['path']).relative_to(PARENT)) if (ROOT / row['path']).is_relative_to(PARENT) else row
                        for row in profile['files']]
    profile['status_inventory_context_binding'] = binding(context)
    profile['claim_ceiling'] = 'Seventeen authored handlers; exact missing operation inventory is calculated. Actual full runtime and assigned Agent typed participation remain unqualified.'
    emit(API / 'contract-profile.json', profile)
    rows = {row['path']: row for row in previous['files']}
    for path in files(API) + [PARENT / 'source-manifest.json', context, API / 'contract-profile.json', Path(__file__).resolve()]:
        row = binding(path)
        rows[row['path']] = row
    for row in rows.values():
        assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256']
    emit(API / 'source-manifest.json', {**previous, 'files': [rows[key] for key in sorted(rows)],
        'parent_source_binding': binding(PARENT / 'source-manifest.json'), 'context_binding': binding(context),
        'retained_inherited_methods': retained, 'unchanged_inherited_method_count': 293,
        'whole_API_qualified': False, 'current_Agent_qualified': False, 'task_complete': False, 'goal_complete': False})
    emit(RUN / 'API50-status-inventory-static-0001.json', {
        'schema_version': 'lab-static-operation-inventory/v1-candidate', 'result': 'PASS',
        'source_binding': binding(API / 'source-manifest.json'), 'profile_binding': binding(API / 'contract-profile.json'),
        'original_catalog_binding': binding(catalog), 'declared_operations': declared,
        'authored_handler_operations': supported, 'unimplemented_operations': missing,
        'declared_count': 34, 'authored_count': 17, 'unimplemented_count': 17,
        'retained_original_test_methods': 293, 'only_changed_API_file': 'handlers.py',
        'actual_public_calls': 0, 'runtime_qualified': False, 'authority_effect': 'none', 'task_complete': False})
    print(json.dumps({'result': 'FROZEN', 'source_binding': binding(API / 'source-manifest.json'),
        'profile_binding': binding(API / 'contract-profile.json'), 'authored_handlers': 17,
        'original_methods_retained': 293, 'unimplemented_count': len(missing)}), flush=True)


if __name__ == '__main__':
    main()
