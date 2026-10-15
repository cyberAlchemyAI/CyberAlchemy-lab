"""Keep native dependencies explicit outside the repository-only profile reader."""
import ast
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-v77'
API = BASE / 'api-v78'


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
    assert not API.exists() and not (BASE / 'lesson-host-composition-v28').exists()
    spec = importlib.util.spec_from_file_location('_cal_API78_parent_guard', OLD / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    parent = guard.verify('c04febd484c4a18cd2e6140dbdde31c68ab848e9b9623117d8861eb696d00b81')
    terminal_path = RUN / 'API77-machine-lifecycle-full-terminal-0001.json'
    terminal = load(terminal_path)
    report_path = RUN / 'API77-machine-lifecycle-full-0001.json'
    report = load(report_path)
    assert terminal['actual_exit_code'] == 1 and terminal['report_binding'] == bind(report_path)
    assert report['actual_cases'] == report['completed_Machine_public_replies'] == 0 and report['errors'] == 2
    shutil.copytree(OLD, API, ignore=shutil.ignore_patterns('receipts', '__pycache__', 'source-manifest.json', 'contract-profile.json'))
    shutil.copytree(BASE / 'lesson-host-composition-v27', BASE / 'lesson-host-composition-v28',
                    ignore=shutil.ignore_patterns('receipts', '__pycache__'))
    host = BASE / 'lesson-host-composition-v28/host.py'
    host.write_text(host.read_text().replace('api-v77/service.py', 'api-v78/service.py'))
    lesson = API / 'lesson_selection.py'
    lesson.write_text(lesson.read_text().replace('lesson-host-composition-v27', 'lesson-host-composition-v28'))
    retained = []
    local = []
    for folder in [API, BASE / 'lesson-host-composition-v28']:
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
    externals = [row for row in profile['files'] if Path(row['path']).is_absolute()]
    execution = load(BASE / 'current-context-delivery-v9/EXECUTION-DEPENDENCIES.json')
    assert externals == execution['external_dependency_bindings'] and len(externals) == 1
    for row in externals:
        assert bind(Path(row['path'])) == row
    rows = {row['path']: row for row in profile['files'] if not Path(row['path']).is_absolute()}
    for row in list(rows.values()):
        path = ROOT / row['path']
        if path.is_relative_to(OLD):
            new = bind(API / path.relative_to(OLD))
            rows[new['path']] = new
    inputs = [Path(__file__).resolve(), terminal_path, report_path,
              RUN / 'API77-machine-lifecycle-full-0001.log', RUN / 'API77-machine-lifecycle-full-driver-0001.log',
              RUN / 'API77-independent-selection-0001.json', BASE / 'current-context-delivery-v9/EXECUTION-DEPENDENCIES.json']
    for row in local + [bind(path) for path in inputs]:
        rows[row['path']] = row
    # Exercise the unchanged repository reader on every prospective repository row.
    spec = importlib.util.spec_from_file_location('_cal_API78_repository_binding_reader', BASE / 'coupling/loader.py')
    repository = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(repository)
    for row in rows.values():
        repository.original(row)
    profile.update(files=[rows[key] for key in sorted(rows)],
                   external_execution_dependency_bindings=externals,
                   external_dependency_guard='API source guard and selected Context preflight retain exact native declaration and bytes.',
                   parent_failed_API_profile_binding=bind(OLD / 'contract-profile.json'))
    emit(API / 'contract-profile.json', profile)
    full = {row['path']: row for row in parent['files']}
    for row in [*rows.values(), *externals, bind(API / 'contract-profile.json'), bind(OLD / 'source-manifest.json')]:
        assert full.get(row['path'], row) == row, row['path']
        full[row['path']] = row
    for row in full.values():
        assert bind(ROOT / row['path']) == row, row['path']
    value = {**parent, 'files': [full[key] for key in sorted(full)],
             'parent_source_binding': bind(OLD / 'source-manifest.json'),
             'retained_inherited_methods': retained, 'unchanged_inherited_method_count': 323,
             'explicit_revised_methods': 0, 'binding_only_revised_methods': [],
             'repository_and_external_profile_bindings_separated': True,
             'native_executable_retained_in_full_source_guard': True,
             'prospective_repository_profile_guard_passed': True,
             'current_Agent_qualified': False, 'whole_API_qualified': False,
             'runtime_qualification_transferred': False, 'task_complete': False, 'goal_complete': False}
    emit(API / 'source-manifest.json', value)
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(API / 'source-manifest.json'),
                      'profile_binding': bind(API / 'contract-profile.json'), 'retained_methods': 323,
                      'guarded_external_native_dependencies': len(externals), 'runtime_qualified': False}), flush=True)


if __name__ == '__main__':
    main()
