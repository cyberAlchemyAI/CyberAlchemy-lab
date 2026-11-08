"""Transferable, fixture-only authority release primitives.

This module deliberately has no live issuance entrypoint.  A successor must
bind a fresh stage receipt, exact Source/Reader pins, and a reviewed Reader
loader before calling these primitives on a real Context family.
"""
from __future__ import annotations

import hashlib
import json
import os
import stat
from pathlib import Path

OLD_STAGE = Path('/tmp/cal-context-family-20261020-0001')
OLD_STAGE_RECEIPT_SHA = '29f423fdd02e49931be361dd475be54457af383b58dd1ac4cb38f40a48125b6d'
EXPECTED_SCOPE = 'scope:cyberalchemy-lab-first-agent-episode'


class Refused(RuntimeError):
    pass


def need(ok: bool, why: str) -> None:
    if not ok:
        raise Refused(why)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def wire(value: dict) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False,
                       allow_nan=False) + '\n').encode('utf-8')


def stale_stage_preflight() -> dict:
    """Read-only check of the historically reviewed stage; never restage it."""
    receipt = OLD_STAGE / 'stage-receipt.json'
    root = OLD_STAGE / 'root'
    need(receipt.is_file() and root.is_dir(), 'STALE_STAGE_ABSENT_FRESH_FAMILY_REQUIRED')
    raw = receipt.read_bytes()
    need(sha(raw) == OLD_STAGE_RECEIPT_SHA, 'STALE_STAGE_RECEIPT_CHANGED')
    value = json.loads(raw)
    need(value['status'] == 'STAGE_ONLY_PASS' and
         value['security_profile'] == 'trusted_local_fixture',
         'STALE_STAGE_RECEIPT_INVALID')
    return {'status': 'HISTORICAL_STAGE_PRESENT_ONLY', 'receipt_sha256': sha(raw)}


def checked_fixture_parent(path: Path) -> int:
    """Hold a disposable fixture directory and reject links/wrong ownership."""
    path = Path(path)
    need(path.parent == Path('/tmp') and
         path.name.startswith('cal-authority-release-transfer-fixture-'),
         'FIXTURE_ROOT_REQUIRED')
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        st = os.fstat(fd)
        need(stat.S_ISDIR(st.st_mode) and stat.S_IMODE(st.st_mode) == 0o700 and
             st.st_uid == os.getuid() == os.geteuid() and
             st.st_gid == os.getgid() == os.getegid(), 'FIXTURE_CUSTODY')
        return fd
    except BaseException:
        os.close(fd)
        raise


def exclusive_one_shot_fixture(path: Path, event: dict, inject: str | None = None) -> dict:
    """Causally exercise exclusive durable intent; leave failures consumed.

    No by-name deletion is attempted after a write/close/fsync ambiguity.
    The caller owns the disposable fixture directory for test cleanup.
    """
    parent = checked_fixture_parent(path)
    leaf = 'attempt.json'
    fd = None
    errors = []
    try:
        fd = os.open(leaf, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                     os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=parent)
        raw = wire({'schema': 'context-authority-transfer-fixture/v1',
                    'event': event, 'retry_allowed': False})
        try:
            need(os.write(fd, raw) == len(raw), 'SHORT_WRITE')
            if inject == 'write':
                raise OSError('INJECTED_WRITE_UNCERTAINTY')
            os.fsync(fd)
        except BaseException as exc:
            errors.append(type(exc).__name__)
        try:
            os.close(fd)
            fd = None
            if inject == 'close':
                raise OSError('INJECTED_CLOSE_UNCERTAINTY')
        except BaseException as exc:
            errors.append(type(exc).__name__)
        try:
            os.fsync(parent)
            if inject == 'parent_fsync':
                raise OSError('INJECTED_PARENT_FSYNC_UNCERTAINTY')
        except BaseException as exc:
            errors.append(type(exc).__name__)
        return {'status': 'UNKNOWN_PRESERVE_NO_RETRY' if errors else 'FIXTURE_INTENT_DURABLE',
                'retry_allowed': False, 'marker': str(path / leaf),
                'marker_sha256': sha(raw) if not errors else None,
                'errors': errors}
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass
        os.close(parent)


def signed_scope_guard(signed, expected_scope: str = EXPECTED_SCOPE) -> str:
    """A held-view join; a real issuer must prove the Reader origin separately."""
    signed.guard()
    scope = signed.view.data['config']['scope_ref']
    need(type(scope) is str and scope == expected_scope and
         signed.sources.scope_ref == scope, 'SIGNED_SCOPE_MISMATCH')
    signed.guard()
    return scope


def live_issue(*_args, **_kwargs):
    """No old-stage effect: exact fresh selection and Reader loader are absent."""
    raise Refused('FRESH_STAGE_SELECTION_AND_INDEPENDENT_REVIEW_REQUIRED')
