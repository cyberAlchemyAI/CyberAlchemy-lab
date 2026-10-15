"""Bind completed seven controls and exact inputs before isolated lifecycle effects."""
import ast
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-v29'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    terminal = RUN / 'current-Agent-controls-terminal-0004.json'
    report = json.loads((API / 'receipts/current-controls.json').read_bytes())
    assert report['result'] == 'PASS'
    assert report['tests_run'] == report['expected_tests'] == len(report['cases']) == 7
    assert all(row['result'] == 'PASS' for row in report['cases'])
    assert bind(API / 'source-manifest.json')['sha256'] == report['source_sha256']
    assert bind(API / 'contract-profile.json')['sha256'] == report['profile_sha256']
    put(terminal, {'session_id': 47235, 'actual_terminal_tool_chunk': 'fe4754', 'exit_code': 0,
                   'result': 'PASS', 'tests_run': 7,
                   'source_binding': bind(API / 'source-manifest.json'),
                   'profile_binding': bind(API / 'contract-profile.json'),
                   'checks_binding': bind(API / 'receipts/current-controls.json'),
                   'log_binding': bind(API / 'current-controls-0001.log'),
                   'current_Agent_qualified': False, 'task_complete': False,
                   'authority_effect': 'none', 'actual_owner_outcome': None})
    rows = {}
    def add(row):
        assert rows.get(row['path'], row) == row
        assert bind(ROOT / row['path']) == row, row['path']
        rows[row['path']] = row
    for row in json.loads((API / 'source-manifest.json').read_bytes())['files']:
        add(row)
    for path in [API / 'source-manifest.json', API / 'contract-profile.json',
                 API / 'receipts/current-controls.json', API / 'current-controls-0001.log', terminal]:
        add(bind(path))
    proof = RUN / 'current-Agent-controls-proof-0004.json'
    put(proof, {'schema_version': 'lab-current-Agent-controls-proof/v1-candidate', 'result': 'PASS',
                'files': [rows[k] for k in sorted(rows)], 'tests_run': 7,
                'terminal_binding': bind(terminal), 'current_Agent_qualified': False,
                'task_complete': False, 'authority_effect': 'none', 'actual_owner_outcome': None})
    context = RUN / 'context-R03-current-Agent-development-observation-0001.json'
    selected = [RUN / 'authorization.json', RUN.parents[1] / 'work-pack/tasks/R03.md',
                RUN / 'context-R03-current-Agent-API-0004.json', API / 'source-manifest.json',
                API / 'contract-profile.json', proof, terminal,
                RUN / 'observe-R03-current-Agent-API-0001.py']
    for path in selected:
        assert path.is_file(), str(path)
    put(context, {'schema_version': 'lab-bounded-context/v1-candidate',
                  'task': 'R03 bounded actual Agent lifecycle development observation',
                  'strict_coverage': 'PASS', 'blockers': [],
                  'source_bindings': [bind(path) for path in selected],
                  'obligations': [{'id': key, 'status': 'covered'} for key in [
                      'completed-seven-controls', 'exact-inputs-before-effects',
                      'new-owned-local-host-key-workspace-only', 'actual-open-context-close-retry',
                      'short-memory-zeroed-and-never-persisted', 'fixed-source-period-unchanged',
                      'no-whole-regression-qualification', 'sole-owner-R08-after-S02']],
                  'write_scope': [str(API / 'receipts'), str(RUN),
                                  'new test-owned temporary roots only'],
                  'constraints': ['Whole146/134 remains pending; observation is scoped evidence only.',
                                  'No canonical admission, existing/live store, owner authority or publication.',
                                  'Keep predecessor terminal failures and incomplete runs.'],
                  'validation': 'Actual independently authenticated lifecycle, raw bodies, memory disposal and retry.',
                  'task_complete': False, 'authority_effect': 'none', 'actual_owner_outcome': None})
    for path in selected + [context, Path(__file__)]:
        if path.suffix == '.py':
            ast.parse(path.read_bytes())
        add(bind(path))
    source = RUN / 'current-Agent-development-observation-source-0001.json'
    put(source, {'schema_version': 'lab-current-Agent-development-observation-source/v1-candidate',
                 'files': [rows[k] for k in sorted(rows)],
                 'api_source_binding': bind(API / 'source-manifest.json'),
                 'api_profile_binding': bind(API / 'contract-profile.json'),
                 'terminal_binding': bind(terminal), 'context_binding': bind(context),
                 'frozen_before_independent_owned_host_key_workspace_or_Session_effects': True,
                 'whole_API_qualification': False, 'current_Agent_qualified': False,
                 'task_complete': False, 'authority_effect': 'none', 'actual_owner_outcome': None})
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(source),
                      'controls_proof_binding': bind(proof), 'files': len(rows)}), flush=True)


if __name__ == '__main__':
    main()
