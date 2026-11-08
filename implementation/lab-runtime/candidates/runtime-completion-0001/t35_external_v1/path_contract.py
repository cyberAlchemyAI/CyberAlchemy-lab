"""Closed path and intent rules for a prospective external T35 family.

This module validates candidate data. It never turns a validated candidate
into a writer capability; installed custody and owner proofs are absent.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import stat
from pathlib import Path, PurePosixPath

REPO = PurePosixPath('/home/vlad_/projects/CyberAlchemy-lab')
STORAGE_ROOT = PurePosixPath('/var/lib/cyberalchemy-lab/source8-v1')
OUTPUT_PARENT = STORAGE_ROOT / 'instances'
SNAPSHOT_PARENT = PurePosixPath('/run/cyberalchemy-lab/source8-inputs')
INTENT_VERSION = 'lab-T35-external-root-intent/v1-inactive'
NAME_RE = re.compile(r'legacy-[a-z0-9](?:[a-z0-9-]{0,38}[a-z0-9])?\Z')
HEX_RE = re.compile(r'[0-9a-f]{64}\Z')


class ContractError(ValueError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise ContractError(message)


def canonical_path(value: str, *, absolute: bool) -> PurePosixPath:
    require(type(value) is str and bool(value) and '\x00' not in value and '\\' not in value,
            'closed POSIX path required')
    require(value.startswith('/') is absolute, 'path authority class differs')
    require('//' not in value and not value.endswith('/') and all(p not in ('', '.', '..') for p in value.split('/')[1 if absolute else 0:]),
            'noncanonical path component')
    result = PurePosixPath(value)
    require(str(result) == value, 'noncanonical path spelling')
    return result


def instance_name(value: str) -> str:
    require(type(value) is str and NAME_RE.fullmatch(value) is not None,
            'closed fresh legacy instance required')
    return value


def family_path(instance: str) -> PurePosixPath:
    return OUTPUT_PARENT / instance_name(instance)


def _digest(value: object) -> None:
    require(type(value) is str and HEX_RE.fullmatch(value) is not None,
            'exact SHA-256 required')


def _identity(value: object, *, mount: bool) -> None:
    keys = {'dev', 'ino', 'mount_id'} if mount else {'dev', 'ino'}
    require(type(value) is dict and set(value) == keys and all(type(v) is int and v > 0 for v in value.values()),
            'closed positive filesystem identity required')


def check_binding(row: object, *, kind: str, family: PurePosixPath | None = None) -> dict:
    require(type(row) is dict and set(row) == {'path', 'sha256'}, 'closed exact binding required')
    _digest(row['sha256'])
    if kind == 'source_api':
        path = canonical_path(row['path'], absolute=False)
        require(bool(path.parts) and not path.parts[0].startswith('-'), 'repository-relative input required')
    elif kind == 'output':
        require(family is not None, 'selected family required for output')
        path = canonical_path(row['path'], absolute=True)
        require(path != family and family in path.parents, 'output must be beneath exact family')
    else:
        raise ContractError('unknown binding authority class')
    return row


def bind_output(path: str | Path, raw: bytes, *, family: PurePosixPath) -> dict:
    name = str(path)
    check_binding({'path': name, 'sha256': hashlib.sha256(raw).hexdigest()}, kind='output', family=family)
    return {'path': name, 'sha256': hashlib.sha256(raw).hexdigest()}


def bind_input(path: str | Path, raw: bytes, *, snapshot: PurePosixPath) -> dict:
    name = canonical_path(str(path), absolute=True)
    require(snapshot in name.parents and name != snapshot, 'input outside exact read-only snapshot')
    relative = name.relative_to(snapshot)
    return check_binding({'path': str(relative), 'sha256': hashlib.sha256(raw).hexdigest()}, kind='source_api')


def binding_path(path: str | Path, *, family: PurePosixPath, snapshot: PurePosixPath) -> str:
    name = canonical_path(str(path), absolute=True)
    if family in name.parents:
        return str(name)
    require(snapshot in name.parents and name != snapshot, 'path outside selected output or input authority')
    return str(name.relative_to(snapshot))


def _utc(value: object) -> dt.datetime:
    require(type(value) is str, 'aware UTC period required')
    try:
        parsed = dt.datetime.fromisoformat(value)
    except ValueError as error:
        raise ContractError('invalid UTC period') from error
    require(parsed.utcoffset() == dt.timedelta(0), 'aware UTC period required')
    return parsed


def validate_intent(intent: object, *, now: dt.datetime | None = None) -> dict:
    """Validate shape and path authority only; never authenticate its claims."""
    fields = {'schema_version', 'authority_effect', 'instance', 'output_family_path',
              'storage_root_identity', 'output_parent_identity', 'service_uid',
              'service_gid', 'supervisor_unit', 'cgroup_path', 'mount_namespace',
              'not_before', 'expires_at', 'signed_period_binding',
              'slot_lock_binding', 'slot_lock_identity', 't02_custody_receipt_binding',
              'input_snapshot_path', 'input_snapshot_identity',
              'input_manifest_binding', 'code_bindings', 'api_bindings'}
    require(type(intent) is dict and set(intent) == fields and
            intent['schema_version'] == INTENT_VERSION and intent['authority_effect'] == 'none',
            'closed inactive external-root intent required')
    family = family_path(intent['instance'])
    require(intent['output_family_path'] == str(family), 'exact external family output differs')
    _identity(intent['storage_root_identity'], mount=True)
    _identity(intent['output_parent_identity'], mount=True)
    _identity(intent['input_snapshot_identity'], mount=True)
    _identity(intent['slot_lock_identity'], mount=False)
    require(type(intent['service_uid']) is int and type(intent['service_gid']) is int and
            intent['service_uid'] > 0 and intent['service_gid'] > 0 and
            intent['service_uid'] != 1000 and intent['service_gid'] != 1000,
            'dedicated numeric service identity required')
    require(type(intent['supervisor_unit']) is str and
            intent['supervisor_unit'] == 'cal-source8-writer@' + intent['instance'] + '.service',
            'exact one-family supervisor unit required')
    require(type(intent['cgroup_path']) is str and
            intent['cgroup_path'] == '/system.slice/' + intent['supervisor_unit'],
            'exact supervisor cgroup required')
    require(type(intent['mount_namespace']) is str and
            re.fullmatch(r'mnt:\[[1-9][0-9]*\]', intent['mount_namespace']) is not None,
            'pinned mount namespace identity required')
    snapshot = canonical_path(intent['input_snapshot_path'], absolute=True)
    require(snapshot.parent == SNAPSHOT_PARENT and HEX_RE.fullmatch(snapshot.name) is not None,
            'closed read-only input snapshot path required')
    for key in ('signed_period_binding', 'slot_lock_binding', 't02_custody_receipt_binding',
                'input_manifest_binding'):
        check_binding(intent[key], kind='source_api')
    for key in ('code_bindings', 'api_bindings'):
        rows = intent[key]
        require(type(rows) is dict and bool(rows) and all(type(k) is str and k for k in rows),
                'closed current input selection required')
        for row in rows.values():
            check_binding(row, kind='source_api')
    start, end = _utc(intent['not_before']), _utc(intent['expires_at'])
    require(end - start == dt.timedelta(hours=24), 'exact 24-hour successor period required')
    if now is not None:
        require(now.tzinfo is not None and start <= now < end, 'current successor period required')
    return intent


def parse_intent(raw: bytes, *, now: dt.datetime | None = None) -> dict:
    """Parse exact Root intent bytes without duplicate or nonfinite aliases."""
    require(type(raw) is bytes and 0 < len(raw) <= 2 * 1024 * 1024,
            'bounded Root intent bytes required')
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate Root intent key')
            result[key] = value
        return result
    try:
        parsed = json.loads(raw, object_pairs_hook=pairs,
                            parse_constant=lambda _: require(False, 'nonfinite Root intent'))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ContractError('invalid Root intent JSON') from error
    return validate_intent(parsed, now=now)


def no_symlink_ancestors(path: str | Path) -> bool:
    """Read-only local inspection; an absent leaf is permitted for planning."""
    target = canonical_path(str(path), absolute=True)
    current = Path('/')
    for part in target.parts[1:]:
        current = current / part
        try:
            info = os.lstat(current)
        except FileNotFoundError:
            return True
        require(not stat.S_ISLNK(info.st_mode), 'symlink or alias component refused')
    return True


def fd_mount_id(fd: int) -> int:
    with open(f'/proc/self/fdinfo/{fd}', encoding='ascii') as stream:
        rows = [r for r in stream if r.startswith('mnt_id:')]
    require(len(rows) == 1, 'mount ID unavailable')
    return int(rows[0].split(':', 1)[1].strip())


def current_cgroup() -> str:
    with open('/proc/self/cgroup', encoding='ascii') as stream:
        rows = [r.strip() for r in stream]
    require(len(rows) == 1 and rows[0].startswith('0::'), 'unselected cgroup layout')
    return rows[0][3:]


def verify_process_and_parent(intent: dict, parent_fd: int) -> None:
    """One observation at an effect boundary; does not prove continuous exclusion."""
    validate_intent(intent)
    require(os.getresuid() == (intent['service_uid'],) * 3 and
            os.getresgid() == (intent['service_gid'],) * 3 and os.getgroups() == [],
            'service UID/GID or supplementary groups differ')
    require(os.readlink('/proc/self/ns/mnt') == intent['mount_namespace'],
            'mount namespace drift')
    require(current_cgroup() == intent['cgroup_path'], 'supervisor cgroup drift')
    info = os.fstat(parent_fd)
    expected = intent['output_parent_identity']
    require(stat.S_ISDIR(info.st_mode) and stat.S_IMODE(info.st_mode) == 0o700 and
            info.st_uid == intent['service_uid'] and info.st_gid == intent['service_gid'] and
            (info.st_dev, info.st_ino, fd_mount_id(parent_fd)) ==
            (expected['dev'], expected['ino'], expected['mount_id']),
            'held external parent identity differs')
    # An FD can retain the original inode after a canonical path is renamed.
    # Walk again from `/` with O_NOFOLLOW and compare both held and reopened
    # identities, including the separately pinned storage root.
    from .held_paths import HeldCanonicalDirectory, verify_parent_chain
    with HeldCanonicalDirectory(str(OUTPUT_PARENT)) as canonical:
        verify_parent_chain(intent, canonical)
        reopened = os.fstat(canonical.fd)
        require((info.st_dev, info.st_ino, fd_mount_id(parent_fd)) ==
                (reopened.st_dev, reopened.st_ino, fd_mount_id(canonical.fd)),
                'held output parent detached from canonical path')
