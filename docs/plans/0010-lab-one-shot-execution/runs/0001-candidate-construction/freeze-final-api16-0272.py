"""Freeze a separate final candidate from exact completed contribution bindings."""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-integration-v15'
NEW = BASE / 'api-integration-v16'
SOURCE = '87a1b1971166c0dfd9517d060bd6bf9d3b643544da809d2e87e3bc432cc449ac'
PROFILE = '88f4c0bc7cdf5a2e455739a83975e4ddfc8e0381f19709d52fe710efeacffc9a'
FINAL_NAMES = ('source-manifest.json', 'contract-profile.json', 'SCHEMA-EXECUTION-DEPENDENCIES.json')

def bind(path):
    path = Path(path)
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

def load(path):
    return json.loads(Path(path).read_bytes())

def emit(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')

def verified(row):
    assert set(row) == {'path', 'sha256'}
    path = ROOT / row['path']
    assert not path.is_symlink()
    assert bind(path) == row, row['path']
    return row

def merge(rows, row):
    old = rows.get(row['path'])
    assert old is None or old == row, ('conflicting immutable input', row['path'])
    rows[row['path']] = row

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--inputs-sha256', required=True)
    args = parser.parse_args()
    assert bind(args.inputs)['sha256'] == args.inputs_sha256
    inputs = load(args.inputs)
    assert set(inputs) == {'schema_version', 'contributions', 'execution_files', 'evidence_files',
                          'profile_bindings', 'authority_effect', 'actual_owner_outcome'}
    assert inputs['schema_version'] == 'lab-final-API-freeze-inputs/v1-candidate'
    assert inputs['authority_effect'] == 'none' and inputs['actual_owner_outcome'] is None
    assert all(not (NEW / name).exists() for name in FINAL_NAMES)
    assert bind(OLD / 'contract-profile.json')['sha256'] == PROFILE
    spec = importlib.util.spec_from_file_location('_cal_API16_final_parent_guard', OLD / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    parent = guard.verify(SOURCE)
    old_profile = load(OLD / 'contract-profile.json')
    full = {row['path']: row for row in parent['files']}
    profile_rows = {row['path']: row for row in old_profile['files']}
    for row in (bind(OLD / 'source-manifest.json'), bind(OLD / 'contract-profile.json')):
        merge(full, row)
        merge(profile_rows, row)
    contributions = []
    for selected in inputs['contributions']:
        verified(selected)
        manifest = load(ROOT / selected['path'])
        assert manifest['authority_effect'] == 'none' and manifest['actual_owner_outcome'] is None
        selected_rows = manifest.get('files')
        if selected_rows is None:
            selected_rows = [*manifest['provider_files'], *manifest['retained_proof_files']]
        assert selected_rows
        for row in selected_rows:
            verified(row)
            merge(full, row)
            merge(profile_rows, row)
        merge(full, selected)
        merge(profile_rows, selected)
        contributions.append(selected)

    local = []
    for path in sorted(NEW.rglob('*')):
        if not path.is_file() or {'receipts', '__pycache__'} & set(path.relative_to(NEW).parts):
            continue
        assert not path.is_symlink()
        if path.suffix == '.py':
            ast.parse(path.read_text())
        row = bind(path)
        local.append(row)
        merge(full, row)
        merge(profile_rows, row)

    old_prefix = OLD.relative_to(ROOT).as_posix() + '/'
    new_prefix = NEW.relative_to(ROOT).as_posix() + '/'
    selection = load(OLD / 'SCHEMA-EXECUTION-DEPENDENCIES.json')
    for row in [bind(args.inputs), bind(Path(__file__).resolve()),
                *inputs['evidence_files'], *inputs['profile_bindings'].values()]:
        verified(row)
        merge(full, row)
        merge(profile_rows, row)
    execution = {}
    reasons = {}
    for old_row in selection['files']:
        key = new_prefix + old_row['path'][len(old_prefix):] if old_row['path'].startswith(old_prefix) else old_row['path']
        row = bind(ROOT / key)
        if not old_row['path'].startswith(old_prefix):
            assert row == old_row
        merge(execution, row)
        reasons[key] = selection['selection_reasons'][old_row['path']]
    for item in inputs['execution_files']:
        assert set(item) == {'binding', 'reasons'} and item['reasons']
        row = verified(item['binding'])
        assert full.get(row['path']) == row, ('execution outside full source', row['path'])
        merge(execution, row)
        reasons[row['path']] = item['reasons']
    for row in local:
        # Every candidate Python module and local schema is an active code input;
        # no dynamically created private grant/workspace/journal is selected.
        path = ROOT / row['path']
        if path.suffix == '.py' or path.name.endswith('.schema.json') or path.name in (
                'schema-inputs.json', 'dependency-selection.json', 'integration-members.json'):
            merge(execution, row)
            reasons[row['path']] = ['Actual final common candidate code or local schema input.']
    assert all(profile_rows.get(k) == v for k, v in execution.items())
    # Validate the full immutable input union before creating any final file.
    for row in full.values():
        verified(row)
    selection.update(files=[execution[k] for k in sorted(execution)], selection_reasons=reasons,
                     parent_source_binding=bind(OLD / 'source-manifest.json'),
                     parent_profile_binding=bind(OLD / 'contract-profile.json'))
    emit(NEW / 'SCHEMA-EXECUTION-DEPENDENCIES.json', selection)
    selection_row = bind(NEW / 'SCHEMA-EXECUTION-DEPENDENCIES.json')
    merge(profile_rows, selection_row)
    merge(full, selection_row)
    profile = dict(old_profile)
    profile.update(files=[profile_rows[k] for k in sorted(profile_rows)],
                   integration_members_binding=bind(NEW / 'integration-members.json'),
                   schema_execution_dependency_binding=selection_row,
                   final_contribution_bindings=contributions,
                   final_freeze_input_binding=bind(args.inputs),
                   **inputs['profile_bindings'])
    profile['claim_ceiling'] = ('34 authored candidate operations, exact final Source8 and original '
        'genuine Work history implementations. New final-family wire/regression qualification, '
        'human pilot and final owner review remain required. No predecessor qualification transfer.')
    emit(NEW / 'contract-profile.json', profile)
    merge(full, bind(NEW / 'contract-profile.json'))
    guard.verify(SOURCE)
    for row in full.values():
        verified(row)
    manifest = dict(parent)
    for key, value in list(manifest.items()):
        if (key.endswith('_qualified') or key in ('runtime_qualification_transferred',
            'task_complete', 'goal_complete', 'prospective_repository_profile_guard_passed')):
            manifest[key] = False
    manifest.update(files=[full[k] for k in sorted(full)],
                    parent_source_binding=bind(OLD / 'source-manifest.json'),
                    schema_execution_dependency_binding=selection_row,
                    final_contribution_bindings=contributions,
                    final_freeze_input_binding=bind(args.inputs),
                    freeze_finalizer_binding=bind(Path(__file__).resolve()),
                    integration_members_binding=bind(NEW / 'integration-members.json'),
                    expected_regression_cases=345,predecessor_declared_method_bodies=345,
                    successor_method_body_retention_requires_AST_ledger=True,
                    claim_ceiling=profile['claim_ceiling'],
                    authored_handler_count=34, whole_API_qualified=False,
                    runtime_qualification_transferred=False, task_complete=False, goal_complete=False)
    manifest.update(inputs['profile_bindings'])
    emit(NEW / 'source-manifest.json', manifest)
    print(json.dumps({'result': 'FROZEN_UNQUALIFIED',
                      'source_binding': bind(NEW / 'source-manifest.json'),
                      'profile_binding': bind(NEW / 'contract-profile.json'),
                      'source_files': len(full), 'execution_files': len(execution),
                      'predecessor_rows_retained': len(parent['files']),
                      'authority_effect': 'none', 'task_complete': False, 'goal_complete': False}), flush=True)

if __name__ == '__main__':
    main()
