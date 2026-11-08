#!/usr/bin/env python3
"""Effect-disabled WSL storage bootstrap model. No host apply entrypoint exists.

The scratch core proves ordering and empty-inode rollback mechanics. It is not
an administrator installer or an activation capability.
"""

from __future__ import annotations

import argparse
import errno
import json
import os
import re
import secrets
import stat
import sys
import tempfile
from dataclasses import dataclass


ROOT = "/var/lib/cyberalchemy-lab/source8-v1"
NAMES = ("cyberalchemy-lab", "source8-v1", "instances", "custody", "retained")
HOST_PATHS = (
    "/var/lib/cyberalchemy-lab",
    ROOT,
    ROOT + "/instances",
    ROOT + "/custody",
    ROOT + "/retained",
)
O_DIR = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
SCRATCH = re.compile(r"/tmp/cal-host-install-candidate-0002-[a-z0-9_]{6,32}\Z")
_LIVE: dict[str, tuple[str, int, int]] = {}


class Refused(RuntimeError):
    pass


@dataclass(frozen=True)
class Created:
    name: str
    dev: int
    ino: int
    mode: int


@dataclass(frozen=True)
class ScratchSession:
    path: str
    fd: int
    token: str


def new_scratch_session() -> ScratchSession:
    """Create a fresh process-local fixture, not a production custody token."""
    if os.geteuid() == 0:
        raise Refused("ROOT_EXECUTION_REFUSED")
    path = tempfile.mkdtemp(prefix="cal-host-install-candidate-0002-", dir="/tmp")
    os.chmod(path, 0o700)
    fd = os.open(path, O_DIR)
    value = os.fstat(fd)
    token = secrets.token_hex(16)
    _LIVE[token] = (path, value.st_dev, value.st_ino)
    return ScratchSession(path, fd, token)


def close_scratch_session(session: ScratchSession) -> None:
    _LIVE.pop(session.token, None)
    os.close(session.fd)


def _dir(fd: int, uid: int, gid: int, mode: int, dev: int) -> os.stat_result:
    value = os.fstat(fd)
    if (not stat.S_ISDIR(value.st_mode) or value.st_uid != uid or value.st_gid != gid
            or stat.S_IMODE(value.st_mode) != mode or value.st_dev != dev
            or os.get_inheritable(fd)):
        raise Refused("DIRECTORY_IDENTITY_REFUSED")
    return value


def _named(parent: int, name: str, child: int) -> None:
    value = os.stat(name, dir_fd=parent, follow_symlinks=False)
    held = os.fstat(child)
    if not stat.S_ISDIR(value.st_mode) or (value.st_dev, value.st_ino) != (held.st_dev, held.st_ino):
        raise Refused("NAMED_ATTACHMENT_REFUSED")


def _scratch_parent(session: ScratchSession, parent: int) -> os.stat_result:
    if os.geteuid() == 0:
        raise Refused("ROOT_EXECUTION_REFUSED")
    witness = _LIVE.get(session.token)
    if witness is None or witness[0] != session.path:
        raise Refused("FRESH_SCRATCH_SESSION_REQUIRED")
    root = os.fstat(session.fd)
    try:
        attached = os.stat(session.path, follow_symlinks=False)
    except OSError as error:
        raise Refused("SCRATCH_SESSION_DETACHED") from error
    if ((root.st_dev, root.st_ino) != (witness[1], witness[2])
            or (attached.st_dev, attached.st_ino) != (witness[1], witness[2])):
        raise Refused("SCRATCH_SESSION_DETACHED")
    path = os.readlink(f"/proc/self/fd/{parent}")
    if not SCRATCH.fullmatch(session.path) or not (
            path == session.path or path.startswith(session.path + "/")):
        raise Refused("SCRATCH_PARENT_REQUIRED")
    value = os.fstat(parent)
    if (not stat.S_ISDIR(value.st_mode) or value.st_uid != os.geteuid()
            or value.st_gid != os.getegid() or stat.S_IMODE(value.st_mode) != 0o700):
        raise Refused("SCRATCH_PARENT_IDENTITY_REFUSED")
    return value


def _make(session: ScratchSession, parent: int, name: str, uid: int,
          gid: int, dev: int) -> tuple[int, Created]:
    # Always create at 0700; the public 0755 ancestor is widened last.
    if name not in NAMES:
        raise Refused("NAME_REFUSED")
    _scratch_parent(session, parent)
    actual = os.readlink(f"/proc/self/fd/{parent}")
    expected = (session.path if name == NAMES[0]
                else session.path + "/" + NAMES[0] if name == NAMES[1]
                else session.path + "/" + NAMES[0] + "/" + NAMES[1])
    if actual != expected:
        raise Refused("SCRATCH_STAGE_PARENT_REFUSED")
    os.mkdir(name, mode=0o700, dir_fd=parent)
    os.fsync(parent)
    # This checks attachment after mkdir but cannot identify the inode that
    # mkdir itself created if a same-UID actor can replace the parent entry.
    child = os.open(name, O_DIR, dir_fd=parent)
    try:
        value = _dir(child, uid, gid, 0o700, dev)
        _named(parent, name, child)
        os.fsync(child)
        return child, Created(name, value.st_dev, value.st_ino, 0o700)
    except BaseException:
        os.close(child)
        raise


def _fixture_stage(session: ScratchSession) -> list[Created]:
    """Scratch-only model. Never call with /var/lib or privilege."""
    parent = session.fd
    base = _scratch_parent(session, parent)
    uid, gid, dev = base.st_uid, base.st_gid, base.st_dev
    old_umask = os.umask(0o077)
    created: list[Created] = []
    held: list[int] = [os.dup(parent)]
    try:
        current, first = _make(session, held[-1], NAMES[0], uid, gid, dev)
        held.append(current)
        created.append(first)
        next_fd, second = _make(session, held[-1], NAMES[1], uid, gid, dev)
        held.append(next_fd)
        created.append(second)
        for name in NAMES[2:]:
            child, witness = _make(session, held[-1], name, uid, gid, dev)
            created.append(witness)
            os.close(child)
        # Only this ancestor becomes traverseable after the private root exists.
        os.fchmod(held[1], 0o755)
        os.fsync(held[1])
        os.fsync(held[0])
        _dir(held[1], uid, gid, 0o755, dev)
        _named(held[0], NAMES[0], held[1])
        _dir(held[2], uid, gid, 0o700, dev)
        _named(held[1], NAMES[1], held[2])
        return [Created(first.name, first.dev, first.ino, 0o755), *created[1:]]
    finally:
        for fd in reversed(held):
            os.close(fd)
        os.umask(old_umask)


def _fixture_rollback_plan(session: ScratchSession, created: list[Created]) -> dict:
    """Inspect reversibility without unlinking a name under a writable parent.

    A checked name can be replaced before rmdir; this candidate contains no
    rollback deletion route. A root-owned inaccessible parent is prerequisite
    to a future effectful rollback release.
    """
    parent = session.fd
    _scratch_parent(session, parent)
    if [row.name for row in created] != list(NAMES):
        raise Refused("ROLLBACK_WITNESS_REFUSED")
    a = os.open(NAMES[0], O_DIR, dir_fd=parent)
    b = None
    leaves: list[int] = []
    try:
        b = os.open(NAMES[1], O_DIR, dir_fd=a)
        for row in created[2:]:
            leaves.append(os.open(row.name, O_DIR, dir_fd=b))
        # Preflight the entire scratch rollback before the first deletion.
        for held_parent, held_child, row in ((parent, a, created[0]),
                                             (a, b, created[1]),
                                             *((b, fd, row) for fd, row in zip(leaves, created[2:]))):
            value = os.fstat(held_child)
            if ((value.st_dev, value.st_ino) != (row.dev, row.ino)
                    or stat.S_IMODE(value.st_mode) != row.mode):
                raise Refused("ROLLBACK_DEPENDENCY_OR_IDENTITY")
            _named(held_parent, row.name, held_child)
        if (set(os.listdir(a)) != {NAMES[1]}
                or set(os.listdir(b)) != set(NAMES[2:])
                or any(os.listdir(fd) for fd in leaves)):
            raise Refused("ROLLBACK_DEPENDENCY_OR_IDENTITY")
        return {"status": "DRY_RUN_ONLY_PARENT_WRITABLE",
                "empty_witnesses": [row.name for row in created],
                "deletion_enabled": False}
    finally:
        for fd in leaves:
            os.close(fd)
        if b is not None:
            os.close(b)
        os.close(a)


def plan() -> dict:
    """Read-only public route; no host authority follows from its observation."""
    state = {}
    for path in ("/var", "/var/lib", *HOST_PATHS):
        try:
            value = os.lstat(path)
            state[path] = {"type": "directory" if stat.S_ISDIR(value.st_mode) else "other",
                           "uid": value.st_uid, "gid": value.st_gid,
                           "mode": oct(stat.S_IMODE(value.st_mode)),
                           "device": value.st_dev, "inode": value.st_ino}
        except FileNotFoundError:
            state[path] = {"type": "absent"}
    acl = {}
    held = []
    try:
        current = os.open("/", O_DIR)
        held.append(current)
        for name in ("var", "lib"):
            current = os.open(name, O_DIR, dir_fd=current)
            held.append(current)
            path = "/var" if name == "var" else "/var/lib"
            acl[path] = {}
            for attribute in ("system.posix_acl_access", "system.posix_acl_default"):
                try:
                    os.getxattr(current, attribute)
                    acl[path][attribute] = "present"
                except OSError as error:
                    acl[path][attribute] = ("absent" if error.errno == errno.ENODATA
                                            else "unknown:" + errno.errorcode.get(error.errno, str(error.errno)))
    except OSError as error:
        acl["chain"] = "unknown:" + errno.errorcode.get(error.errno, str(error.errno))
    finally:
        for fd in reversed(held):
            os.close(fd)
    return {"status": "INACTIVE_NO_HOST_APPLY", "proposed_paths": HOST_PATHS,
            "observed": state, "acl_xattrs_on_held_ancestors": acl,
            "activation": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", action="store_true", help="read-only host snapshot (default)")
    parser.add_argument("--apply", action="store_true", help="always refuse; no host installer released")
    args = parser.parse_args()
    if args.apply:
        print("HOST_INSTALL_EFFECT_DISABLED", file=sys.stderr)
        return 3
    print(json.dumps(plan(), sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
