"""Read all selected bytes through anchored directory descriptors.

Descriptors and metadata exist for this pass only. Every file is actually read
and hashed. This module carries no permission, actor, clock or runtime state.
"""
import hashlib
import os
from pathlib import Path
import re
import stat
import threading


class Refusal(ValueError):
    pass


def require(value, reason):
    if not value:
        raise Refusal(reason)


def identity(info):
    return info.st_dev, info.st_ino


def file_state(info):
    return (*identity(info), info.st_size, info.st_mtime_ns, info.st_ctime_ns)


class Custody:
    def __init__(self, rows, root, selected_external, *, max_file_bytes=64 * 1024 * 1024):
        self.root = Path(root)
        require(self.root.is_absolute() and '..' not in self.root.parts, 'absolute custody root required')
        require(type(max_file_bytes) is int and max_file_bytes > 0, 'positive host file-byte ceiling required')
        self.max_file_bytes = max_file_bytes
        self.rows = tuple(dict(row) for row in rows)
        require(all(set(row) == {'path', 'sha256'} for row in self.rows), 'closed dependency rows required')
        require(len({row['path'] for row in self.rows}) == len(self.rows), 'duplicate selected path')
        self.selected = {row['path']: row for row in self.rows}
        require(list(selected_external) == [row for row in self.rows if Path(row['path']).is_absolute()],
                'absolute dependency is outside exact explicit external selection')
        self.paths = {}
        for row in self.rows:
            name = row['path']
            require(type(name) is str and bool(name) and '\\' not in name,
                    'invalid selected dependency path')
            path = Path(name)
            require(path.as_posix() == name and '..' not in path.parts,
                    'noncanonical selected dependency path')
            require(re.fullmatch('[0-9a-f]{64}', row['sha256']) is not None,
                    'exact dependency hash required')
            self.paths[name] = path if path.is_absolute() else self.root / path
        self.directories = {}
        self.observed = {}
        self.started = False
        self.closed = False
        self.thread = None

    def __enter__(self):
        require(not self.started and not self.closed, 'custody pass cannot be reused')
        require(hasattr(os, 'O_NOFOLLOW') and hasattr(os, 'O_DIRECTORY'), 'anchored no-follow reads unavailable')
        self.started = True
        self.thread = threading.get_ident()
        return self

    def live(self):
        require(self.started and not self.closed, 'custody pass is closed or unstarted')
        require(self.thread == threading.get_ident(), 'custody pass belongs to another thread')

    def directory(self, path):
        self.live()
        if path in self.directories:
            return self.directories[path][0]
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
        if path == Path('/'):
            descriptor = os.open('/', flags)
        else:
            parent = self.directory(path.parent)
            descriptor = os.open(path.name, flags, dir_fd=parent)
        info = os.fstat(descriptor)
        if not stat.S_ISDIR(info.st_mode):
            os.close(descriptor)
            raise Refusal('selected ancestor is not a directory')
        self.directories[path] = descriptor, identity(info)
        return descriptor

    def read(self, row):
        self.live()
        require(self.selected.get(row.get('path')) == row, 'unselected dependency row')
        path = self.paths[row['path']]
        parent = self.directory(path.parent)
        declared = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
        require(stat.S_ISREG(declared.st_mode), 'selected dependency is not a regular file')
        descriptor = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC, dir_fd=parent)
        try:
            before = os.fstat(descriptor)
            require(stat.S_ISREG(before.st_mode), 'selected dependency is not a regular file')
            require(file_state(before) == file_state(declared), 'selected file replaced before opening')
            require(before.st_size <= self.max_file_bytes, 'selected dependency exceeds host file-byte ceiling')
            pieces = []
            size = 0
            while True:
                raw = os.read(descriptor, 1024 * 1024)
                if not raw:
                    break
                size += len(raw)
                require(size <= self.max_file_bytes, 'dependency grew beyond host file-byte ceiling')
                pieces.append(raw)
            raw = b''.join(pieces)
            after = os.fstat(descriptor)
            current = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
            require(file_state(before) == file_state(after) == file_state(current),
                    'selected file changed or was replaced during reading')
            require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'selected dependency bytes changed')
            self.observed[path] = parent, path.name, file_state(after)
            return raw
        finally:
            os.close(descriptor)

    def guard(self):
        self.live()
        for path, (descriptor, selected) in self.directories.items():
            current = os.lstat(path)
            require(stat.S_ISDIR(current.st_mode) and identity(current) == selected == identity(os.fstat(descriptor)),
                    'selected directory path changed or became a symlink')
        for path, (parent, name, selected) in self.observed.items():
            current = os.stat(name, dir_fd=parent, follow_symlinks=False)
            require(stat.S_ISREG(current.st_mode) and file_state(current) == selected,
                    'selected file changed after reading')

    def __exit__(self, error_type, error, traceback):
        self.live()
        failure = None
        try:
            self.guard()
            if error_type is None:
                require(set(self.observed) == set(self.paths.values()), 'complete selected dependency pass required')
        except BaseException as caught:
            failure = caught
        finally:
            for descriptor, selected in reversed(tuple(self.directories.values())):
                os.close(descriptor)
            self.directories.clear()
            self.observed.clear()
            self.closed = True
        if error_type is None and failure is not None:
            raise failure
        return False
