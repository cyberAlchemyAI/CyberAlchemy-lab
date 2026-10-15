"""Freeze the live application composition; transfer no runtime qualification."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-v82'
API = BASE / 'api-v83'
ADAPTER = BASE / 'lesson-application-v2'


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
    return {node.name: ast.dump(node, include_attributes=False) for node in ast.walk(ast.parse(path.read_text()))
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')}


def main():
    spec = importlib.util.spec_from_file_location('_cal_API83_parent_guard', OLD / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    parent = guard.verify('0b643269ba41067d62f7d6e6a6affd263cde5e26d82f99a486741b2c502f040d')
    retained, local = [], []
    for folder in [API, ADAPTER, BASE / 'lesson-host-composition-v33']:
        for path in sorted(folder.rglob('*')):
            if not path.is_file() or {'receipts', '__pycache__'} & set(path.parts):continue
            if path.name in ('source-manifest.json', 'contract-profile.json'):continue
            if path.suffix == '.py':
                ast.parse(path.read_text())
                old_path = OLD / path.relative_to(API) if folder == API else None
                if old_path is not None and old_path.exists():
                    assert methods(old_path) == methods(path), path
                    retained.extend(path.relative_to(API).as_posix() + ':' + name for name in methods(path))
            local.append(bind(path))
    assert len(retained) == 323
    source_paths = [OLD / 'source-manifest.json', OLD / 'auth.py', OLD / 'authentication.schema.json',
                    BASE / 'lesson-application-v1/preparation.py', ADAPTER / 'DESIGN.md',
                    ROOT / 'docs/proposals/0008-lab-api-contracts/operations/lesson.apply.json',
                    ROOT / 'docs/proposals/0007-lab-integrated-schema-package/schemas/lesson-application-request.schema.json',
                    ROOT / 'authority/artifact-types/lesson-application/v1/schema.json',
                    RUN / 'API82-application-context-clarification-0001.json', RUN / 'authorization.json',
                    RUN / 'author-API83-live-application-composition-0001.py', Path(__file__).resolve()]
    context = RUN / 'context-R03-live-application-composition-0083.json'
    emit(context, {'schema_version': 'lab-bounded-context/v1-candidate', 'task': 'R03 application/current Session composition',
                   'source_bindings': [bind(path) for path in source_paths],
                   'constraints': ['Private v2 policy composes original participation, actual operator, source period and exact application method.',
                                   'Declared future identities create no resources; actual original eligibility precedes durable one-use reservation and RAM allocation.',
                                   'Original real clocks, 900-second ceiling, disposal, source guards and all323 inherited test ASTs remain.',
                                   'Original public application contract and handler count23 remain;11 original operations are still missing.',
                                   'Positive application/outcome/full API qualification and sole final admission checkpoint remain pending.'],
                   'runtime_qualified': False, 'actual_owner_outcome': None, 'authority_effect': 'none'})
    profile = load(OLD / 'contract-profile.json')
    assert len(profile['implemented_operations']) == 23
    rows = {row['path']: row for row in profile['files']}
    for row in list(rows.values()):
        path = ROOT / row['path']
        if path.is_relative_to(OLD):rows[bind(API / path.relative_to(OLD))['path']] = bind(API / path.relative_to(OLD))
    for row in local + [bind(path) for path in [*source_paths, context]]:
        assert rows.get(row['path'], row) == row, row['path']
        rows[row['path']] = row
    for row in rows.values():assert not Path(row['path']).is_absolute() and bind(ROOT / row['path']) == row
    profile.update(files=[rows[key] for key in sorted(rows)], lesson_application_context_binding=bind(context),
                   lesson_application_method_binding=bind(ADAPTER / 'preparation.py'),
                   claim_ceiling='23 authored handlers; current Session/application composition repaired. Actual application and full API qualification remain pending.')
    emit(API / 'contract-profile.json', profile)
    full = {row['path']: row for row in parent['files']}
    for row in [*rows.values(), bind(API / 'contract-profile.json'), bind(OLD / 'source-manifest.json')]:
        assert full.get(row['path'], row) == row, row['path']
        full[row['path']] = row
    for row in full.values():assert bind(ROOT / row['path']) == row
    value = {**parent, 'files': [full[key] for key in sorted(full)],
             'parent_source_binding': bind(OLD / 'source-manifest.json'), 'retained_inherited_methods': retained,
             'unchanged_inherited_method_count': 323, 'explicit_revised_methods': 0, 'binding_only_revised_methods': [],
             'authored_handler_count': 23, 'lesson_application_context_binding': bind(context),
             'lesson_application_method_binding': bind(ADAPTER / 'preparation.py'),
             'lesson_apply_actual_runtime_qualified': False, 'lesson_assess_actual_runtime_qualified': False,
             'current_Agent_qualified': False, 'whole_API_qualified': False, 'runtime_qualification_transferred': False,
             'task_complete': False, 'goal_complete': False}
    emit(API / 'source-manifest.json', value)
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(API / 'source-manifest.json'),
                      'profile_binding': bind(API / 'contract-profile.json'), 'retained_unchanged_methods': 323,
                      'authored_handlers': 23, 'remaining_handlers': 11, 'runtime_qualified': False}), flush=True)


if __name__ == '__main__':main()
