"""No-replace publisher and exact evidence-byte audit for LC-U02-05 authoring.

This protects numbered evidence from accidental overwrite; it does not pin
evolving candidate source or grant any runtime effect/activation authority.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import stat

from .held_paths import HeldCanonicalDirectory
from .path_contract import canonical_path, require

REPO = Path(__file__).resolve().parents[5]
EVIDENCE = REPO / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U02-05'
NUMBERED = re.compile(r'[a-z][a-z0-9-]*-[0-9]{4}\.(?:json|jsonl|txt|md)\Z')


def _name(value: str) -> str:
    require(type(value) is str and NUMBERED.fullmatch(value) is not None,
            'versioned LC-U02-05 evidence leaf required')
    return value


def _publish_in(root: Path, name: str, raw: bytes) -> dict:
    _name(name)
    require(type(raw) is bytes and 0 < len(raw) <= 64 * 1024 * 1024,
            'bounded exact evidence bytes required')
    canonical_path(str(root), absolute=True)
    with HeldCanonicalDirectory(str(root)) as held:
        require(held.attached(), 'evidence parent detached')
        fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                     0o600, dir_fd=held.fd)
        try:
            written = 0
            while written < len(raw):
                amount = os.write(fd, raw[written:])
                require(amount > 0, 'evidence write made no progress')
                written += amount
            os.fsync(fd)
            info = os.fstat(fd)
            require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and
                    info.st_size == len(raw) and held.attached(),
                    'new evidence leaf or parent changed')
        finally:
            os.close(fd)
        os.fsync(held.fd)
        current = os.stat(name, dir_fd=held.fd, follow_symlinks=False)
        require(held.attached() and stat.S_ISREG(current.st_mode) and
                (current.st_dev, current.st_ino, current.st_mode, current.st_uid,
                 current.st_gid, current.st_nlink, current.st_size, current.st_mtime_ns,
                 current.st_ctime_ns) ==
                (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid,
                 info.st_nlink, info.st_size, info.st_mtime_ns, info.st_ctime_ns),
                'published evidence leaf detached before return')
    return {'path': str(root / name), 'sha256': hashlib.sha256(raw).hexdigest(),
            'size_bytes': len(raw)}


def publish_numbered(name: str, raw: bytes) -> dict:
    """Create a new numbered evidence leaf in this unit's exact evidence root."""
    row = _publish_in(EVIDENCE, name, raw)
    row['path'] = str((EVIDENCE / name).relative_to(REPO))
    return row


def _audit_in(root: Path, row: dict) -> None:
    require(type(row) is dict and set(row) == {'path', 'sha256', 'size_bytes'} and
            type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}', row['sha256']) and
            type(row['size_bytes']) is int and 0 < row['size_bytes'] <= 64 * 1024 * 1024,
            'closed historical evidence binding required')
    selected = canonical_path(row['path'], absolute=row['path'].startswith('/'))
    path = Path(selected) if selected.is_absolute() else REPO / str(selected)
    require(path.parent == root and NUMBERED.fullmatch(path.name) is not None,
            'historical binding outside numbered evidence root')
    with HeldCanonicalDirectory(str(root)) as held:
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC,
                     dir_fd=held.fd)
        try:
            before = os.fstat(fd)
            require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
                    before.st_size == row['size_bytes'], 'historical evidence type or size differs')
            digest = hashlib.sha256()
            size = 0
            while True:
                chunk = os.read(fd, 1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                require(size <= before.st_size, 'historical evidence grew')
                digest.update(chunk)
            after = os.fstat(fd)
            attached = os.stat(path.name, dir_fd=held.fd, follow_symlinks=False)
            def stable(info):
                return (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid,
                        info.st_nlink, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
            require(size == before.st_size and digest.hexdigest() == row['sha256'] and
                    stable(before) == stable(after) == stable(attached) and held.attached(),
                    'historical evidence bytes or attachment differ')
        finally:
            os.close(fd)


def audit_evidence(rows: list[dict]) -> int:
    """Verify only explicitly frozen evidence/log/review bindings, never source."""
    require(type(rows) is list and all(type(r) is dict and type(r.get('path')) is str for r in rows) and
            all(not r['path'].startswith('/') for r in rows) and
            len(rows) == len({r['path'] for r in rows}),
            'unique explicit historical evidence list required')
    for row in rows:
        _audit_in(EVIDENCE, row)
    return len(rows)
