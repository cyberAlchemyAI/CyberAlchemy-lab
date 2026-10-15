"""Exact API source and selected environment before owned effects."""
import hashlib,importlib.metadata,json,os,platform,stat,re
from pathlib import Path,PurePosixPath
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]


def _verify_files(root, rows):
    """Read every original file through current, per-call directory anchors.

    Anchors cache only open directory descriptors inside this invocation.
    Bytes, hashes, permissions, channels and grants are never cached. Verify
    file identity across each read and directory attachment after all reads.
    """
    root = Path(root)
    assert root.is_absolute(), 'absolute source root required'
    ancestry = {}
    for path in (root, *root.parents):
        value = path.lstat()
        assert stat.S_ISDIR(value.st_mode), 'unsafe source ancestor '
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
            handle = os.open(parts[-1], os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                             dir_fd=directory(parts[:-1]))
        handles[parts] = handle
        value = os.fstat(handle)
        assert stat.S_ISDIR(value.st_mode), 'source ancestor is not a directory'
        stamps[parts] = (value.st_dev, value.st_ino)
        return handle

    def identity(value):
        return (value.st_dev, value.st_ino, value.st_size,
                value.st_mtime_ns, value.st_ctime_ns)

    try:
        directory(())
        for row in rows:
            path = row['path']
            relative = PurePosixPath(path)
            assert type(path) is str and relative.parts \
                and '..' not in relative.parts and relative.as_posix() == path, 'unsafe source path'
            # Existing frozen selections include exact absolute migration sources
            # and the native reader. Preserve their complete selection and guard
            # every ancestor through the filesystem anchor; no external default.
            if not relative.is_absolute():
                relative = PurePosixPath(root.as_posix()) / relative
            relative = PurePosixPath(*relative.parts[1:])
            assert relative.parts, 'source path names the filesystem root'
            parent = directory(relative.parts[:-1])
            handle = os.open(relative.parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK,
                             dir_fd=parent)
            try:
                before = os.fstat(handle)
                assert stat.S_ISREG(before.st_mode), 'source is not a regular file '+path
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
                assert stat.S_ISREG(current.st_mode) and size == before.st_size \
                    and identity(before) == identity(after) == identity(current), 'source changed during read '+path
                assert digest.hexdigest() == row['sha256'], 'source changed '+path
                file_stamps.append((relative.parts, identity(current)))
                verified += 1
            finally:
                os.close(handle)
        for parts, expected in file_stamps:
            value = os.stat(parts[-1], dir_fd=handles[parts[:-1]], follow_symlinks=False)
            assert stat.S_ISREG(value.st_mode) and identity(value) == expected, 'source changed after read '
        for parts in sorted(handles, key=len, reverse=True):
            value = os.stat('/'.join(parts) or '.', dir_fd=handles[()], follow_symlinks=False)
            assert stat.S_ISDIR(value.st_mode) and (value.st_dev, value.st_ino) == stamps[parts], \
                'source directory attachment changed'
        for path, expected in ancestry.items():
            value = path.lstat()
            assert stat.S_ISDIR(value.st_mode) and (value.st_dev, value.st_ino) == expected, \
                'source root ancestry changed'
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
    require(type(name) is str and bool(name) and '\\' not in name and '\x00' not in name,
            'unsafe capture path')
    path = PurePosixPath(name)
    require(path.as_posix() == name and '..' not in path.parts and name not in ('.', '/'), 'unsafe capture path')
    require(type(binding['sha256']) is str and re.fullmatch('[a-f0-9]{64}', binding['sha256']),
            'independent capture digest required')
    root = Path(root)
    require(root.is_absolute() and '..' not in root.parts, 'absolute capture root required')
    if not path.is_absolute():
        path = PurePosixPath(root.as_posix()) / path
    parts = path.parts[1:]
    directories = []
    file_handle = None
    links = []
    def identity(value):
        return (value.st_dev, value.st_ino, value.st_mode, value.st_uid, value.st_gid,
                value.st_nlink, value.st_size, value.st_mtime_ns, value.st_ctime_ns)
    try:
        parent = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        directories.append(parent)
        for part in parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                            dir_fd=parent)
            directories.append(child)
            info = os.fstat(child)
            require(stat.S_ISDIR(info.st_mode) and info.st_mode & 0o111, 'unsafe capture ancestor')
            attached = os.stat(part, dir_fd=parent, follow_symlinks=False)
            require(stat.S_ISDIR(attached.st_mode) and (attached.st_dev, attached.st_ino) ==
                    (info.st_dev, info.st_ino), 'capture ancestor changed during open')
            links.append((parent, part, child, info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid))
            parent = child
        file_handle = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK,
                              dir_fd=parent)
        before = os.fstat(file_handle)
        require(stat.S_ISREG(before.st_mode) and before.st_mode & 0o444, 'regular readable capture required')
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
        require(stat.S_ISREG(attached.st_mode) and size == before.st_size and
                identity(before) == identity(after) == identity(attached), 'capture file identity changed')
        require(digest.hexdigest() == binding['sha256'], 'capture digest differs')
        for ancestor, part, held, device, inode, mode, uid, gid in reversed(links):
            value = os.stat(part, dir_fd=ancestor, follow_symlinks=False)
            held_value = os.fstat(held)
            require(stat.S_ISDIR(value.st_mode) and
                    (value.st_dev, value.st_ino, value.st_mode, value.st_uid, value.st_gid) ==
                    (held_value.st_dev, held_value.st_ino, held_value.st_mode, held_value.st_uid, held_value.st_gid) ==
                    (device, inode, mode, uid, gid), 'capture ancestor attachment changed')
        require(identity(os.fstat(file_handle)) == identity(os.stat(parts[-1], dir_fd=parent,
                follow_symlinks=False)) == identity(before), 'capture file changed before return')
        return b''.join(chunks)
    except OSError as error:
        raise ValueError('capture unsafe/unreadable/missing attachment') from error
    finally:
        if file_handle is not None:
            os.close(file_handle)
        for handle in reversed(directories):
            os.close(handle)


def _accounting(manifest):
    """Verify all original row accounting separately from actual current bytes."""
    from types import ModuleType
    book=manifest['input_accounting']
    assert type(book) is dict and set(book)=={
        'component_binding','module_binding','source_binding','profile_binding',
        'unavailable_binding','selection_binding'},'closed input accounting bindings required'
    def captured(binding):
        assert type(binding) is dict and set(binding)=={'path','sha256'},'exact accounting binding required'
        return _capture_exact(ROOT,binding)
    helper=HERE.parent/'runtime-input-accounting-v1-completion-0001'
    assert book['component_binding']=={
        'path':str((helper/'source-manifest.json').relative_to(ROOT)),
        'sha256':'54fad4029d47435faaa3a6dad215f6d268b6589c1be982d9e764f27ef2880729'},'independent accounting component differs'
    assert book['module_binding']=={
        'path':str((helper/'accounting.py').relative_to(ROOT)),
        'sha256':'3063e5eafd2ffd2873ee034a0516f8c35c3ca6f9178971fb9788176107debc78'},'independent accounting code differs'
    component=json.loads(captured(book['component_binding']))
    assert book['module_binding'] in component['files'],'accounting code outside frozen component'
    raw=captured(book['module_binding'])
    module=ModuleType('_cal_api17_exact_accounting')
    module.__file__=str(helper/'accounting.py')
    # Compile the exact captured bytes each invocation; no pyc or module cache.
    exec(compile(raw,module.__file__,'exec'),module.__dict__)
    return module.verify(captured(book['source_binding']),captured(book['profile_binding']),
        captured(book['unavailable_binding']),book['unavailable_binding']['sha256'],
        captured(book['selection_binding']),book['selection_binding']['sha256'],
        manifest['files'],ROOT)


def verify(pin):
    path=HERE/'source-manifest.json'
    source_binding={'path':str(path.relative_to(ROOT)),'sha256':pin}
    raw=_capture_exact(ROOT,source_binding)
    manifest=json.loads(raw)
    assert manifest['schema_version']=='lab-runtime-execution-source/v2-candidate','explicit current execution manifest required'
    assert manifest['environment']=={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},'API environment differs'
    assert manifest['authority_effect']=='none' and manifest['actual_owner_outcome'] is None
    before=_accounting(manifest)
    _verify_files(ROOT, manifest['files'])
    after=_accounting(manifest)
    assert before['historical_original_physical_closure']==after['historical_original_physical_closure']=='REFUSED', 'historical proof cannot inherit execution PASS'
    assert before['original_source_files']==after['original_source_files'] and before['original_profile_files']==after['original_profile_files'], 'complete original row accounting changed'
    assert _capture_exact(ROOT,source_binding)==raw,'source manifest changed during verification'
    return manifest
