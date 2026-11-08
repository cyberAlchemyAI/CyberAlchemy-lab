"""Held-dirfd, nofollow copy primitive for the separate Mapper stage.

No real Source file is copied by importing this module. The tested optional
hook is for synthetic ancestor-swap probes only; production callers omit it.
"""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import os
from pathlib import Path
import stat
import sys
from typing import Callable

FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
LEAF_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def identity(info: os.stat_result) -> tuple[int, ...]:
    return (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid,
            info.st_nlink, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def dir_identity(info: os.stat_result) -> tuple[int, ...]:
    # Creating a selected child changes directory mtime/ctime and sometimes
    # link count. Attachment, ownership and effective mode must remain fixed.
    return (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid)


def close_all(fds: list[int], primary: BaseException | None = None) -> None:
    """Attempt every close; accumulate exact secondary errors on a primary.

    Do not rewrite an existing cause: it may carry the selected-byte failure's
    own provenance. Multiple nested finally blocks append to one ordered tuple.
    """
    failures: list[tuple[int, BaseException]] = []
    for fd in reversed(fds):
        try:
            os.close(fd)
        except BaseException as error:
            failures.append((fd, error))
    if failures:
        if primary is not None:
            previous = getattr(primary, 'secondary_close_errors', ())
            primary.secondary_close_errors = previous + tuple(failures)
            primary.add_note('Secondary owned-FD close failures retained: ' +
                             ', '.join(f'fd={fd}:{type(error).__name__}:{error!r}'
                                       for fd, error in failures))
            return
        for fd, error in failures:
            error.add_note(f'owned_fd={fd}')
        raise BaseExceptionGroup('one or more owned FDs failed to close',
                                 [error for _, error in failures])


@contextmanager
def parent_chain(path: Path):
    path = Path(path)
    require(path.is_absolute() and path.name not in ('', '.', '..') and
            '..' not in path.parts, 'absolute normalized path required')
    opened = [os.open('/', FLAGS)]
    try:
        for part in path.parent.parts[1:]:
            opened.append(os.open(part, FLAGS, dir_fd=opened[-1]))
        before = tuple(dir_identity(os.fstat(fd)) for fd in opened)
        yield opened[-1], before
        require(before == tuple(dir_identity(os.fstat(fd)) for fd in opened),
                'held ancestor identity changed')
    finally:
        close_all(opened, sys.exception())


def reattached(path: Path, expected_chain: tuple[tuple[int, ...], ...],
               expected_leaf: tuple[int, ...]) -> None:
    with parent_chain(path) as (parent, chain):
        require(chain == expected_chain, 'ancestor path was detached or replaced')
        actual = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
        require(identity(actual) == expected_leaf, 'leaf path was detached or replaced')


def mkdir_exact(path: Path, mode: int) -> None:
    path = Path(path)
    require(mode in (0o700, 0o755), 'closed stage directory mode required')
    with parent_chain(path) as (parent, chain):
        os.mkdir(path.name, mode, dir_fd=parent)
        child = os.open(path.name, FLAGS, dir_fd=parent)
        try:
            os.fchmod(child, mode)
            os.fsync(child)
            os.fsync(parent)
            observed = os.fstat(child)
            require(stat.S_ISDIR(observed.st_mode) and observed.st_uid == os.getuid() and
                    stat.S_IMODE(observed.st_mode) == mode,
                    'created stage directory owner/mode differs')
            reattached(path, chain, identity(observed))
        finally:
            close_all([child], sys.exception())


def copy_exact(source: Path, target: Path, expected_sha: str,
               target_mode: int, source_mode: int,
               after_copy_hook: Callable[[], None] | None = None) -> None:
    source, target = Path(source), Path(target)
    require(source != target and target_mode in (0o444, 0o600, 0o755) and
            source_mode in (0o444, 0o600, 0o644, 0o755), 'closed copy paths/modes required')
    with parent_chain(source) as (source_parent, source_chain):
        before = os.stat(source.name, dir_fd=source_parent, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
                before.st_uid == os.getuid() and stat.S_IMODE(before.st_mode) == source_mode,
                'source member type/owner/mode differs')
        fd_in = os.open(source.name, LEAF_FLAGS, dir_fd=source_parent)
        try:
            opened = os.fstat(fd_in)
            require(identity(opened) == identity(before), 'source leaf changed before open')
            with parent_chain(target) as (target_parent, target_chain):
                fd_out = os.open(target.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                                 os.O_NOFOLLOW | os.O_CLOEXEC, target_mode,
                                 dir_fd=target_parent)
                digest = hashlib.sha256()
                copied = 0
                try:
                    while True:
                        chunk = os.read(fd_in, 1024 * 1024)
                        if not chunk:
                            break
                        digest.update(chunk)
                        copied += len(chunk)
                        view = memoryview(chunk)
                        while view:
                            count = os.write(fd_out, view)
                            require(count > 0, 'destination write made no progress')
                            view = view[count:]
                    os.fchmod(fd_out, target_mode)
                    os.fsync(fd_out)
                    written = os.fstat(fd_out)
                    require(stat.S_ISREG(written.st_mode) and written.st_nlink == 1 and
                            written.st_uid == os.getuid() and
                            stat.S_IMODE(written.st_mode) == target_mode and
                            copied == written.st_size and digest.hexdigest() == expected_sha,
                            'destination bytes/owner/mode differ')
                    require(identity(os.fstat(fd_in)) == identity(opened),
                            'source changed during copy')
                    fd_readback = os.open(target.name, LEAF_FLAGS, dir_fd=target_parent)
                    try:
                        require(identity(os.fstat(fd_readback)) == identity(written),
                                'destination readback leaf differs')
                        readback = hashlib.sha256()
                        remaining = copied
                        while remaining:
                            chunk = os.read(fd_readback, min(1024 * 1024, remaining))
                            require(bool(chunk), 'destination readback shortened')
                            readback.update(chunk)
                            remaining -= len(chunk)
                        require(os.read(fd_readback, 1) == b'' and
                                readback.hexdigest() == expected_sha and
                                identity(os.fstat(fd_readback)) == identity(written),
                                'destination readback bytes or identity differ')
                    finally:
                        close_all([fd_readback], sys.exception())
                    os.fsync(target_parent)
                    if after_copy_hook is not None:
                        after_copy_hook()
                    reattached(source, source_chain, identity(opened))
                    reattached(target, target_chain, identity(written))
                finally:
                    close_all([fd_out], sys.exception())
        finally:
            close_all([fd_in], sys.exception())


def write_exact(path: Path, raw: bytes, mode: int = 0o600) -> str:
    """Durably create one small owned receipt by held parent and readback."""
    require(mode == 0o600 and len(raw) <= 1024 * 1024, 'closed receipt mode/size required')
    path = Path(path)
    digest = hashlib.sha256(raw).hexdigest()
    with parent_chain(path) as (parent, chain):
        fd = os.open(path.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                     os.O_NOFOLLOW | os.O_CLOEXEC, mode, dir_fd=parent)
        try:
            view = memoryview(raw)
            while view:
                count = os.write(fd, view)
                require(count > 0, 'receipt write made no progress')
                view = view[count:]
            os.fchmod(fd, mode)
            os.fsync(fd)
            written = os.fstat(fd)
            require(stat.S_ISREG(written.st_mode) and written.st_uid == os.getuid() and
                    written.st_nlink == 1 and stat.S_IMODE(written.st_mode) == mode and
                    written.st_size == len(raw), 'receipt inode differs')
            readback = os.open(path.name, LEAF_FLAGS, dir_fd=parent)
            try:
                require(identity(os.fstat(readback)) == identity(written), 'receipt readback inode differs')
                actual = bytearray()
                while len(actual) < len(raw):
                    chunk = os.read(readback, len(raw) - len(actual))
                    require(bool(chunk), 'receipt readback shortened')
                    actual.extend(chunk)
                require(os.read(readback, 1) == b'' and
                        hashlib.sha256(actual).hexdigest() == digest and
                        identity(os.fstat(readback)) == identity(written),
                        'receipt readback differs')
            finally:
                close_all([readback], sys.exception())
            os.fsync(parent)
            reattached(path, chain, identity(written))
        finally:
            close_all([fd], sys.exception())
    return digest
