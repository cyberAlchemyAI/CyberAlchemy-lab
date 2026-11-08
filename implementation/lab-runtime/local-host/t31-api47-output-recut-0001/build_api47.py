"""One-shot closed API47 successor for current private workflow output producers."""
import hashlib
import json
import os
from pathlib import Path
import stat

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-integration-v46-t31-workflow-current-0002'
NEW = BASE / 'api-integration-v47-t31-output-current-0001'
ADAPTER = ROOT / 'implementation/lab-runtime/local-host/t31-api47-output-bootstrap-0002/bootstrap.py'
OLD_SOURCE = 'caf4aa1f4dbfcc8a5eab336e15704487f3e1913b8d76bfbcfbd88b56204a0969'
OLD_PROFILE = 'a4a2afdf2853f135a473c19b8dd83dc4cd3b587bc00821a227a4790a365c7402'
CLAIM = ('Current T31 API source with selected all28 output-assembler code and true-origin staged producer '
         'allowlist only; no private output plan, original producer call, workflow transition, or authority effect qualified.')


def exact(path):
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('closed absolute path required')
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
            while True:
                chunk = os.read(fd, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
            after = os.fstat(fd)
            attached = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
            if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns) or (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (attached.st_dev, attached.st_ino, attached.st_size, attached.st_mtime_ns, attached.st_ctime_ns):
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


def main():
    if digest(OLD/'source-manifest.json') != OLD_SOURCE or digest(OLD/'contract-profile.json') != OLD_PROFILE:
        raise ValueError('frozen API46 input differs')
    if NEW.exists():
        raise ValueError('API47 output already exists')
    manifest = json.loads(exact(OLD/'source-manifest.json'))
    profile = json.loads(exact(OLD/'contract-profile.json'))
    old_prefix = OLD.relative_to(ROOT).as_posix() + '/'
    own = [selected for selected in manifest['files'] if selected['path'].startswith(old_prefix)]
    if len(own) != 201 or len(manifest['files']) != 207 or len({r['path'] for r in own}) != 201:
        raise ValueError('frozen API46 source inventory differs')
    actual = {p.relative_to(OLD).as_posix() for p in OLD.rglob('*') if p.is_file()
              and p.name not in ('source-manifest.json', 'rebind-receipt.json')
              and '__pycache__' not in p.parts and p.suffix != '.pyc'}
    if actual != {r['path'][len(old_prefix):] for r in own}:
        raise ValueError('frozen API46 physical inventory differs')
    for selected in own:
        if digest(OLD / selected['path'][len(old_prefix):]) != selected['sha256']:
            raise ValueError('frozen API46 byte differs')
    if digest(ADAPTER) != '06b8346aba1feef12e07a0d14c7a6b5cb95f1aaaebd76827e042f3ed83cdcc85':
        raise ValueError('API47 adapter release pin differs')
    NEW.mkdir(mode=0o700)
    changed = {'workflow_output_registry.py', 'guard.py'}
    for selected in own:
        name = selected['path'][len(old_prefix):]
        if name in changed or name == 'contract-profile.json':
            continue
        destination = NEW/name
        destination.parent.mkdir(parents=True, exist_ok=True)
        new_file(destination, exact(OLD/name))
    registry = exact(OLD/'workflow_output_registry.py').decode()
    old_staged = "STAGED_PRODUCER_ORIGINS = ("
    head, tail = registry.split(old_staged, 1)
    first, end = tail.split('\n', 1)
    if first.count('api-integration-v23/') != 7:
        raise ValueError('seven historical staged producer origins required')
    first = first.replace('api-integration-v23/', NEW.name + '/')
    new_file(NEW/'workflow_output_registry.py', (head + old_staged + first + '\n' + end).encode())
    guard = exact(OLD/'guard.py').decode()
    expected = "helper_paths = {str((HERE.parent / helper / name).relative_to(ROOT))\n                    for helper in helpers for name in ('__init__.py','generation.py')}"
    if guard.count(expected) != 1:
        raise ValueError('frozen API46 helper closure differs')
    added = expected + "\n    helper_paths.add('" + ADAPTER.relative_to(ROOT).as_posix() + "')"
    new_file(NEW/'guard.py', guard.replace(expected, added).encode())
    old_profile_rows = profile['files']
    rebound = [row(NEW / selected['path'][len(old_prefix):]) if selected['path'].startswith(old_prefix) else selected
               for selected in old_profile_rows]
    if len(rebound) != 33424 or sum(x['path'].startswith(OLD.relative_to(ROOT).as_posix()+'/') for x in rebound) != 0:
        raise ValueError('API46 profile recut differs')
    rebound.append(row(ADAPTER))
    if len({r['path'] for r in rebound}) != len(rebound):
        raise ValueError('API47 profile duplicate row')
    profile['files'] = sorted(rebound, key=lambda item: item['path'])
    profile['integration_members_binding'] = row(NEW/'integration-members.json')
    profile['claim_ceiling'] = CLAIM
    save(NEW/'contract-profile.json', profile)
    files = [row(NEW / selected['path'][len(old_prefix):]) if selected['path'].startswith(old_prefix) else selected
             for selected in manifest['files']]
    files.append(row(ADAPTER))
    if len(files) != 208 or len({r['path'] for r in files}) != 208:
        raise ValueError('API47 selected source closure differs')
    manifest['files'] = sorted(files, key=lambda item: item['path'])
    manifest['profile_binding'] = row(NEW/'contract-profile.json')
    manifest['predecessor_source_manifest_binding'] = row(OLD/'source-manifest.json')
    manifest['claim_ceiling'] = CLAIM
    save(NEW/'source-manifest.json', manifest)
    receipt = {'schema_version':'lab-T31-API47-output-origin-rebind/v1-candidate',
               'successor_package':NEW.relative_to(ROOT).as_posix(),
               'successor_manifest_sha256':digest(NEW/'source-manifest.json'),
               'predecessor_source_binding':row(OLD/'source-manifest.json'),
               'successor_source_binding':row(NEW/'source-manifest.json'),
               'successor_profile_binding':row(NEW/'contract-profile.json'),
               'adapter_binding':row(ADAPTER), 'source_files':len(files), 'profile_files':len(rebound),
               'staged_origin_replacements':7, 'authority_effect':'none', 'actual_producer_calls':0,
               'claim_ceiling':CLAIM}
    save(NEW/'rebind-receipt.json', receipt)
    print(json.dumps({'source_sha256':digest(NEW/'source-manifest.json'),
                      'profile_sha256':digest(NEW/'contract-profile.json'),
                      'source_files':len(files),'profile_files':len(rebound)}))


if __name__ == '__main__':
    main()
