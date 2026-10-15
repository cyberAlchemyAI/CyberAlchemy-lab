"""Freeze candidate assessment implementation without inheriting runtime claims."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-v81'
API = BASE / 'api-v82'
ADAPTER = BASE / 'lesson-application-v1'


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
    spec = importlib.util.spec_from_file_location('_cal_API82_parent_guard', OLD / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    parent = guard.verify('336f1f8f14ef13fd9634dc0e85aeeef7eff02dfe103da2c092ad0b902ec83ba8')
    unchanged, revised = [], []
    local = []
    for folder in [API, ADAPTER, BASE / 'lesson-host-composition-v32']:
        for path in sorted(folder.rglob('*')):
            if not path.is_file() or {'receipts', '__pycache__'} & set(path.parts):
                continue
            if path.name in ['source-manifest.json', 'contract-profile.json']:
                continue
            if path.suffix == '.py':
                text = path.read_text()
                ast.parse(text)
                old_path = OLD / path.relative_to(API) if folder == API else None
                if old_path is not None and old_path.exists():
                    before = methods(old_path.read_text())
                    actual = methods(text)
                    expected = methods(old_path.read_text().replace('self.assertEqual(len(SUPPORTED),22)', 'self.assertEqual(len(SUPPORTED),23)'))
                    assert expected == actual, path
                    for name in before:
                        ref = path.relative_to(API).as_posix() + ':' + name
                        (unchanged if before[name] == actual[name] else revised).append(ref)
            local.append(bind(path))
    assert len(unchanged) + len(revised) == 323
    assert len(revised) == 3
    context = RUN / 'context-R03-lesson-application-0082.json'
    source_paths = [OLD / 'source-manifest.json', ROOT / 'docs/proposals/0008-lab-api-contracts/operations/lesson.apply.json',
                    ROOT / 'docs/proposals/0007-lab-integrated-schema-package/schemas/lesson-application-request.schema.json',
                    ROOT / 'authority/artifact-types/lesson-outcome-assessment/v1/schema.json',
                    ADAPTER / 'preparation.py', RUN / 'authorization.json', RUN / 'author-API82-lesson-application-0001.py', Path(__file__).resolve()]
    emit(context, {'schema_version': 'lab-bounded-context/v1-candidate', 'task': 'R03 original lesson.apply adapter',
                   'strict_coverage': 'PASS', 'blockers': [], 'source_bindings': [bind(path) for path in source_paths],
                   'constraints': ['Actual live parent Session, exact current Lesson, original selection/applicability/instruction and prospective target/core validation required.',
                                   'Conflicts/overrides, actual delegated action bounds and attributed application preparation remain distinct from tool dispatch and effectiveness.',
                                   'This operation prepares an application record only; no tool dispatch, general efficacy, admission or activation occurs.',
                                   'Current Actor, source cut, private routing, original JCS/journal/retry/deadline and source exit checks remain.',
                                   'All323 predecessor methods retained; only3 exact current supported-handler count expectations change21to22.',
                                   'Original public contract unchanged; candidate runtime qualification remains pending.'],
                   'runtime_qualified': False, 'actual_owner_outcome': None, 'authority_effect': 'none'})
    profile = load(OLD / 'contract-profile.json')
    profile['implemented_operations'].append('lesson.apply')
    assert len(profile['implemented_operations']) == 23
    rows = {row['path']: row for row in profile['files']}
    for row in list(rows.values()):
        path = ROOT / row['path']
        if path.is_relative_to(OLD):
            new = bind(API / path.relative_to(OLD))
            rows[new['path']] = new
    for row in local + [bind(path) for path in [*source_paths, context]]:
        assert rows.get(row['path'], row) == row, row['path']
        rows[row['path']] = row
    for row in rows.values():
        assert not Path(row['path']).is_absolute() and bind(ROOT / row['path']) == row
    profile.update(files=[rows[key] for key in sorted(rows)], lesson_application_context_binding=bind(context),
                   lesson_application_method_binding=bind(ADAPTER / 'preparation.py'),
                   claim_ceiling='Twenty-three authored handlers; selected lesson.apply actual live Session/application correspondence and affected inherited runtime qualification remain required. No complete API or governing authority.')
    emit(API / 'contract-profile.json', profile)
    full = {row['path']: row for row in parent['files']}
    for row in [*rows.values(), bind(API / 'contract-profile.json'), bind(OLD / 'source-manifest.json')]:
        assert full.get(row['path'], row) == row, row['path']
        full[row['path']] = row
    for row in full.values():
        assert bind(ROOT / row['path']) == row, row['path']
    value = {**parent, 'files': [full[key] for key in sorted(full)],
             'parent_source_binding': bind(OLD / 'source-manifest.json'), 'retained_inherited_methods': unchanged + revised,
             'unchanged_inherited_method_count': len(unchanged), 'explicit_revised_methods': len(revised),
             'binding_only_revised_methods': revised, 'authored_handler_count': 23,
             'lesson_application_context_binding': bind(context), 'lesson_application_method_binding': bind(ADAPTER / 'preparation.py'),
             'lesson_assess_actual_runtime_qualified': False, 'current_Agent_qualified': False,
             'whole_API_qualified': False, 'runtime_qualification_transferred': False,
             'task_complete': False, 'goal_complete': False}
    emit(API / 'source-manifest.json', value)
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(API / 'source-manifest.json'),
                      'profile_binding': bind(API / 'contract-profile.json'), 'authored_handlers': 23,
                      'missing_operations': 11, 'retained_methods': 323, 'unchanged_methods': len(unchanged),
                      'current_registry_count_expectations_revised': len(revised), 'runtime_qualified': False}), flush=True)


if __name__ == '__main__':
    main()
