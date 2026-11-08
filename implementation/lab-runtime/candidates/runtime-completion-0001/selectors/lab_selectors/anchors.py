"""No-follow byte reads through independently supplied root/member anchors.

An anchor is a trusted caller input, not something inferred from the file to be
checked. These primitives establish integrity; actual custody is a later gate.
"""
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import os
import stat
from lab_contracts.codec import Refusal, closed, need, sha


def relative(path):
    need(type(path) is str and path and '\x00' not in path and '\\' not in path,
         'UNSAFE_PATH')
    p = PurePosixPath(path)
    need(not p.is_absolute() and p.as_posix() == path
         and all(x not in ('', '.', '..') for x in path.split('/')), 'UNSAFE_PATH')
    return p.parts


def identity(s):
    return {'device': s.st_dev, 'inode': s.st_ino, 'uid': s.st_uid,
            'gid': s.st_gid, 'mode': stat.S_IMODE(s.st_mode)}


def stamp(s):
    return (s.st_dev, s.st_ino, s.st_mode, s.st_uid, s.st_gid, s.st_nlink,
            s.st_size, s.st_mtime_ns, s.st_ctime_ns)


@dataclass(frozen=True)
class RootAnchor:
    root_id: str
    path: str
    expected: dict

    def open(self):
        p = Path(self.path)
        need(p.is_absolute() and str(p) == self.path and '..' not in p.parts, 'ROOT_PATH')
        handles = [os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)]
        links = []
        try:
            for part in p.parts[1:]:
                fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                             dir_fd=handles[-1])
                links.append((handles[-1], part, fd))
                handles.append(fd)
            need(identity(os.fstat(handles[-1])) == self.expected, 'ROOT_IDENTITY')
            return handles, links
        except BaseException:
            for fd in reversed(handles):
                os.close(fd)
            raise


class AnchoredReader:
    def __init__(self, roots, allowed_bindings, *, protected_provider=None):
        need(all(type(r) is RootAnchor for r in roots), 'ROOT_ANCHOR_TYPE')
        self.roots = {r.root_id: r for r in roots}
        need(len(self.roots) == len(roots), 'DUPLICATE_ROOT')
        self.allowed = {self.key(b) for b in allowed_bindings}
        need(len(self.allowed) == len(allowed_bindings), 'DUPLICATE_BINDING')
        self.protected_provider = protected_provider

    @staticmethod
    def key(binding):
        from lab_contracts.validation import validate
        validate('ByteBinding', binding)
        relative(binding['relative_path'])
        return tuple(binding[k] for k in ('kind', 'root_id', 'relative_path', 'sha256', 'size_bytes'))

    def read(self, binding, max_bytes=64 * 1024 * 1024):
        need(self.key(binding) in self.allowed, 'UNSELECTED_BINDING')
        need(binding['root_id'] in self.roots, 'UNSELECTED_ROOT')
        need(type(max_bytes) is int and 0 < max_bytes <= 64 * 1024 * 1024
             and binding['size_bytes'] <= max_bytes, 'READ_LIMIT')
        if binding['kind'] == 'protected-input':
            need(self.protected_provider is not None, 'PROTECTED_PERMISSION_REQUIRED')
            # The provider returns selected original bytes only after its current
            # permission/root guards; caller booleans cannot enable this branch.
            raw = self.protected_provider.read(binding, max_bytes=max_bytes)
            need(type(raw) is bytes and len(raw) == binding['size_bytes']
                 and len(raw) <= max_bytes and sha(raw) == binding['sha256'], 'PROTECTED_BYTES')
            return raw
        root = self.roots[binding['root_id']]
        handles, links = root.open()
        fd = None
        try:
            parts = relative(binding['relative_path'])
            for part in parts[:-1]:
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                                dir_fd=handles[-1])
                links.append((handles[-1], part, child))
                handles.append(child)
            fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC,
                         dir_fd=handles[-1])
            before = os.fstat(fd)
            need(stat.S_ISREG(before.st_mode) and before.st_size == binding['size_bytes'], 'FILE_TYPE_SIZE')
            chunks = []
            size = 0
            while True:
                chunk = os.read(fd, min(1024 * 1024, max_bytes - size + 1))
                if not chunk:
                    break
                size += len(chunk)
                need(size <= max_bytes, 'READ_LIMIT')
                chunks.append(chunk)
            raw = b''.join(chunks)
            attached = os.stat(parts[-1], dir_fd=handles[-1], follow_symlinks=False)
            need(stamp(before) == stamp(os.fstat(fd)) == stamp(attached), 'FILE_CHANGED')
            need(len(raw) == binding['size_bytes'] and sha(raw) == binding['sha256'], 'CONTENT_DIGEST')
            for parent, name, child in reversed(links):
                current = os.stat(name, dir_fd=parent, follow_symlinks=False)
                need(stat.S_ISDIR(current.st_mode) and identity(current) == identity(os.fstat(child)),
                     'ANCESTOR_DETACHED')
            need(identity(os.fstat(handles[len(Path(root.path).parts)-1])) == root.expected,
                 'ROOT_CHANGED')
            return raw
        except OSError:
            raise Refusal('UNSAFE_OR_MISSING_FILE') from None
        finally:
            if fd is not None:
                os.close(fd)
            for handle in reversed(handles):
                os.close(handle)


def legacy_json(raw):
    """Parse original metadata without canonicalization or numeric coercion."""
    import json
    from lab_contracts.codec import _pairs
    need(type(raw) is bytes, 'LEGACY_BYTES')
    try:
        return json.loads(raw, object_pairs_hook=_pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(Refusal('NONFINITE_LEGACY')))
    except (ValueError, UnicodeError, RecursionError):
        raise Refusal('LEGACY_JSON') from None
