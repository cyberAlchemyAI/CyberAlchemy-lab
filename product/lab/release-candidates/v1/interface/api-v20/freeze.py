"""Freeze the guarded calculation successor before owned effectful tests."""
import ast
import importlib.metadata
import json
import platform
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
RUN = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path, value):
    with path.open('x') as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write('\n')


def methods(path):
    return {n.name: ast.dump(n, include_attributes=False) for n in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}


def main():
    parent = HERE.parent / 'api-v19'
    assert bind(parent / 'source-manifest.json')['sha256'] == 'fcd98b74253bc5a7f081faed13c2b4c198df55ff3f6e6772563e1d50a784ff1b'
    proof = RUN / 'custody-session-diagnostic-proof-0003.json'
    terminal = json.loads((RUN / 'custody-session-diagnostic-terminal-0003.json').read_bytes())
    assert terminal['exit_code'] == 0 and terminal['actual_test_result'] == 'PASS' and terminal['tests_run'] == 2
    context = RUN / 'context-R03-custody-api-0005.json'
    selected = json.loads(context.read_bytes())
    assert selected['strict_coverage'] == 'PASS' and not selected['blockers']
    previous = json.loads((parent / 'contract-profile.json').read_bytes())
    profile = {**previous, 'files': []}
    for row in previous['files']:
        path = ROOT / row['path']
        profile['files'].append(bind(HERE / path.relative_to(parent) if path.is_relative_to(parent) else path))
    profile['files'].append(bind(HERE / 'guarded_reads.py'))
    assert len({r['path'] for r in profile['files']}) == len(profile['files'])
    profile['claim_ceiling'] = 'Twelve existing candidate operations with sealed pure calculation snapshots and full boundary guards. All original contracts and absolute Assignment period retained. Full146 verification and independent audit pending;22 operations remain.'
    put(HERE / 'contract-profile.json', profile)
    derivation = {}
    for name in ['test_preparation.py', 'test_preparation_corrected.py', 'run_session_checks.py', 'test_custody_sessions.py', 'test_custody_api.py']:
        assert methods(HERE / name) == methods(parent / name)
        derivation[name] = {'methods': len(methods(HERE / name)), 'changed_test_method_ASTs': []}
    assert len(methods(HERE / 'test_guarded_reads.py')) == 17
    put(HERE / 'derivation.json', {
        'schema_version': 'lab-guarded-calculation-successor/v1-candidate', 'parent_source_binding': bind(parent / 'source-manifest.json'),
        'context_binding': bind(context), 'actual_untraced_session_terminal_binding': bind(RUN / 'custody-session-diagnostic-terminal-0003.json'),
        'changes': ['Whole-source verification at entry and exit of closed disposable read calculations; original byte model unchanged',
                    'Copied ExactSources facts with full original get/resolve/schema/witness checks and full parent guards before/after pure preflight',
                    'PermissionBridge checks original actual source and grant; complete post-claim preflight still repeated',
                    'Dispose SQL construction if exit source guard fails; no partially qualified generation is returned'],
        'original_method_derivation': derivation, 'original_tests': 129, 'added_guard_tests': 17, 'all_original_method_ASTs_retained': True,
        'parent_source_or_guard_callbacks_modified': False, 'body_bytes_cached_by_new_helper': False,
        'original_assignment_period_extended_or_reset': False, 'actual_owner_outcome': None, 'authority_effect': 'none', 'task_complete': False})
    rows = {}
    for path in [parent / 'source-manifest.json', proof]:
        for row in json.loads(path.read_bytes())['files']:
            assert rows.get(row['path'], row) == row
            rows[row['path']] = row
        rows[path.relative_to(ROOT).as_posix()] = bind(path)
    for row in selected['source_bindings']:
        item = row['binding']
        assert rows.get(item['path'], item) == item
        rows[item['path']] = item
    rows[context.relative_to(ROOT).as_posix()] = bind(context)
    for path in HERE.rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts:
            if path.suffix == '.py':
                ast.parse(path.read_bytes())
            rows[path.relative_to(ROOT).as_posix()] = bind(path)
    for row in rows.values():
        assert bind(ROOT / row['path']) == row, row['path']
    env = {'python': platform.python_version(), 'jsonschema': importlib.metadata.version('jsonschema'),
           'cryptography': importlib.metadata.version('cryptography')}
    assert env == json.loads((parent / 'source-manifest.json').read_bytes())['environment']
    put(HERE / 'source-manifest.json', {
        'schema_version': 'lab-original-source-API-source/v1-candidate', 'files': sorted(rows.values(), key=lambda r: r['path']),
        'environment': env, 'parent_source_binding': bind(parent / 'source-manifest.json'),
        'profile_binding': bind(HERE / 'contract-profile.json'), 'correction_context_binding': bind(context),
        'terminal_diagnostic_binding': bind(RUN / 'custody-session-diagnostic-terminal-0003.json'),
        'original_test_method_derivation': derivation, 'expected_full_test_methods': 146,
        'original_retained_test_methods': 129, 'additional_snapshot_tests': 17,
        'full_parent_suite_pending_at_freeze': True,
        'final_independent_audit_requires_complete_parent_terminal_and_retained_failure_outputs': True,
        'original_operations': 34, 'implemented_operations': 12, 'remaining_operations': 22,
        'frozen_before_owned_API_effects': True, 'authority_effect': 'none', 'actual_owner_outcome': None, 'task_complete': False})
    print(json.dumps({'result': 'FROZEN', 'files': len(rows), 'source_binding': bind(HERE / 'source-manifest.json'),
                      'profile_binding': bind(HERE / 'contract-profile.json'), 'tests': 146}), flush=True)


if __name__ == '__main__':
    main()
