"""Recover exact temporary dependencies after reboot; never alter signed sources."""
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parents[5]
RUN = Path(__file__).resolve().parent
ENV = Path('/tmp/cal-R02-environment-0001')
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v12'
BOUNDARY = ROOT / 'product/lab/release-candidates/v1/boundary-review/0007'
SOURCE = '5c7f5c69d5795f5a5c0cb8b67c52a47621f8eab746c6afd70d42f06177ddc6ae'
ARCHIVE = '3e2d6e6a1d4f1c96141a2d0e844b8c330053e34adfb6b336716d22ce56c7963d'
OUTPUT = RUN / 'runtime-recovery-0209.json'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def bind(path):
    return {'path': str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
            'sha256': digest(path)}

def full_guard(python):
    code = '''import importlib.util,json
from pathlib import Path
p=Path('product/lab/release-candidates/v1/interface/api-integration-v12/guard.py')
s=importlib.util.spec_from_file_location('_runtime_recovery_guard',p)
g=importlib.util.module_from_spec(s);s.loader.exec_module(g)
m=g.verify('5c7f5c69d5795f5a5c0cb8b67c52a47621f8eab746c6afd70d42f06177ddc6ae')
print(json.dumps({'verified_files':len(m['files']),'environment':m['environment']}))
'''
    result = subprocess.run([str(python), '-B', '-c', code], cwd=ROOT,
                            check=True, capture_output=True, text=True)
    return json.loads(result.stdout)

def main():
    started = datetime.now(timezone.utc).isoformat()
    assert not OUTPUT.exists() and not ENV.exists()
    assert digest(API / 'source-manifest.json') == SOURCE
    source = json.loads((API / 'source-manifest.json').read_text())
    remediation = json.loads((BOUNDARY / 'native-remediation.json').read_text())
    native = Path(remediation['host_provided_native_binding']['path'])
    assert not native.exists()
    assert digest(Path(sys.executable).resolve()) == remediation['expected_R02_environment']['interpreter_sha256']
    for row in remediation['host_ABI_library_bindings']:
        assert digest(Path(row['path'])) == row['sha256'], row['path']
    archive = BOUNDARY / 'protected-native-dependency.snapshot'
    assert digest(archive) == ARCHIVE
    snapshot = json.loads(archive.read_text())
    assert snapshot['schema_version'] == 'lab-exact-public-byte-snapshot/v1-candidate'
    assert snapshot['authority_effect'] == 'none'
    name = 'native/lab-context-native-reader'
    assert set(snapshot['files']) == set(snapshot['sha256s']) == {name, 'native/dependency.json'}
    declaration = base64.b64decode(snapshot['files']['native/dependency.json'], validate=True)
    assert hashlib.sha256(declaration).hexdigest() == snapshot['sha256s']['native/dependency.json']
    json.loads(declaration)
    raw = base64.b64decode(snapshot['files'][name], validate=True)
    assert hashlib.sha256(raw).hexdigest() == snapshot['sha256s'][name] == remediation['host_provided_native_binding']['sha256']
    package = ROOT / 'product/lab/release-candidates/v1/packaging/R02/packages/0001'
    selection = json.loads((package / 'selection.json').read_text())
    source_rows = {r['path']: r['sha256'] for r in source['files']}
    assert digest(package / 'selection.json') == source_rows[str((package / 'selection.json').relative_to(ROOT))]
    wheels = []
    for row in selection['wheels']:
        path = package / 'wheels' / row['filename']
        assert digest(path) == row['sha256']
        wheels.append(path)
    # These absent paths belonged to interrupted temporary candidate runs.
    # This restoration creates no old key, policy, store, lease or Session.
    native.parent.mkdir(parents=True, exist_ok=True)
    with native.open('xb') as stream:
        os.fchmod(stream.fileno(), 0o600)
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    native.chmod(0o755)
    assert bind(native) == remediation['host_provided_native_binding']
    venv.EnvBuilder(with_pip=False).create(ENV)
    python = ENV / 'bin/python'
    subprocess.run([sys.executable, '-m', 'pip', '--python', str(python), 'install',
                    '--no-index', '--no-deps', '--no-compile', *map(str, wheels)],
                   check=True, cwd=ROOT, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    code = 'import importlib.metadata,json;print(json.dumps({n:importlib.metadata.version(n) for n in ' + repr(list(selection['versions'])) + '}))'
    versions = json.loads(subprocess.check_output([str(python), '-B', '-c', code], text=True))
    assert versions == selection['versions']
    entry = full_guard(python)
    exit_guard = full_guard(python)
    assert digest(archive) == ARCHIVE
    report = {'schema_version': 'lab-temporary-runtime-recovery/v1-candidate',
              'result': 'PASS', 'started_at': started,
              'completed_at': datetime.now(timezone.utc).isoformat(),
              'interpreter_binding': bind(Path(sys.executable).resolve()),
              'native_binding': bind(native), 'native_mode': oct(native.stat().st_mode & 0o777),
              'archive_binding': bind(archive), 'wheel_bindings': list(map(bind, wheels)),
              'versions': versions, 'source_entry_guard': entry, 'source_exit_guard': exit_guard,
              'native_executed': False, 'old_private_keys_or_sessions_restored': False,
              'prior_nonexecutable_archive_receipt_changed': False,
              'new_executable_temporary_host_restore': True,
              'interrupted_tests_qualified': False, 'authority_effect': 'none',
              'actual_owner_outcome': None, 'goal_complete': False}
    with OUTPUT.open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': 'PASS', 'report_binding': bind(OUTPUT)}), flush=True)

if __name__ == '__main__':
    main()
