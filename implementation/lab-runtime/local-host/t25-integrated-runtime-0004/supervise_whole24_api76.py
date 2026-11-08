"""Bounded installed API76 observation of all 24 current-family relations."""

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
        'observer': root / 'implementation/lab-runtime/local-host/t25-integrated-runtime-0004/qualify_relation_closure_0002.py',
        'source': root / manifest['binding_paths']['api.source'],
        'profile': root / manifest['binding_paths']['api.profile'],
    }
    for name in ('launcher', 'observer'):
        path = paths[name]
        relative = path.relative_to(root).as_posix()
        need(path.is_file() and not path.is_symlink() and relative in members
             and sha(path) == members[relative]['sha256'], 'installed ' + name + ' differs')
    for name, pin in (('source', args.source_sha256), ('profile', args.profile_sha256)):
        path = paths[name]
        need(path.is_file() and not path.is_symlink() and sha(path) == pin,
             'installed ' + name + ' differs')
    private = root.parent / '.cal-runtime'
    ready = json.loads((private / 'installation.json').read_bytes())
    need(ready['phase'] == 'ready' and ready['package_manifest_sha256'] == args.package_sha256,
         'installed runtime not ready')
    install_result = private / 'INSTALLATION-RESULT.json'
    need(install_result.is_file() and not install_result.is_symlink(),
         'installed cold result missing')
    receipt = json.loads(install_result.read_bytes())
    need(receipt['result'] == 'PASS-fresh-installed-API-cold'
         and receipt['package_manifest_sha256'] == args.package_sha256
         and receipt['API_observation']['source_sha256'] == args.source_sha256
         and receipt['API_observation']['profile_sha256'] == args.profile_sha256,
         'cold installed API selection differs')
    return root, output, paths, install_result, receipt


def cold_receipt_unchanged(path, initial_sha256, initial_cut):
    need(path.is_file() and not path.is_symlink() and sha(path) == initial_sha256,
         'installed cold receipt changed during whole24')
    current = json.loads(path.read_bytes())
    need(current['API_observation']['source_cut'] == initial_cut,
         'installed cold Source cut changed during whole24')


def run(args):
    need(60 <= args.timeout_seconds <= 7200, 'bounded whole24 timeout required')
    root, output, paths, install_result, installed = selected(args)
    output.mkdir(mode=0o700)
    write_once(output / 'SELECTION.json', {
        'schema_version': 'lab-api76-installed-whole24-selection/v1',
        'package_sha256': args.package_sha256, 'source_sha256': args.source_sha256,
        'profile_sha256': args.profile_sha256, 'launcher_sha256': sha(paths['launcher']),
        'observer_sha256': sha(paths['observer']), 'installation_result_sha256': sha(install_result),
        'supervisor_sha256': sha(__file__), 'relation_count': 24, 'authority_effect': 'none'})
    argv = [str(paths['launcher']), '-B', str(paths['observer'])]
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
                raise TimeoutError('installed whole24 exceeded selected timeout') from error
        need(code == 0, 'installed whole24 process failed')
        lines = (output / 'stdout.log').read_text().splitlines()
        need(len(lines) == 1, 'whole24 output must be exactly one JSON result line')
        result = json.loads(lines[0])
        need(result['result'] == 'PASS-exact-live-24-current-family-relations'
             and result['api_source_sha256'] == args.source_sha256
             and result['api_profile_sha256'] == args.profile_sha256
             and result['observer_sha256'] == sha(paths['observer'])
             and result['actual_source_cut'] == installed['API_observation']['source_cut']
             and result['relation_count'] == len(result['relation_versions'])
             == len(result['original_observations']) == 24
             and result['indexed_mapped_original_count'] == result['retained_stream_relation_count'] == 12
             and result['actual_original_bytes_and_endpoint_headers_checked'] is True
             and result['unexpected_same_family_missing_and_duplicate_refused'] is True
             and result['Source_or_callbacks_mutated'] is False
             and result['canonical_admissions'] == 0 and result['authority_effect'] == 'none',
             'whole24 terminal result or selected cut differs')
        _, _, _, final_install_result, _ = selected(args, require_new=False)
        cold_receipt_unchanged(final_install_result,
                               json.loads((output / 'SELECTION.json').read_bytes())['installation_result_sha256'],
                               result['actual_source_cut'])
        write_once(output / 'RELATION-CLOSURE-24-RESULT.json', result)
        terminal = {'schema_version': 'lab-api76-installed-whole24-result/v1',
                    'result': 'PASS-exact-installed-whole24', 'exit_code': code,
                    'selection_sha256': sha(output / 'SELECTION.json'),
                    'observation_sha256': sha(output / 'RELATION-CLOSURE-24-RESULT.json'),
                    'stdout_sha256': sha(output / 'stdout.log'),
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
            'result': 'FAIL-original-whole24-evidence-retained',
            'exception_class': type(error).__name__, 'cause': str(error),
            'exit_code': code, 'ended_at_utc': utc(), 'authority_effect': 'none'})
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for field in ('repository', 'output', 'package-sha256', 'source-sha256', 'profile-sha256'):
        parser.add_argument('--' + field, required=True)
    parser.add_argument('--timeout-seconds', type=int, default=7200)
    print(json.dumps(run(parser.parse_args()), sort_keys=True), flush=True)
