"""Extend the existing guarded model scope across complete derived reads."""
import ast
import copy
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-v79'
API = BASE / 'api-v80'


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


def unchanged_calculation(old_path, new_path, old_name, new_name):
    before = next(n for n in ast.walk(ast.parse(old_path.read_bytes())) if isinstance(n, ast.FunctionDef) and n.name == old_name)
    after = copy.deepcopy(next(n for n in ast.walk(ast.parse(new_path.read_bytes())) if isinstance(n, ast.FunctionDef) and n.name == new_name))
    after.name = old_name
    assert ast.dump(before, include_attributes=False) == ast.dump(after, include_attributes=False)


def main():
    assert not API.exists() and not (BASE / 'lesson-host-composition-v30').exists()
    spec = importlib.util.spec_from_file_location('_cal_API80_parent_guard', OLD / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    parent = guard.verify('c3c45bc13e5389771c5fb0df178d8ed5d39fdb48af6d3fdf88ebb60d32d34792')
    assert load(RUN / 'API79-component-binding-checks-0001.json')['result'] == 'PASS'
    shutil.copytree(OLD, API, ignore=shutil.ignore_patterns('receipts', '__pycache__', 'source-manifest.json', 'contract-profile.json'))
    shutil.copytree(BASE / 'lesson-host-composition-v29', BASE / 'lesson-host-composition-v30', ignore=shutil.ignore_patterns('receipts', '__pycache__'))
    host = BASE / 'lesson-host-composition-v30/host.py'
    host.write_text(host.read_text().replace('api-v79/service.py', 'api-v80/service.py'))
    lesson = API / 'lesson_selection.py'
    lesson.write_text(lesson.read_text().replace('lesson-host-composition-v29', 'lesson-host-composition-v30'))
    path = API / 'artifact_model.py'
    original = 'def connections(view,schemas):\n'
    assert path.read_text().count(original) == 1
    path.write_text(path.read_text().replace(original,
        'def connections(view,schemas):\n'
        '    with model_read_batch(view):\n'
        '        return _connections(view,schemas)\n\n\n'
        'def _connections(view,schemas):\n'))
    path = API / 'handlers.py'
    original = '    def query(self,message,request_binding,outer):\n'
    assert path.read_text().count(original) == 1
    path.write_text(path.read_text().replace(original,
        '    def query(self,message,request_binding,outer):\n'
        '        # Select the exact requested prefix for the original guarded scope.\n'
        '        # The original calculation still performs its own cut/freshness checks.\n'
        "        matches=[view for view in self.available_views if cut(view)==message['source_cut']]\n"
        '        if len(matches)!=1:\n'
        '            return self._query(message,request_binding,outer)\n'
        '        with model.model_read_batch(matches[0]):\n'
        '            return self._query(message,request_binding,outer)\n\n'
        '    def _query(self,message,request_binding,outer):\n'))
    unchanged_calculation(OLD / 'artifact_model.py', API / 'artifact_model.py', 'connections', '_connections')
    unchanged_calculation(OLD / 'handlers.py', API / 'handlers.py', 'query', '_query')
    assert (API / 'guarded_reads.py').read_bytes() == (OLD / 'guarded_reads.py').read_bytes()
    local = []
    retained = []
    for folder in [API, BASE / 'lesson-host-composition-v30']:
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
    context_path = RUN / 'context-R03-complete-model-read-scope-0080.json'
    emit(context_path, {'schema_version': 'lab-bounded-context/v1-candidate', 'task': 'R03 complete guarded model reads',
                        'strict_coverage': 'PASS', 'blockers': [],
                        'source_bindings': [bind(OLD / 'source-manifest.json'), bind(OLD / 'guarded_reads.py'),
                                            bind(OLD / 'artifact_model.py'), bind(OLD / 'handlers.py'),
                                            bind(RUN / 'API79-component-binding-checks-0001.json'), bind(RUN / 'authorization.json')],
                        'constraints': ['Existing model_read_batch and both complete calculation ASTs retained.',
                                        'Actual requested current/historical prefix remains independently validated.',
                                        'Full source, model identity, original byte/schema callbacks and unchanged fact stamp verified at scope entry/exit.',
                                        'No original callback replacement, body/permission cache or clock/deadline extension.',
                                        'All323 inherited method ASTs unchanged; original full integration/lifecycle qualification still required.'],
                        'authority_effect': 'none', 'actual_owner_outcome': None, 'runtime_qualified': False})
    profile = load(OLD / 'contract-profile.json')
    rows = {row['path']: row for row in profile['files']}
    for row in list(rows.values()):
        path = ROOT / row['path']
        if path.is_relative_to(OLD):
            new = bind(API / path.relative_to(OLD))
            rows[new['path']] = new
    for row in local + [bind(Path(__file__).resolve()), bind(context_path)]:
        assert rows.get(row['path'], row) == row, row['path']
        rows[row['path']] = row
    for row in rows.values():
        assert not Path(row['path']).is_absolute() and bind(ROOT / row['path']) == row
    profile.update(files=[rows[key] for key in sorted(rows)],
                   complete_model_read_scope_context_binding=bind(context_path))
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
             'original_complete_query_calculation_AST_retained': True,
             'original_complete_connection_calculation_AST_retained': True,
             'original_guarded_reads_module_unchanged': True,
             'complete_model_read_scope_context_binding': bind(context_path),
             'source_callbacks_replaced': False, 'permissions_cached': False, 'time_bounds_extended': False,
             'current_Agent_qualified': False, 'whole_API_qualified': False,
             'runtime_qualification_transferred': False, 'task_complete': False, 'goal_complete': False}
    emit(API / 'source-manifest.json', value)
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(API / 'source-manifest.json'),
                      'profile_binding': bind(API / 'contract-profile.json'), 'retained_methods': 323,
                      'original_query_and_connection_calculations_preserved': True, 'runtime_qualified': False}), flush=True)


if __name__ == '__main__':
    main()
