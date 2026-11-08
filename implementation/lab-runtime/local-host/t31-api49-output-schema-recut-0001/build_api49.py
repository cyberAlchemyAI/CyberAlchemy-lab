"""No-replace API49: align private output-plan Service constants with true origin.

The selected API48 workflow-auth recut is the immutable predecessor. This
builder changes only the two exact schema constants, seven staged producer
origins, task-local assembler origin, and versioned source/profile bindings.
"""
import hashlib
import json
import os
from pathlib import Path
import stat

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-integration-v48-t31-workflow-current-0003'
NEW = BASE / 'api-integration-v49-t31-output-schema-current-0001'
OLD_ADAPTER = ROOT / 'implementation/lab-runtime/local-host/t31-api48-workflow-bootstrap-0003/bootstrap.py'
NEW_ADAPTER = ROOT / 'implementation/lab-runtime/local-host/t31-api49-output-bootstrap-0001/bootstrap.py'
OLD_SOURCE = 'e1aa5cb84fe11b30ec8a5c2326032aea65c5633e97d009abaa1537cdd9c28e6f'
OLD_PROFILE = '92942b742bf7fc1b249e512eeb3ba9c4472b746b6214803855d2e23a5c11d67a'
OLD_ADAPTER_SHA = '2f608d08379791a4418264f221cd05133d7adc253bff5abc474320ffe66a28a4'
CLAIM = ('Current T31 workflow Source and exact API49 private output schema/origins; '
         'no private plan/grant, WorkflowRun append, actual producer or consumer, '
         'portable installation, or owner effect.')


def sha(raw): return hashlib.sha256(raw).hexdigest()


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
                raise ValueError('selected regular input required')
            chunks = []
            while block := os.read(fd, 1024 * 1024):
                chunks.append(block)
            after = os.fstat(fd)
            named = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
            stamp = lambda v: (v.st_dev, v.st_ino, v.st_size, v.st_mtime_ns, v.st_ctime_ns)
            if stamp(before) != stamp(after) or stamp(after) != stamp(named):
                raise ValueError('selected input changed during read')
            return b''.join(chunks)
        finally:
            os.close(fd)
    finally:
        for handle in reversed(handles):
            os.close(handle)


def digest(path): return sha(exact(path))


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


def replace_exact(raw, old, new, count):
    if raw.count(old) != count:
        raise ValueError('exact API49 edit anchor differs: ' + old[:80])
    return raw.replace(old, new)


def main():
    if digest(OLD / 'source-manifest.json') != OLD_SOURCE or digest(OLD / 'contract-profile.json') != OLD_PROFILE:
        raise ValueError('frozen API48 source/profile differs')
    if digest(OLD_ADAPTER) != OLD_ADAPTER_SHA:
        raise ValueError('frozen API48 assembler differs')
    if NEW.exists() or NEW_ADAPTER.exists():
        raise ValueError('versioned API49 output already exists')
    manifest = json.loads(exact(OLD / 'source-manifest.json'))
    profile = json.loads(exact(OLD / 'contract-profile.json'))
    old_prefix = OLD.relative_to(ROOT).as_posix() + '/'
    new_prefix = NEW.relative_to(ROOT).as_posix() + '/'
    own = [r for r in manifest['files'] if r['path'].startswith(old_prefix)]
    if len(manifest['files']) != 208 or len(own) != 201 or len(profile['files']) != 33425:
        raise ValueError('API48 selected inventory differs')
    physical = {p.relative_to(OLD).as_posix() for p in OLD.rglob('*') if p.is_file()
                and p.name not in ('source-manifest.json', 'rebind-receipt.json')
                and '__pycache__' not in p.parts and p.suffix != '.pyc'}
    if physical != {r['path'][len(old_prefix):] for r in own}:
        raise ValueError('API48 physical/source closure differs')
    for selected in own:
        if digest(OLD / selected['path'][len(old_prefix):]) != selected['sha256']:
            raise ValueError('frozen API48 selected byte differs')

    schema = exact(OLD / 'workflow-output-plan.schema.json').decode()
    old_service = 'product/lab/release-candidates/v1/interface/api-integration-v30/service.py'
    new_service = new_prefix + 'service.py'
    schema = replace_exact(schema, old_service, new_service, 2)
    registry = exact(OLD / 'workflow_output_registry.py').decode()
    registry = replace_exact(registry, old_prefix + 'workflow_', new_prefix + 'workflow_', 7)
    bridge = exact(OLD / 'source_bridge.py').decode()
    bridge = replace_exact(bridge, '_cal_api48_t31_legacy_local_20261023_0001',
                           '_cal_api49_t31_legacy_local_20261023_0001', 1)
    bridge = replace_exact(bridge, '_cal_api48_t31_source8_local_20261023_0001',
                           '_cal_api49_t31_source8_local_20261023_0001', 1)
    guard = exact(OLD / 'guard.py').decode()
    guard = replace_exact(guard, OLD_ADAPTER.relative_to(ROOT).as_posix(),
                          NEW_ADAPTER.relative_to(ROOT).as_posix(), 1)
    adapter = exact(OLD_ADAPTER).decode()
    adapter = replace_exact(adapter, OLD.name, NEW.name, 1)
    changed = {'workflow-output-plan.schema.json': schema.encode(),
               'workflow_output_registry.py': registry.encode(),
               'source_bridge.py': bridge.encode(),
               'guard.py': guard.encode()}
    NEW_ADAPTER.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    new_file(NEW_ADAPTER, adapter.encode())
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
    new_profile_rows = []
    for selected in profile['files']:
        path = selected['path']
        if path.startswith(old_prefix):
            new_profile_rows.append(row(NEW / path[len(old_prefix):]))
        elif path == old_adapter_path:
            new_profile_rows.append(row(NEW_ADAPTER))
        else:
            new_profile_rows.append(selected)
    if len(new_profile_rows) != 33425 or len({r['path'] for r in new_profile_rows}) != 33425:
        raise ValueError('API49 profile inventory differs')
    profile['files'] = sorted(new_profile_rows, key=lambda r: r['path'])
    profile['integration_members_binding'] = row(NEW / 'integration-members.json')
    profile['claim_ceiling'] = CLAIM
    save(NEW / 'contract-profile.json', profile)

    new_source_rows = []
    for selected in manifest['files']:
        path = selected['path']
        if path.startswith(old_prefix):
            new_source_rows.append(row(NEW / path[len(old_prefix):]))
        elif path == old_adapter_path:
            new_source_rows.append(row(NEW_ADAPTER))
        else:
            new_source_rows.append(selected)
    if len(new_source_rows) != 208 or len({r['path'] for r in new_source_rows}) != 208:
        raise ValueError('API49 source inventory differs')
    manifest['files'] = sorted(new_source_rows, key=lambda r: r['path'])
    manifest['profile_binding'] = row(NEW / 'contract-profile.json')
    manifest['predecessor_source_manifest_binding'] = row(OLD / 'source-manifest.json')
    manifest['claim_ceiling'] = CLAIM
    save(NEW / 'source-manifest.json', manifest)
    receipt = {'schema_version': 'lab-T31-API49-output-schema-current-rebind/v1-candidate',
               'predecessor_source_binding': row(OLD / 'source-manifest.json'),
               'successor_source_binding': row(NEW / 'source-manifest.json'),
               'successor_profile_binding': row(NEW / 'contract-profile.json'),
               'adapter_binding': row(NEW_ADAPTER),
               'successor_package': NEW.relative_to(ROOT).as_posix(),
               'successor_manifest_sha256': digest(NEW / 'source-manifest.json'),
               'source_files': len(new_source_rows), 'profile_files': len(new_profile_rows),
               'schema_service_path_replacements': 2, 'staged_origin_replacements': 7,
               'authority_effect': 'none', 'actual_workflow_transitions': 0,
               'claim_ceiling': CLAIM}
    save(NEW / 'rebind-receipt.json', receipt)
    print(json.dumps({'source_sha256': digest(NEW / 'source-manifest.json'),
                      'profile_sha256': digest(NEW / 'contract-profile.json'),
                      'adapter_sha256': digest(NEW_ADAPTER),
                      'source_files': len(new_source_rows), 'profile_files': len(new_profile_rows)},
                     sort_keys=True))


if __name__ == '__main__': main()
