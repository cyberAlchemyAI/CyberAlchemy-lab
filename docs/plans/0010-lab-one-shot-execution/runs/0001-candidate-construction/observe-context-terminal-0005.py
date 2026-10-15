"""Record actual tool terminal observations; never infer exits from log text."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
CONTEXT = ROOT / 'product/lab/release-candidates/v1/interface/current-context-delivery-v5'

def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=['checks', 'audit'])
    parser.add_argument('--observed-tool-session', type=int, required=True)
    parser.add_argument('--observed-exit-code', type=int, required=True)
    parser.add_argument('--observed-terminal-chunk', required=True)
    args = parser.parse_args()
    output = RUN / f'current-context-delivery-{args.phase}-terminal-0005.json'
    assert not output.exists()
    source = CONTEXT / 'source-manifest.json'
    log = RUN / f'current-context-delivery-{args.phase}-0005.log'
    value = {'schema_version': 'lab-actual-terminal-observation/v1-candidate',
             'checked_at': datetime.now(timezone.utc).isoformat(),
             'phase': args.phase, 'terminal_observed': True,
             'tool_session_id': args.observed_tool_session,
             'exit_code': args.observed_exit_code,
             'chunk_id': args.observed_terminal_chunk,
             'source_binding': bind(source), 'log_binding': bind(log),
             'observer_binding': bind(Path(__file__)),
             'authority_effect': 'none', 'actual_owner_outcome': None,
             'task_complete': False, 'Context5_qualified': False}
    if args.phase == 'checks':
        report = CONTEXT / 'receipts/checks.json'
        if report.exists():
            value['report_binding'] = bind(report)
        combined = RUN / 'current-context-delivery-terminal-0005.json'
        assert not combined.exists()
        build = json.loads((RUN / 'current-context-delivery-build-terminal-0005.json').read_bytes())
        assert build['terminal_observed'] is True
        put(output, value)
        put(combined, {'schema_version': 'lab-actual-build-check-terminals/v1-candidate',
                       'build': build, 'checks': value,
                       'selected_exit_codes': {'build': build['exit_code'], 'checks': args.observed_exit_code},
                       'authority_effect': 'none', 'actual_owner_outcome': None,
                       'task_complete': False, 'Context5_qualified': False})
    else:
        value['audit_source_binding'] = bind(RUN / 'current-context-audit-source-0005.json')
        for name in ['independent-audit.json', 'audit-proof-0001.json']:
            path = CONTEXT / 'receipts' / name
            if path.exists():
                value[name] = bind(path)
        put(output, value)
    print(json.dumps({'terminal_binding': bind(output), 'actual_exit_code': args.observed_exit_code}))

if __name__ == '__main__':
    main()
