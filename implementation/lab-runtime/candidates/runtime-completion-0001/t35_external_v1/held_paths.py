"""Nofollow, attachment-aware reads for one inactive T35 external-root intent.

These primitives prove a bounded observation, not continuous writer exclusion.
"""
from __future__ import annotations

import hashlib
import json
import copy
import os
import stat
from pathlib import Path, PurePosixPath

from .path_contract import (OUTPUT_PARENT, STORAGE_ROOT, ContractError,
                            canonical_path, check_binding, fd_mount_id,
                            family_path, require, validate_intent)


def _signature(info: os.stat_result) -> tuple:
    return (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid,
            info.st_nlink, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def _directory_identity(info: os.stat_result) -> tuple:
    # Directory timestamps and link count legitimately change while a held
    # writer creates children. Attachment relies on stable inode/mode/owner.
    return (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid)


class HeldCanonicalDirectory:
    """Hold each component from `/` and recheck attachment from `/`."""

    def __init__(self, path: str | PurePosixPath):
        self.path = canonical_path(str(path), absolute=True)
        self.fds: list[int] = []
        self.records: list[tuple[int, str, int, tuple, int]] = []
        try:
            root = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
            self.fds.append(root)
            for name in self.path.parts[1:]:
                parent = self.fds[-1]
                child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                                dir_fd=parent)
                self.fds.append(child)
                info = os.fstat(child)
                require(stat.S_ISDIR(info.st_mode), 'non-directory held ancestor')
                self.records.append((parent, name, child, _directory_identity(info), fd_mount_id(child)))
            require(self.attached(), 'canonical directory detached at acquisition')
        except BaseException:
            self.close()
            raise

    @property
    def fd(self) -> int:
        require(bool(self.fds), 'closed directory custody')
        return self.fds[-1]

    def at(self, path: str | PurePosixPath) -> int:
        query = canonical_path(str(path), absolute=True)
        require(query == self.path or query in self.path.parents, 'unheld ancestor query')
        return self.fds[len(query.parts) - 1]

    def attached(self) -> bool:
        if not self.fds:
            return False
        try:
            for parent, name, held, initial, mount_id in self.records:
                current = os.fstat(held)
                attached = os.stat(name, dir_fd=parent, follow_symlinks=False)
                if not stat.S_ISDIR(attached.st_mode) or _directory_identity(current) != initial or _directory_identity(attached) != initial:
                    return False
                reopened = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                                   dir_fd=parent)
                try:
                    if _directory_identity(os.fstat(reopened)) != initial or fd_mount_id(reopened) != mount_id:
                        return False
                finally:
                    os.close(reopened)
            return True
        except (OSError, ContractError):
            return False

    def identity(self, path: str | PurePosixPath) -> dict:
        fd = self.at(path)
        info = os.fstat(fd)
        return {'dev': info.st_dev, 'ino': info.st_ino, 'mount_id': fd_mount_id(fd)}

    def close(self) -> None:
        for fd in reversed(self.fds):
            os.close(fd)
        self.fds.clear()
        self.records.clear()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def verify_parent_chain(intent: dict, held: HeldCanonicalDirectory) -> None:
    validate_intent(intent)
    require(held.path == OUTPUT_PARENT and held.attached(), 'held canonical output parent differs')
    require(held.identity(STORAGE_ROOT) == intent['storage_root_identity'], 'storage root inode or mount changed')
    require(held.identity(OUTPUT_PARENT) == intent['output_parent_identity'], 'output parent inode or mount changed')
    # The four relevant storage ancestors must not be writable by the service
    # through owner/group/other privileges. The parent alone is service-owned.
    for name in ('/var', '/var/lib', '/var/lib/cyberalchemy-lab', str(STORAGE_ROOT)):
        info = os.fstat(held.at(name))
        require(info.st_uid == 0 and info.st_gid == 0 and info.st_mode & 0o022 == 0,
                'root-owned storage ancestor policy differs')
    parent = os.fstat(held.fd)
    require(parent.st_uid == intent['service_uid'] and parent.st_gid == intent['service_gid'] and
            stat.S_IMODE(parent.st_mode) == 0o700, 'dedicated output parent policy differs')


def verify_snapshot_chain(intent: dict, held: HeldCanonicalDirectory) -> None:
    validate_intent(intent)
    require(held.path == PurePosixPath(intent['input_snapshot_path']) and held.attached(),
            'exact held input snapshot differs')
    require(held.identity(held.path) == intent['input_snapshot_identity'],
            'input snapshot inode or mount changed')
    require(os.fstatvfs(held.fd).f_flag & os.ST_RDONLY != 0,
            'input snapshot mount is not read-only')


def resolve_binding(intent: dict, row: dict, *, kind: str) -> Path:
    validate_intent(intent)
    family = family_path(intent['instance'])
    check_binding(row, kind=kind, family=family)
    if kind == 'source_api':
        return Path(intent['input_snapshot_path']) / row['path']
    return Path(row['path'])


def _read_selected(intent: dict, row: dict, *, kind: str, maximum: int = 64 * 1024 * 1024,
                   require_readonly_snapshot: bool = True,
                   expected_mode: int | None = None) -> bytes:
    """Read one exact row after holding/rechecking every canonical ancestor."""
    require(type(maximum) is int and 0 <= maximum <= 64 * 1024 * 1024,
            'bounded selected input maximum required')
    path = resolve_binding(intent, row, kind=kind)
    parent_path = path.parent
    with HeldCanonicalDirectory(str(parent_path)) as parent:
        if kind == 'source_api':
            snapshot = PurePosixPath(intent['input_snapshot_path'])
            require(snapshot == PurePosixPath(parent_path) or snapshot in PurePosixPath(parent_path).parents,
                    'selected source outside snapshot')
            require(parent.identity(snapshot) == intent['input_snapshot_identity'],
                    'selected snapshot inode or mount changed')
            if require_readonly_snapshot:
                require(os.fstatvfs(parent.at(snapshot)).f_flag & os.ST_RDONLY != 0,
                        'selected snapshot mount is writable')
        else:
            family = family_path(intent['instance'])
            require(family == PurePosixPath(parent_path) or family in PurePosixPath(parent_path).parents,
                    'selected output outside family')
            require(parent.identity(STORAGE_ROOT) == intent['storage_root_identity'] and
                    parent.identity(OUTPUT_PARENT) == intent['output_parent_identity'],
                    'selected external ancestor identity differs')
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC,
                     dir_fd=parent.fd)
        try:
            before = os.fstat(fd)
            require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and 0 <= before.st_size <= maximum,
                    'bounded regular single-link selected leaf required')
            if expected_mode is not None:
                require(stat.S_IMODE(before.st_mode) == expected_mode,
                        'selected executable mode differs')
            data = bytearray()
            while len(data) < before.st_size:
                chunk = os.read(fd, min(1024 * 1024, before.st_size - len(data)))
                require(bool(chunk), 'selected leaf shortened')
                data.extend(chunk)
            require(os.read(fd, 1) == b'' and _signature(os.fstat(fd)) == _signature(before),
                    'selected leaf changed during read')
            attached = os.stat(path.name, dir_fd=parent.fd, follow_symlinks=False)
            require(_signature(attached) == _signature(before) and parent.attached(),
                    'selected leaf or ancestor detached')
            if kind == 'source_api':
                snapshot = PurePosixPath(intent['input_snapshot_path'])
                require(parent.identity(snapshot) == intent['input_snapshot_identity'] and
                        (not require_readonly_snapshot or
                         os.fstatvfs(parent.at(snapshot)).f_flag & os.ST_RDONLY != 0),
                        'input snapshot changed before read completion')
            else:
                require(parent.identity(STORAGE_ROOT) == intent['storage_root_identity'] and
                        parent.identity(OUTPUT_PARENT) == intent['output_parent_identity'],
                        'external output ancestors changed before read completion')
            require(hashlib.sha256(data).hexdigest() == row['sha256'], 'selected leaf digest differs')
            return bytes(data)
        finally:
            os.close(fd)


def _parse_closed(raw: bytes) -> dict:
    def pairs(rows):
        value = {}
        for key, item in rows:
            require(key not in value, 'duplicate selected snapshot key')
            value[key] = item
        return value
    value = json.loads(raw, object_pairs_hook=pairs,
                       parse_constant=lambda _: (_ for _ in ()).throw(ContractError('nonfinite selection')))
    require(type(value) is dict, 'selected snapshot object required')
    return value


def selected_manifest_rows(raw: bytes, intent: dict) -> dict[str, dict]:
    """Pure membership check used by selected and disposable test readers."""
    value = _parse_closed(raw)
    require(set(value) == {'schema_version', 'authority_effect', 'files'} and
            value['schema_version'] == 'lab-T35-external-root-input-selection/v1-inactive' and
            value['authority_effect'] == 'none' and type(value['files']) is list and
            bool(value['files']), 'closed inactive input selection required')
    rows: dict[str, dict] = {}
    for row in value['files']:
        check_binding(row, kind='source_api')
        require(row['path'] not in rows, 'duplicate selected Source/API path')
        rows[row['path']] = row
    for group in ('code_bindings', 'api_bindings'):
        for selected in intent[group].values():
            require(rows.get(selected['path']) == selected,
                    'selected code/API binding absent from pinned snapshot manifest')
    return rows


class SelectedSnapshot:
    """Only Root-intent-pinned repository-relative rows are readable."""

    def __init__(self, intent: dict):
        validate_intent(intent)
        self._intent = copy.deepcopy(intent)
        self._intent_bytes = json.dumps(self._intent, sort_keys=True,
                                        separators=(',', ':'), allow_nan=False).encode()
        manifest = self._intent['input_manifest_binding']
        raw = _read_selected(self._intent, manifest, kind='source_api', maximum=2 * 1024 * 1024)
        self._rows = selected_manifest_rows(raw, self._intent)
        self.manifest = copy.deepcopy(manifest)

    @property
    def intent(self) -> dict:
        return copy.deepcopy(self._intent)

    @property
    def rows(self) -> dict[str, dict]:
        return copy.deepcopy(self._rows)

    def _unchanged(self) -> None:
        current = json.dumps(self._intent, sort_keys=True,
                             separators=(',', ':'), allow_nan=False).encode()
        require(current == self._intent_bytes, 'selected Root intent mutated after acquisition')

    def read(self, row: dict, *, maximum: int = 64 * 1024 * 1024) -> bytes:
        self._unchanged()
        check_binding(row, kind='source_api')
        require(self._rows.get(row['path']) == row, 'Source/API row absent from selected snapshot')
        return _read_selected(self._intent, row, kind='source_api', maximum=maximum)

    def read_executable(self, row: dict, *, mode: int = 0o755) -> bytes:
        self._unchanged()
        check_binding(row, kind='source_api')
        require(self._rows.get(row['path']) == row and type(mode) is int and mode == 0o755,
                'selected executable row or required mode differs')
        return _read_selected(self._intent, row, kind='source_api',
                              maximum=32 * 1024 * 1024, expected_mode=mode)
