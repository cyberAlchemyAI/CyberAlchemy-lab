"""Observe actual Context imports and schema construction; no runtime selection change."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
from datetime import datetime, timezone

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
HERE = ROOT / 'product/lab/release-candidates/v1/interface/current-context-delivery-v5'
PIN = '2908afb3d739d92d403c3f4035fe5742d626899a23b401103065b21e9314b5f3'
sys.dont_write_bytecode = True


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': sha(path.read_bytes())}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--observer-source-sha256', required=True)
    args = parser.parse_args()
    own = RUN / 'execution-dependency-observer-source-0001.json'
    assert sha(own.read_bytes()) == args.observer_source_sha256
    for row in json.loads(own.read_bytes())['files']:
        assert bind(ROOT / row['path']) == row
    original = HERE / 'source-manifest.json'
    assert sha(original.read_bytes()) == PIN
    source = json.loads(original.read_bytes())
    selected = {row['path']: row for row in source['files']}
    for row in selected.values():
        assert bind(ROOT / row['path']) == row, row['path']
    observed = {}
    forbidden_writes = []
    enabled = True

    def audit(event, values):
        if not enabled or event != 'open':
            return
        name, mode, flags = values
        if not isinstance(name, (str, bytes, os.PathLike)):
            return
        path = Path(os.fsdecode(name))
        if not path.is_absolute():
            path = Path.cwd() / path
        path = Path(os.path.abspath(path))
        if path.is_relative_to(ROOT):
            key = path.relative_to(ROOT).as_posix()
            writing = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
            if writing:
                forbidden_writes.append(key)
                raise ValueError('Dependency observation refuses repository writes')
            observed[key] = observed.get(key, 0) + 1

    sys.addaudithook(audit)
    name = '_cal_R03_execution_dependency_observation_0001'
    spec = importlib.util.spec_from_file_location(name, HERE / '__init__.py', submodule_search_locations=[str(HERE)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    producer = __import__(name + '.build', fromlist=['API'])
    schemas = producer.API.Schemas(producer.API_PROFILE_PIN)
    schemas.guard()
    enabled = False
    imports = []
    for module in list(sys.modules.values()):
        name = getattr(module, '__file__', None)
        if name is None:
            continue
        path = Path(name)
        if path.is_absolute() and path.is_relative_to(ROOT) and path.is_file():
            imports.append(bind(path))
    imports = {row['path']: row for row in imports}
    actual_rows = []
    unselected = []
    bytecode = []
    for name, count in sorted(observed.items()):
        path = ROOT / name
        if not path.is_file():
            continue
        row = bind(path)
        if path.suffix == '.pyc':
            bytecode.append(row)
        elif selected.get(name) != row:
            unselected.append(row)
        actual_rows.append({**row, 'actual_open_events': count})
    assert not forbidden_writes
    for row in selected.values():
        assert bind(ROOT / row['path']) == row, row['path']
    output = RUN / 'execution-dependency-observation-0001.json'
    value = {'schema_version': 'lab-execution-dependency-observation/v1-candidate',
             'result': 'PASS', 'checked_at': datetime.now(timezone.utc).isoformat(),
             'observer_source_binding': bind(own), 'original_Context_source_binding': bind(original),
             'observed_phase': 'Actual imports and API25 schema constructor/guard only',
             'repository_imports': [imports[key] for key in sorted(imports)],
             'observed_repository_read_files': actual_rows,
             'observed_unselected_nonbytecode_files': unselected,
             'observed_bytecode_files': bytecode,
             'full_source_bytes_verified_before_and_after': True,
             'current_source_or_native_mapping_replayed': False,
             'Context_or_Session_generated': False, 'execution_dependency_closure_complete': False,
             'runtime_selection_changed': False, 'callbacks_replaced': False,
             'policy_or_clock_cached': False, 'current_Agent_qualified': False,
             'actual_owner_outcome': None, 'authority_effect': 'none', 'task_complete': False,
             'remaining_obligations': ['Deferred imports and runtime data-selected paths.',
                                       'Actual signed replay/native mapping/Context generation and error/recovery paths.',
                                       'Explicit selection reasons and fail-closed execution closure.',
                                       'Full successor50 plus independent audit and affected API/lifecycle qualification.']}
    with output.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': 'PASS', 'observation_binding': bind(output),
                      'repository_imports': len(imports), 'repository_read_files': len(actual_rows),
                      'unselected_nonbytecode': len(unselected), 'bytecode': len(bytecode),
                      'execution_dependency_closure_complete': False}), flush=True)


if __name__ == '__main__':
    main()
