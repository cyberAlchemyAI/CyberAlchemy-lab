"""Serial selected-ABI accounting for every inherited API53 method.

This candidate is not a final T15 cut. Each whole class runs in one child,
with no parallel workers. Unexecuted methods receive an explicit status.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v53-t16-challenge-source-0001'
SOURCE_SHA = '7944431236ce9437516104b33ed04024994e0d9d45a2c2152eacf71612fd09ff'
PROFILE_SHA = '7480e7bf7d848a16d50bf7f56d6c4a24bd6175b0fa61d35fa796f9bf76c99f7d'
INVENTORY = ROOT / 'implementation/lab-runtime/local-host/t16-api49-provisional-regression-0001/INVENTORY-0001.json'
INVENTORY_SHA = 'bd83d446316e30a912616eb55552ae2935305b206c6400c8e067501f0912f3f3'
WORKER = ROOT / 'implementation/lab-runtime/local-host/t16-api53-serial-regression-0001/run_bucket.py'
WORKER_SHA = 'bb15c299516bb49d5e28985e7e867432257e2505bd8f0bc60f2d0e885e10268e'
SELECTION = HERE / 'RUNNER-SELECTION-0003.json'
INSTALL = ROOT / 'implementation/lab-runtime/local-host/t03-d95-margin-api-recut-0001/working/installation-0001'
INSTALL_RECEIPT = ROOT / 'implementation/lab-runtime/local-host/t03-d95-margin-api-recut-0001/installation-receipt.json'
INSTALL_RECEIPT_SHA = '7f32ee98bfff06ae68c5c90e5874816b405acfb1d076d5edf33a220f059d54b5'
DEPENDENCY_SELECTION = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json'
DEPENDENCY_SELECTION_SHA = '2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'
LOADER_SHA = 'bda779ea9e9ad234f60315477d7cfd0bdde861cd8ddd9df8cdaf62f18c4cec14'
PYTHON_SHA = '52e0a13e60a981d8c4b6478be2ba5176f69da07948a056bf49cf6f077e30cb41'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def utc():
    return datetime.now(timezone.utc).isoformat()


def exact(path, expected=None):
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('absolute closed selection required')
    handles = []
    try:
        parent = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        handles.append(parent)
        for part in path.parts[1:-1]:
            parent = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            handles.append(parent)
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent)
        try:
            before = os.fstat(fd)
            if not stat.S_ISREG(before.st_mode):
                raise ValueError('selected regular file required')
            raw = bytearray()
            while block := os.read(fd, 1024 * 1024):
                raw.extend(block)
            after = os.fstat(fd)
            named = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
            stamp = lambda item: (item.st_dev, item.st_ino, item.st_size, item.st_mtime_ns, item.st_ctime_ns)
            if (stamp(before) != stamp(after) or stamp(after) != stamp(named)
                    or (expected is not None and sha(raw) != expected)):
                raise ValueError('selected byte differs: ' + str(path))
            return bytes(raw)
        finally:
            os.close(fd)
    finally:
        for handle in reversed(handles):
            os.close(handle)


def selected_inventory(selection_sha):
    selection = json.loads(exact(SELECTION, selection_sha))
    if selection != {
        'schema_version': 'lab-T16-API53-selected-ABI-runner-selection/v1',
        'source_sha256': SOURCE_SHA, 'profile_sha256': PROFILE_SHA,
        'inventory_sha256': INVENTORY_SHA, 'worker_sha256': WORKER_SHA,
        'coordinator_sha256': sha(exact(Path(__file__).absolute())),
        'installation_receipt_sha256': INSTALL_RECEIPT_SHA,
        'dependency_selection_sha256': DEPENDENCY_SELECTION_SHA,
        'loader_sha256': LOADER_SHA, 'python_sha256': PYTHON_SHA,
        'selected_class_count': 21, 'selected_method_count': 345,
        'serial_fresh_process_per_class': True,
    }:
        raise ValueError('externally selected serial runner differs')
    exact(API / 'source-manifest.json', SOURCE_SHA)
    exact(API / 'contract-profile.json', PROFILE_SHA)
    exact(WORKER, WORKER_SHA)
    receipt = json.loads(exact(INSTALL_RECEIPT, INSTALL_RECEIPT_SHA))
    if (receipt.get('owned_root') != INSTALL.relative_to(ROOT).as_posix()
            or receipt.get('owned_member_count') != 1010
            or receipt.get('selected_dependency_sha256') != '2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'):
        raise ValueError('selected ABI installation receipt differs')
    dependency = json.loads(exact(DEPENDENCY_SELECTION, DEPENDENCY_SELECTION_SHA))
    members = {row['destination']: row for row in dependency['inputs']}
    members.update(dependency['wheel_members'])
    if len(members) != 1010 or not INSTALL.is_dir() or INSTALL.is_symlink():
        raise ValueError('selected dependency member set or owned root differs')
    root_state = INSTALL.lstat()
    if root_state.st_uid != os.getuid() or stat.S_IMODE(root_state.st_mode) != 0o700:
        raise ValueError('selected dependency root privacy differs')
    inherited_intermediate_dirs = {
        'lib', 'deps/jsonschema_specifications/schemas',
        'lib/python3.14/venv/scripts',
    }
    actual = set()
    actual_directories = set()
    for entry in INSTALL.rglob('*'):
        if entry.is_symlink():
            raise ValueError('selected dependency has a linked member')
        if entry.is_file():
            actual.add(entry.relative_to(INSTALL).as_posix())
        elif entry.is_dir():
            state = entry.lstat()
            relative = entry.relative_to(INSTALL).as_posix()
            actual_directories.add(relative)
            expected_mode = 0o755 if relative in inherited_intermediate_dirs else 0o700
            if state.st_uid != os.getuid() or stat.S_IMODE(state.st_mode) != expected_mode:
                raise ValueError('selected dependency directory privacy differs')
        else:
            raise ValueError('selected dependency has an unsafe member')
    if actual != set(members):
        raise ValueError('selected dependency closure differs')
    expected_directories = set()
    for name in members:
        parent = Path(name).parent
        while parent != Path('.'):
            expected_directories.add(parent.as_posix())
            parent = parent.parent
    if actual_directories != expected_directories:
        raise ValueError('selected dependency directory closure differs')
    for name, row in sorted(members.items()):
        if (not isinstance(name, str) or not name or name.startswith('/')
                or '..' in Path(name).parts or Path(name).as_posix() != name):
            raise ValueError('unsafe selected dependency path')
        raw = exact(INSTALL / name, row['sha256'])
        if len(raw) != row['size_bytes']:
            raise ValueError('selected dependency size differs: ' + name)
        wanted_mode = (0o755 if row.get('kind') in {'interpreter', 'native-executable'}
                       or name == 'lib/abi/ld-linux-x86-64.so.2' else 0o644)
        state = (INSTALL / name).lstat()
        if state.st_uid != os.getuid() or stat.S_IMODE(state.st_mode) != wanted_mode:
            raise ValueError('selected dependency file mode or owner differs: ' + name)
    if (sha(exact(INSTALL / 'lib/abi/ld-linux-x86-64.so.2')) != LOADER_SHA
            or sha(exact(INSTALL / 'bin/python')) != PYTHON_SHA):
        raise ValueError('selected ABI executable differs')
    inventory = json.loads(exact(INVENTORY, INVENTORY_SHA))
    buckets = inventory['buckets']
    if len(buckets) != 21 or sum(len(ids) for ids in buckets.values()) != 345:
        raise ValueError('inherited class/method inventory differs')
    all_ids = [identity for ids in buckets.values() for identity in ids]
    if len(set(all_ids)) != 345:
        raise ValueError('inherited method IDs overlap')
    return buckets


def file_new(path, raw):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())


def synthetic(ids, status, at):
    return [{'id': identity, 'result': status, 'executed': False,
             'started_at_utc': None, 'ended_at_utc': at} for identity in ids]


def worker_command(bucket, run_id):
    paths = [str(INSTALL / 'deps'), str(API.parent), str(ROOT)]
    bootstrap = (
        'import importlib.metadata,json,platform,runpy,sys; '
        'sys.path[:0]=json.loads(sys.argv[1]); '
        'assert (platform.python_version(),importlib.metadata.version("jsonschema"),'
        'importlib.metadata.version("cryptography"))==("3.14.4","4.23.0","46.0.5"); '
        'target=sys.argv[2]; sys.argv=[target,*sys.argv[3:]]; '
        'runpy.run_path(target,run_name="__main__")'
    )
    return [str(INSTALL / 'lib/abi/ld-linux-x86-64.so.2'), '--inhibit-cache',
            '--library-path', str(INSTALL / 'lib/abi'), str(INSTALL / 'bin/python'),
            '-I', '-X', 'utf8', '-B', '-S', '-c', bootstrap, json.dumps(paths),
            str(WORKER), '--bucket', bucket, '--run-id', run_id,
            '--runner-sha256', WORKER_SHA]


def validate_worker_result(result, bucket, run_id, ids, exit_code, timed_out):
    if not isinstance(result, dict):
        raise ValueError('worker result object required')
    if (result.get('schema_version') != 'lab-t16-api53-serial-bucket/v1'
            or result.get('bucket') != bucket or result.get('run_id') != run_id
            or result.get('selected_ids') != ids
            or result.get('source_sha256') != SOURCE_SHA
            or result.get('profile_sha256') != PROFILE_SHA
            or result.get('inventory_sha256') != INVENTORY_SHA
            or result.get('runner_sha256') != WORKER_SHA
            or result.get('result') not in ('PASS', 'FAIL')
            or not isinstance(result.get('cases'), list)
            or len(result['cases']) != len(ids)
            or any(not isinstance(item, dict) for item in result['cases'])
            or [item.get('id') for item in result['cases']] != ids
            or not isinstance(result.get('tests_run'), int)
            or not 0 <= result['tests_run'] <= len(ids)
            or not isinstance(result.get('exact_case_set'), bool)
            or not isinstance(result.get('all_methods_executed'), bool)
            or not isinstance(result.get('entry_guard_passed'), bool)
            or not isinstance(result.get('exit_guard_passed'), bool)):
        raise ValueError('worker result selection or case set differs')
    if any(not isinstance(item.get('executed'), bool) or not isinstance(item.get('result'), str)
           for item in result['cases']):
        raise ValueError('worker case status differs')
    if result['result'] == 'PASS' and (
            timed_out or exit_code != 0 or result['tests_run'] != len(ids)
            or not result['exact_case_set'] or not result['all_methods_executed']
            or not result['entry_guard_passed'] or not result['exit_guard_passed']
            or any(item['result'] != 'PASS' or not item['executed'] for item in result['cases'])):
        raise ValueError('worker PASS lacks process and guard proof')
    if result['result'] == 'FAIL' and exit_code == 0:
        raise ValueError('worker failure disagrees with process exit')


def run(run_id, max_buckets, timeout_seconds, selection_sha):
    if not re.fullmatch(r'[a-z][a-z0-9-]{0,31}', run_id):
        raise ValueError('closed run identity required')
    if not 1 <= max_buckets <= 21 or not 60 <= timeout_seconds <= 14400:
        raise ValueError('bounded serial execution parameters required')
    buckets = selected_inventory(selection_sha)
    os.umask(0o077)
    # The pinned worker writes to its own HERE/working; aggregate those same bytes.
    work = WORKER.parent / 'working' / run_id
    work.mkdir(mode=0o700, parents=True, exist_ok=False)
    if work.is_symlink():
        raise ValueError('unsafe serial result directory')
    events = work / 'SERIAL-EVENTS.jsonl'
    fd = os.open(events, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    stream = os.fdopen(fd, 'w')
    def event(value):
        stream.write(json.dumps({'at_utc': utc(), **value}, sort_keys=True) + '\n')
        stream.flush(); os.fsync(stream.fileno())
    started = utc()
    event({'phase': 'start', 'run_id': run_id, 'bucket_count': len(buckets),
           'method_count': 345, 'max_buckets': max_buckets})
    rows = []
    bucket_rows = []
    stopped_for_selection = False
    for index, (bucket, ids) in enumerate(buckets.items()):
        if index >= max_buckets or stopped_for_selection:
            reason = 'NOT-RUN-SELECTION-REFUSAL' if stopped_for_selection else 'NOT-RUN-PLANNED'
            rows.extend(synthetic(ids, reason, utc()))
            bucket_rows.append({'bucket': bucket, 'result': reason, 'tests_run': 0})
            continue
        try:
            selected_inventory(selection_sha)
        except BaseException as error:
            stopped_for_selection = True
            rows.extend(synthetic(ids, 'NOT-RUN-SELECTION-REFUSAL', utc()))
            bucket_rows.append({'bucket': bucket, 'result': 'NOT-RUN-SELECTION-REFUSAL',
                                'tests_run': 0, 'cause': str(error)})
            event({'phase': 'selection-refusal', 'bucket': bucket, 'cause': str(error)})
            continue
        safe = bucket.replace(':', '-').replace('.', '-')
        log = work / (safe + '-LOG.txt')
        result_path = work / (safe + '-RESULT.json')
        event({'phase': 'bucket-start', 'bucket': bucket, 'position': index + 1})
        log_fd = os.open(log, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        timed_out = False
        with os.fdopen(log_fd, 'wb') as output:
            try:
                child = subprocess.run(
                    worker_command(bucket, run_id),
                    stdin=subprocess.DEVNULL, stdout=output, stderr=subprocess.STDOUT,
                    cwd=ROOT, timeout=timeout_seconds, check=False)
                exit_code = child.returncode
            except subprocess.TimeoutExpired:
                timed_out = True
                exit_code = None
        if result_path.exists():
            try:
                raw = exact(result_path)
                result = json.loads(raw)
                validate_worker_result(result, bucket, run_id, ids, exit_code, timed_out)
                rows.extend(result['cases'])
                bucket_rows.append({'bucket': bucket, 'result': result['result'],
                                    'tests_run': result['tests_run'],
                                    'all_methods_executed': result['all_methods_executed'],
                                    'exact_case_set': result['exact_case_set'],
                                    'entry_guard_passed': result['entry_guard_passed'],
                                    'exit_guard_passed': result['exit_guard_passed'],
                                    'worker_result_sha256': sha(raw),
                                    'worker_exit_code': exit_code, 'timed_out': timed_out,
                                    'log_sha256': sha(exact(log))})
            except (ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
                rows.extend(synthetic(ids, 'WORKER-RESULT-REFUSED', utc()))
                bucket_rows.append({'bucket': bucket, 'result': 'WORKER-RESULT-REFUSED',
                                    'tests_run': 0, 'worker_exit_code': exit_code,
                                    'timed_out': timed_out, 'cause': str(error),
                                    'log_sha256': sha(exact(log))})
        else:
            status = 'NOT-RUN-WORKER-TIMEOUT' if timed_out else 'NOT-RUN-WORKER-EXIT'
            rows.extend(synthetic(ids, status, utc()))
            bucket_rows.append({'bucket': bucket, 'result': status, 'tests_run': 0,
                                'worker_exit_code': exit_code, 'timed_out': timed_out,
                                'log_sha256': sha(exact(log))})
        try:
            selected_inventory(selection_sha)
        except BaseException as error:
            stopped_for_selection = True
            bucket_rows[-1]['selection_refused_after_bucket'] = str(error)
        event({'phase': 'bucket-terminal', **bucket_rows[-1]})
    stream.close()
    all_ids = [identity for ids in buckets.values() for identity in ids]
    if len(rows) != len(all_ids) or [row['id'] for row in rows] != all_ids:
        raise ValueError('serial aggregation lacks exact 345 ordered IDs')
    try:
        selected_inventory(selection_sha)
        selection_unchanged = True
    except BaseException:
        selection_unchanged = False
    passed = (selection_unchanged and max_buckets == 21
              and all(item['result'] == 'PASS' and item['executed'] for item in rows)
              and all(item['result'] == 'PASS' and item['all_methods_executed']
                      and item['exact_case_set'] and item['entry_guard_passed']
                      and item['exit_guard_passed'] and item['worker_exit_code'] == 0
                      and not item['timed_out'] and not item.get('selection_refused_after_bucket')
                      for item in bucket_rows))
    receipt = {
        'schema_version': 'lab-T16-API53-selected-ABI-inherited-regression/v1',
        'run_id': run_id, 'source_manifest_sha256': SOURCE_SHA,
        'profile_sha256': PROFILE_SHA, 'inventory_sha256': INVENTORY_SHA,
        'worker_sha256': WORKER_SHA, 'coordinator_sha256': sha(exact(Path(__file__).absolute())),
        'runner_selection_sha256': selection_sha,
        'installation_receipt_sha256': INSTALL_RECEIPT_SHA,
        'dependency_selection_sha256': DEPENDENCY_SELECTION_SHA,
        'loader_sha256': LOADER_SHA, 'python_sha256': PYTHON_SHA,
        'started_at_utc': started, 'ended_at_utc': utc(),
        'serial_fresh_process_per_class': True,
        'selected_bucket_count': 21, 'selected_case_count': 345,
        'attempted_bucket_limit': max_buckets,
        'selection_unchanged_at_completion': selection_unchanged,
        'bucket_results': bucket_rows, 'cases': rows,
        'executed_method_count': sum(item['executed'] for item in rows),
        'pass_method_count': sum(item['result'] == 'PASS' and item['executed'] for item in rows),
        'result': 'PASS' if passed else 'INCOMPLETE-OR-FAIL',
        't15_final_family_frozen': False,
        't16_qualified': False,
        'authority_effect': 'none',
        'claim_ceiling': 'Provisional API53 serial regression only; full T16 requires final T15 cut and every actual method PASS.',
        'events_sha256': sha(exact(events)),
    }
    target = work / 'SERIAL-RESULT.json'
    file_new(target, (json.dumps(receipt, sort_keys=True, indent=2) + '\n').encode())
    print(json.dumps({'result': receipt['result'], 'executed': receipt['executed_method_count'],
                      'passed': receipt['pass_method_count'], 'selected': 345,
                      'receipt': str(target), 'sha256': sha(exact(target))}, sort_keys=True))
    return passed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--run-id')
    parser.add_argument('--max-buckets', type=int, default=21)
    parser.add_argument('--timeout-seconds', type=int, default=14400)
    parser.add_argument('--selection-sha256', required=True)
    args = parser.parse_args()
    buckets = selected_inventory(args.selection_sha256)
    if args.dry_run:
        print(json.dumps({'source_sha256': SOURCE_SHA, 'profile_sha256': PROFILE_SHA,
                          'buckets': len(buckets), 'cases': sum(len(ids) for ids in buckets.values()),
                          'serial_fresh_process_per_class': True}, sort_keys=True))
        return 0
    if args.run_id is None:
        parser.error('--run-id is required for execution')
    return 0 if run(args.run_id, args.max_buckets, args.timeout_seconds,
                    args.selection_sha256) else 1


if __name__ == '__main__':
    raise SystemExit(main())
