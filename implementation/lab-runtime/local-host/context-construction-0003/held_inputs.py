"""Read-only, held-FD predecessor byte adapter. Does not authenticate an issuer."""
from __future__ import annotations

import hashlib
import os
import stat
from pathlib import PurePosixPath

PIN_PATHS = {
    'source': 'source/source-manifest.json',
    'source_package': 'source/packages/0001/manifest.json',
    'mapped': 'mapped/source-manifest.json',
    'mapped_package': 'mapped/packages/0001/manifest.json',
}


class Refused(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise Refused(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def _identity(item, *, leaf):
    return (item.st_dev, item.st_ino, item.st_mode, item.st_size if leaf else 0)


def _open_chain(path: str):
    pure = PurePosixPath(path)
    require(pure.is_absolute() and str(pure) == path and '..' not in pure.parts and
            '//' not in path and len(pure.parts) >= 3, 'noncanonical held path')
    fds = []
    try:
        fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
        fds.append(fd)
        for component in pure.parts[1:-1]:
            fd = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                         dir_fd=fd)
            fds.append(fd)
        before = os.stat(pure.name, dir_fd=fd, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
                before.st_size <= 32 * 1024 * 1024, 'held leaf must be a bounded regular file')
        fd = os.open(pure.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC,
                     dir_fd=fd)
        fds.append(fd)
        after = os.fstat(fd)
        require(stat.S_ISREG(after.st_mode) and after.st_dev == before.st_dev and
                after.st_ino == before.st_ino and after.st_nlink == 1 and
                after.st_size == before.st_size, 'held leaf changed during nonblocking open')
        identities = []
        for index, descriptor in enumerate(fds):
            item = os.fstat(descriptor)
            require(stat.S_ISREG(item.st_mode) if index == len(fds) - 1 else stat.S_ISDIR(item.st_mode),
                    'held path type differs')
            if index == len(fds) - 1:
                require(item.st_nlink == 1, 'held input has multiple links')
            identities.append(_identity(item, leaf=index == len(fds) - 1))
        return fds, tuple(identities)
    except BaseException:
        for descriptor in reversed(fds):
            os.close(descriptor)
        raise


def _read_fd(fd: int) -> bytes:
    chunks = []
    offset = 0
    while True:
        part = os.pread(fd, 1024 * 1024, offset)
        if not part:
            break
        chunks.append(part)
        offset += len(part)
        require(offset <= 32 * 1024 * 1024, 'held manifest exceeds selected size cap')
    return b''.join(chunks)


class HeldPredecessors:
    """Holds every ancestor and leaf; reopens exact paths to check attachment."""

    def __init__(self, family: str, bindings: dict):
        root = PurePosixPath(family)
        require(root.is_absolute() and str(root) == family and '..' not in root.parts and
                type(bindings) is dict and set(bindings) == set(PIN_PATHS),
                'closed held predecessor selection required')
        self.family = family
        self._bindings = {}
        self._held = {}
        self.closed = False
        try:
            for name, suffix in PIN_PATHS.items():
                row = bindings[name]
                path = str(root / suffix)
                require(type(row) is dict and set(row) == {'path', 'sha256'} and
                        row['path'] == path and type(row['sha256']) is str and
                        len(row['sha256']) == 64 and
                        all(c in '0123456789abcdef' for c in row['sha256']),
                        'exact same-family predecessor binding required')
                self._bindings[name] = dict(row)
                fds, identities = _open_chain(path)
                try:
                    raw = _read_fd(fds[-1])
                    require(digest(raw) == row['sha256'] and len(raw) == identities[-1][3],
                            'held predecessor bytes differ')
                except BaseException:
                    for descriptor in reversed(fds):
                        os.close(descriptor)
                    raise
                self._held[name] = (fds, identities)
        except BaseException:
            self.close()
            raise

    def read(self, path: str) -> bytes:
        require(not self.closed, 'held descriptors closed')
        names = [name for name, row in self._bindings.items() if row['path'] == path]
        require(len(names) == 1, 'unselected held path')
        name = names[0]
        fds, identities = self._held[name]
        require(tuple(_identity(os.fstat(fd), leaf=index == len(fds) - 1)
                      for index, fd in enumerate(fds)) == identities, 'held identity changed')
        reopened, current = _open_chain(path)
        try:
            require(current == identities, 'held path attachment changed')
            raw = _read_fd(fds[-1])
            require(digest(raw) == self._bindings[name]['sha256'] and len(raw) == identities[-1][3],
                    'held bytes changed')
            return raw
        finally:
            for fd in reversed(reopened):
                os.close(fd)

    def close(self):
        if not getattr(self, 'closed', False):
            for fds, _ in reversed(list(self._held.values())):
                for fd in reversed(fds):
                    os.close(fd)
            self._held.clear()
            self.closed = True

    @property
    def bindings(self):
        return {name: dict(row) for name, row in self._bindings.items()}

    def __enter__(self):
        require(not self.closed, 'held descriptors closed')
        return self

    def __exit__(self, *_):
        self.close()
