"""Owned descriptor boundaries; no cleanup or inferred recovery authority."""
from contextlib import contextmanager
import hashlib
import os
from pathlib import Path
import stat
import uuid
from .capture import capture_path

def require(value, message):
    if not value:
        raise ValueError(message)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def read(path):
    return capture_path(path, maximum=32*1024*1024)

@contextmanager
def directory(path):
    path = Path(path)
    require(path.is_absolute() and '..' not in path.parts, 'exact absolute directory required')
    fds = [os.open('/', os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)]
    links = []
    try:
        for name in path.parts[1:]:
            parent = fds[-1]
            child = os.open(name, os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW, dir_fd=parent)
            fds.append(child)
            info = os.fstat(child)
            links.append((parent, name, child, (info.st_dev, info.st_ino, info.st_uid, info.st_mode)))
        yield fds[-1]
        for parent, name, child, expected in links:
            a = os.stat(name, dir_fd=parent, follow_symlinks=False)
            b = os.fstat(child)
            key = lambda s: (s.st_dev, s.st_ino, s.st_uid, s.st_mode)
            require(key(a) == key(b) == expected, 'owned directory attachment changed')
    finally:
        for fd in reversed(fds):
            os.close(fd)

def sync(path):
    with directory(path) as fd:
        os.fsync(fd)

def write(path, raw):
    path = Path(path)
    require(type(raw) is bytes and len(raw) <= 32*1024*1024, 'bounded original output bytes required')
    with directory(path.parent) as parent:
        fd = os.open(path.name, os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW, 0o600, dir_fd=parent)
        try:
            selected = os.fstat(fd)
            offset = 0
            while offset < len(raw):
                count = os.write(fd, raw[offset:])
                require(count > 0, 'owned write stalled')
                offset += count
            os.fsync(fd)
            attached = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
            require((selected.st_dev, selected.st_ino) == (attached.st_dev, attached.st_ino)
                    and stat.S_ISREG(attached.st_mode) and attached.st_uid == os.getuid()
                    and stat.S_IMODE(attached.st_mode) == 0o600 and attached.st_size == len(raw),
                    'owned output changed during write')
            os.fsync(parent)
        finally:
            os.close(fd)

def atomic(path, raw):
    path = Path(path)
    temporary = path.parent/('.'+path.name+'-'+uuid.uuid4().hex)
    write(temporary, raw)
    with directory(path.parent) as parent:
        os.replace(temporary.name, path.name, src_dir_fd=parent, dst_dir_fd=parent)
        os.fsync(parent)

def canonical(value):
    import json
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()

@contextmanager
def held_directory(path):
    """Expose checks of every held ancestor for the versioned publisher."""
    path=Path(path)
    require(path.is_absolute() and '..'not in path.parts,'exact held directory required')
    fds=[os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)];links=[]
    key=lambda s:(s.st_dev,s.st_ino,s.st_uid,s.st_mode)
    def attached():
        for parent,name,child,stamp in links:
            require(key(os.stat(name,dir_fd=parent,follow_symlinks=False))==key(os.fstat(child))==stamp,
                    'held publisher ancestor detached')
    try:
        for name in path.parts[1:]:
            parent=fds[-1];child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent)
            fds.append(child);links.append((parent,name,child,key(os.fstat(child))))
        attached();yield fds[-1],attached;attached()
    finally:
        for fd in reversed(fds):os.close(fd)
