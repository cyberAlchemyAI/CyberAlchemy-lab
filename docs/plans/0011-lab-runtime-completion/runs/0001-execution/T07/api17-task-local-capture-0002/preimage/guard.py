"""Exact API source and selected environment before owned effects."""
import hashlib,importlib.metadata,json,os,platform,stat
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


def _accounting(manifest):
    """Verify all original row accounting separately from actual current bytes."""
    from types import ModuleType
    book=manifest['input_accounting']
    assert type(book) is dict and set(book)=={
        'component_binding','module_binding','source_binding','profile_binding',
        'unavailable_binding','selection_binding'},'closed input accounting bindings required'
    def captured(binding):
        assert type(binding) is dict and set(binding)=={'path','sha256'},'exact accounting binding required'
        _verify_files(ROOT,[binding])
        raw=(ROOT/binding['path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==binding['sha256'],'accounting bytes changed'
        return raw
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
    path=HERE/'source-manifest.json';raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==pin,'independent API source pin differs'
    manifest=json.loads(raw)
    assert manifest['schema_version']=='lab-runtime-execution-source/v2-candidate','explicit current execution manifest required'
    assert manifest['environment']=={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},'API environment differs'
    assert manifest['authority_effect']=='none' and manifest['actual_owner_outcome'] is None
    before=_accounting(manifest)
    _verify_files(ROOT, manifest['files'])
    after=_accounting(manifest)
    assert before['historical_original_physical_closure']==after['historical_original_physical_closure']=='REFUSED', 'historical proof cannot inherit execution PASS'
    assert before['original_source_files']==after['original_source_files'] and before['original_profile_files']==after['original_profile_files'], 'complete original row accounting changed'
    assert path.read_bytes()==raw,'source manifest changed during verification'
    return manifest
