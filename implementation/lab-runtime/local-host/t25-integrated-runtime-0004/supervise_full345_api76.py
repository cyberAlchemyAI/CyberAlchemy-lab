"""Bounded external supervisor for one installed API76 345-method regression."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess


REPOSITORY = Path(__file__).resolve().parents[4]
API76 = 'product/lab/release-candidates/v1/interface/api-integration-v76-current-repairs-0001'


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def utc():
    return datetime.now(timezone.utc).isoformat()


def write_once(path, value):
    raw = (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()
    handle = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(handle, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def selected(args, *, require_new=True):
    root = Path(args.repository).absolute()
    output = Path(args.output).absolute()
    need(root.is_dir() and not root.is_symlink() and not any(path.is_symlink() for path in root.parents),
         'unlinked installed repository required')
    need(output.parent.is_dir() and not any(path.is_symlink() for path in output.parents)
         and not output.is_relative_to(REPOSITORY) and not output.is_relative_to(root.parent.parent),
         'private output outside source and installation required')
    if require_new:
        need(not output.exists() and not output.is_symlink(), 'fresh private output required')
    for pin in (args.package_sha256, args.source_sha256, args.profile_sha256):
        need(bool(re.fullmatch('[a-f0-9]{64}', pin)), 'exact lowercase digest required')
    need(bool(re.fullmatch('[a-z][a-z0-9-]{0,31}', args.run_id)),
         'bounded unique regression run id required')
    manifest_path = root / '.cal-package-manifest.json'
    need(manifest_path.is_file() and not manifest_path.is_symlink()
         and sha(manifest_path) == args.package_sha256, 'installed package manifest differs')
    manifest = json.loads(manifest_path.read_bytes())
    need(manifest['entrypoint']['api_directory'] == API76
         and manifest['binding_paths']['api.source'] == API76 + '/source-manifest.json'
         and manifest['binding_paths']['api.profile'] == API76 + '/contract-profile.json',
         'selected installed API76 binding differs')
    members = {row.get('repository_path', row['path']): row for row in manifest['members']
               if row.get('namespace_path') is None}
    need(len(members) == sum(row.get('namespace_path') is None for row in manifest['members']),
         'duplicate installed repository member')
    paths = {
        'launcher': root / 'implementation/lab-runtime/local-host/t25-native-launcher-0001/selected-python',
        'coordinator': root / 'implementation/lab-runtime/local-host/t25-integrated-runtime-0004/regression.py',
        'worker': root / 'implementation/lab-runtime/local-host/t25-integrated-runtime-0004/regression_worker.py',
        'source': root / manifest['binding_paths']['api.source'],
        'profile': root / manifest['binding_paths']['api.profile'],
    }
    for name in ('launcher', 'coordinator', 'worker'):
        path = paths[name]
        relative = path.relative_to(root).as_posix()
        need(path.is_file() and not path.is_symlink() and relative in members
             and sha(path) == members[relative]['sha256'], 'installed ' + name + ' differs')
    for name, pin in (('source', args.source_sha256), ('profile', args.profile_sha256)):
        path = paths[name]
        need(path.is_file() and not path.is_symlink() and sha(path) == pin,
             'installed ' + name + ' differs')
    private = root.parent / '.cal-runtime'
    ready_path = private / 'installation.json'
    need(ready_path.is_file() and not ready_path.is_symlink(), 'ready installation receipt required')
    ready = json.loads(ready_path.read_bytes())
    need(ready['phase'] == 'ready' and ready['package_manifest_sha256'] == args.package_sha256,
         'installed runtime not ready')
    if require_new:
        need(not (private / 'regression' / args.run_id).exists(), 'regression run id already exists')
    paths['ready'] = ready_path
    return root, output, private, paths


def run(args):
    need(60 <= args.timeout_seconds <= 65000, 'bounded full-suite timeout required')
    root, output, private, paths = selected(args)
    output.mkdir(mode=0o700)
    write_once(output / 'SELECTION.json', {
        'schema_version': 'lab-api76-installed-full345-selection/v1',
        'package_sha256': args.package_sha256, 'source_sha256': args.source_sha256,
        'profile_sha256': args.profile_sha256, 'launcher_sha256': sha(paths['launcher']),
        'coordinator_sha256': sha(paths['coordinator']), 'worker_sha256': sha(paths['worker']),
        'installation_ready_sha256': sha(paths['ready']),
        'supervisor_sha256': sha(__file__), 'run_id': args.run_id,
        'method_count': 345, 'bucket_count': 21, 'authority_effect': 'none'})
    argv = [str(paths['launcher']), '-B', str(paths['coordinator']), '--run-id', args.run_id,
            '--workers', '1', '--timeout-seconds', '14400']
    process = None
    code = None
    try:
        with (output / 'stdout.log').open('xb') as stdout, (output / 'stderr.log').open('xb') as stderr:
            process = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                       cwd=root, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'),
                                       start_new_session=True)
            write_once(output / 'PROCESS.json', {'pid': process.pid, 'process_group': process.pid,
                                                 'argv': argv, 'started_at_utc': utc(),
                                                 'authority_effect': 'none'})
            try:
                code = process.wait(timeout=args.timeout_seconds)
            except subprocess.TimeoutExpired as error:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                code = process.wait(timeout=30)
                raise TimeoutError('installed full345 exceeded selected timeout') from error
        regression_root = private / 'regression' / args.run_id
        receipt_path = regression_root / 'REGRESSION-RESULT.json'
        need(code == 0 and receipt_path.is_file() and not receipt_path.is_symlink(),
             'installed full345 process failed or receipt missing')
        receipt = json.loads(receipt_path.read_bytes())
        need(receipt['result'] == 'PASS' and receipt['full_suite_selected'] is True
             and receipt['run_id'] == args.run_id and receipt['max_concurrency'] == 1
             and receipt['worker_sha256'] == sha(paths['worker'])
             and receipt['selection_sha256'] == sha(regression_root / 'SELECTION.json')
             and receipt['selected_method_count'] == receipt['executed_method_count']
             == receipt['pass_method_count'] == 345
             and receipt['selected_bucket_count'] == len(receipt['bucket_results']) == 21
             and receipt['source_sha256'] == args.source_sha256
             and receipt['profile_sha256'] == args.profile_sha256
             and receipt['exact_case_set'] is True and receipt['selection_unchanged'] is True
             and receipt['authority_effect'] == 'none' and receipt['t16_qualified'] is False
             and all(row['status'] == 'PASS' for row in receipt['bucket_results']),
             'installed full345 terminal result differs')
        selected(args, require_new=False)
        need(sha(paths['ready']) == json.loads((output / 'SELECTION.json').read_bytes())['installation_ready_sha256'],
             'installed ready receipt changed during full345')
        terminal = {'schema_version': 'lab-api76-installed-full345-result/v1',
                    'result': 'PASS-actual-installed-345-maintained-methods',
                    'exit_code': code, 'selection_sha256': sha(output / 'SELECTION.json'),
                    'receipt_sha256': sha(receipt_path), 'stdout_sha256': sha(output / 'stdout.log'),
                    'stderr_sha256': sha(output / 'stderr.log'), 'ended_at_utc': utc(),
                    'authority_effect': 'none'}
        write_once(output / 'PROCESS-RESULT.json', terminal)
        return terminal
    except BaseException as error:
        if process is not None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            if process.poll() is None:
                process.wait(timeout=30)
        write_once(output / 'FAILED-RETAINED.json', {
            'result': 'FAIL-original-regression-evidence-retained',
            'exception_class': type(error).__name__, 'cause': str(error),
            'exit_code': code, 'ended_at_utc': utc(), 'authority_effect': 'none'})
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for field in ('repository', 'output', 'package-sha256', 'source-sha256', 'profile-sha256', 'run-id'):
        parser.add_argument('--' + field, required=True)
    parser.add_argument('--timeout-seconds', type=int, default=65000)
    print(json.dumps(run(parser.parse_args()), sort_keys=True), flush=True)
