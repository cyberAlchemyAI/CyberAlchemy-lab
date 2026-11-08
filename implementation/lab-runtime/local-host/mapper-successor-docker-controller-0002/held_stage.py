"""Owned attempt capability for a consumed-once Mapper stage.

All destination operations use held directory descriptors. The named attempt
and root must still point to those descriptors before private source opens
and before PASS. UNKNOWN writes use only the originally claimed attempt FD.
"""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import os
from pathlib import Path
import stat
import sys

from anchored_copy import (FLAGS, LEAF_FLAGS, close_all, dir_identity,
                           identity, parent_chain, reattached, require)


def parts_for(relative: str) -> tuple[str, ...]:
    path = Path(relative)
    parts = path.parts
    require(bool(parts) and not path.is_absolute() and
            all(part not in ('', '.', '..') for part in parts) and
            '/'.join(parts) == relative, 'closed relative stage path required')
    return parts


class HeldAttempt:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.parent_fd: int | None = None
        self.fd: int | None = None
        self.root_fd: int | None = None
        self.parent_identity: tuple[tuple[int, ...], ...] | None = None
        self.claimed = False
        self.directories: dict[str, tuple[int, ...]] = {}
        self.files: dict[str, tuple[int, ...]] = {}

    def claim(self) -> None:
        require(not self.claimed and self.fd is None, 'attempt already claimed')
        with parent_chain(self.path) as (parent, chain):
            self.parent_fd = os.dup(parent)
            self.parent_identity = chain
            os.mkdir(self.path.name, 0o700, dir_fd=self.parent_fd)
            # This assignment is deliberately immediately after successful
            # mkdir, before open/chmod/fsync can fail. A lost mkdir never owns.
            self.claimed = True
            self.fd = os.open(self.path.name, FLAGS, dir_fd=self.parent_fd)
            os.fchmod(self.fd, 0o700)
            os.fsync(self.fd)
            os.fsync(self.parent_fd)
            self.attached()

    def attached(self) -> None:
        require(self.claimed and self.fd is not None and
                self.parent_fd is not None and self.parent_identity is not None,
                'attempt has no owned FD')
        held = os.fstat(self.fd)
        require(stat.S_ISDIR(held.st_mode) and held.st_uid == os.getuid() and
                stat.S_IMODE(held.st_mode) == 0o700 and
                dir_identity(os.fstat(self.parent_fd)) == self.parent_identity[-1],
                'held attempt owner or parent changed')
        with parent_chain(self.path) as (parent, chain):
            named = os.stat(self.path.name, dir_fd=parent, follow_symlinks=False)
            require(chain == self.parent_identity and
                    dir_identity(named) == dir_identity(held),
                    'claimed attempt detached or replaced')
        if self.root_fd is not None:
            root = os.fstat(self.root_fd)
            named_root = os.stat('root', dir_fd=self.fd, follow_symlinks=False)
            require(stat.S_ISDIR(root.st_mode) and root.st_uid == os.getuid() and
                    stat.S_IMODE(root.st_mode) == 0o755 and
                    dir_identity(root) == dir_identity(named_root),
                    'claimed root detached or replaced')

    @contextmanager
    def parent(self, relative: str):
        require(self.fd is not None, 'attempt FD unavailable')
        parts = parts_for(relative)
        opened = [os.dup(self.fd)]
        try:
            prefix = []
            for part in parts[:-1]:
                opened.append(os.open(part, FLAGS, dir_fd=opened[-1]))
                prefix.append(part)
                name = '/'.join(prefix)
                require(name in self.directories and
                        dir_identity(os.fstat(opened[-1])) == self.directories[name],
                        'selected stage directory detached or replaced')
            yield opened[-1], parts[-1]
        finally:
            close_all(opened, sys.exception())

    def mkdir(self, relative: str, mode: int) -> None:
        require(mode in (0o700, 0o755), 'closed directory mode required')
        self.attached()
        with self.parent(relative) as (parent, name):
            os.mkdir(name, mode, dir_fd=parent)
            child = os.open(name, FLAGS, dir_fd=parent)
            try:
                os.fchmod(child, mode)
                os.fsync(child)
                os.fsync(parent)
                info = os.fstat(child)
                named = os.stat(name, dir_fd=parent, follow_symlinks=False)
                require(stat.S_ISDIR(info.st_mode) and info.st_uid == os.getuid() and
                        stat.S_IMODE(info.st_mode) == mode and
                        dir_identity(info) == dir_identity(named),
                        'created directory owner/mode/attachment changed')
                self.directories[relative] = dir_identity(info)
                if relative == 'root':
                    require(self.root_fd is None, 'root already held')
                    self.root_fd = os.dup(child)
            finally:
                close_all([child], sys.exception())
        self.attached()

    def bind_root(self) -> None:
        require(self.fd is not None and self.root_fd is not None,
                'root must have been bound at creation')
        self.attached()

    def write(self, relative: str, raw: bytes, *, attached: bool = True) -> str:
        require(len(raw) <= 1024 * 1024, 'receipt too large')
        if attached:
            self.attached()
        digest = hashlib.sha256(raw).hexdigest()
        with self.parent(relative) as (parent, name):
            fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                         os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=parent)
            try:
                view = memoryview(raw)
                while view:
                    count = os.write(fd, view)
                    require(count > 0, 'receipt write made no progress')
                    view = view[count:]
                os.fchmod(fd, 0o600)
                os.fsync(fd)
                written = os.fstat(fd)
                require(stat.S_ISREG(written.st_mode) and written.st_nlink == 1 and
                        written.st_uid == os.getuid() and
                        stat.S_IMODE(written.st_mode) == 0o600 and
                        written.st_size == len(raw), 'receipt inode differs')
                rd = os.open(name, LEAF_FLAGS, dir_fd=parent)
                try:
                    require(identity(os.fstat(rd)) == identity(written),
                            'receipt readback inode differs')
                    h = hashlib.sha256()
                    while True:
                        block = os.read(rd, 1024 * 1024)
                        if not block:
                            break
                        h.update(block)
                    require(h.hexdigest() == digest and
                            identity(os.fstat(rd)) == identity(written),
                            'receipt readback bytes differ')
                finally:
                    close_all([rd], sys.exception())
                named = os.stat(name, dir_fd=parent, follow_symlinks=False)
                require(identity(named) == identity(written), 'receipt attachment changed')
                os.fsync(parent)
                self.files[relative] = identity(written)
            finally:
                close_all([fd], sys.exception())
        if attached:
            self.attached()
        return digest

    def copy(self, source: Path, relative: str, digest: str,
             target_mode: int, source_mode: int) -> None:
        require(target_mode in (0o444, 0o600, 0o755) and
                source_mode in (0o444, 0o600, 0o644, 0o755),
                'closed file modes required')
        self.attached()  # check immediately before any private source open
        source = Path(source)
        with parent_chain(source) as (source_parent, source_chain):
            before = os.stat(source.name, dir_fd=source_parent, follow_symlinks=False)
            require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
                    before.st_uid == os.getuid() and
                    stat.S_IMODE(before.st_mode) == source_mode,
                    'source file owner/mode differs')
            fd_in = os.open(source.name, LEAF_FLAGS, dir_fd=source_parent)
            try:
                opened = os.fstat(fd_in)
                require(identity(opened) == identity(before), 'source open changed')
                with self.parent(relative) as (parent, name):
                    fd_out = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                                     os.O_NOFOLLOW | os.O_CLOEXEC,
                                     target_mode, dir_fd=parent)
                    try:
                        h = hashlib.sha256()
                        copied = 0
                        while True:
                            block = os.read(fd_in, 1024 * 1024)
                            if not block:
                                break
                            h.update(block)
                            copied += len(block)
                            view = memoryview(block)
                            while view:
                                count = os.write(fd_out, view)
                                require(count > 0, 'copy write made no progress')
                                view = view[count:]
                        os.fchmod(fd_out, target_mode)
                        os.fsync(fd_out)
                        written = os.fstat(fd_out)
                        require(stat.S_ISREG(written.st_mode) and written.st_nlink == 1 and
                                written.st_uid == os.getuid() and
                                stat.S_IMODE(written.st_mode) == target_mode and
                                copied == written.st_size and h.hexdigest() == digest and
                                identity(os.fstat(fd_in)) == identity(opened),
                                'copied bytes/identity/mode differ')
                        rd = os.open(name, LEAF_FLAGS, dir_fd=parent)
                        try:
                            require(identity(os.fstat(rd)) == identity(written),
                                    'copied readback inode differs')
                            readback = hashlib.sha256()
                            while True:
                                block = os.read(rd, 1024 * 1024)
                                if not block:
                                    break
                                readback.update(block)
                            require(readback.hexdigest() == digest and
                                    identity(os.fstat(rd)) == identity(written),
                                    'copied readback bytes differ')
                        finally:
                            close_all([rd], sys.exception())
                        named = os.stat(name, dir_fd=parent, follow_symlinks=False)
                        require(identity(named) == identity(written),
                                'copied destination detached')
                        os.fsync(parent)
                        self.files[relative] = identity(written)
                        reattached(source, source_chain, identity(opened))
                    finally:
                        close_all([fd_out], sys.exception())
            finally:
                close_all([fd_in], sys.exception())
        self.attached()

    def file_hash(self, relative: str, digest: str, mode: int) -> None:
        require(mode in (0o444, 0o600, 0o755), 'closed verification mode')
        self.attached()
        with self.parent(relative) as (parent, name):
            before = os.stat(name, dir_fd=parent, follow_symlinks=False)
            require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
                    before.st_uid == os.getuid() and
                    stat.S_IMODE(before.st_mode) == mode and
                    self.files.get(relative) == identity(before),
                    'staged file mode or identity differs')
            fd = os.open(name, LEAF_FLAGS, dir_fd=parent)
            try:
                require(identity(os.fstat(fd)) == identity(before),
                        'staged file open changed')
                h = hashlib.sha256()
                while True:
                    block = os.read(fd, 1024 * 1024)
                    if not block:
                        break
                    h.update(block)
                require(h.hexdigest() == digest and
                        identity(os.fstat(fd)) == identity(before) and
                        identity(os.stat(name, dir_fd=parent, follow_symlinks=False)) ==
                        identity(before), 'staged file hash/identity differs')
            finally:
                close_all([fd], sys.exception())
        self.attached()

    def inventory(self) -> tuple[set[str], set[str]]:
        self.attached()
        require(self.root_fd is not None, 'root FD unavailable')
        files, dirs = set(), set()

        def descend(fd: int, prefix: str) -> None:
            with os.scandir(fd) as scan:
                names = list(scan)
            for entry in names:
                relative = prefix + entry.name
                info = os.stat(entry.name, dir_fd=fd, follow_symlinks=False)
                require(info.st_uid == os.getuid(), 'staged entry owner differs')
                if stat.S_ISDIR(info.st_mode):
                    dirs.add(relative)
                    require(self.directories.get('root/' + relative) ==
                            dir_identity(info), 'staged directory identity differs')
                    child = os.open(entry.name, FLAGS, dir_fd=fd)
                    try:
                        require(dir_identity(os.fstat(child)) == dir_identity(info),
                                'staged directory open changed')
                        descend(child, relative + '/')
                    finally:
                        close_all([child], sys.exception())
                else:
                    require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1,
                            'staged nonregular entry')
                    files.add(relative)
        descend(self.root_fd, '')
        self.attached()
        return files, dirs

    def directory(self, relative: str, mode: int) -> None:
        self.attached()
        with self.parent(relative) as (parent, name):
            before = os.stat(name, dir_fd=parent, follow_symlinks=False)
            require(stat.S_ISDIR(before.st_mode) and before.st_uid == os.getuid() and
                    stat.S_IMODE(before.st_mode) == mode and
                    self.directories.get(relative) == dir_identity(before),
                    'staged directory mode or identity differs')
            fd = os.open(name, FLAGS, dir_fd=parent)
            try:
                require(dir_identity(os.fstat(fd)) == dir_identity(before),
                        'staged directory open changed')
            finally:
                close_all([fd], sys.exception())
        self.attached()

    def exists(self, relative: str) -> bool:
        self.attached()
        with self.parent(relative) as (parent, name):
            try:
                os.stat(name, dir_fd=parent, follow_symlinks=False)
                return True
            except FileNotFoundError:
                return False

    def close(self, primary: BaseException | None = None) -> None:
        fds = [fd for fd in (self.parent_fd, self.fd, self.root_fd) if fd is not None]
        self.parent_fd = self.fd = self.root_fd = None
        close_all(fds, primary)
