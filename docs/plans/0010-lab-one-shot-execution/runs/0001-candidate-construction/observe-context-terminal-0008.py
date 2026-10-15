"""Record a tool terminal only after it has actually been returned."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
SELECTED = ROOT / 'product/lab/release-candidates/v1/interface/current-context-delivery-v8'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=['build', 'audit'])
    parser.add_argument('--session', type=int, required=True)
    parser.add_argument('--exit-code', type=int, required=True)
    parser.add_argument('--chunk', required=True)
    args = parser.parse_args()
    assert args.exit_code == 0
    source = SELECTED / 'source-manifest.json'
    assert bind(source)['sha256'] == 'de6957eb09db5bd052ae494f808f6d02aaeba0641316d62753c13a7d9a0d0bf6'
    log = RUN / ('current-context-delivery-' + args.phase + '-0008.log')
    assert log.is_file()
    if args.phase == 'build':
        result = json.loads((SELECTED / 'packages/0001/build-result.json').read_bytes())
        assert result['result'] == 'PASS' and result['actual_generated_artifact_carriers'] == 30
        observation_path = RUN / 'current-context-code-execution-build-0008.json'
        observation = json.loads(observation_path.read_bytes())
        assert observation['entrypoint_outcome'] == {'entrypoint_exit': 0, 'exception_type': None}
        assert observation['source_sha256'] == bind(source)['sha256']
        assert observation['actual_repository_execution_events']
        assert all(row['executed_code_matches_exact_source_compilation'] for row in observation['actual_repository_execution_events'])
        output = RUN / 'current-context-build-terminal-0008.json'
        extra = {'build_result_binding': bind(SELECTED / 'packages/0001/build-result.json'),
                 'code_execution_observation_binding': bind(observation_path)}
    else:
        audit = SELECTED / 'receipts/independent-audit.json'
        result = json.loads(audit.read_bytes())
        assert result['result'] == 'PASS' and result['selected_methods'] == 50
        output = RUN / 'current-context-delivery-audit-terminal-0008.json'
        extra = {'audit_binding': bind(audit)}
    value = {'schema_version': 'lab-observed-context-terminal/v1-candidate',
             'terminal_observed': True, 'exit_code': args.exit_code,
             'tool_session_id': args.session, 'chunk_id': args.chunk,
             'phase': args.phase, 'observed_at': datetime.now(timezone.utc).isoformat(),
             'source_binding': bind(source), 'log_binding': bind(log),
             'observer_binding': bind(Path(__file__)), 'authority_effect': 'none',
             'actual_owner_outcome': None, **extra}
    with output.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': 'PASS', 'terminal_binding': bind(output)}), flush=True)


if __name__ == '__main__':
    main()
