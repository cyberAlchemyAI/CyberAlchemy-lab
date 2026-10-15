"""Freeze exact fresh Context selection without transferring predecessor runtime claims."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-v75'
API = BASE / 'api-v77'
CONTEXT = BASE / 'current-context-delivery-v9'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def load(path):
    return json.loads(path.read_bytes())


def emit(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def methods(text):
    return {n.name: ast.dump(n, include_attributes=False) for n in ast.walk(ast.parse(text))
            if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}


def main():
    context_proof = CONTEXT / 'receipts/qualification-0001.json'
    qualification = load(context_proof)
    assert qualification['result'] == 'PASS' and qualification['selected_methods'] == 50
    assert qualification['actual_build_exit_code'] == qualification['actual_check_exit_code'] == qualification['actual_audit_exit_code'] == 0
    spec = importlib.util.spec_from_file_location('_cal_API77_parent_guard', OLD / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    parent = guard.verify('35c97975fe0be4541d6a87f0881b60c11991746b8b3e661ccbbd81c34aaa4b20')
    first = load(RUN / 'API76-fresh-binding-revision-0001.json')
    second = load(RUN / 'API77-current-binding-revision-0001.json')
    changes = {**first['replacements'], **second['changes']}
    # Compose the lesson-host selection through both preserved drafts.
    changes['lesson-host-composition-v25'] = 'lesson-host-composition-v27'
    unchanged, revised = [], []
    local = []
    for folder in [API, BASE / 'lesson-host-composition-v27']:
        for path in sorted(folder.rglob('*')):
            if not path.is_file() or {'receipts', '__pycache__'} & set(path.parts):
                continue
            if path.name in ['source-manifest.json', 'contract-profile.json']:
                continue
            if path.suffix == '.py':
                ast.parse(path.read_bytes())
                if folder == API:
                    original = (OLD / path.relative_to(API)).read_text()
                    normalized = original
                    for before, after in changes.items():
                        normalized = normalized.replace(before, after)
                    expected, actual = methods(normalized), methods(path.read_text())
                    assert expected == actual, path
                    old = methods(original)
                    for name in old:
                        ref = path.relative_to(API).as_posix() + ':' + name
                        (unchanged if old[name] == actual[name] else revised).append(ref)
            local.append(bind(path))
    assert len(unchanged) + len(revised) == 323
    profile = load(OLD / 'contract-profile.json')
    assert len(profile['implemented_operations']) == 21
    catalog = load(ROOT / profile['original_operation_catalog_binding']['path'])
    assert len(catalog['operations']) == 34
    rows = {row['path']: row for row in profile['files']}
    def add(row):
        assert rows.get(row['path'], row) == row, row['path']
        assert bind(ROOT / row['path']) == row, row['path']
        rows[row['path']] = row
    for row in list(rows.values()):
        path = ROOT / row['path']
        if path.is_relative_to(OLD):
            add(bind(API / path.relative_to(OLD)))
    for row in load(CONTEXT / 'EXECUTION-DEPENDENCIES.json')['files']:
        add(row)
    inputs = [context_proof, CONTEXT / 'source-manifest.json', CONTEXT / 'packages/0001/manifest.json',
              CONTEXT / 'EXECUTION-DEPENDENCIES.json', RUN / 'authorization.json',
              RUN / 'API76-fresh-binding-revision-0001.json', RUN / 'API77-current-binding-revision-0001.json',
              RUN / 'author-API76-fresh-context-selection-0001.py', RUN / 'author-API77-current-assertion-bindings-0001.py',
              RUN / 'qualify-API77-machine-lifecycle-full-0001.py', Path(__file__).resolve()]
    for row in local + [bind(path) for path in inputs]:
        add(row)
    profile.update(files=[rows[key] for key in sorted(rows)],
                   qualified_context_proof_binding=bind(context_proof),
                   selected_current_context_source_binding=bind(CONTEXT / 'source-manifest.json'),
                   selected_current_context_package_binding=bind(CONTEXT / 'packages/0001/manifest.json'),
                   fresh_source_selection_revision_binding=bind(RUN / 'API77-current-binding-revision-0001.json'),
                   claim_ceiling='Twenty-one authored handlers. Current API/Machine/lifecycle qualification required under exact fresh source and Context bindings; no runtime qualification transfer.')
    emit(API / 'contract-profile.json', profile)
    full = {row['path']: row for row in parent['files']}
    for row in [*qualification['files'], *rows.values(), bind(context_proof), bind(API / 'contract-profile.json'), bind(OLD / 'source-manifest.json')]:
        assert full.get(row['path'], row) == row, row['path']
        full[row['path']] = row
    for row in full.values():
        assert bind(ROOT / row['path']) == row, row['path']
    source = {**parent, 'files': [full[key] for key in sorted(full)],
              'parent_source_binding': bind(OLD / 'source-manifest.json'),
              'qualified_context_proof_binding': bind(context_proof),
              'retained_inherited_methods': unchanged + revised,
              'unchanged_inherited_method_count': len(unchanged), 'explicit_revised_methods': len(revised),
              'binding_only_revised_methods': revised, 'total_retained_method_bodies': 323,
              'authored_handler_count': 21, 'qualified_public_handler_count': 0,
              'remaining_qualified_operations': 34, 'original_contracts_preserved': 34,
              'whole_API_qualified': False, 'current_Agent_qualified': False,
              'fresh_context_selected': True, 'runtime_qualification_transferred': False,
              'fresh_binding_revision': bind(RUN / 'API77-current-binding-revision-0001.json'),
              'task_complete': False, 'goal_complete': False}
    for key in source:
        if key.endswith('_actual_runtime_qualified'):
            source[key] = False
    emit(API / 'source-manifest.json', source)
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(API / 'source-manifest.json'),
                      'profile_binding': bind(API / 'contract-profile.json'), 'original_contracts': 34,
                      'authored_handlers': 21, 'unimplemented_operations': 13,
                      'retained_methods': 323, 'unchanged_methods': len(unchanged),
                      'exact_binding_revised_methods': len(revised), 'runtime_qualified': False}), flush=True)


if __name__ == '__main__':
    main()
