"""Serial fresh-process accounting for every inherited API52 method.

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
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v52-t16-metadata-current-0001'
SOURCE_SHA = '060b501c32bb9cc3292f0e2a3124a89770ab5f69c6a749a823c466660dc96020'
PROFILE_SHA = '5da736d675d92e9fc72b1a197eea27d449610b2be8c621075aec81380fcb9c12'
INVENTORY = ROOT / 'implementation/lab-runtime/local-host/t16-api49-provisional-regression-0001/INVENTORY-0001.json'
INVENTORY_SHA = 'bd83d446316e30a912616eb55552ae2935305b206c6400c8e067501f0912f3f3'
WORKER = HERE / 'run_bucket.py'
WORKER_SHA = '182455f97a49fd042d6898ff95215ed225f43921bd0fe74eea9ce751ca4dd6af'
SELECTION = HERE / 'RUNNER-SELECTION-0001.json'


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
        'schema_version': 'lab-T16-API52-serial-runner-selection/v1',
        'source_sha256': SOURCE_SHA, 'profile_sha256': PROFILE_SHA,
        'inventory_sha256': INVENTORY_SHA, 'worker_sha256': WORKER_SHA,
        'coordinator_sha256': sha(exact(Path(__file__).absolute())),
        'selected_class_count': 21, 'selected_method_count': 345,
        'serial_fresh_process_per_class': True,
    }:
        raise ValueError('externally selected serial runner differs')
    exact(API / 'source-manifest.json', SOURCE_SHA)
    exact(API / 'contract-profile.json', PROFILE_SHA)
    exact(WORKER, WORKER_SHA)
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


def run(run_id, max_buckets, timeout_seconds, selection_sha):
    if not re.fullmatch(r'[a-z][a-z0-9-]{0,31}', run_id):
        raise ValueError('closed run identity required')
    if not 1 <= max_buckets <= 21 or not 60 <= timeout_seconds <= 3600:
        raise ValueError('bounded serial execution parameters required')
    buckets = selected_inventory(selection_sha)
    os.umask(0o077)
    work = HERE / 'working' / run_id
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
                    [sys.executable, '-I', '-B', str(WORKER), '--bucket', bucket,
                     '--run-id', run_id, '--runner-sha256', WORKER_SHA],
                    stdin=subprocess.DEVNULL, stdout=output, stderr=subprocess.STDOUT,
                    cwd=ROOT, timeout=timeout_seconds, check=False)
                exit_code = child.returncode
            except subprocess.TimeoutExpired:
                timed_out = True
                exit_code = None
        if result_path.exists():
            raw = exact(result_path)
            result = json.loads(raw)
            if (result['bucket'] != bucket or result['run_id'] != run_id
                    or result['selected_ids'] != ids or result['source_sha256'] != SOURCE_SHA
                    or result['profile_sha256'] != PROFILE_SHA or result['runner_sha256'] != WORKER_SHA
                    or len(result['cases']) != len(ids)
                    or [item['id'] for item in result['cases']] != ids):
                raise ValueError('worker result selection or case set differs: ' + bucket)
            rows.extend(result['cases'])
            bucket_rows.append({'bucket': bucket, 'result': result['result'],
                                'tests_run': result['tests_run'],
                                'all_methods_executed': result['all_methods_executed'],
                                'worker_result_sha256': sha(raw),
                                'worker_exit_code': exit_code, 'timed_out': timed_out,
                                'log_sha256': sha(exact(log))})
        else:
            status = 'NOT-RUN-WORKER-TIMEOUT' if timed_out else 'NOT-RUN-WORKER-EXIT'
            rows.extend(synthetic(ids, status, utc()))
            bucket_rows.append({'bucket': bucket, 'result': status, 'tests_run': 0,
                                'worker_exit_code': exit_code, 'timed_out': timed_out,
                                'log_sha256': sha(exact(log))})
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
              and all(item['result'] == 'PASS' and item['all_methods_executed'] for item in bucket_rows))
    receipt = {
        'schema_version': 'lab-T16-API52-serial-inherited-regression/v1',
        'run_id': run_id, 'source_manifest_sha256': SOURCE_SHA,
        'profile_sha256': PROFILE_SHA, 'inventory_sha256': INVENTORY_SHA,
        'worker_sha256': WORKER_SHA, 'coordinator_sha256': sha(exact(Path(__file__).absolute())),
        'runner_selection_sha256': selection_sha,
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
        'claim_ceiling': 'Provisional API52 serial regression only; full T16 requires final T15 cut and every actual method PASS.',
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
    parser.add_argument('--timeout-seconds', type=int, default=3600)
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
