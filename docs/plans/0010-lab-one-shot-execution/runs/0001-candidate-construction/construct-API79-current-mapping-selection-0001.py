"""Rebind the native package digest to the independently qualified current mapper."""
import ast
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-v78'
API = BASE / 'api-v79'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def load(path):
    return json.loads(path.read_bytes())


def emit(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def methods(path):
    return {n.name: ast.dump(n, include_attributes=False) for n in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}


def main():
    assert not API.exists() and not (BASE / 'lesson-host-composition-v29').exists()
    diagnosis_path = RUN / 'API78-mapping-pin-diagnosis-0001.json'
    diagnosis = load(diagnosis_path)
    assert diagnosis['result'] == 'PASS' and diagnosis['original_stale_pin_refused'] and diagnosis['original_current_pin_cold_replay_passed']
    mapper = BASE / 'current-mapped-context-v4/qualification-0001.json'
    assert load(mapper)['result'] == 'PASS' and load(mapper)['package_binding'] == diagnosis['actual_current_package_binding']
    spec = importlib.util.spec_from_file_location('_cal_API79_parent_guard', OLD / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    parent = guard.verify('c8088066e55dc97e6762d87d5cb1ba4fcfc18fcfa8ccb15bd2e3607ca8a17243')
    shutil.copytree(OLD, API, ignore=shutil.ignore_patterns('receipts', '__pycache__', 'source-manifest.json', 'contract-profile.json'))
    shutil.copytree(BASE / 'lesson-host-composition-v28', BASE / 'lesson-host-composition-v29', ignore=shutil.ignore_patterns('receipts', '__pycache__'))
    bridge = API / 'custody_context_sessions.py'
    text = bridge.read_text()
    old = "MAPPING_PIN='" + diagnosis['stale_declared_package_sha256'] + "'"
    assert text.count(old) == 1
    bridge.write_text(text.replace(old, "MAPPING_PIN='" + diagnosis['actual_current_package_binding']['sha256'] + "'"))
    host = BASE / 'lesson-host-composition-v29/host.py'
    host.write_text(host.read_text().replace('api-v78/service.py', 'api-v79/service.py'))
    lesson = API / 'lesson_selection.py'
    lesson.write_text(lesson.read_text().replace('lesson-host-composition-v28', 'lesson-host-composition-v29'))
    local = []
    retained = []
    for folder in [API, BASE / 'lesson-host-composition-v29']:
        for path in sorted(folder.rglob('*')):
            if not path.is_file() or '__pycache__' in path.parts:
                continue
            if path.suffix == '.py':
                ast.parse(path.read_bytes())
                if folder == API:
                    assert methods(path) == methods(OLD / path.relative_to(API)), path
                    retained += [path.relative_to(API).as_posix() + ':' + name for name in methods(path)]
            local.append(bind(path))
    assert len(retained) == 323
    profile = load(OLD / 'contract-profile.json')
    rows = {row['path']: row for row in profile['files']}
    for row in list(rows.values()):
        path = ROOT / row['path']
        if path.is_relative_to(OLD):
            new = bind(API / path.relative_to(OLD))
            rows[new['path']] = new
    inputs = [Path(__file__).resolve(), diagnosis_path, RUN / 'diagnose-API78-mapping-pin-0001.py', mapper]
    for row in local + [bind(path) for path in inputs] + [o['binding'] for o in diagnosis['public_failure_observations']]:
        assert rows.get(row['path'], row) == row, row['path']
        rows[row['path']] = row
    spec = importlib.util.spec_from_file_location('_cal_API79_repository_binding_reader', BASE / 'coupling/loader.py')
    repository = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(repository)
    for row in rows.values():
        repository.original(row)
    profile.update(files=[rows[key] for key in sorted(rows)],
                   current_mapping_package_binding=diagnosis['actual_current_package_binding'],
                   native_mapping_selection_diagnosis_binding=bind(diagnosis_path))
    emit(API / 'contract-profile.json', profile)
    full = {row['path']: row for row in parent['files']}
    for row in [*rows.values(), bind(API / 'contract-profile.json'), bind(OLD / 'source-manifest.json')]:
        assert full.get(row['path'], row) == row, row['path']
        full[row['path']] = row
    for row in full.values():
        assert bind(ROOT / row['path']) == row, row['path']
    value = {**parent, 'files': [full[key] for key in sorted(full)],
             'parent_source_binding': bind(OLD / 'source-manifest.json'),
             'retained_inherited_methods': retained, 'unchanged_inherited_method_count': 323,
             'explicit_revised_methods': 0, 'binding_only_revised_methods': [],
             'current_mapping_package_binding': diagnosis['actual_current_package_binding'],
             'native_mapping_selection_diagnosis_binding': bind(diagnosis_path),
             'source_callbacks_replaced': False, 'permissions_cached': False, 'time_bounds_extended': False,
             'current_Agent_qualified': False, 'whole_API_qualified': False,
             'runtime_qualification_transferred': False, 'task_complete': False, 'goal_complete': False}
    emit(API / 'source-manifest.json', value)
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(API / 'source-manifest.json'),
                      'profile_binding': bind(API / 'contract-profile.json'), 'retained_methods': 323,
                      'current_mapping_package_binding': diagnosis['actual_current_package_binding'],
                      'runtime_qualified': False}), flush=True)


if __name__ == '__main__':
    main()
