"""Finish the unsealed API48 after retaining the failed external-path verifier.

The original helper's exact manifest intentionally pins neighboring migration
source files. Verify declared paths and hashes without rewriting their identities.
The frozen v2 composition remains intact; v3 is an exclusive successor.
"""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
API, PARENT = BASE / 'api-v48', BASE / 'api-v47'
OLD, NEW = BASE / 'typed-host-composition-v2', BASE / 'typed-host-composition-v3'
PIN = '666fcd2bc4f0e77b257a26915d26aab8083a8ac6c252dd9bc0f259a7ede80c62'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)}


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')


def files(path):
    return [p for p in path.rglob('*') if p.is_file()
            and not {'receipts', '__pycache__'} & set(p.parts)
            and p.name not in ('source-manifest.json', 'contract-profile.json')]


def main():
    assert not NEW.exists() and not (API / 'source-manifest.json').exists()
    failure = RUN / 'API48-freeze-attempt-0001-terminal.json'
    put(failure, {'schema_version': 'lab-builder-terminal/v1-candidate', 'actual_exit_code': 1,
        'session_id': 59768, 'final_tool_chunk': '81e36d', 'result': 'FAIL',
        'reason': 'Final manifest iteration used relative_to(ROOT) for already declared exact external source paths.',
        'API_source_manifest_published': False, 'frozen_composition_preserved': bind(OLD / 'source-manifest.json'),
        'script_binding': bind(RUN / 'freeze-R03-typed-host-API-0048-0001.py'),
        'actual_owner_outcome': None, 'authority_effect': 'none', 'task_complete': False})
    previous = json.loads((OLD / 'source-manifest.json').read_bytes())
    for row in previous['files'] + previous['input_bindings']:
        assert sha(ROOT / row['path']) == row['sha256'], row['path']
    NEW.mkdir()
    for path in files(OLD):
        target = NEW / path.relative_to(OLD)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
    path = NEW / 'preparation.py'
    text = path.read_text()
    old = 'require(path.is_relative_to(ROOT) and path.is_file() and not path.is_symlink()'
    assert text.count(old) == 1
    path.write_text(text.replace(old, 'require(path.is_file() and not path.is_symlink()'))
    schema_path = NEW / 'routing.schema.json'
    schema = json.loads(schema_path.read_bytes())
    schema['$id'] = 'urn:cyberalchemy-lab:typed-preparation-routing:v3-candidate'
    schema['properties']['schema_version']['const'] = 'lab-typed-preparation-routing/v3-candidate'
    schema_path.write_text(json.dumps(schema, indent=2, sort_keys=True) + '\n')
    path = NEW / 'DESIGN.md'
    path.write_text(path.read_text() + '\n## Exact external migration pins\n\nV3 preserves each absolute migration-source path declared by the independently\npinned helper manifest. Every original regular-file, symlink and byte-hash\ncheck remains. No caller-selected file path is accepted by this correction.\nThe original failed API48 freeze attempt and frozen v2 source remain preserved.\n')
    loader = API / 'typed_preparation.py'
    text = loader.read_text()
    assert text.count("'typed-host-composition-v2'") == 1
    loader.write_text(text.replace("'typed-host-composition-v2'", "'typed-host-composition-v3'")
                      .replace('_typed_preparation_v2', '_typed_preparation_v3'))
    old_context = RUN / 'context-R03-typed-host-API-0048.json'
    context = RUN / 'context-R03-typed-host-API-0048-recovered-0001.json'
    document = json.loads(old_context.read_bytes())
    document['write_scope'] = [API.relative_to(ROOT).as_posix(), NEW.relative_to(ROOT).as_posix()]
    document['source_bindings'] += [bind(old_context), bind(OLD / 'source-manifest.json'), bind(failure)]
    document['constraints'].append('Preserve exact absolute external migration-source pins and every original file/hash check.')
    put(context, document)
    inputs = previous['input_bindings'] + [bind(OLD / 'source-manifest.json'), bind(context),
                                          bind(failure), bind(Path(__file__).resolve())]
    put(NEW / 'source-manifest.json', {**previous, 'schema_version': 'lab-typed-host-composition-source/v3-candidate',
        'files': [bind(path) for path in sorted(files(NEW))], 'input_bindings': inputs,
        'parent_source_binding': bind(OLD / 'source-manifest.json'), 'external_exact_migration_pins_preserved': True})
    old_profile_path = API / 'contract-profile.json'
    # This profile was produced before API48 had a source manifest and is not a
    # sealed source. Save its exact original bytes before replacing that draft.
    saved = RUN / 'API48-unsealed-contract-profile-attempt-0001.json'
    with saved.open('xb') as stream:
        stream.write(old_profile_path.read_bytes())
    profile = json.loads(old_profile_path.read_bytes())
    profile['files'] = [bind(ROOT / row['path']) if row['path'] == loader.relative_to(ROOT).as_posix() else row
                        for row in profile['files']]
    profile['typed_composition_context_binding'] = bind(context)
    profile['typed_composition_source_binding'] = bind(NEW / 'source-manifest.json')
    old_profile_path.write_text(json.dumps(profile, indent=2, sort_keys=True) + '\n')
    spec = importlib.util.spec_from_file_location('_cal_API48_recovery_parent_guard', PARENT / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    parent = guard.verify(PIN)
    retained = []
    for path in files(PARENT):
        if path.suffix != '.py':
            continue
        def methods(p):
            return {n.name: ast.dump(n, include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes()))
                    if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}
        assert methods(path) == methods(API / path.relative_to(PARENT))
        retained.extend(path.relative_to(PARENT).as_posix() + ':' + name for name in methods(path))
    assert len(retained) == 293
    rows = {row['path']: row for row in parent['files'] + inputs}
    for path in files(API) + files(NEW) + files(OLD) + [PARENT / 'source-manifest.json', OLD / 'source-manifest.json',
        NEW / 'source-manifest.json', API / 'contract-profile.json', context, old_context, saved, failure,
        RUN / 'freeze-R03-typed-host-API-0048-0001.py', Path(__file__).resolve()]:
        row = bind(path)
        rows[row['path']] = row
    for row in rows.values():
        assert sha(ROOT / row['path']) == row['sha256'], row['path']
    put(API / 'source-manifest.json', {**parent, 'files': [rows[k] for k in sorted(rows)],
        'parent_source_binding': bind(PARENT / 'source-manifest.json'), 'context_binding': bind(context),
        'retained_inherited_methods': retained, 'unchanged_inherited_method_count': 293,
        'typed_composition_source_binding': bind(NEW / 'source-manifest.json'),
        'whole_API_qualified': False, 'current_Agent_qualified': False, 'task_complete': False, 'goal_complete': False})
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(API / 'source-manifest.json'),
        'profile_binding': bind(API / 'contract-profile.json'), 'composition_source_binding': bind(NEW / 'source-manifest.json'),
        'unchanged_original_methods': 293, 'authored_handlers': 17, 'public_typed_qualified': False}), flush=True)


if __name__ == '__main__':
    main()
