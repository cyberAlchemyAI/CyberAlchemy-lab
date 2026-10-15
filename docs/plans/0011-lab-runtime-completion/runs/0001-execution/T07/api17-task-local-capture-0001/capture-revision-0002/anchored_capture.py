"""Same verified no-follow metadata bytes; no callback, clock or body cache."""
import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import stat


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
