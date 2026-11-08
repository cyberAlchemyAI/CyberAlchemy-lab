#!/usr/bin/env python3
"""Inert broker candidate 0008. Public host-write routes always refuse.

The caller must already have verified a Root intent and a continuously held
slot. This module cannot establish either authority. Production policy fixes
the instances/custody owners to root; tests use an isolated UID-owned fixture.
"""

from __future__ import annotations

import hashlib
import fcntl
import json
import os
import re
import stat
from dataclasses import dataclass
from typing import Any


NAME = re.compile(r"[a-z0-9][a-z0-9-]{0,47}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
EPOCH = re.compile(r"e[1-9][0-9]{0,9}\Z")
O_DIR = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC


class Refused(RuntimeError):
    pass


def activation_capability() -> None:
    """The installed proc/namespace/slot oracle has not been selected."""
    raise Refused("HOST_ACTIVATION_DISABLED")


def _read_held_regular(fd: int, *, uid: int, gid: int, mode: int,
                       max_bytes: int = 1 << 20) -> tuple[bytes, os.stat_result]:
    noatime = getattr(os, "O_NOATIME", None)
    if noatime is None or not (fcntl.fcntl(fd, fcntl.F_GETFL) & noatime):
        raise Refused("O_NOATIME_REQUIRED_BEFORE_READ")
    if os.get_inheritable(fd):
        raise Refused("inheritable input descriptor")
    before = os.fstat(fd)
    if not stat.S_ISREG(before.st_mode) or before.st_uid != uid or before.st_gid != gid:
        raise Refused("input type or owner mismatch")
    if stat.S_IMODE(before.st_mode) != mode or before.st_size > max_bytes:
        raise Refused("input mode or size mismatch")
    chunks = []
    offset = 0
    while offset < before.st_size:
        chunk = os.pread(fd, min(65536, before.st_size - offset), offset)
        if not chunk:
            raise Refused("short held input read")
        chunks.append(chunk)
        offset += len(chunk)
    after = os.fstat(fd)
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns,
            before.st_ctime_ns, before.st_atime_ns) != (after.st_dev, after.st_ino,
                                    after.st_size, after.st_mtime_ns,
                                    after.st_ctime_ns, after.st_atime_ns):
        raise Refused("held input changed during read")
    return b"".join(chunks), after


def _fixture_root(fd: int, leaf: str) -> str:
    """Accidental-write guard for tests, not a security boundary against root."""
    try:
        path = os.readlink(f"/proc/self/fd/{fd}")
    except OSError as error:
        raise Refused("FIXTURE_SCOPE_UNAVAILABLE") from error
    prefix = "/tmp/cal-host-candidate-0008-"
    if not path.startswith(prefix) or not path.endswith("/" + leaf):
        raise Refused("FIXTURE_SCOPE_REQUIRED")
    suffix = path[len(prefix):-len("/" + leaf)]
    if not re.fullmatch(r"[a-z0-9_]{6,32}", suffix):
        raise Refused("FIXTURE_SCOPE_REQUIRED")
    return path[:-len("/" + leaf)]


def open_noatime_input(parent_fd: int, name: str, *, uid: int, gid: int,
                       mode: int) -> int:
    """Open an exact held input with nofollow and noatime or refuse.

    The caller must separately establish the root-owned parent and its
    attachment. This helper neither verifies Root issuer nor slot authority.
    """
    noatime = getattr(os, "O_NOATIME", None)
    if not NAME.fullmatch(name) or noatime is None:
        raise Refused("invalid name or O_NOATIME unavailable")
    try:
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | noatime,
                     dir_fd=parent_fd)
    except OSError as error:
        raise Refused("O_NOATIME_INPUT_OPEN_REFUSED") from error
    try:
        st = os.fstat(fd)
        if (not stat.S_ISREG(st.st_mode) or st.st_uid != uid or st.st_gid != gid
                or stat.S_IMODE(st.st_mode) != mode or os.get_inheritable(fd)):
            raise Refused("input owner, mode, or descriptor mismatch")
        return fd
    except BaseException:
        os.close(fd)
        raise


def verify_named_attachment(parent_fd: int, name: str, child_fd: int, *,
                            parent_uid: int, parent_gid: int,
                            child_uid: int, child_gid: int,
                            parent_mode: int, child_mode: int, device: int,
                            expected_mount_id: int) -> tuple[int, int]:
    """Check one held child is still the named entry of a held, trusted parent.

    This is a point-in-time check. The parent must be inaccessible for writes
    by an untrusted actor throughout the create-to-open interval.
    """
    if not NAME.fullmatch(name):
        raise Refused("invalid attachment name")
    _directory(parent_fd, uid=parent_uid, gid=parent_gid, mode=parent_mode,
               device=device, expected_mount_id=expected_mount_id)
    child = _directory(child_fd, uid=child_uid, gid=child_gid, mode=child_mode,
                       device=device, expected_mount_id=expected_mount_id)
    named = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    if not stat.S_ISDIR(named.st_mode) or (named.st_dev, named.st_ino) != (child.st_dev, child.st_ino):
        raise Refused("named directory detached or replaced")
    return child.st_dev, child.st_ino


@dataclass(frozen=True)
class BoundInputs:
    """Caller-supplied file pins, rechecked from held descriptors before effect.

    A digest does not prove issuer authority or continuous custody; the
    protected Root/slot verifier and installed namespace remain separate.
    """
    intent_fd: int
    intent_sha256: str
    intent_uid: int
    intent_gid: int
    intent_mode: int
    slot_sha256: str
    slot_uid: int
    slot_gid: int
    slot_mode: int
    slot_device: int
    slot_inode: int

    def verify(self, attempt: "SelectedAttempt") -> None:
        if not HEX64.fullmatch(self.intent_sha256) or not HEX64.fullmatch(self.slot_sha256):
            raise Refused("invalid input digest")
        if self.intent_sha256 != attempt.root_intent_sha256:
            raise Refused("Root intent digest does not bind attempt")
        intent, _ = _read_held_regular(self.intent_fd, uid=self.intent_uid,
                                      gid=self.intent_gid, mode=self.intent_mode)
        slot, slot_stat = _read_held_regular(attempt.slot_fd, uid=self.slot_uid,
                                            gid=self.slot_gid, mode=self.slot_mode)
        if hashlib.sha256(intent).hexdigest() != self.intent_sha256:
            raise Refused("Root intent bytes changed")
        if hashlib.sha256(slot).hexdigest() != self.slot_sha256:
            raise Refused("slot bytes changed")
        if (slot_stat.st_dev, slot_stat.st_ino) != (self.slot_device, self.slot_inode):
            raise Refused("slot inode changed")


def _directory(fd: int, *, uid: int, gid: int, mode: int, device: int | None = None,
               expected_mount_id: int | None = None) -> os.stat_result:
    if os.get_inheritable(fd):
        raise Refused("inheritable directory descriptor")
    st = os.fstat(fd)
    if not stat.S_ISDIR(st.st_mode) or st.st_uid != uid or st.st_gid != gid:
        raise Refused("directory type or owner mismatch")
    if stat.S_IMODE(st.st_mode) != mode or st.st_nlink < 2:
        raise Refused("directory mode or link count mismatch")
    if device is not None and st.st_dev != device:
        raise Refused("directory device mismatch")
    if expected_mount_id is not None and mount_id(fd) != expected_mount_id:
        raise Refused("directory mount mismatch")
    return st


def open_directory_chain(anchor_fd: int, components: tuple[str, ...], *, uid: int,
                         gid: int, modes: tuple[int, ...], device: int,
                         expected_mount_id: int) -> int:
    """Traverse only exact names through held, nofollow directory descriptors."""
    if len(components) != len(modes):
        raise Refused("chain length mismatch")
    current = os.dup(anchor_fd)
    os.set_inheritable(current, False)
    try:
        for name, mode in zip(components, modes):
            if not NAME.fullmatch(name):
                raise Refused("invalid ancestor component")
            child = os.open(name, O_DIR, dir_fd=current)
            try:
                _directory(child, uid=uid, gid=gid, mode=mode, device=device,
                           expected_mount_id=expected_mount_id)
            except BaseException:
                os.close(child)
                raise
            os.close(current)
            current = child
        return current
    except BaseException:
        os.close(current)
        raise


@dataclass(frozen=True)
class SelectedAttempt:
    root_intent_sha256: str
    epoch: str
    child_name: str
    slot_fd: int

    def validate(self) -> os.stat_result:
        if not HEX64.fullmatch(self.root_intent_sha256):
            raise Refused("invalid Root intent digest")
        if not EPOCH.fullmatch(self.epoch) or not NAME.fullmatch(self.child_name):
            raise Refused("invalid epoch or child name")
        if os.get_inheritable(self.slot_fd):
            raise Refused("inheritable slot descriptor")
        slot = os.fstat(self.slot_fd)
        if not stat.S_ISREG(slot.st_mode):
            raise Refused("slot is not a regular file")
        return slot


def _write_exclusive(directory_fd: int, name: str, body: dict[str, Any]) -> None:
    directory = os.fstat(directory_fd)
    if (os.geteuid() == 0 or not stat.S_ISDIR(directory.st_mode)
            or directory.st_uid != os.geteuid()):
        raise Refused("FIXTURE_ONLY_NO_ROOT_WRITES")
    _fixture_root(directory_fd, "custody")
    encoded = (json.dumps(body, sort_keys=True, separators=(",", ":")) + "\n").encode()
    fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                 0o600, dir_fd=directory_fd)
    try:
        if os.get_inheritable(fd) or stat.S_IMODE(os.fstat(fd).st_mode) != 0o600:
            raise Refused("record mode or inheritance mismatch")
        if os.write(fd, encoded) != len(encoded):
            raise Refused("short record write")
        os.fsync(fd)
    finally:
        os.close(fd)
    os.fsync(directory_fd)


@dataclass
class PreparedChild:
    child_fd: int
    child_name: str
    child_device: int
    child_inode: int
    host_mount_id: int
    claim_name: str
    slot_claim_name: str

    def close(self) -> None:
        if self.child_fd >= 0:
            os.close(self.child_fd)
            self.child_fd = -1


def mount_id(fd: int) -> int:
    if os.get_inheritable(fd):
        raise Refused("inheritable descriptor")
    with open(f"/proc/self/fdinfo/{fd}", encoding="ascii") as handle:
        values = [line.split(":", 1)[1].strip() for line in handle if line.startswith("mnt_id:")]
    if len(values) != 1 or not values[0].isdigit():
        raise Refused("missing mount identity")
    return int(values[0])


def _prepare_fixture_child(instances_fd: int, custody_fd: int, attempt: SelectedAttempt,
                  *, parent_uid: int, parent_gid: int, service_uid: int,
                  service_gid: int, device: int, expected_mount_id: int) -> PreparedChild:
    """Reserve one exact attempt, create its child 0700, retain its O_PATH FD.

    This is a disposable unprivileged fixture mechanism only. The caller
    keeps the returned FD until the fixture identity check.
    A failure leaves a custody claim and/or child for explicit reconciliation.
    """
    if os.geteuid() == 0 or parent_uid != os.geteuid() or parent_gid != os.getegid() or service_uid != os.geteuid() or service_gid != os.getegid():
        raise Refused("FIXTURE_ONLY_NO_ROOT_WRITES")
    if (os.fstat(instances_fd).st_dev, os.fstat(instances_fd).st_ino) == (os.fstat(custody_fd).st_dev, os.fstat(custody_fd).st_ino):
        raise Refused("instances and custody roots are the same inode")
    if _fixture_root(instances_fd, "instances") != _fixture_root(custody_fd, "custody"):
        raise Refused("FIXTURE_SCOPE_MISMATCH")
    instances = _directory(instances_fd, uid=parent_uid, gid=parent_gid, mode=0o700,
                           device=device, expected_mount_id=expected_mount_id)
    custody = _directory(custody_fd, uid=parent_uid, gid=parent_gid, mode=0o700,
                         device=device, expected_mount_id=expected_mount_id)
    if (instances.st_dev, instances.st_ino) == (custody.st_dev, custody.st_ino):
        raise Refused("instances and custody roots are the same inode")
    slot = attempt.validate()
    if attempt.child_name != f"i-{attempt.root_intent_sha256[:16]}-{attempt.epoch}":
        raise Refused("child name does not bind intent and epoch")
    if len(attempt.child_name) > 48:
        raise Refused("child name too long")
    try:
        os.stat(attempt.child_name, dir_fd=instances_fd, follow_symlinks=False)
    except FileNotFoundError:
        pass
    else:
        raise Refused("child name already exists")

    claim = f"{attempt.root_intent_sha256}-{attempt.epoch}.claim.json"
    slot_claim = f"slot-{slot.st_dev:x}-{slot.st_ino:x}.claim.json"
    core = {"schema": "cal-host-custody-0006", "root_intent_sha256": attempt.root_intent_sha256,
            "epoch": attempt.epoch, "child_name": attempt.child_name,
            "slot_device": slot.st_dev, "slot_inode": slot.st_ino}
    try:
        _write_exclusive(custody_fd, slot_claim, dict(core, state="slot-reserved"))
    except FileExistsError as error:
        raise Refused("held slot already reserved") from error
    _write_exclusive(custody_fd, claim, dict(core, state="claimed"))

    # Mode 0700 is passed to mkdirat itself: no create-then-chmod interval.
    os.mkdir(attempt.child_name, mode=0o700, dir_fd=instances_fd)
    child_fd = os.open(attempt.child_name,
                       os.O_PATH | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                       dir_fd=instances_fd)
    try:
        st = _directory(child_fd, uid=parent_uid, gid=parent_gid, mode=0o700,
                        device=device, expected_mount_id=expected_mount_id)
        # An O_PATH descriptor cannot list entries; hold a second nofollow FD.
        scan_fd = os.open(attempt.child_name, O_DIR, dir_fd=instances_fd)
        try:
            scan = os.fstat(scan_fd)
            if (scan.st_dev, scan.st_ino) != (st.st_dev, st.st_ino) or os.listdir(scan_fd):
                raise Refused("child identity or empty preimage mismatch")
            # fchown acts on the held inode, never on a later pathname lookup.
            os.fchown(scan_fd, service_uid, service_gid)
            os.fsync(scan_fd)
        finally:
            os.close(scan_fd)
        # The host parent remains root-controlled. Only the selected child changes owner.
        st = _directory(child_fd, uid=service_uid, gid=service_gid, mode=0o700,
                        device=device, expected_mount_id=expected_mount_id)
        current = os.stat(attempt.child_name, dir_fd=instances_fd, follow_symlinks=False)
        if (current.st_dev, current.st_ino) != (st.st_dev, st.st_ino):
            raise Refused("child entry changed during preparation")
        mid = mount_id(child_fd)
        # Make the child entry and its held-inode ownership durable before a
        # prepared record can claim that the child exists.
        os.fsync(instances_fd)
        _write_exclusive(custody_fd, claim.replace(".claim.json", ".prepared.json"),
                         dict(core, state="prepared", child_device=st.st_dev,
                              child_inode=st.st_ino, host_mount_id=mid))
        return PreparedChild(child_fd, attempt.child_name, st.st_dev, st.st_ino,
                             mid, claim, slot_claim)
    except BaseException:
        os.close(child_fd)
        raise


def prepare_child(*_args: Any, **_kwargs: Any) -> PreparedChild:
    """Production-name entrypoint is disabled before any input read or write."""
    activation_capability()
    raise AssertionError("unreachable")


def prepare_bound_child(instances_fd: int, custody_fd: int, attempt: SelectedAttempt,
                        binding: BoundInputs, *, parent_uid: int, parent_gid: int,
                        service_uid: int, service_gid: int, device: int,
                        expected_mount_id: int) -> PreparedChild:
    """Disposable core for a future root-only broker; no host entrypoint calls it.

    Unlike 0006, this checks exact held Root/slot file bytes and their stat
    identities. A later installed broker must also prove issuer, slot-lock,
    parent/ancestor exclusivity and namespace/proc denial before activation.
    """
    activation_capability()
    attempt.validate()
    binding.verify(attempt)
    if parent_uid == service_uid or parent_gid == service_gid:
        raise Refused("service principal overlaps broker parent")
    _directory(instances_fd, uid=parent_uid, gid=parent_gid, mode=0o700,
               device=device, expected_mount_id=expected_mount_id)
    _directory(custody_fd, uid=parent_uid, gid=parent_gid, mode=0o700,
               device=device, expected_mount_id=expected_mount_id)
    # No claim may be created if a caller expects an untrusted principal to
    # own the parent. In tests this is a negative control, not a root proof.
    if parent_uid != 0 or parent_gid != 0:
        raise Refused("broker parents must be root-owned")
    result = prepare_child(instances_fd, custody_fd, attempt,
                           parent_uid=parent_uid, parent_gid=parent_gid,
                           service_uid=service_uid, service_gid=service_gid,
                           device=device, expected_mount_id=expected_mount_id)
    try:
        verify_named_attachment(instances_fd, attempt.child_name, result.child_fd,
                                parent_uid=parent_uid, parent_gid=parent_gid,
                                child_uid=service_uid, child_gid=service_gid,
                                parent_mode=0o700, child_mode=0o700,
                                device=device, expected_mount_id=expected_mount_id)
        binding.verify(attempt)
        return result
    except BaseException:
        result.close()
        raise


def check_target_identity(prepared: PreparedChild, target_parent_fd: int,
                          target_name: str, *, parent_uid: int, parent_gid: int,
                          parent_mode: int, parent_device: int) -> dict[str, int]:
    """Necessary post-bind check, not proof of the path-resolution interval."""
    if not NAME.fullmatch(target_name):
        raise Refused("invalid target name")
    _directory(target_parent_fd, uid=parent_uid, gid=parent_gid,
               mode=parent_mode, device=parent_device)
    if parent_mode & 0o022:
        raise Refused("target parent writable by group or other")
    held = os.fstat(prepared.child_fd)
    if (held.st_dev, held.st_ino) != (prepared.child_device, prepared.child_inode):
        raise Refused("held source identity changed")
    target_fd = os.open(target_name, os.O_PATH | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                        dir_fd=target_parent_fd)
    try:
        target = os.fstat(target_fd)
        if (target.st_dev, target.st_ino) != (prepared.child_device, prepared.child_inode):
            raise Refused("target inode differs from held source")
        return {"source_device": prepared.child_device, "source_inode": prepared.child_inode,
                "host_mount_id": prepared.host_mount_id, "target_mount_id": mount_id(target_fd)}
    finally:
        os.close(target_fd)


if __name__ == "__main__":
    raise SystemExit("Inert broker candidate: no host activation CLI is installed")
