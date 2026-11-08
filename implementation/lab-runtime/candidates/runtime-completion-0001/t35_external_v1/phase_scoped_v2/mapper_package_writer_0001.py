"""Scratch-only held Mapper package writer; no builder, IPC, or native effect.

The caller owns an already-created disposable /tmp family. This module writes
only its mapped/packages/0001 subtree and a scratch attempt marker. It makes
no claim about Source, native output, Context, or protected host custody.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import threading

from ..held_paths import HeldCanonicalDirectory
from ..path_contract import fd_mount_id
from . import mapper_package_plan_0002 as plan

ATTEMPT = '.mapper-package-writer-attempt-0001'
MARKER = b'lc-u02-05-disposable-mapper-package-writer-0001\n'
MAX_EVENT = 256 * 1024
MAX_OTHER = 4 * 1024 * 1024
MAX_PACKAGE = 32 * 1024 * 1024
FIXED = ('request.json', 'native-output.json', 'mapping.json',
         'build-result.json', 'manifest.json')
SCHEDULE = tuple(f'semantic/{i:08d}.json' for i in range(1, 26)) + \
           tuple(f'governance/{i:08d}.json' for i in range(1, 26)) + FIXED
if set(SCHEDULE) != plan.expected_package_files(25):
    raise RuntimeError('selected package leaf schedule differs')


class Refusal(RuntimeError):
    pass


def require(ok: bool, code: str) -> None:
    if not ok:
        raise Refusal(code)


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _dir_identity(fd: int) -> tuple:
    row = os.fstat(fd)
    return (row.st_dev, row.st_ino, row.st_uid, row.st_gid,
            stat.S_IMODE(row.st_mode), fd_mount_id(fd))


def _file_signature(row: os.stat_result) -> tuple:
    return (row.st_dev, row.st_ino, row.st_mode, row.st_uid, row.st_gid,
            row.st_nlink, row.st_size, row.st_mtime_ns, row.st_ctime_ns)


def _closed_json(raw: bytes) -> object:
    def pairs(rows):
        value = {}
        for key, item in rows:
            require(key not in value, 'manifest_duplicate_key')
            value[key] = item
        return value
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(
                          Refusal('manifest_nonfinite')))


class PackageWriter:
    """One-shot writer with sticky UNKNOWN and retained scratch on failure."""

    def __init__(self, mapped: Path, source_binding: dict[str, str]):
        require(type(mapped) is type(Path('/')) and mapped.is_absolute() and
                mapped.name == 'mapped' and
                mapped.parent.name == 'legacy-fixture-source' and
                mapped.parent.parent.name == 'output' and
                mapped.parent.parent.parent.parent == Path('/tmp') and
                mapped.parent.parent.parent.name.startswith(
                    'lc-u02-05-mapper-writer-') and
                '..' not in mapped.parts,
                'scratch_scope')
        require(type(source_binding) is dict and
                set(source_binding) == {'path', 'sha256'} and
                source_binding['path'] == plan.FAMILY + '/mapped/source-manifest.json' and
                type(source_binding['sha256']) is str and
                len(source_binding['sha256']) == 64 and
                all(c in '0123456789abcdef' for c in source_binding['sha256']),
                'source_binding')
        self.mapped = mapped
        self.scratch = mapped.parent.parent.parent
        self.source_binding = dict(source_binding)
        self.uid, self.gid = os.geteuid(), os.getegid()
        self.held = None
        self.packages_fd = None
        self.package_fd = None
        self.event_fds: dict[str, int] = {}
        self.identities: dict[str, tuple] = {}
        self.hashes: dict[str, str] = {}
        self.file_signatures: dict[str, tuple] = {}
        self.index = 0
        self.total = 0
        self.unknown = False
        self.closed = False
        self.finished = False
        self.close_errors = 0
        try:
            self.held = HeldCanonicalDirectory(str(mapped))
            for path in (self.scratch, self.scratch / 'output',
                         mapped.parent, mapped):
                row = os.fstat(self.held.at(str(path)))
                require(stat.S_ISDIR(row.st_mode) and row.st_uid == self.uid and
                        row.st_gid == self.gid and stat.S_IMODE(row.st_mode) == 0o700,
                        'scratch_owner_or_mode')
            require(self.held.attached() and
                    'packages' not in os.listdir(self.held.fd),
                    'mapped_baseline')
            self._claim_attempt()
            self.packages_fd = self._mkdir(self.held.fd, 'packages')
            self.package_fd = self._mkdir(self.packages_fd, '0001')
            self._attached()
            require(os.listdir(self.packages_fd) == ['0001'] and
                    os.listdir(self.package_fd) == [], 'package_precreate')
        except BaseException:
            self.unknown = True
            self.close()
            raise

    def _claim_attempt(self) -> None:
        root_fd = self.held.at(str(self.scratch))
        fd = os.open(ATTEMPT, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                     os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=root_fd)
        try:
            os.fchmod(fd, 0o600)
            self._write_all(fd, MARKER)
            os.fsync(fd)
            first = os.fstat(fd)
            require(stat.S_ISREG(first.st_mode) and first.st_nlink == 1 and
                    first.st_uid == self.uid and first.st_gid == self.gid and
                    stat.S_IMODE(first.st_mode) == 0o600 and
                    first.st_size == len(MARKER), 'attempt_marker_custody')
        finally:
            os.close(fd)
        os.fsync(root_fd)
        check = os.open(ATTEMPT, os.O_RDONLY | os.O_NOFOLLOW |
                        os.O_NONBLOCK | os.O_CLOEXEC, dir_fd=root_fd)
        try:
            named = os.stat(ATTEMPT, dir_fd=root_fd, follow_symlinks=False)
            require(_file_signature(os.fstat(check)) == _file_signature(first) ==
                    _file_signature(named) and
                    os.read(check, len(MARKER) + 1) == MARKER,
                    'attempt_marker_readback')
        finally:
            os.close(check)
        require(self.held.attached(), 'attempt_marker_detached')

    @staticmethod
    def _write_all(fd: int, raw: bytes) -> None:
        offset = 0
        while offset < len(raw):
            count = os.write(fd, raw[offset:])
            require(count > 0, 'short_write')
            offset += count

    def _mkdir(self, parent: int, name: str) -> int:
        # A caller umask of 0777 otherwise creates mode 0000 and prevents
        # opening the inode for fchmod. This disposable writer is single-threaded.
        require(threading.active_count() == 1, 'multithreaded_umask')
        previous_umask = os.umask(0o077)
        try:
            os.mkdir(name, 0o700, dir_fd=parent)
        finally:
            os.umask(previous_umask)
        child = os.open(name, os.O_RDONLY | os.O_DIRECTORY |
                        os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=parent)
        try:
            os.fchmod(child, 0o700)
            row = os.fstat(child)
            require(stat.S_ISDIR(row.st_mode) and row.st_uid == self.uid and
                    row.st_gid == self.gid and stat.S_IMODE(row.st_mode) == 0o700,
                    'directory_custody')
            os.fsync(child)
            os.fsync(parent)
            identity = _dir_identity(child)
            attached = os.stat(name, dir_fd=parent, follow_symlinks=False)
            require((attached.st_dev, attached.st_ino, attached.st_uid,
                     attached.st_gid, stat.S_IMODE(attached.st_mode)) ==
                    identity[:5], 'directory_detached')
            self.identities[name] = identity
            return child
        except BaseException:
            os.close(child)
            raise

    def _attached_dir(self, fd: int, parent: int, name: str,
                      expected: tuple) -> None:
        require(_dir_identity(fd) == expected, 'held_directory_changed')
        row = os.stat(name, dir_fd=parent, follow_symlinks=False)
        require(stat.S_ISDIR(row.st_mode) and
                (row.st_dev, row.st_ino, row.st_uid, row.st_gid,
                 stat.S_IMODE(row.st_mode)) == expected[:5],
                'directory_detached')
        reopened = os.open(name, os.O_RDONLY | os.O_DIRECTORY |
                           os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=parent)
        try:
            require(_dir_identity(reopened) == expected,
                    'directory_mount_changed')
        finally:
            os.close(reopened)

    def _attached(self) -> None:
        require(self.held is not None and self.held.attached(),
                'held_ancestor_detached')
        if self.packages_fd is not None:
            self._attached_dir(self.packages_fd, self.held.fd, 'packages',
                               self.identities['packages'])
        if self.package_fd is not None:
            self._attached_dir(self.package_fd, self.packages_fd, '0001',
                               self.identities['0001'])
        for name, fd in self.event_fds.items():
            self._attached_dir(fd, self.package_fd, name,
                               self.identities[name])

    def _scan(self) -> None:
        self._attached()
        require(set(os.listdir(self.packages_fd)) == {'0001'},
                'package_sibling')
        expected_root = set(self.hashes) & set(FIXED)
        expected_root |= set(self.event_fds)
        require(set(os.listdir(self.package_fd)) == expected_root,
                'package_extra_or_missing')
        for family, fd in self.event_fds.items():
            expected = {name.split('/', 1)[1] for name in self.hashes
                        if name.startswith(family + '/')}
            require(set(os.listdir(fd)) == expected,
                    'event_extra_or_missing')
        for name, signature in self.file_signatures.items():
            family, separator, leaf = name.partition('/')
            parent = self.event_fds[family] if separator else self.package_fd
            entry = leaf if separator else family
            row = os.stat(entry, dir_fd=parent, follow_symlinks=False)
            require(_file_signature(row) == signature and
                    stat.S_ISREG(row.st_mode) and row.st_nlink == 1,
                    'emitted_leaf_changed')

    def _readback(self, parent: int, leaf: str, expected: bytes,
                  written_fd: int) -> tuple:
        first = os.fstat(written_fd)
        named = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
        require(stat.S_ISREG(first.st_mode) and first.st_nlink == 1 and
                first.st_uid == self.uid and first.st_gid == self.gid and
                stat.S_IMODE(first.st_mode) == 0o600 and
                first.st_size == len(expected) and
                _file_signature(first) == _file_signature(named),
                'leaf_custody')
        check = os.open(leaf, os.O_RDONLY | os.O_NOFOLLOW |
                        os.O_NONBLOCK | os.O_CLOEXEC, dir_fd=parent)
        try:
            require(_file_signature(os.fstat(check)) == _file_signature(first),
                    'leaf_reopen_changed')
            raw = bytearray()
            while len(raw) < len(expected):
                part = os.read(check, min(65536, len(expected) - len(raw)))
                require(bool(part), 'leaf_truncated')
                raw.extend(part)
            require(os.read(check, 1) == b'' and bytes(raw) == expected and
                    _file_signature(os.fstat(check)) == _file_signature(first),
                    'leaf_readback_changed')
        finally:
            os.close(check)
        return _file_signature(first)

    def _validate_manifest(self, raw: bytes) -> None:
        try:
            value = _closed_json(raw)
        except (ValueError, UnicodeError, Refusal) as error:
            raise Refusal('manifest_parse') from error
        require(type(value) is dict and set(value) ==
                {'schema_version', 'files', 'source_manifest_binding',
                 'authority_effect', 'actual_owner_outcome'} and
                value['schema_version'] == 'lab-mapped-context-package/v1-candidate' and
                value['source_manifest_binding'] == self.source_binding and
                value['authority_effect'] == 'none' and
                value['actual_owner_outcome'] is None and
                type(value['files']) is list and len(value['files']) == 54,
                'manifest_claims')
        expected = sorted(name for name in SCHEDULE if name != 'manifest.json')
        for row, name in zip(value['files'], expected):
            require(type(row) is dict and set(row) == {'path', 'sha256'} and
                    row == {'path': plan.PACKAGE + '/' + name,
                            'sha256': self.hashes.get(name)},
                    'manifest_binding')
        canonical = (json.dumps(value, indent=2, sort_keys=True,
                                ensure_ascii=False, allow_nan=False) + '\n').encode()
        require(raw == canonical, 'manifest_encoding')

    def emit(self, name: str, raw: bytes) -> dict[str, object]:
        require(not self.closed and not self.unknown and not self.finished,
                'writer_unavailable')
        try:
            require(type(name) is str and type(raw) is bytes and
                    self.index < len(SCHEDULE) and name == SCHEDULE[self.index],
                    'leaf_order')
            limit = MAX_EVENT if '/' in name else MAX_OTHER
            require(len(raw) <= limit and self.total + len(raw) <= MAX_PACKAGE,
                    'leaf_or_package_budget')
            self._scan()
            if name == 'manifest.json':
                self._validate_manifest(raw)
            if '/' in name:
                family, leaf = name.split('/', 1)
                if family not in self.event_fds:
                    self.event_fds[family] = self._mkdir(self.package_fd, family)
                parent = self.event_fds[family]
            else:
                leaf, parent = name, self.package_fd
            fd = os.open(leaf, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                         os.O_NOFOLLOW | os.O_CLOEXEC, 0o600,
                         dir_fd=parent)
            try:
                os.fchmod(fd, 0o600)
                self._write_all(fd, raw)
                os.fsync(fd)
                signature = self._readback(parent, leaf, raw, fd)
                os.fsync(parent)
            finally:
                os.close(fd)
            self.hashes[name] = _sha(raw)
            self.file_signatures[name] = signature
            self.index += 1
            self.total += len(raw)
            self._scan()
            return {'path': name, 'sha256': self.hashes[name],
                    'size': len(raw), 'durable_observed': True}
        except BaseException:
            self.unknown = True
            raise

    def finish(self) -> dict[str, object]:
        require(not self.closed and not self.unknown and not self.finished,
                'writer_unavailable')
        try:
            require(self.index == len(SCHEDULE) and
                    set(self.hashes) == set(SCHEDULE), 'package_incomplete')
            self._scan()
            for name in SCHEDULE:
                family, _, leaf = name.partition('/')
                parent = self.event_fds[family] if leaf else self.package_fd
                entry = leaf if leaf else family
                fd = os.open(entry, os.O_RDONLY | os.O_NOFOLLOW |
                             os.O_NONBLOCK | os.O_CLOEXEC, dir_fd=parent)
                try:
                    row = os.fstat(fd)
                    require(stat.S_ISREG(row.st_mode) and row.st_nlink == 1 and
                            row.st_uid == self.uid and row.st_gid == self.gid and
                            stat.S_IMODE(row.st_mode) == 0o600 and
                            row.st_size <= (MAX_EVENT if leaf else MAX_OTHER),
                            'final_leaf_custody')
                    data = bytearray()
                    while len(data) <= row.st_size:
                        part = os.read(fd, min(65536, row.st_size + 1 - len(data)))
                        if not part:
                            break
                        data.extend(part)
                    named = os.stat(entry, dir_fd=parent, follow_symlinks=False)
                    require(len(data) == row.st_size and
                            _sha(data) == self.hashes[name] and
                            _file_signature(row) == _file_signature(os.fstat(fd)) ==
                            _file_signature(named), 'final_leaf_changed')
                finally:
                    os.close(fd)
            self._attached()
            self.finished = True
            return {'leaf_count': 55, 'manifest_row_count': 54,
                    'total_bytes': self.total, 'scratch_retained': True,
                    'package_writer_complete': True}
        except BaseException:
            self.unknown = True
            raise

    def close(self) -> None:
        if self.closed:
            return
        self.closed = True
        for fd in reversed(list(self.event_fds.values())):
            try:
                os.close(fd)
            except OSError:
                self.close_errors += 1
        self.event_fds.clear()
        for name in ('package_fd', 'packages_fd'):
            fd = getattr(self, name)
            if fd is not None:
                try:
                    os.close(fd)
                except OSError:
                    self.close_errors += 1
                setattr(self, name, None)
        if self.held is not None:
            try:
                self.held.close()
            except OSError:
                self.close_errors += 1
            self.held = None
        if self.close_errors:
            self.unknown = True

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
