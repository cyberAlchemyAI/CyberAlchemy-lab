"""Fresh installed T03 first/later/consumer replay with retained terminal evidence.

This runner is intentionally inert until an installed successor selection file is
provided. Run one phase per process; the caller itself creates fresh operation
keys and private workspaces. Never point this at a prior evidence root.
"""
import argparse
import hashlib
import json
import os
import signal
import stat
import subprocess
from datetime import datetime, timezone
from pathlib import Path

OLD = Path('/home/vlad_/.local/share/cyberalchemy-lab/t03-installed-learning-evidence-20261026-0001')
RESULTS = {
    'first': ('first_run.py', 'FIRST-SESSION.json', 'PASS-local-current-one-Lesson-selection-and-close'),
    'later': ('later_run.py', 'LATER-SESSION.json', 'PASS-local-current-Lesson-later-application-independent-assessment'),
    'consumer': ('consume_run.py', 'CONSUMER-SESSION.json', 'PASS-local-assessed-result-later-Session-consumption-and-close'),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_new(path, value):
    raw = (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as out:
        out.write(raw)
        out.flush()
        os.fsync(out.fileno())


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def under(path, root):
    return path == root or root in path.parents


def validate_selection(path):
    value = json.loads(path.read_bytes())
    require(set(value) == {'schema_version', 'installation_repository', 'evidence_root',
                           'api_source_ref', 'api_source_sha256', 'profile_ref',
                           'profile_sha256', 'package_manifest_sha256',
                           'caller_dir', 'caller_bindings',
                           'first_emitter_code', 'first_emitter_sha256'},
            'closed fresh replay selection required')
    require(value['schema_version'] == 'lab-t03-fresh-installed-replay-selection/v1',
            'fresh replay selection version differs')
    repo = Path(value['installation_repository'])
    base = Path(value['evidence_root'])
    caller = Path(value['caller_dir'])
    require(all(p.is_absolute() for p in (repo, base, caller)) and
            all('..' not in p.parts for p in (repo, base, caller)),
            'absolute normalized installed/caller/evidence paths required')
    require(repo.is_dir() and not under(repo, OLD) and 'final-local-product-20261026-0003' not in str(repo),
            'fresh installed successor repository required')
    package_path = repo / '.cal-package-manifest.json'
    require(package_path.is_file() and not package_path.is_symlink()
            and sha(package_path) == value['package_manifest_sha256'],
            'installed package manifest bytes differ')
    package = json.loads(package_path.read_bytes())
    source_ref, profile_ref = value['api_source_ref'], value['profile_ref']
    require(type(source_ref) is str and type(profile_ref) is str
            and Path(source_ref).parent == Path(profile_ref).parent
            and Path(source_ref).parent.name.startswith('api-integration-v76-')
            and package['entrypoint']['api_directory'] == str(Path(source_ref).parent)
            and package['binding_paths']['api.source'] == source_ref
            and package['binding_paths']['api.profile'] == profile_ref,
            'installed package does not select exact API76 source/profile paths')
    require(source_ref in package['generated_metadata_paths']
            and profile_ref in package['generated_metadata_paths'],
            'selected generated source/profile omitted from installed package metadata closure')
    require(not under(base, OLD) and base != OLD and base.parent.is_dir()
            and not any(part.is_symlink() for part in base.parents),
            'fresh private evidence root required')
    require(caller.is_dir() and caller == repo / 'implementation/lab-runtime/local-host/t03-installed-learning-caller-0005',
            'reviewed first-emitter-capable T03 caller required')
    emitter = Path(value['first_emitter_code'])
    require(emitter == repo / 'implementation/lab-runtime/local-host/t31-native-first-emitter-0002/native_first_emitter.py'
            and emitter.is_absolute() and emitter.is_file() and not emitter.is_symlink()
            and sha(emitter) == value['first_emitter_sha256'],
            'reviewed native first-emitter adapter bytes differ')
    for ref, digest in ((value['api_source_ref'], value['api_source_sha256']),
                        (value['profile_ref'], value['profile_sha256'])):
        file = repo / ref
        require(type(ref) is str and not Path(ref).is_absolute() and '..' not in Path(ref).parts
                and len(digest) == 64 and file.is_file() and not file.is_symlink()
                and sha(file) == digest, 'selected installed source/profile bytes differ')
    py = repo / 'implementation/lab-runtime/local-host/t25-native-launcher-0001/selected-python'
    require(py.is_file() and os.access(py, os.X_OK), 'installed selected Python launcher absent')
    actual = {p.name: sha(p) for p in sorted(caller.glob('*.py')) if p.is_file() and not p.is_symlink()}
    require(value['caller_bindings'] == actual and len(actual) >= 6,
            'reviewed caller bytes differ')
    members = {row['path']: row['sha256'] for row in package['members']}
    for path in [emitter, *sorted(caller.glob('*.py'))]:
        require(not path.is_symlink()
                and members.get(str(path.relative_to(repo))) == sha(path),
                'installed caller/emitter bytes outside selected package members')
    return value, repo, base, caller, py


def parent_receipt(base, phase, selection):
    if phase == 'first':
        return None, None
    previous = 'first' if phase == 'later' else 'later'
    receipt = base / previous / RESULTS[previous][1]
    process = base / (previous + '.PROCESS-RESULT.json')
    cold_path = base / (previous + '.COLD-READBACK.json')
    require(receipt.is_file() and process.is_file() and cold_path.is_file(),
            'prior phase terminal/cold originals absent')
    row = json.loads(receipt.read_bytes())
    prior = json.loads(process.read_bytes())
    cold = json.loads(cold_path.read_bytes())
    require(row.get('result') == RESULTS[previous][2] and prior['exit_code'] == 0
            and prior['passed'] is True
            and prior['terminal_receipt_sha256'] == sha(receipt)
            and prior['api_source_sha256'] == selection['api_source_sha256']
            and prior['profile_sha256'] == selection['profile_sha256']
            and prior['package_manifest_sha256'] == selection['package_manifest_sha256']
            and cold['passed'] is True
            and cold['process_result_sha256'] == sha(process)
            and cold['phase_originals'][receipt.name]['sha256'] == sha(receipt)
            and cold['terminal_result'] == RESULTS[previous][2],
            'prior phase did not pass under this installed source/profile')
    return receipt, sha(receipt)


def cold_inventory(phase_dir):
    rows = {}
    for path in sorted(phase_dir.rglob('*')):
        require(not path.is_symlink(), 'linked evidence path refused')
        if path.is_file():
            rows[str(path.relative_to(phase_dir))] = {'sha256': sha(path),
                'size_bytes': path.stat().st_size}
    return rows


def inspect_inventory(phase_dir):
    return {p.name: sha(p) for p in sorted(phase_dir.glob('*-inspect-reply.json'))}


def stop_group(child):
    if child.poll() is None:
        try:
            os.killpg(child.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    child.wait()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--selection', required=True)
    ap.add_argument('--phase', required=True, choices=RESULTS)
    ap.add_argument('--child-timeout-seconds', type=int, default=10800)
    args = ap.parse_args()
    require(3600 <= args.child_timeout_seconds <= 21600, 'bounded native phase timeout required')
    selection_path = Path(args.selection)
    require(selection_path.is_absolute() and selection_path.is_file(), 'absolute selection file required')
    selection, repo, base, caller, python = validate_selection(selection_path)
    selection_digest = sha(selection_path)
    if args.phase == 'first':
        require(not base.exists(), 'fresh evidence root already exists')
        base.mkdir(mode=0o700)
        write_new(base / 'SELECTION.json', selection)
        write_new(base / 'SELECTION-PIN.json', {'sha256': selection_digest,
                                                'authority_effect': 'none'})
    else:
        require(base.is_dir() and stat.S_IMODE(base.stat().st_mode) == 0o700
                and json.loads((base / 'SELECTION.json').read_bytes()) == selection
                and json.loads((base / 'SELECTION-PIN.json').read_bytes())['sha256'] == selection_digest,
                'fresh replay selection changed between phases')
    prior, prior_sha = parent_receipt(base, args.phase, selection)
    script, terminal_name, expected = RESULTS[args.phase]
    phase_dir = base / args.phase
    require(not phase_dir.exists(), 'phase evidence root already exists')
    target = phase_dir / terminal_name
    stdout = base / (args.phase + '.stdout.log')
    stderr = base / (args.phase + '.stderr.log')
    command = [str(python), '-B', str(caller / script), '--evidence', str(phase_dir)]
    if args.phase == 'first':
        command.extend(['--first-emitter-code', selection['first_emitter_code'],
                        '--first-emitter-sha256', selection['first_emitter_sha256']])
    if prior is not None:
        command.extend(['--first-receipt' if args.phase == 'later' else '--later-receipt', str(prior)])
    started = datetime.now(timezone.utc).isoformat()
    fdout = os.open(stdout, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    fderr = os.open(stderr, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fdout, 'wb') as out, os.fdopen(fderr, 'wb') as err:
        try:
            child = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                     cwd=repo, start_new_session=True)
            try:
                exit_code = child.wait(timeout=args.child_timeout_seconds)
                timed_out = False
            except subprocess.TimeoutExpired:
                stop_group(child)
                exit_code = None
                timed_out = True
        except BaseException:
            if 'child' in locals() and child.poll() is None:
                stop_group(child)
            raise
        out.flush(); os.fsync(out.fileno())
        err.flush(); os.fsync(err.fileno())
    terminal = json.loads(target.read_bytes()) if target.is_file() else None
    passed = (exit_code == 0 and terminal is not None and terminal.get('result') == expected
              and terminal.get('api_source_binding', {}).get('sha256') == selection['api_source_sha256']
              and terminal.get('profile_binding', {}).get('sha256') == selection['profile_sha256'])
    if passed and args.phase == 'first':
        emission = terminal.get('native_first_emission') or {}
        emission_path = Path(emission.get('receipt_path', ''))
        passed = (emission.get('posture') == 'produced-uncommitted'
                  and emission.get('formal_output_count') == 3
                  and emission.get('adapter_sha256') == selection['first_emitter_sha256']
                  and under(emission_path, phase_dir)
                  and emission_path.is_file()
                  and sha(emission_path) == emission.get('receipt_sha256'))
    process = {'phase': args.phase, 'started_at_utc': started,
               'ended_at_utc': datetime.now(timezone.utc).isoformat(),
               'exit_code': exit_code, 'timed_out': timed_out, 'passed': passed,
               'terminal_receipt_path': str(target) if terminal is not None else None,
               'terminal_receipt_sha256': sha(target) if terminal is not None else None,
               'stdout_sha256': sha(stdout), 'stderr_sha256': sha(stderr),
               'prior_receipt_sha256': prior_sha,
               'selection_sha256': selection_digest,
               'api_source_sha256': selection['api_source_sha256'],
               'profile_sha256': selection['profile_sha256'],
               'package_manifest_sha256': selection['package_manifest_sha256'],
               'first_emitter_sha256': selection['first_emitter_sha256'],
               'operation_inspect_reply_sha256': inspect_inventory(phase_dir) if phase_dir.exists() else {},
               'authority_effect': 'none'}
    write_new(base / (args.phase + '.PROCESS-RESULT.json'), process)
    cold = {'phase': args.phase, 'process_result_sha256': sha(base / (args.phase + '.PROCESS-RESULT.json')),
            'phase_originals': cold_inventory(phase_dir) if phase_dir.exists() else {},
            'operation_inspect_reply_sha256': process['operation_inspect_reply_sha256'],
            'terminal_result': terminal.get('result') if terminal is not None else None,
            'passed': passed, 'private_originals_retained': True,
            'authority_effect': 'none'}
    write_new(base / (args.phase + '.COLD-READBACK.json'), cold)
    print(json.dumps({'phase': args.phase, 'passed': passed, 'process_result': str(base / (args.phase + '.PROCESS-RESULT.json')),
                      'cold_readback': str(base / (args.phase + '.COLD-READBACK.json'))}, sort_keys=True), flush=True)
    if not passed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
