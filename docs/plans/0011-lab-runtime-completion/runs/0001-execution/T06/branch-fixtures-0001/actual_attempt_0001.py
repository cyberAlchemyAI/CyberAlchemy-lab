"""One expressly permitted real T06 attempt; report contains no private bodies."""
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import time
import traceback
from types import SimpleNamespace

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
INTERFACE = ROOT / 'product/lab/release-candidates/v1/interface'
RUN = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
HERE = RUN / 'T06/branch-fixtures-0001'
DRIVER = HERE / 'revision-0003'
API = INTERFACE / 'api-integration-v17'
INSTALL = INTERFACE / 'runtime-dependencies-v2-completion-0001/installations/0004'
SOURCE_SHA = 'a909f378b8a1c5f6f02fe6bcbafa56da7f2fe873a3865ab7853b443d57b249f2'
PROFILE_SHA = 'f5b411e7b59b9b50ac46dd7372aad086001dcabd214bf8eb639f8ab826886429'
DRIVER_SHA = '18761ff01edd53eb67c68d04e043d5a12b38426fe82d94c43bc7e04aeb40e539'
SDK_SHA = '15cd8e4e863d110c0da025091220f6efdc7fee8509b001c5bbee816307cfdabd'
PROVISION_SHA = '81920701206b6e8556b973c975c0c6dd00fb83c2f21a3bea42b472d834cb117d'
GUARD_SHA = '65ba71adb3b885f6fedc268be29f982f1f03139265f00a7e9ed08ff19b6adeb3'
DEPENDENCY_SHA = '2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def need(value, reason):
    if not value:
        raise ValueError(reason)


def captured_module(name, path, expected):
    raw = path.read_bytes()
    need(sha(raw) == expected and not any(p.is_symlink() for p in (path, *path.parents)), 'selected exact code bytes differ')
    spec = importlib.util.spec_from_loader(name, loader=None, origin=str(path))
    module = importlib.util.module_from_spec(spec); module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def dependency_guard():
    selection_path = RUN / 'T07/revision-0002/dependency-selection-0002.json'
    raw = selection_path.read_bytes(); need(sha(raw) == DEPENDENCY_SHA, 'independent full dependency selection differs')
    selected = json.loads(raw)
    rows = {r['destination']: {'sha256': r['sha256'], 'size_bytes': r['size_bytes'],
                             'mode': 0o755 if r['kind'] in {'interpreter', 'native-executable'} else 0o644}
            for r in selected['inputs']}
    rows.update(selected['wheel_members']); rows['lib/abi/ld-linux-x86-64.so.2']['mode'] = 0o755
    need(len(rows) == 1010, 'full installed closure required')
    for name, row in rows.items():
        path = INSTALL / name
        need(not any(p.is_symlink() for p in (path, *path.parents)), 'unsafe selected dependency')
        before = path.lstat()
        need(stat.S_ISREG(before.st_mode) and before.st_uid == os.getuid()
             and stat.S_IMODE(before.st_mode) == row['mode'] and before.st_size == row['size_bytes'], 'selected dependency identity differs')
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        try:
            actual = os.fstat(fd); need((actual.st_dev, actual.st_ino, actual.st_mtime_ns, actual.st_ctime_ns)
                                        == (before.st_dev, before.st_ino, before.st_mtime_ns, before.st_ctime_ns), 'dependency attachment differs')
            digest = hashlib.sha256()
            while chunk := os.read(fd, 1024 * 1024):
                digest.update(chunk)
            after = os.fstat(fd); current = path.lstat()
            fields = lambda x: (x.st_dev, x.st_ino, x.st_mode, x.st_uid, x.st_size, x.st_mtime_ns, x.st_ctime_ns)
            need(fields(before) == fields(after) == fields(current) and digest.hexdigest() == row['sha256'], 'dependency bytes changed')
        finally:
            os.close(fd)
    return {'status': 'PASS', 'installed_files': 1010, 'selection_sha256': DEPENDENCY_SHA}


def save_new(path, value):
    raw = (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
    with path.open('xb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())


def main():
    started = time.monotonic(); report = {'schema_version': 'lab-T06-actual-attempt/v1-candidate', 'attempt': 1,
        'started_at': datetime.now(timezone.utc).isoformat(), 'authority_effect': 'none', 'actual_owner_outcome': None,
        'whole_API_qualified': False, 'task_complete': False, 'private_credentials_public_exported': False,
        'source_sha256': SOURCE_SHA, 'profile_sha256': PROFILE_SHA, 'driver_selection_sha256': DRIVER_SHA,
        'SDK_manifest_sha256': SDK_SHA, 'provisioning_receipt_sha256': PROVISION_SHA, 'events': []}
    state = None; phase = 'entry-dependency-guard'; guard = None
    def event(name, **extra):
        row = {'event': name, 'elapsed_seconds': time.monotonic() - started, **extra}
        report['events'].append(row); print(json.dumps(row, sort_keys=True), flush=True)
    try:
        report['dependencies_entry'] = dependency_guard(); event('all-1010-installed-inputs-entry-PASS')
        guard = captured_module('_T06_actual_selected_guard', API / 'guard.py', GUARD_SHA)
        phase = 'entry-source-guard'; selected = guard.verify(SOURCE_SHA)
        need(sha((API / 'contract-profile.json').read_bytes()) == PROFILE_SHA, 'selected profile differs')
        event('all-27080-current-source-inputs-entry-PASS', historical_physical_closure='REFUSED')
        rows = json.loads((DRIVER / 'driver-selection.json').read_bytes())
        need(sha((DRIVER / 'driver-selection.json').read_bytes()) == DRIVER_SHA, 'driver input selection differs')
        expected = {row['path']: row['sha256'] for row in rows['files']}
        declared = {row['path']: row['sha256'] for row in json.loads((API / 'contract-profile.json').read_bytes())['files']}
        need(all(declared.get(name) == pin for name, pin in expected.items()), 'actual producer or driver outside selected true origin')
        prep_path = DRIVER / 'prepare_branches.py'; driver_path = DRIVER / 'drive_operator.py'
        prep = captured_module('_T06_actual_selected_preparer', prep_path, expected[prep_path.relative_to(ROOT).as_posix()])
        driver = captured_module('_T06_actual_selected_driver', driver_path, expected[driver_path.relative_to(ROOT).as_posix()])
        phase = 'stage-new-independent-candidate-key-custody'
        state = prep.stage_keys(DRIVER / 'driver-selection.json', DRIVER_SHA)
        event('new-candidate-key-custody-staged', private_key_bodies_exported=False)
        phase = 'actual-original-branch-construction'
        record = prep.prepare(state, DRIVER / 'driver-selection.json', DRIVER_SHA, SOURCE_SHA, PROFILE_SHA,
                              RUN / 'lease-sensitive-runtime.lock')
        need(record['original_Action_producer_lease_closed'] is True, 'original preparation lease not closed')
        report['actual_three_branch_construction'] = 'PASS'; report['original_preparation_lease_closed'] = True
        report['same_preparation_Schemas_instance'] = record['same_preparation_Schemas_instance']
        event('three-actual-original-branches-constructed-and-preparation-lease-closed')
        phase = 'actual-SDK-fresh-child-handoff-authentication-and-shutdown'
        args = SimpleNamespace(sdk_directory=str(INTERFACE / 'composite-operator-v1-completion-0001/revision-0003'),
                               sdk_source_sha256=SDK_SHA,
                               provisioning_path='docs/plans/0011-lab-runtime-completion/runs/0001-execution/T34/task-session-result-v4.json',
                               provisioning_sha256=PROVISION_SHA,
                               lease_lock=str(RUN / 'lease-sensitive-runtime.lock'))
        private_log = state / 'driver-private-observer.log'
        fd = os.open(private_log, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'w') as output, redirect_stdout(output), redirect_stderr(output):
            result = driver.run(record, args)
        report['SDK_result'] = result
        event('actual-SDK-full34-startup-authentication-and-owned-shutdown', actual_child_exit=result['process_exit_code'])
        report['status'] = 'PASS-startup-only'; returncode = 0
    except Exception as error:
        report['status'] = 'REFUSED'; report['failed_phase'] = phase
        report['error_class'] = type(error).__name__
        report['error_message_sha256'] = sha(str(error).encode())
        report['frames'] = [{'file': frame.filename, 'line': frame.lineno, 'function': frame.name}
                            for frame in traceback.extract_tb(error.__traceback__)]
        event('actual-attempt-refused', phase=phase, error_class=type(error).__name__)
        returncode = 1
    finally:
        if state is not None:
            # Retain this own state's locator privately for exact later audit;
            # public evidence exports only its independently useful hash.
            custody = {'root': str(state), 'root_identity': [state.stat().st_dev, state.stat().st_ino,
                       state.stat().st_uid, stat.S_IMODE(state.stat().st_mode)], 'attempt': 1}
            fd = os.open(state / 'attempt-observer-custody.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            with os.fdopen(fd, 'wb') as output:
                output.write(json.dumps(custody, sort_keys=True).encode()); output.flush(); os.fsync(output.fileno())
            report['own_custody_locator_sha256'] = sha(str(state).encode())
            report['own_private_state_retained'] = True
        report['dependencies_exit'] = dependency_guard()
        if guard is not None:
            guard.verify(SOURCE_SHA); report['source_exit'] = {'status': 'PASS', 'current_files': 27080,
                                                           'historical_physical_closure': 'REFUSED'}
        report['finished_at'] = datetime.now(timezone.utc).isoformat(); report['elapsed_seconds'] = time.monotonic() - started
        save_new(HERE / 'actual-attempt-0001.json', report)
        print(json.dumps({'report': str(HERE / 'actual-attempt-0001.json'), 'status': report['status'],
                          'failed_phase': report.get('failed_phase'), 'elapsed_seconds': report['elapsed_seconds']}, sort_keys=True), flush=True)
    return returncode


if __name__ == '__main__':
    raise SystemExit(main())
