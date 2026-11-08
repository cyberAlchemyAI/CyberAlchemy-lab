"""Rollback only an exact, owned, uncommitted technical stage in a private root."""

import hashlib
import fcntl
import os
from pathlib import PurePosixPath
import stat


def need(value, reason):
    if not value:
        raise ValueError(reason)


def identity(info):
    return (info.st_dev, info.st_ino, info.st_uid, stat.S_IMODE(info.st_mode))


def rollback(root, stage_name, expected_files):
    """Remove a known exact subset after a precommit fault; preserve everything else.

    The caller must already have closed the publisher and observed its explicit
    precommit residue result. The private root is owned by this disposable run.
    """
    need(type(expected_files) is dict and expected_files, 'selected byte set required')
    need(stage_name.startswith('.') and '/' not in stage_name and '..' not in stage_name,
         'selected stage name required')
    expected = {}
    for path, raw in expected_files.items():
        p = PurePosixPath(path)
        need(type(path) is str and path and not p.is_absolute() and '..' not in p.parts
             and p.as_posix() == path and type(raw) is bytes, 'selected stage path required')
        expected[path] = hashlib.sha256(raw).digest()
    root_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    held = []
    lock_fd = None
    locked = False
    try:
        info = os.fstat(root_fd)
        need(stat.S_ISDIR(info.st_mode) and info.st_uid == os.getuid()
             and stat.S_IMODE(info.st_mode) == 0o700, 'private owned root required')
        lock_fd = os.open('publisher.lock', os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC,
                          dir_fd=root_fd)
        lock_info = os.fstat(lock_fd)
        need(stat.S_ISREG(lock_info.st_mode) and lock_info.st_uid == os.getuid()
             and stat.S_IMODE(lock_info.st_mode) == 0o600
             and identity(lock_info) == identity(os.stat('publisher.lock', dir_fd=root_fd,
                                                        follow_symlinks=False)),
             'owned publisher lock custody differs')
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('publisher lock busy; rollback refused') from None
        locked = True
        need(set(os.listdir(root_fd)) == {'publisher.lock', stage_name},
             'foreign root residue preserved')
        stage_fd = os.open(stage_name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                           dir_fd=root_fd)
        held.append(stage_fd)
        stage_info = os.fstat(stage_fd)
        need(stat.S_ISDIR(stage_info.st_mode) and stage_info.st_uid == os.getuid()
             and stat.S_IMODE(stage_info.st_mode) == 0o700, 'owned stage required')

        def stage_attached():
            current = os.stat(stage_name, dir_fd=root_fd, follow_symlinks=False)
            need(stat.S_ISDIR(current.st_mode) and identity(current) == identity(stage_info)
                 == identity(os.fstat(stage_fd)), 'held stage attachment changed')
            need(identity(os.fstat(lock_fd)) == identity(os.stat(
                'publisher.lock', dir_fd=root_fd, follow_symlinks=False)),
                 'publisher lock attachment changed')

        stage_attached()
        observed = []

        def scan(fd, prefix):
            rows = []
            for name in sorted(os.listdir(fd)):
                need(name not in ('', '.', '..') and '/' not in name, 'unsafe stage entry')
                path = prefix + name
                info = os.stat(name, dir_fd=fd, follow_symlinks=False)
                if stat.S_ISDIR(info.st_mode):
                    need(info.st_uid == os.getuid() and stat.S_IMODE(info.st_mode) == 0o700,
                         'foreign stage directory preserved')
                    child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                                    dir_fd=fd)
                    held.append(child)
                    need(identity(os.fstat(child)) == identity(info), 'stage directory attachment changed')
                    children = scan(child, path + '/')
                    rows.append(('dir', fd, name, info, children))
                else:
                    need(path in expected and stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid()
                         and stat.S_IMODE(info.st_mode) == 0o600 and info.st_nlink == 1,
                         'foreign stage leaf preserved')
                    leaf = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC,
                                   dir_fd=fd)
                    try:
                        before = os.fstat(leaf)
                        need(stat.S_ISREG(before.st_mode) and identity(before) == identity(info)
                             and before.st_size == info.st_size,
                             'stage leaf attachment changed')
                        with os.fdopen(os.dup(leaf), 'rb') as stream:
                            digest = hashlib.file_digest(stream, 'sha256').digest()
                        after = os.fstat(leaf)
                        need(digest == expected[path] and
                             (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
                             == (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns),
                             'unselected stage bytes preserved')
                    finally:
                        os.close(leaf)
                    observed.append(path)
                    rows.append(('file', fd, name, info, None))
            return rows

        rows = scan(stage_fd, '')
        need(observed and len(observed) < len(expected), 'partial precommit stage required')

        def remove(rows):
            for kind, fd, name, info, children in rows:
                stage_attached()
                if children is not None:
                    remove(children)
                stage_attached()
                current = os.stat(name, dir_fd=fd, follow_symlinks=False)
                if kind == 'dir':
                    need(identity(current) == identity(info), 'stage directory changed before rollback')
                    os.rmdir(name, dir_fd=fd)
                else:
                    need((current.st_dev, current.st_ino, current.st_mtime_ns, current.st_ctime_ns)
                         == (info.st_dev, info.st_ino, info.st_mtime_ns, info.st_ctime_ns),
                         'stage leaf changed before rollback')
                    os.unlink(name, dir_fd=fd)
                os.fsync(fd)

        remove(rows)
        stage_attached()
        need(not os.listdir(stage_fd), 'stage not empty after exact rollback')
        os.rmdir(stage_name, dir_fd=root_fd)
        os.fsync(root_fd)
        need(set(os.listdir(root_fd)) == {'publisher.lock'}, 'rollback root differs')
        return {'rolled_back_selected_files': len(observed), 'foreign_residue_deleted': False}
    finally:
        if locked:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
        if lock_fd is not None:
            os.close(lock_fd)
        for fd in reversed(held):
            os.close(fd)
        os.close(root_fd)
