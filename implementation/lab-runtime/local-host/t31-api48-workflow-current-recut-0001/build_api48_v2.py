"""No-replace current workflow-source and output-origin recut from API47."""

import hashlib
import json
import os
from pathlib import Path
import stat


ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-integration-v47-t31-output-current-0001'
NEW = BASE / 'api-integration-v48-t31-workflow-current-0002'
OLD_ADAPTER = ROOT / 'implementation/lab-runtime/local-host/t31-api47-output-bootstrap-0002/bootstrap.py'
NEW_ADAPTER = ROOT / 'implementation/lab-runtime/local-host/t31-api48-workflow-bootstrap-0002/bootstrap.py'
OLD_SOURCE = 'de4487eef78b5737cd2f4919c1e7280b5eef2e78dc5beb342cde87cb19651fd1'
OLD_PROFILE = '2c62d15d212b1151ce91928a0f78346d0679725bd9953f972dd86c64af2660f9'
OLD_ADAPTER_SHA = '06b8346aba1feef12e07a0d14c7a6b5cb95f1aaaebd76827e042f3ed83cdcc85'
CURRENT = {
    'adapter_binding': ('reader/source-manifest.json', 'b3461a1e68a5da06ad6c47966eb4ed448e67f2318baf5e7e956937d15f007877'),
    'source_binding': ('source/source-manifest.json', '0dc869f614e4d1f4be29c4b85f60dd5abd8f25b9fe84e1dc779932aee90c50d4'),
    'package_binding': ('source/packages/0001/manifest.json', '7006fd4fac3327b76f4ffcc03d93ffb070bb25288ca7bab7e7e5b20470baf22c'),
}
FAMILY = ROOT / 'implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-ce4d53a6479188a5'
CLAIM = ('Current T31 signed workflow-source control plus exact API48 staged-output origins; '
         'no private grant/plan, WorkflowRun append, output producer, consumer, portable installation, or owner effect.')


def exact(path):
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('absolute closed path required')
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
            chunks = []
            while block := os.read(fd, 1024 * 1024):
                chunks.append(block)
            after = os.fstat(fd)
            attached = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
            stamp = lambda v: (v.st_dev, v.st_ino, v.st_size, v.st_mtime_ns, v.st_ctime_ns)
            if stamp(before) != stamp(after) or stamp(after) != stamp(attached):
                raise ValueError('selected file changed during read')
            return b''.join(chunks)
        finally:
            os.close(fd)
    finally:
        for handle in reversed(handles):
            os.close(handle)


def digest(path):
    return hashlib.sha256(exact(path)).hexdigest()


def row(path):
    return {'path': Path(path).relative_to(ROOT).as_posix(), 'sha256': digest(path)}


def new_file(path, raw):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def save(path, value):
    new_file(path, (json.dumps(value, sort_keys=True, indent=2) + '\n').encode())


def change_one(raw, old, new, *, count=1):
    if raw.count(old) != count:
        raise ValueError('selected edit anchor differs: ' + old[:50])
    return raw.replace(old, new)


def main():
    if digest(OLD / 'source-manifest.json') != OLD_SOURCE or digest(OLD / 'contract-profile.json') != OLD_PROFILE:
        raise ValueError('frozen API47 input differs')
    if digest(OLD_ADAPTER) != OLD_ADAPTER_SHA:
        raise ValueError('selected API47 adapter differs')
    if NEW.exists() or NEW_ADAPTER.exists():
        raise ValueError('versioned API48 output already exists')
    manifest = json.loads(exact(OLD / 'source-manifest.json'))
    profile = json.loads(exact(OLD / 'contract-profile.json'))
    old_prefix = OLD.relative_to(ROOT).as_posix() + '/'
    new_prefix = NEW.relative_to(ROOT).as_posix() + '/'
    own = [r for r in manifest['files'] if r['path'].startswith(old_prefix)]
    if len(manifest['files']) != 208 or len(own) != 201 or len(profile['files']) != 33425:
        raise ValueError('API47 selected inventory differs')
    actual = {p.relative_to(OLD).as_posix() for p in OLD.rglob('*') if p.is_file()
              and p.name not in ('source-manifest.json', 'rebind-receipt.json')
              and '__pycache__' not in p.parts and p.suffix != '.pyc'}
    if actual != {r['path'][len(old_prefix):] for r in own}:
        raise ValueError('API47 physical inventory differs')
    for r in own:
        if digest(OLD / r['path'][len(old_prefix):]) != r['sha256']:
            raise ValueError('API47 selected byte differs')
    for suffix, pin in CURRENT.values():
        if digest(FAMILY / suffix) != pin:
            raise ValueError('current T31 family binding differs: ' + suffix)
    old_adapter_raw = exact(OLD_ADAPTER).decode()
    if old_adapter_raw.count(OLD.name) != 1:
        raise ValueError('old API47 adapter anchors differ')
    adapter_raw = old_adapter_raw.replace(OLD.name, NEW.name).encode()
    source_bridge = exact(OLD / 'source_bridge.py').decode()
    method = "def current_workflow_bindings():\n    paths={\n"
    for name, (suffix, _) in CURRENT.items():
        method += "        '" + name + "':ROOT/'" + (FAMILY / suffix).relative_to(ROOT).as_posix() + "',\n"
    method += "    }\n    pins={\n"
    for name, (_, pin) in CURRENT.items():
        method += "        '" + name + "':'" + pin + "',\n"
    method += "    }\n    result={key:{'ref':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())} for key,p in paths.items()}\n    require(all(result[k]['sha256']==pins[k] for k in result),'current workflow Source/Reader/package selection changed')\n    return result\n\n"
    source_bridge = change_one(source_bridge, 'def reader_factory(view):', method + 'def reader_factory(view):')
    source_bridge = change_one(source_bridge, '_cal_api46_t31_legacy_local_20261023_0001',
                               '_cal_api48_t31_legacy_local_20261023_0001')
    source_bridge = change_one(source_bridge, '_cal_api46_t31_source8_local_20261023_0001',
                               '_cal_api48_t31_source8_local_20261023_0001')
    auth = exact(OLD / 'auth.py').decode()
    old_auth = "source.require(value['workflow_source_control']==source.workflow_bindings(),'independent workflow source pins differ')"
    new_auth = "expected_workflow_source=(source.current_workflow_bindings() if value['source_name']==source.CURRENT_LEGACY_NAME else source.workflow_bindings())\n            source.require(value['workflow_source_control']==expected_workflow_source,'independent workflow source pins differ')"
    auth = change_one(auth, old_auth, new_auth)
    registry = exact(OLD / 'workflow_output_registry.py').decode()
    head, tail = registry.split('STAGED_PRODUCER_ORIGINS = (', 1)
    first, end = tail.split('\n', 1)
    if first.count(OLD.name + '/workflow_') != 7:
        raise ValueError('seven API47 staged origins required')
    registry = head + 'STAGED_PRODUCER_ORIGINS = (' + first.replace(OLD.name + '/workflow_', NEW.name + '/workflow_') + '\n' + end
    guard = exact(OLD / 'guard.py').decode()
    guard = change_one(guard, OLD_ADAPTER.relative_to(ROOT).as_posix(), NEW_ADAPTER.relative_to(ROOT).as_posix())
    changed = {'source_bridge.py': source_bridge.encode(), 'auth.py': auth.encode(),
               'workflow_output_registry.py': registry.encode(), 'guard.py': guard.encode()}
    NEW_ADAPTER.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    new_file(NEW_ADAPTER, adapter_raw)
    NEW.mkdir(mode=0o700)
    for selected in own:
        name = selected['path'][len(old_prefix):]
        if name == 'contract-profile.json':
            continue
        target = NEW / name
        target.parent.mkdir(parents=True, exist_ok=True)
        new_file(target, changed.get(name, exact(OLD / name)))
    old_adapter_path = OLD_ADAPTER.relative_to(ROOT).as_posix()
    new_adapter_path = NEW_ADAPTER.relative_to(ROOT).as_posix()
    profile_rows = []
    for selected in profile['files']:
        path = selected['path']
        if path.startswith(old_prefix):
            profile_rows.append(row(NEW / path[len(old_prefix):]))
        elif path == old_adapter_path:
            profile_rows.append(row(NEW_ADAPTER))
        else:
            profile_rows.append(selected)
    if len(profile_rows) != 33425 or len({r['path'] for r in profile_rows}) != 33425:
        raise ValueError('API48 profile replacement differs')
    profile['files'] = sorted(profile_rows, key=lambda r: r['path'])
    profile['integration_members_binding'] = row(NEW / 'integration-members.json')
    profile['claim_ceiling'] = CLAIM
    save(NEW / 'contract-profile.json', profile)
    files = []
    for selected in manifest['files']:
        path = selected['path']
        if path.startswith(old_prefix):
            files.append(row(NEW / path[len(old_prefix):]))
        elif path == old_adapter_path:
            files.append(row(NEW_ADAPTER))
        else:
            files.append(selected)
    if len(files) != 208 or len({r['path'] for r in files}) != 208:
        raise ValueError('API48 source replacement differs')
    manifest['files'] = sorted(files, key=lambda r: r['path'])
    manifest['profile_binding'] = row(NEW / 'contract-profile.json')
    manifest['predecessor_source_manifest_binding'] = row(OLD / 'source-manifest.json')
    manifest['claim_ceiling'] = CLAIM
    save(NEW / 'source-manifest.json', manifest)
    receipt = {'schema_version': 'lab-T31-API48-workflow-current-rebind/v2-candidate',
               'successor_package': NEW.relative_to(ROOT).as_posix(),
               'predecessor_source_binding': row(OLD / 'source-manifest.json'),
               'successor_source_binding': row(NEW / 'source-manifest.json'),
               'successor_manifest_sha256': digest(NEW / 'source-manifest.json'),
               'successor_profile_binding': row(NEW / 'contract-profile.json'),
               'adapter_binding': row(NEW_ADAPTER),
               'current_workflow_source_bindings': {key: row(FAMILY / suffix) for key, (suffix, _) in CURRENT.items()},
               'historical_workflow_source_binding_preserved': True,
               'source_files': len(files), 'profile_files': len(profile_rows),
               'staged_origin_replacements': 7, 'authority_effect': 'none',
               'actual_workflow_transitions': 0, 'claim_ceiling': CLAIM}
    save(NEW / 'rebind-receipt.json', receipt)
    print(json.dumps({'source_sha256': digest(NEW / 'source-manifest.json'),
                      'profile_sha256': digest(NEW / 'contract-profile.json'),
                      'adapter_sha256': digest(NEW_ADAPTER),
                      'source_files': len(files), 'profile_files': len(profile_rows)}, sort_keys=True))


if __name__ == '__main__':
    main()
