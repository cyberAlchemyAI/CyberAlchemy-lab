"""Use the original frozen entrypoint with a passive repository execution audit."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
SELECTED = ROOT / 'product/lab/release-candidates/v1/interface/current-context-delivery-v9'
sys.dont_write_bytecode = True


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['build', 'checks'])
    parser.add_argument('--observer-source-sha256', required=True)
    parser.add_argument('--source-sha256', required=True)
    parser.add_argument('--mapped-package-sha256', required=True)
    parser.add_argument('--package-sha256')
    args = parser.parse_args()
    own = RUN / 'current-context-code-audit-source-0009.json'
    assert sha(own.read_bytes()) == args.observer_source_sha256
    own_rows = json.loads(own.read_bytes())['files']
    for row in own_rows:
        assert sha((ROOT / row['path']).read_bytes()) == row['sha256']
    source = SELECTED / 'source-manifest.json'
    assert sha(source.read_bytes()) == args.source_sha256
    rows = {row['path']: row for row in json.loads(source.read_bytes())['files']}
    for row in own_rows:
        assert rows.get(row['path'], row) == row
        rows[row['path']] = row
    events = []
    enabled = True

    def audit(event, values):
        if not enabled or event != 'exec':
            return
        code = values[0]
        filename = code.co_filename
        if filename.startswith('<'):
            return
        path = Path(filename)
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.is_relative_to(ROOT):
            return
        key = path.relative_to(ROOT).as_posix()
        assert key in rows, 'Unselected repository execution path: ' + key
        raw = path.read_bytes()
        assert sha(raw) == rows[key]['sha256'], 'Executed repository source changed: ' + key
        expected = compile(raw, filename, 'exec', dont_inherit=True, optimize=sys.flags.optimize)
        assert code == expected and code.co_filename == expected.co_filename, 'Executed code differs from exact selected source: ' + key
        events.append({**rows[key], 'executed_code_matches_exact_source_compilation': True})

    sys.addaudithook(audit)
    entry = SELECTED / 'run.py'
    sys.argv = [str(entry), args.mode, '--source-sha256', args.source_sha256,
                '--mapped-package-sha256', args.mapped_package_sha256]
    if args.package_sha256 is not None:
        sys.argv += ['--package-sha256', args.package_sha256]
    outcome = None
    try:
        exec(compile(entry.read_bytes(), str(entry), 'exec', dont_inherit=True),
             {'__name__': '__main__', '__file__': str(entry)})
        outcome = {'entrypoint_exit': 0, 'exception_type': None}
    except BaseException as error:
        outcome = {'entrypoint_exit': error.code if isinstance(error, SystemExit) else None,
                   'exception_type': type(error).__name__}
        raise
    finally:
        enabled = False
        output = RUN / ('current-context-code-execution-' + args.mode + '-0009.json')
        value = {'schema_version': 'lab-repository-code-execution-observation/v1-candidate',
                 'phase': args.mode, 'observer_source_sha256': args.observer_source_sha256,
                 'source_sha256': args.source_sha256, 'entrypoint_outcome': outcome,
                 'actual_repository_execution_events': events,
                 'execution_checked_before_each_repository_module_exec': True,
                 'source_callbacks_replaced': False, 'clock_replaced': False,
                 'policy_or_permission_cached': False,
                 'scope': 'Repository module execution during this phase. External engine and interpreter dependencies retain their separately declared checks.',
                 'actual_owner_outcome': None, 'authority_effect': 'none',
                 'current_Agent_qualified': False, 'Context_qualified': False, 'task_complete': False}
        with output.open('x') as stream:
            json.dump(value, stream, indent=2, sort_keys=True)
            stream.write('\n')
        print(json.dumps({'code_execution_events': len(events), 'observation_ref': output.relative_to(ROOT).as_posix(),
                          'entrypoint_outcome': outcome}), flush=True)


if __name__ == '__main__':
    main()
