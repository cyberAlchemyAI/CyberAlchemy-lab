"""Freeze completed API30 controls and retained failures before a fresh episode."""
import ast
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-v30'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    controls = API / 'receipts/current-controls.json'
    report = json.loads(controls.read_bytes())
    assert report['result'] == 'PASS'
    assert report['tests_run'] == report['expected_tests'] == len(report['cases']) == 7
    assert all(case['result'] == 'PASS' for case in report['cases'])
    assert report['source_sha256'] == bind(API / 'source-manifest.json')['sha256']
    assert report['profile_sha256'] == bind(API / 'contract-profile.json')['sha256']
    terminal = RUN / 'current-Agent-controls-terminal-0005.json'
    observed = json.loads(terminal.read_bytes())
    assert observed['exit_code'] == 0 and observed['terminal_observed']
    rows = {}

    def add(row):
        assert rows.get(row['path'], row) == row, row['path']
        assert bind(ROOT / row['path']) == row, row['path']
        rows[row['path']] = row

    # Keep the complete prior diagnostic and its unchanged input closure.
    failed = RUN / 'current-Agent-development-observation-failed-proof-0002.json'
    prior = json.loads(failed.read_bytes())
    assert prior['result'] == 'FAIL'
    for selected in [prior, json.loads((API / 'source-manifest.json').read_bytes())]:
        for row in selected['files']:
            add(row)
    script = RUN / 'observe-R03-current-Agent-API-0003.py'
    ast.parse(script.read_bytes())
    ast.parse(Path(__file__).read_bytes())
    context = RUN / 'context-R03-current-Agent-development-observation-0003.json'
    put(context, {
        'schema_version': 'lab-bounded-context/v1-candidate',
        'task': 'R03 observe actual API30 Session lifecycle after Context4 qualification',
        'strict_coverage': 'PASS',
        'source_bindings': [bind(failed), bind(API / 'source-manifest.json'),
                            bind(API / 'contract-profile.json'), bind(controls), bind(terminal)],
        'constraints': [
            'Fresh independently authenticated owned host and private workspace only.',
            'Original absolute Assignment period and all expired grants remain unchanged.',
            'Same lifecycle and RAM disposal assertions; retain public replies before expectations.',
            'Diagnostic exception tracing is removed; no handler, permission or clock is changed.',
            'Full146/134 and independent whole API qualification remain separate obligations.',
            'No owner outcome, canonical admission, permanent Agent or release is created.'
        ],
        'authority_effect': 'none', 'actual_owner_outcome': None
    })
    for path in [failed, API / 'source-manifest.json', API / 'contract-profile.json',
                 controls, terminal, script, Path(__file__), context]:
        add(bind(path))
    output = RUN / 'current-Agent-development-observation-source-0003.json'
    put(output, {
        'schema_version': 'lab-current-Agent-development-observation-source/v1-candidate',
        'files': [rows[key] for key in sorted(rows)],
        'api_source_binding': bind(API / 'source-manifest.json'),
        'api_profile_binding': bind(API / 'contract-profile.json'),
        'context_binding': bind(context), 'predecessor_failed_proof_binding': bind(failed),
        'frozen_before_independent_owned_host_key_workspace_or_Session_effects': True,
        'whole_API_qualification': False, 'current_Agent_qualified': False,
        'task_complete': False, 'authority_effect': 'none', 'actual_owner_outcome': None
    })
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(output),
                      'files': len(rows)}), flush=True)


if __name__ == '__main__':
    main()
