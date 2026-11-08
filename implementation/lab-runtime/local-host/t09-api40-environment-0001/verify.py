"""Cold current-composite environment check for the selected API40 fixture cut."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v40-current-t06-0001'
SDK = ROOT / 'product/lab/release-candidates/v1/interface/composite-operator-v1-current-api40-0001/revision-0001'
OVERLAY = ROOT / 'implementation/lab-runtime/local-host/t06-jsonschema-419-overlay-0001'
INSTALL = ROOT / 'implementation/lab-runtime/local-host/t06-current-composite-successor-0001/working/installation-0001'
PINS = {
    API / 'source-manifest.json': '45412c382dc0cc9c807dd2bf4ec67037c7ae58854fcbb42cb15a96f0f7f3a219',
    API / 'contract-profile.json': 'cbfd53a80f41a2ffd7ac28b88fa9e19a232ad291c8cb3791a302a4e8349c7614',
    API / 'rebind-receipt.json': '45328cee8171522d5af15208732527514e191bf72cbec0e2d5bcbeffe7c836d4',
    SDK / 'source-manifest.json': 'f123c4e02828c1c3f88dfc4b74adc3bdf1cc2919bc53df8ccf68e00ff677da1e',
    OVERLAY / 'source-manifest.json': '574bd9f1fc976755eb0bf075b2ec7c14d8c378e8c6b074fa4df0e50af3951bd7',
    INSTALL / 'installation.json': '5821d37ce536e08c639493ceb8d165949e65cf5dd9771af5576a724082cca13b',
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_exact(path, digest):
    path = Path(path)
    if not path.is_absolute() or not path.is_relative_to(ROOT) or '..' in path.parts:
        raise ValueError('selected environment input outside repository')
    handles = []
    attachments = []
    leaf = None
    try:
        parent = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        handles.append(parent)
        for name in path.parts[1:-1]:
            child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            handles.append(child)
            before = os.fstat(child)
            attached = os.stat(name, dir_fd=parent, follow_symlinks=False)
            if not stat.S_ISDIR(before.st_mode) or (before.st_dev, before.st_ino, before.st_mode) != (attached.st_dev, attached.st_ino, attached.st_mode):
                raise ValueError('selected environment ancestor changed')
            attachments.append((parent, name, child, before.st_dev, before.st_ino, before.st_mode))
            parent = child
        leaf = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        before = os.fstat(leaf)
        if not stat.S_ISREG(before.st_mode) or before.st_size > 64 * 1024 * 1024:
            raise ValueError('selected environment input not bounded regular file')
        chunks = []
        remaining = before.st_size + 1
        while remaining:
            part = os.read(leaf, min(1024 * 1024, remaining))
            if not part:
                break
            chunks.append(part)
            remaining -= len(part)
        raw = b''.join(chunks)
        after = os.fstat(leaf)
        attached = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
        identity = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        if len(raw) != before.st_size or identity(before) != identity(after) or identity(before) != identity(attached):
            raise ValueError('selected environment input changed during read')
        for ancestor, name, held, dev, ino, mode in reversed(attachments):
            current = os.stat(name, dir_fd=ancestor, follow_symlinks=False)
            if (current.st_dev, current.st_ino, current.st_mode) != (dev, ino, mode) or (os.fstat(held).st_dev, os.fstat(held).st_ino, os.fstat(held).st_mode) != (dev, ino, mode):
                raise ValueError('selected environment ancestor changed')
        if sha(raw) != digest:
            raise ValueError('selected environment input changed: ' + str(path))
        return raw
    except OSError as error:
        raise ValueError('selected environment input missing, linked or unsafe') from error
    finally:
        if leaf is not None:
            os.close(leaf)
        for handle in reversed(handles):
            os.close(handle)


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def command(include_overlay=True):
    loader = INSTALL / 'lib/abi/ld-linux-x86-64.so.2'
    python = INSTALL / 'bin/python'
    paths = [str(API.parent), str(INSTALL / 'deps')]
    if include_overlay:
        paths.insert(1, str(OVERLAY / 'overlay'))
    code = (
        'import importlib,json,sys; '
        'sys.path[:0]=json.loads(sys.argv[1]); '
        'import cryptography,jsonschema; '
        'g=importlib.import_module("api-integration-v40-current-t06-0001.guard"); '
        'r=json.loads(open(sys.argv[2],"rb").read()); '
        'g.verify(r["successor_manifest_sha256"]); '
        'print(json.dumps({"python":"%d.%d.%d"%sys.version_info[:3],'
        '"jsonschema":jsonschema.__version__,"cryptography":cryptography.__version__, '
        '"guard":"PASS"},sort_keys=True))'
    )
    return [str(loader), '--inhibit-cache', '--library-path', str(INSTALL / 'lib/abi'),
            str(python), '-I', '-X', 'utf8', '-B', '-S', '-c', code,
            json.dumps(paths), str(API / 'rebind-receipt.json')]


def selected_members():
    for path, pin in PINS.items():
        read_exact(path, pin)
    for manifest in (SDK / 'source-manifest.json', OVERLAY / 'source-manifest.json'):
        rows = json.loads(read_exact(manifest, PINS[manifest]))['files']
        if len({row['path'] for row in rows}) != len(rows):
            raise ValueError('duplicate selected environment member')
        for row in rows:
            relative = Path(row['path'])
            if relative.is_absolute() or '..' in relative.parts or relative.as_posix() != row['path']:
                raise ValueError('unsafe selected environment member')
            raw = read_exact(ROOT / relative, row['sha256'])
            if len(raw) != row['size_bytes']:
                raise ValueError('selected environment member size differs')


def verify(*, expected_environment=None, include_overlay=True):
    selected_members()
    source = json.loads(read_exact(API / 'source-manifest.json', PINS[API / 'source-manifest.json']))
    selected = source['environment']
    if expected_environment is not None and expected_environment != selected:
        raise ValueError('requested composite environment differs from selected source')
    if source['profile_binding'] != {'path': (API / 'contract-profile.json').relative_to(ROOT).as_posix(),
                                     'sha256': PINS[API / 'contract-profile.json']}:
        raise ValueError('API source/profile environment selection differs')
    rebind = json.loads(read_exact(API / 'rebind-receipt.json', PINS[API / 'rebind-receipt.json']))
    if rebind['successor_manifest_sha256'] != PINS[API / 'source-manifest.json']:
        raise ValueError('API rebind receipt source selection differs')
    metadata = json.loads(read_exact(INSTALL / 'installation.json', PINS[INSTALL / 'installation.json']))
    files = metadata['installed_files']
    if len(files) != 1010 or metadata['result'] != 'PASS' or metadata['private_inputs_shipped'] is not False:
        raise ValueError('installed dependency environment differs')
    control = module(SDK / 'control.py', 't09_selected_sdk_control')
    if control.installed(INSTALL, files) != 1010:
        raise ValueError('installed dependency closure differs')
    outcome = subprocess.run(command(include_overlay), cwd=ROOT, capture_output=True, text=True,
                             env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'PYTHONNOUSERSITE': '1',
                                  'PYTHONDONTWRITEBYTECODE': '1'}, timeout=180)
    if outcome.returncode:
        if not include_overlay and 'API environment differs' in outcome.stderr:
            raise ValueError('API environment differs without selected jsonschema overlay')
        raise ValueError('selected composite interpreter/ABI or API guard refused')
    actual = json.loads(outcome.stdout)
    if actual != {**selected, 'guard': 'PASS'}:
        raise ValueError('actual composite environment differs from selected source')
    if control.installed(INSTALL, files) != 1010:
        raise ValueError('installed dependency closure changed after child')
    selected_members()
    return {'schema_version': 'lab-T09-current-composite-environment/v1',
            'status': 'PASS', 'selected_environment': selected,
            'actual_environment': actual, 'installed_file_count': len(files),
            'api_source_sha256': PINS[API / 'source-manifest.json'],
            'api_profile_sha256': PINS[API / 'contract-profile.json'],
            'api_rebind_receipt_sha256': PINS[API / 'rebind-receipt.json'],
            'sdk_source_sha256': PINS[SDK / 'source-manifest.json'],
            'overlay_source_sha256': PINS[OVERLAY / 'source-manifest.json'],
            'installation_sha256': PINS[INSTALL / 'installation.json'],
            'authority_effect': 'none'}


if __name__ == '__main__':
    print(json.dumps(verify(), sort_keys=True, indent=2))
