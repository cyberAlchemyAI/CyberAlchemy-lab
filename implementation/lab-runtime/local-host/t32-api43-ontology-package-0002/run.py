"""Cold-recover the exact API43-selected ontology input package after a child kill.

This exercises the native package consumed by ontology.project. It is a
technical precursor; the authenticated API operation still uses its own store.
"""
from dataclasses import asdict
import base64
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import types

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).resolve().parent
PARENT = ROOT / 'implementation/lab-runtime/local-host/t32-api43-current-route-0001'
PARENT_SHA = '51ff3e160a5a7e11d3d9f0f7dd4aa12f54f3a60fb54455b3e1f0946853f17f5c'
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v43-r03-0005-composite-0001'
PACKAGE = ROOT / 'product/lab/release-candidates/v1/interface/current-mapped-context-v4/packages/0001'
NATIVE = ROOT / 'product/lab/release-candidates/v1/interface/native-batch-recovery-v1-completion-0001'
RECEIPT = HERE / 'RUN-0002.json'

# Python receives selected executable bytes on stdin. Neither child opens its
# Python entrypoint by pathname after the parent has checked its source hash.
CAPTURED_EXEC = '''import base64,json,sys,types
p=json.loads(sys.stdin.buffer.read())
if p.get("overlay"):
 sys.path.insert(0,p["overlay"])
for row in p["modules"]:
 m=types.ModuleType(row["name"]);m.__file__=row["file"]
 sys.modules[row["name"]]=m
 exec(compile(base64.b64decode(row["source"]),row["file"],"exec"),m.__dict__)
sys.argv=p["argv"]
g={"__name__":"__main__","__file__":p["entry_file"]}
exec(compile(base64.b64decode(p["entry_source"]),p["entry_file"],"exec"),g)
'''


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def compact(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def parent_module():
    raw = (PARENT / 'run.py').read_bytes()
    need(sha(raw) == PARENT_SHA, 'selected T32 recovery runner changed')
    module = types.ModuleType('_cal_t32_api43_selected_recovery')
    module.__file__ = str(PARENT / 'run.py')
    exec(compile(raw, module.__file__, 'exec', dont_inherit=True), module.__dict__)
    module._selected_runner_raw = raw
    return module


def selected_package(R, profile_rows):
    manifest_path = PACKAGE / 'manifest.json'
    manifest_ref = manifest_path.relative_to(ROOT).as_posix()
    need(manifest_ref in profile_rows, 'ontology package manifest not profile selected')
    manifest_raw = R.selected(manifest_path, profile_rows[manifest_ref])
    manifest = json.loads(manifest_raw)
    declared = {row['path']: row['sha256'] for row in manifest['files']}
    need(len(declared) == len(manifest['files']), 'ontology package has duplicate paths')
    paths = [PACKAGE / 'native-output.json', PACKAGE / 'request.json']
    for family in ('semantic', 'governance'):
        paths.extend(sorted((PACKAGE / family).glob('*.json')))
    need(len(paths) == 52, 'ontology package event closure differs')
    originals = {}
    for path in paths:
        ref = path.relative_to(ROOT).as_posix()
        need(ref in declared and ref in profile_rows and declared[ref] == profile_rows[ref],
             'ontology input not selected by package and API43 profile: ' + ref)
        originals[ref] = R.selected(path, declared[ref])
    events = {family: [json.loads(originals[path.relative_to(ROOT).as_posix()])
                       for path in sorted((PACKAGE / family).glob('*.json'))]
              for family in ('semantic', 'governance')}
    need(len(events['semantic']) == len(events['governance']) == 25,
         'selected ontology native event count differs')
    expected = json.loads(originals[(PACKAGE / 'native-output.json').relative_to(ROOT).as_posix()])
    need(expected['cut']['semantic_cursor'] == 25 and expected['governance_cursor'] == 25,
         'selected ontology expected native cut differs')
    read_request_raw = originals[(PACKAGE / 'request.json').relative_to(ROOT).as_posix()]
    read_request = json.loads(read_request_raw)
    need(read_request['selector']['semantic_cursor'] == read_request['governance_cursor'] == 25,
         'selected ontology read request cursor differs')
    return manifest_raw, events, expected, read_request_raw


def encoded(raw):
    return base64.b64encode(raw).decode('ascii')


def child_payload(entry_file, entry_raw, argv, modules=(), overlay=None):
    return compact({'entry_file': str(entry_file), 'entry_source': encoded(entry_raw),
                    'argv': [str(a) for a in argv], 'overlay': overlay,
                    'modules': [{'name': name, 'file': str(path), 'source': encoded(raw)}
                                for name, path, raw in modules]})


def run():
    need(not RECEIPT.exists(), 'T32 ontology receipt already exists')
    os.umask(0o077)
    started = time.monotonic()
    runner_sha = sha(Path(__file__).read_bytes())
    R = parent_module()
    _, Store, profile_rows, native_originals = R.select_current()
    manifest_raw, events, expected, read_request_raw = selected_package(R, profile_rows)
    executable = NATIVE / 'build-observer/debug/lab-ontology-native'
    executable_sha = profile_rows[executable.relative_to(ROOT).as_posix()]
    child_script = NATIVE / 'child_run.py'
    fixture_path = NATIVE / 'fixtures.py'
    store_path = NATIVE / 'recoverable_store.py'
    def native_raw(path):
        return native_originals[path.relative_to(ROOT).as_posix()]
    child_originals = (
        ('fixtures', fixture_path, native_raw(fixture_path)),
        ('recoverable_store', store_path, native_raw(store_path)))
    child_raw = native_raw(child_script)
    with tempfile.TemporaryDirectory(prefix='cal-t32-api43-package-', dir='/tmp') as location:
        parent = Path(location)
        parent.chmod(0o700)
        root = parent / 'store'
        root.mkdir(mode=0o700)
        info = root.stat()
        identity = (info.st_dev, info.st_ino)
        store = Store.GenerationStore(root, identity, executable, executable_sha)
        store.bootstrap()
        before = (root / 'HEAD.json').read_bytes()
        request = parent / 'event-request.json'
        request.write_bytes(compact(events))
        pending, pins = store.prepare(request, sha(request.read_bytes()))
        sentinel = root / 'foreign-sibling.bin'
        sentinel.write_bytes(b'foreign selected sibling survives')
        marker = parent / 'child-checkpoint'
        selection = parent / 'child-selection.json'
        selection.write_bytes(compact({
            'root': str(root), 'identity': identity, 'executable': str(executable),
            'executable_sha256': executable_sha, 'pending': str(pending),
            'pins': asdict(pins), 'kind': 'native', 'stage': 'after-first-link',
            'family': 'semantic', 'marker': str(marker)}))
        child = subprocess.Popen([sys.executable, '-I', '-B', '-c', CAPTURED_EXEC],
                                 cwd=ROOT, stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 start_new_session=True,
                                 env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C',
                                      'PYTHONDONTWRITEBYTECODE': '1'})
        child.stdin.write(child_payload(child_script, child_raw,
                                        (child_script, selection), child_originals))
        child.stdin.close()
        child.stdin = None
        try:
            deadline = time.monotonic() + 45
            while not marker.exists() and child.poll() is None and time.monotonic() < deadline:
                time.sleep(0.02)
            need(marker.exists() and child.poll() is None, 'selected native checkpoint absent')
            need(marker.read_bytes() == b'after-first-link', 'native checkpoint differs')
            need((root / 'HEAD.json').read_bytes() == before and
                 store.read_committed()['result'] == 'EMPTY-GENESIS',
                 'interrupted child changed previous committed cut')
            need(os.getpgid(child.pid) == child.pid, 'child process group differs')
            os.killpg(child.pid, signal.SIGKILL)
            child.communicate(timeout=10)
        finally:
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGKILL)
                child.communicate(timeout=10)
        need(child.returncode == -signal.SIGKILL and (root / 'HEAD.json').read_bytes() == before,
             'process kill changed committed HEAD')
        recovery_result = parent / 'recovery-result.json'
        recovery_selection = parent / 'recovery-selection.json'
        recovery_selection.write_bytes(compact({
            'root': str(root), 'identity': identity, 'executable': str(executable),
            'executable_sha256': executable_sha, 'pending': str(pending),
            'pins': asdict(pins), 'result_path': str(recovery_result)}))
        recovered = subprocess.run([sys.executable, '-I', '-B', '-c', CAPTURED_EXEC],
                                   input=child_payload(PARENT / 'run.py', R._selected_runner_raw,
                                                       (PARENT / 'run.py', '--recover', recovery_selection),
                                                       overlay=str(ROOT / 'implementation/lab-runtime/local-host/t06-jsonschema-419-overlay-0001/overlay')),
                                   cwd=ROOT, capture_output=True, timeout=120,
                                   env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C',
                                        'PYTHONDONTWRITEBYTECODE': '1'})
        need(recovered.returncode == 0, 'fresh-process native recovery refused: ' + sha(recovered.stderr))
        recovery = json.loads(recovery_result.read_bytes())
        need(recovery['committed'] is True and recovery['idempotent'] is False and
             recovery['semantic_count'] == recovery['governance_count'] == 25,
             'fresh-process recovery counts differ')
        fresh = Store.GenerationStore(root, identity, executable, executable_sha)
        cold = fresh.read_committed()
        native = cold['native_cut']
        need(cold['result'] == 'PASS' and native['semantic_events'] == events['semantic'] and
             native['governance_events'] == events['governance'] and native['cut'] == expected['cut'],
             'cold recovered native package differs from selected ontology cut')
        head = (root / 'HEAD.json').read_bytes()
        need(recovery['head_sha256'] == sha(head) and
             fresh.run(pending, pins, recover=True)['idempotent'] and
             (root / 'HEAD.json').read_bytes() == head,
             'exact native recovery retry duplicated effect')
        need(sentinel.read_bytes() == b'foreign selected sibling survives',
             'foreign sibling changed')
        need(sha(Path(__file__).read_bytes()) == runner_sha and
             sha((PARENT / 'run.py').read_bytes()) == PARENT_SHA,
             'selected runner bytes changed during native recovery')
        result = {
            'schema_version': 'lab-T32-api43-ontology-package-recovery/v2-candidate',
            'result': 'PASS', 'api_source_sha256': R.SOURCE_SHA,
            'api_profile_sha256': R.PROFILE_SHA,
            'selected_runner_sha256': runner_sha,
            'selected_parent_runner_sha256': PARENT_SHA,
            'selected_child_entry_sha256': sha(child_raw),
            'selected_fixture_module_sha256': sha(native_raw(fixture_path)),
            'selected_store_module_sha256': sha(native_raw(store_path)),
            'captured_executor_sha256': sha(CAPTURED_EXEC.encode()),
            'child_and_recovery_python_entry_from_captured_bytes': True,
            'selected_package_manifest_sha256': sha(manifest_raw),
            'selected_ontology_read_request_sha256': sha(read_request_raw),
            'selected_native_request_sha256': sha(compact(events)),
            'expected_ontology_cut_sha256': sha(compact(expected['cut'])),
            'recovered_ontology_cut_sha256': sha(compact(native['cut'])),
            'semantic_events': 25, 'governance_events': 25,
            'child_exit': child.returncode, 'fresh_process_recovery': True,
            'old_head_unchanged_before_recovery': True,
            'exact_retry_idempotent': True, 'foreign_sibling_preserved': True,
            'authenticated_api_operation_integrated': False,
            'authority_effect': 'none', 'T32_complete': False,
            'elapsed_seconds': round(time.monotonic() - started, 3)}
    raw = json.dumps(result, sort_keys=True, indent=2, allow_nan=False).encode() + b'\n'
    fd = os.open(RECEIPT, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as file:
        file.write(raw)
        file.flush()
        os.fsync(file.fileno())
    return result


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True))
