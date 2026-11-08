"""H79 explicit fail-closed correction to reviewed H78 inactive candidate.

All former asserts are executable integrity predicates under optimized Python.
"""
"""Exact API source and selected environment before owned effects."""
from . import runtime_selection as PORTABLE
import hashlib, importlib.metadata, json, os, platform, stat, re
from pathlib import Path, PurePosixPath
HERE = Path(__file__).resolve().parent
ROOT = PORTABLE.ROOT

def _verify_files(root, rows):
    """Read every original file through current, per-call directory anchors.

    Anchors cache only open directory descriptors inside this invocation.
    Bytes, hashes, permissions, channels and grants are never cached. Verify
    file identity across each read and directory attachment after all reads.
    """
    root = Path(root)
    if not root.is_absolute():
        raise ValueError('absolute source root required')
    ancestry = {}
    for path in (root, *root.parents):
        value = path.lstat()
        if not stat.S_ISDIR(value.st_mode):
            raise ValueError('unsafe source ancestor ')
        ancestry[path] = (value.st_dev, value.st_ino)
    handles = {}
    stamps = {}
    file_stamps = []
    verified = 0

    def directory(parts):
        if parts in handles:
            return handles[parts]
        if not parts:
            handle = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        else:
            handle = os.open(parts[-1], os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=directory(parts[:-1]))
        handles[parts] = handle
        value = os.fstat(handle)
        if not stat.S_ISDIR(value.st_mode):
            raise ValueError('source ancestor is not a directory')
        stamps[parts] = (value.st_dev, value.st_ino)
        return handle

    def identity(value):
        return (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)
    try:
        directory(())
        for row in rows:
            path = row['path']
            relative = PurePosixPath(path)
            if not (type(path) is str and relative.parts and ('..' not in relative.parts) and (relative.as_posix() == path)):
                raise ValueError('unsafe source path')
            if not relative.is_absolute():
                relative = PurePosixPath(root.as_posix()) / relative
            relative = PurePosixPath(*relative.parts[1:])
            if not relative.parts:
                raise ValueError('source path names the filesystem root')
            parent = directory(relative.parts[:-1])
            handle = os.open(relative.parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK, dir_fd=parent)
            try:
                before = os.fstat(handle)
                if not stat.S_ISREG(before.st_mode):
                    raise ValueError('source is not a regular file ' + path)
                digest = hashlib.sha256()
                size = 0
                while True:
                    raw = os.read(handle, 1024 * 1024)
                    if not raw:
                        break
                    digest.update(raw)
                    size += len(raw)
                after = os.fstat(handle)
                current = os.stat(relative.parts[-1], dir_fd=parent, follow_symlinks=False)
                if not (stat.S_ISREG(current.st_mode) and size == before.st_size and (identity(before) == identity(after) == identity(current))):
                    raise ValueError('source changed during read ' + path)
                if not digest.hexdigest() == row['sha256']:
                    raise ValueError('source changed ' + path)
                file_stamps.append((relative.parts, identity(current)))
                verified += 1
            finally:
                os.close(handle)
        for parts, expected in file_stamps:
            value = os.stat(parts[-1], dir_fd=handles[parts[:-1]], follow_symlinks=False)
            if not (stat.S_ISREG(value.st_mode) and identity(value) == expected):
                raise ValueError('source changed after read ')
        for parts in sorted(handles, key=len, reverse=True):
            value = os.stat('/'.join(parts) or '.', dir_fd=handles[()], follow_symlinks=False)
            if not (stat.S_ISDIR(value.st_mode) and (value.st_dev, value.st_ino) == stamps[parts]):
                raise ValueError('source directory attachment changed')
        for path, expected in ancestry.items():
            value = path.lstat()
            if not (stat.S_ISDIR(value.st_mode) and (value.st_dev, value.st_ino) == expected):
                raise ValueError('source root ancestry changed')
        return {'verified_files': verified, 'anchored_directories': len(handles)}
    finally:
        for parts in sorted(handles, key=len, reverse=True):
            os.close(handles[parts])

def _capture_exact(root, binding):
    """Capture <=64 MiB with exact SHA and fresh complete attachment checks."""

    def require(value, reason):
        if not value:
            raise ValueError(reason)
    require(type(binding) is dict and set(binding) == {'path', 'sha256'}, 'closed exact capture binding required')
    name = binding['path']
    require(type(name) is str and bool(name) and ('\\' not in name) and ('\x00' not in name), 'unsafe capture path')
    path = PurePosixPath(name)
    require(path.as_posix() == name and '..' not in path.parts and (name not in ('.', '/')), 'unsafe capture path')
    require(type(binding['sha256']) is str and re.fullmatch('[a-f0-9]{64}', binding['sha256']), 'independent capture digest required')
    root = Path(root)
    require(root.is_absolute() and '..' not in root.parts, 'absolute capture root required')
    if not path.is_absolute():
        path = PurePosixPath(root.as_posix()) / path
    parts = path.parts[1:]
    directories = []
    file_handle = None
    links = []

    def identity(value):
        return (value.st_dev, value.st_ino, value.st_mode, value.st_uid, value.st_gid, value.st_nlink, value.st_size, value.st_mtime_ns, value.st_ctime_ns)
    try:
        parent = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        directories.append(parent)
        for part in parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=parent)
            directories.append(child)
            info = os.fstat(child)
            require(stat.S_ISDIR(info.st_mode) and info.st_mode & 73, 'unsafe capture ancestor')
            attached = os.stat(part, dir_fd=parent, follow_symlinks=False)
            require(stat.S_ISDIR(attached.st_mode) and (attached.st_dev, attached.st_ino) == (info.st_dev, info.st_ino), 'capture ancestor changed during open')
            links.append((parent, part, child, info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid))
            parent = child
        file_handle = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK, dir_fd=parent)
        before = os.fstat(file_handle)
        require(stat.S_ISREG(before.st_mode) and before.st_mode & 292, 'regular readable capture required')
        require(before.st_size <= 64 * 1024 * 1024, 'capture metadata exceeds 64 MiB')
        size = 0
        digest = hashlib.sha256()
        chunks = []
        while True:
            chunk = os.read(file_handle, min(1024 * 1024, 64 * 1024 * 1024 - size + 1))
            if not chunk:
                break
            size += len(chunk)
            require(size <= 64 * 1024 * 1024, 'capture metadata grew beyond 64 MiB')
            digest.update(chunk)
            chunks.append(chunk)
        after = os.fstat(file_handle)
        attached = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        require(stat.S_ISREG(attached.st_mode) and size == before.st_size and (identity(before) == identity(after) == identity(attached)), 'capture file identity changed')
        require(digest.hexdigest() == binding['sha256'], 'capture digest differs')
        for ancestor, part, held, device, inode, mode, uid, gid in reversed(links):
            value = os.stat(part, dir_fd=ancestor, follow_symlinks=False)
            held_value = os.fstat(held)
            require(stat.S_ISDIR(value.st_mode) and (value.st_dev, value.st_ino, value.st_mode, value.st_uid, value.st_gid) == (held_value.st_dev, held_value.st_ino, held_value.st_mode, held_value.st_uid, held_value.st_gid) == (device, inode, mode, uid, gid), 'capture ancestor attachment changed')
        require(identity(os.fstat(file_handle)) == identity(os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)) == identity(before), 'capture file changed before return')
        return b''.join(chunks)
    except OSError as error:
        raise ValueError('capture unsafe/unreadable/missing attachment') from error
    finally:
        if file_handle is not None:
            os.close(file_handle)
        for handle in reversed(directories):
            os.close(handle)

def verify(pin):
    """Exact local successor bytes; historical input accounting is unqualified."""
    PORTABLE.guard()
    expected = PORTABLE.binding('api.source')
    if expected != {'path':str((HERE/'source-manifest.json').relative_to(ROOT)),'sha256':pin}:
        raise ValueError('API source differs from trusted private installation selection')
    path = HERE / 'source-manifest.json'
    selected = {'path': str(path.relative_to(ROOT)), 'sha256': pin}
    raw = _capture_exact(ROOT, selected)
    manifest = json.loads(raw)
    required = {'schema_version','environment','authority_effect','actual_owner_outcome',
                'historical_input_accounting_qualified','claim_ceiling','files',
                'family_source_manifest_binding','family_source_package_binding',
                'family_reader_manifest_binding','family_mapped_package_binding',
                'family_mapping_binding',
                'family_context_manifest_binding','family_context_package_binding',
                'profile_binding','engine_profile_binding','predecessor_source_manifest_binding'}
    if set(manifest) != required or manifest['schema_version'] != 'lab-api30-current-source-successor/v1':
        raise ValueError('selected local API successor manifest differs')
    if manifest['environment'] != {'python': platform.python_version(),
                                  'jsonschema': importlib.metadata.version('jsonschema'),
                                  'cryptography': importlib.metadata.version('cryptography')}:
        raise ValueError('API environment differs')
    if manifest['authority_effect'] != 'none' or manifest['actual_owner_outcome'] is not None or manifest['historical_input_accounting_qualified'] is not False:
        raise ValueError('local successor claim exceeded')
    rows = manifest['files']
    if type(rows) is not list or not rows or len({r['path'] for r in rows}) != len(rows):
        raise ValueError('closed unique successor byte rows required')
    package = HERE.relative_to(ROOT).as_posix() + '/'
    helpers = ('machine-context-scope-v3-api25-completion-0001',
               'machine-context-scope-v4-api33-legacy-0001',
               'machine-context-scope-v5-api33-current-legacy-0001')
    helper_paths = {str((HERE.parent / helper / name).relative_to(ROOT))
                    for helper in helpers for name in ('__init__.py','generation.py')}
    lesson_paths = {str((HERE.parent / helper / name).relative_to(ROOT))
                    for helper, names in (
                        ('lesson-host-composition-v50-t03-final-live-0001', ('__init__.py','host.py','plan.schema.json')),
                        ('lesson-application-v8-t03-scope-custody-0001', ('__init__.py','preparation.py')),
                        ('lesson-assessment-v4-t03-independent-effect-0001', ('__init__.py','preparation.py')))
                    for name in names}
    helper_paths |= lesson_paths
    helper_paths |= {'product/lab/release-candidates/v1/interface/api-integration-v30/source-manifest.json', 'authority/admissions/lab-specialist-owner-bootstrap-v1-0003/instances/project-state.json', 'authority/project-state-transitions/current.json'}
    helper_paths.add("implementation/lab-runtime/local-host/t22-api30-episode-inspection-0002/episode.py")
    helper_paths |= set(('implementation/lab-runtime/local-host/t25-integrated-runtime-0004/child_bootstrap.py', 'implementation/lab-runtime/local-host/t25-integrated-runtime-0004/installed_selection.py', 'implementation/lab-runtime/local-host/t25-integrated-runtime-0004/native_install.py', 'implementation/lab-runtime/local-host/t25-native-launcher-0001/selected-python'))
    helper_paths |= {str((HERE.parent / helper / name).relative_to(ROOT))
                     for helper in ('classification-preparation-v9', 'failure-preparation-v5')
                     for name in ('preparation.py', 'routing.schema.json')}
    helper_paths.add('authority/artifact-types/ontology-view/v1/fixtures/valid/record.json')
    actual_helpers = set()
    for row in rows:
        if type(row) is not dict or set(row) != {'path','sha256'} or type(row['path']) is not str or type(row['sha256']) is not str or not re.fullmatch('[a-f0-9]{64}',row['sha256']):
            raise ValueError('invalid successor byte row')
        if row['path'] in helper_paths:
            actual_helpers.add(row['path'])
        elif not row['path'].startswith(package):
            raise ValueError('foreign successor byte row')
    if actual_helpers != helper_paths:
        raise ValueError('external Machine/Lesson helper closure differs')
    actual = {p.relative_to(ROOT).as_posix() for p in HERE.rglob('*')
              if p.is_file() and p != path and p.name != 'rebind-receipt.json'
              and '__pycache__' not in p.parts and 'receipts' not in p.parts and p.suffix != '.pyc'}
    listed = {r['path'] for r in rows if r['path'].startswith(package)}
    if actual != listed:
        raise ValueError('local successor file set differs')
    selected_bindings = (manifest['family_source_manifest_binding'],
                         manifest['family_source_package_binding'],
                         manifest['family_reader_manifest_binding'],
                         manifest['family_mapped_package_binding'],
                         manifest['family_mapping_binding'],
                         manifest['family_context_manifest_binding'],
                         manifest['family_context_package_binding'],
                         manifest['profile_binding'],
                         manifest['engine_profile_binding'],
                         manifest['predecessor_source_manifest_binding'])
    for binding in selected_bindings:
        _capture_exact(ROOT,binding)
    _verify_files(ROOT,rows)
    for binding in selected_bindings:
        _capture_exact(ROOT,binding)
    if _capture_exact(ROOT,selected) != raw:
        raise ValueError('local successor manifest changed during verification')
    return manifest
