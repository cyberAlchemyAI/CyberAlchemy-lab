"""Exercise the selected API43 native batch wrapper across a real child kill.

This is a local technical route. It selects the API43 Source/profile and the
original native wrapper from that profile; it does not grant a Lab operation.
"""
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
import tempfile
import time
import types


ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).resolve().parent
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v43-r03-0005-composite-0001'
NATIVE = ROOT / 'product/lab/release-candidates/v1/interface/native-batch-recovery-v1-completion-0001'
SOURCE_SHA = '22cd380b7544721c6519c869e430a99cbb6b84c3e863a425125f3d9944981560'
PROFILE_SHA = 'bc660fbd0ac6055dc49b008c9c46c4b09925e1e3cd8795940a0563348b04a2e6'
RECEIPT = HERE / 'RUN-0002.json'


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def selected(path, digest):
    path = Path(path)
    need(path.is_absolute() and path.is_relative_to(ROOT) and
         not path.is_symlink() and not any(p.is_symlink() for p in path.parents),
         'selected source origin differs')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_size <= 64 * 1024 * 1024,
             'selected source is not a bounded regular file')
        chunks = []
        while block := os.read(fd, 1024 * 1024):
            chunks.append(block)
        after = os.fstat(fd)
        current = path.lstat()
        stamp = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_uid,
                           s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        need(stamp(before) == stamp(after) == stamp(current),
             'selected source changed during read')
    finally:
        os.close(fd)
    raw = b''.join(chunks)
    need(sha(raw) == digest, 'selected source bytes differ: ' + str(path))
    return raw


def load(name, path, raw):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(raw, str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


def select_current():
    source_raw = selected(API / 'source-manifest.json', SOURCE_SHA)
    profile_raw = selected(API / 'contract-profile.json', PROFILE_SHA)
    source = json.loads(source_raw)
    profile = json.loads(profile_raw)
    need(source['profile_binding'] == {
        'path': (API / 'contract-profile.json').relative_to(ROOT).as_posix(),
        'sha256': PROFILE_SHA}, 'API43 selected another profile')
    source_rows = {r['path']: r['sha256'] for r in source['files']}
    profile_rows = {r['path']: r['sha256'] for r in profile['files']}
    need(len(source_rows) == len(source['files']) == 207 and
         len(profile_rows) == len(profile['files']) == 33434,
         'API43 selected row inventory differs')
    guard = API / 'guard.py'
    guard_raw = selected(guard, source_rows[guard.relative_to(ROOT).as_posix()])
    load('_cal_t32_api43_guard', guard, guard_raw).verify(SOURCE_SHA)
    paths = [NATIVE / name for name in (
        'fixtures.py', 'recoverable_store.py', 'child_run.py',
        'bin-production/lab-ontology-native',
        'build-observer/debug/lab-ontology-native')]
    originals = {}
    for path in paths:
        ref = path.relative_to(ROOT).as_posix()
        need(ref in profile_rows, 'native route not selected by API43 profile: ' + ref)
        originals[ref] = selected(path, profile_rows[ref])
    fixtures = load('fixtures', NATIVE / 'fixtures.py',
                    originals[(NATIVE / 'fixtures.py').relative_to(ROOT).as_posix()])
    store = load('_cal_t32_selected_store', NATIVE / 'recoverable_store.py',
                 originals[(NATIVE / 'recoverable_store.py').relative_to(ROOT).as_posix()])
    return fixtures, store, profile_rows, originals


def publish(value):
    raw = (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
    fd = os.open(RECEIPT, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    return sha(raw)


def recover_child(selection_path):
    """Cold process entry: independently reselect code and finish one pending batch."""
    os.umask(0o077)
    value = json.loads(Path(selection_path).read_bytes())
    need(set(value) == {'root', 'identity', 'executable', 'executable_sha256',
                        'pending', 'pins', 'result_path'}, 'closed recovery selection required')
    root = Path(value['root'])
    result_path = Path(value['result_path'])
    need(root.is_absolute() and result_path.parent == root.parent and
         result_path.name == 'recovery-result.json' and not result_path.exists(),
         'owned recovery result path differs')
    _, S, rows, _ = select_current()
    executable = Path(value['executable'])
    need(executable == NATIVE / 'build-observer/debug/lab-ontology-native' and
         rows[executable.relative_to(ROOT).as_posix()] == value['executable_sha256'],
         'recovery native executable differs from current profile')
    store = S.GenerationStore(root, tuple(value['identity']), executable,
                              value['executable_sha256'])
    result = store.run(value['pending'], S.PendingPins(**value['pins']), recover=True)
    cold = store.read_committed()
    need(result['committed'] and not result['idempotent'] and cold['result'] == 'PASS',
         'cold process did not commit and replay native batch')
    payload = {'schema_version': 'lab-T32-selected-recovery-child/v1',
               'committed': True, 'idempotent': False,
               'semantic_count': len(cold['native_cut']['semantic_events']),
               'governance_count': len(cold['native_cut']['governance_events']),
               'head_sha256': sha((root / 'HEAD.json').read_bytes())}
    raw = (json.dumps(payload, sort_keys=True, indent=2) + '\n').encode()
    fd = os.open(result_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    return payload


def run():
    need(not RECEIPT.exists(), 'T32 receipt already exists')
    os.umask(0o077)
    started = time.monotonic()
    fixtures, S, rows, originals = select_current()
    production = NATIVE / 'bin-production/lab-ontology-native'
    observer = NATIVE / 'build-observer/debug/lab-ontology-native'
    observer_sha = rows[observer.relative_to(ROOT).as_posix()]
    child_script = NATIVE / 'child_run.py'
    with tempfile.TemporaryDirectory(prefix='cal-t32-api43-route-', dir='/tmp') as name:
        parent = Path(name)
        parent.chmod(0o700)
        base_request, base_events = fixtures.sealed_fixture(production, parent / 'base')
        next_request, next_events = fixtures.sealed_fixture(production, parent / 'next', offset=3)
        root = parent / 'store'
        root.mkdir(mode=0o700)
        info = root.stat()
        identity = (info.st_dev, info.st_ino)
        current = S.GenerationStore(root, identity, observer, observer_sha)
        current.bootstrap()
        first, first_pins = current.prepare(base_request, sha(base_request.read_bytes()))
        need(current.run(first, first_pins)['committed'], 'baseline native append did not commit')
        prior = current.read_committed()
        need(prior['native_cut']['semantic_events'] == base_events['semantic'] and
             prior['native_cut']['governance_events'] == base_events['governance'],
             'baseline cold replay differs')
        pending, pins = current.prepare(next_request, sha(next_request.read_bytes()))
        before = (root / 'HEAD.json').read_bytes()
        foreign = root / 'foreign-sibling.bin'
        foreign.write_bytes(b'owned foreign residue must survive')
        marker = parent / 'child-checkpoint'
        selection = parent / 'child-selection.json'
        selection.write_text(json.dumps({
            'root': str(root), 'identity': identity, 'executable': str(observer),
            'executable_sha256': observer_sha, 'pending': str(pending),
            'pins': asdict(pins), 'kind': 'native', 'stage': 'after-first-link',
            'family': 'semantic', 'marker': str(marker)}, sort_keys=True))
        child = subprocess.Popen([sys.executable, '-I', '-B', str(child_script), str(selection)],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 start_new_session=True,
                                 env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C',
                                      'PYTHONDONTWRITEBYTECODE': '1'})
        try:
            deadline = time.monotonic() + 45
            while not marker.exists() and child.poll() is None and time.monotonic() < deadline:
                time.sleep(0.02)
            if not marker.exists() or child.poll() is not None:
                _, error = child.communicate(timeout=10) if child.poll() is not None else (b'', b'')
                raise ValueError('selected native checkpoint absent: ' + sha(error))
            need(marker.read_bytes() == b'after-first-link', 'wrong native checkpoint')
            need(os.getpgid(child.pid) == child.pid, 'child did not own its process group')
            need(current.read_committed()['native_cut']['semantic_events'] == base_events['semantic'],
                 'previous complete cut unreadable before process kill')
            os.killpg(child.pid, signal.SIGKILL)
            child.communicate(timeout=10)
        finally:
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGKILL)
                child.communicate(timeout=10)
        need(child.returncode == -signal.SIGKILL and (root / 'HEAD.json').read_bytes() == before,
             'process kill changed committed HEAD')
        recovery_selection = parent / 'recovery-selection.json'
        recovery_selection.write_text(json.dumps({
            'root': str(root), 'identity': identity, 'executable': str(observer),
            'executable_sha256': observer_sha, 'pending': str(pending),
            'pins': asdict(pins), 'result_path': str(parent / 'recovery-result.json')},
            sort_keys=True))
        recovery = subprocess.run([sys.executable, '-B', str(HERE / 'run.py'),
                                   '--recover', str(recovery_selection)],
                                  cwd=ROOT, capture_output=True, timeout=120,
                                  env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C',
                                       'PYTHONDONTWRITEBYTECODE': '1',
                                       'PYTHONPATH': str(ROOT / 'implementation/lab-runtime/local-host/t06-jsonschema-419-overlay-0001/overlay')})
        need(recovery.returncode == 0, 'fresh-process recovery refused: ' + sha(recovery.stderr))
        child_result_raw = (parent / 'recovery-result.json').read_bytes()
        child_result = json.loads(child_result_raw)
        need(child_result['committed'] is True and child_result['idempotent'] is False and
             child_result['semantic_count'] == child_result['governance_count'] == 6 and
             child_result['head_sha256'] == sha((root / 'HEAD.json').read_bytes()),
             'fresh-process recovery receipt differs')
        fresh = S.GenerationStore(root, identity, observer, observer_sha)
        final = fresh.read_committed()
        need(final['native_cut']['semantic_events'] == base_events['semantic'] + next_events['semantic']
             and final['native_cut']['governance_events'] == base_events['governance'] + next_events['governance'],
             'cold recovered event bytes differ')
        head = (root / 'HEAD.json').read_bytes()
        need(fresh.run(pending, pins, recover=True)['idempotent'] and
             (root / 'HEAD.json').read_bytes() == head,
             'exact retry duplicated native effect')
        need(foreign.read_bytes() == b'owned foreign residue must survive',
             'foreign residue was altered')
        for ref, raw in originals.items():
            need(selected(ROOT / ref, rows[ref]) == raw,
                 'selected native route changed during run')
        result = {
            'schema_version': 'lab-T32-api43-selected-native-route/v2-candidate',
            'status': 'PASS-bounded-current-cut-recovery',
            'api_source_sha256': SOURCE_SHA,
            'api_profile_sha256': PROFILE_SHA,
            'selected_native_files': len(originals),
            'observer_executable_sha256': observer_sha,
            'process_kill_checkpoint': 'semantic:after-first-link',
            'child_exit_code': child.returncode,
            'old_cut_readable_during_interrupted_append': True,
            'fresh_process_recovery_committed': True,
            'fresh_process_recovery_receipt_sha256': sha(child_result_raw),
            'exact_original_native_events_cold_replayed': True,
            'exact_retry_idempotent': True,
            'foreign_residue_preserved': True,
            'full_api_operation_integrated': False,
            'power_loss_durability_tested': False,
            'authority_effect': 'none',
            'elapsed_seconds': round(time.monotonic() - started, 3),
        }
    return result, publish(result)


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--recover':
        print(json.dumps(recover_child(sys.argv[2]), sort_keys=True))
    elif len(sys.argv) == 1:
        value, digest = run()
        print(json.dumps({'status': value['status'], 'receipt_sha256': digest}, sort_keys=True))
    else:
        raise ValueError('T32 selected runner accepts no arguments or --recover selection')
