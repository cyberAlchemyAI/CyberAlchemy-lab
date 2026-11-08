#!/usr/bin/python3.14 -I
"""Unexecuted one-shot WSL storage release candidate.

The only live effect route requires a root-owned installed copy at a fixed
location and an exact, independently reviewed current host preimage. This
checkout copy cannot pass that deployment guard. No rollback deletion exists.
"""

from __future__ import annotations

import argparse
import errno
import hashlib
import json
import os
import re
import stat
import sys
from dataclasses import dataclass


VERSION = "cal-wsl-source8-storage-release/0003"
DEPLOYED = "/usr/local/libexec/cal-host-storage-release-0003/release.py"
RECEIPT = "/usr/local/libexec/cal-host-storage-release-0003/review-receipt.json"
RUNTIME_PINS = "/usr/local/libexec/cal-host-storage-release-0003/runtime-pins.json"
INTERPRETER = "/usr/bin/python3.14"
INTERPRETER_SHA256 = "52e0a13e60a981d8c4b6478be2ba5176f69da07948a056bf49cf6f077e30cb41"
TARGET = "/var/lib/cyberalchemy-lab"
O_DIR = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
O_NEW = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC
CLAIM = ".storage-bootstrap-consumed.json"
PREPARED = ".storage-bootstrap-prepared.json"
PINNED = {
    "/": (2096, 2, 0, 0, 0o755, 82),
    "/var": (2096, 49155, 0, 0, 0o755, 82),
    "/var/lib": (2096, 42045, 0, 0, 0o755, 82),
}
PINNED_SOURCE = "/dev/sdd"
PINNED_FSTYPE = "ext4"
PATH_NAMES = ("cyberalchemy-lab", "source8-v1", "instances", "custody", "retained")
ACL_ATTRS = ("system.posix_acl_access", "system.posix_acl_default")


class Refused(RuntimeError):
    pass


@dataclass(frozen=True)
class HostPins:
    ancestors: dict[str, tuple[int, int, int, int, int, int]]
    primary_source: str
    primary_fstype: str


LIVE = HostPins(PINNED, PINNED_SOURCE, PINNED_FSTYPE)


def _canonical(body: dict) -> bytes:
    return (json.dumps(body, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _mount_id(fd: int) -> int:
    with open(f"/proc/self/fdinfo/{fd}", encoding="ascii") as stream:
        matches = [row.partition(":")[2].strip() for row in stream if row.startswith("mnt_id:")]
    if len(matches) != 1 or not matches[0].isdecimal():
        raise Refused("MOUNT_ID_UNKNOWN")
    return int(matches[0])


def _check_directory(fd: int, expected: tuple[int, int, int, int, int, int]) -> os.stat_result:
    value = os.fstat(fd)
    actual = (value.st_dev, value.st_ino, value.st_uid, value.st_gid,
              stat.S_IMODE(value.st_mode), _mount_id(fd))
    if (not stat.S_ISDIR(value.st_mode) or actual != expected
            or os.get_inheritable(fd)):
        raise Refused("PINNED_ANCESTOR_CHANGED")
    for attribute in ACL_ATTRS:
        try:
            os.getxattr(fd, attribute)
        except OSError as error:
            if error.errno == errno.ENODATA:
                continue
            raise Refused("ACL_UNKNOWN") from error
        raise Refused("ACL_PRESENT")
    return value


def _decode_mount_field(field: str) -> str:
    return re.sub(r"\\([0-7]{3})", lambda match: chr(int(match.group(1), 8)), field)


def _mount_rows() -> list[dict]:
    rows = []
    with open("/proc/self/mountinfo", encoding="utf-8") as stream:
        for line in stream:
            left, sep, right = line.strip().partition(" - ")
            if not sep:
                raise Refused("MOUNTINFO_PARSE")
            fields, fs = left.split(), right.split()
            if len(fields) < 6 or len(fs) < 3:
                raise Refused("MOUNTINFO_PARSE")
            rows.append({"id": int(fields[0]), "device": fields[2],
                         "root": _decode_mount_field(fields[3]),
                         "point": _decode_mount_field(fields[4]),
                         "options": fields[5].split(","), "fstype": fs[0],
                         "source": _decode_mount_field(fs[1])})
    return rows


def _ancestor_of(parent: str, child: str) -> bool:
    return parent == "/" or child == parent or child.startswith(parent.rstrip("/") + "/")


def _check_mounts(pins: HostPins) -> None:
    rows = _mount_rows()
    selected_id = pins.ancestors["/var/lib"][5]
    selected = [row for row in rows if row["id"] == selected_id]
    if len(selected) != 1:
        raise Refused("STORAGE_MOUNT_CHANGED")
    storage = selected[0]
    device = pins.ancestors["/var/lib"][0]
    if (storage["device"] != f"{os.major(device)}:{os.minor(device)}"
            or storage["point"] not in ("/", "/var/lib")
            or storage["root"] != "/"
            or storage["fstype"] != pins.primary_fstype
            or storage["source"] != pins.primary_source or "rw" not in storage["options"]):
        raise Refused("STORAGE_MOUNT_CHANGED")
    for row in rows:
        if row is storage:
            continue
        if (row["point"] in ("/var", "/var/lib", TARGET)
                or _ancestor_of(TARGET, row["point"])):
            raise Refused("TARGET_MOUNT_OVERLAY")
        if row["device"] == storage["device"] and _ancestor_of(row["root"], TARGET):
            if "rw" in row["options"]:
                raise Refused("WRITABLE_ALIAS")


def _deployed_code() -> None:
    if os.getuid() != 0 or os.geteuid() != 0 or os.getgid() != 0 or os.getegid() != 0:
        raise Refused("ROOT_IDENTITY_REQUIRED")
    if os.path.abspath(__file__) != DEPLOYED:
        raise Refused("ROOT_OWNED_DEPLOYMENT_REQUIRED")
    if (os.path.realpath(sys.executable) != INTERPRETER or not sys.flags.isolated
            or not sys.flags.no_site or not sys.flags.dont_write_bytecode
            or not sys.flags.ignore_environment):
        raise Refused("ISOLATED_INTERPRETER_REQUIRED")
    if _sha_file(INTERPRETER) != INTERPRETER_SHA256:
        raise Refused("INTERPRETER_HASH_CHANGED")
    if sys.path != ["/usr/lib/python314.zip", "/usr/lib/python3.14",
                    "/usr/lib/python3.14/lib-dynload"]:
        raise Refused("IMPORT_PATH_CHANGED")
    parts = ("/", "/usr", "/usr/local", "/usr/local/libexec",
             "/usr/local/libexec/cal-host-storage-release-0003", DEPLOYED)
    for index, path in enumerate(parts):
        value = os.lstat(path)
        if (value.st_uid != 0 or value.st_gid != 0 or stat.S_IMODE(value.st_mode) & 0o022
                or (not stat.S_ISREG(value.st_mode) if index == len(parts) - 1
                    else not stat.S_ISDIR(value.st_mode))):
            raise Refused("DEPLOYED_CODE_UNTRUSTED")
    if stat.S_IMODE(os.lstat(DEPLOYED).st_mode) != 0o500:
        raise Refused("DEPLOYED_CODE_MODE")


def _sha_file(path: str) -> str:
    noatime = getattr(os, "O_NOATIME", None)
    if noatime is None:
        raise Refused("NOATIME_UNAVAILABLE")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | noatime)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_uid != 0 or before.st_gid != 0:
            raise Refused("PINNED_CODE_FILE_UNTRUSTED")
        digest = hashlib.sha256()
        while True:
            chunk = os.read(fd, 65536)
            if not chunk:
                break
            digest.update(chunk)
        after = os.fstat(fd)
        if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns,
                before.st_ctime_ns, before.st_atime_ns) != (
                after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns,
                after.st_ctime_ns, after.st_atime_ns):
            raise Refused("PINNED_CODE_CHANGED_DURING_READ")
        return digest.hexdigest()
    finally:
        os.close(fd)


def _reviewed_receipt(receipt_sha256: str) -> None:
    if not re.fullmatch(r"[0-9a-f]{64}", receipt_sha256):
        raise Refused("RECEIPT_PIN_INVALID")
    if _sha_file(RECEIPT) != receipt_sha256:
        raise Refused("RECEIPT_HASH_CHANGED")
    fd = os.open(RECEIPT, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NOATIME)
    try:
        value = os.fstat(fd)
        if stat.S_IMODE(value.st_mode) != 0o400 or value.st_nlink != 1:
            raise Refused("RECEIPT_MODE_OR_LINK")
        payload = os.read(fd, 8193)
        if len(payload) > 8192:
            raise Refused("RECEIPT_TOO_LARGE")
    finally:
        os.close(fd)
    receipt = json.loads(payload)
    reviewer = receipt.get("reviewer")
    if (receipt.get("schema") != "cal-host-storage-reviewed-receipt/v1"
            or receipt.get("verdict") != "PASS_FOR_ONE_SHOT_STORAGE_ONLY"
            or not isinstance(reviewer, str)
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/@-]{2,127}", reviewer)
            or receipt.get("release_sha256") != _sha_file(DEPLOYED)
            or receipt.get("runtime_pins_sha256") != _sha_file(RUNTIME_PINS)
            or receipt.get("target") != TARGET
            or receipt.get("preimage_sha256") != hashlib.sha256(_canonical({
                "ancestors": LIVE.ancestors, "source": LIVE.primary_source,
                "fstype": LIVE.primary_fstype})).hexdigest()):
        raise Refused("REVIEW_RECEIPT_SCOPE_REFUSED")
    _runtime_closure()


def _runtime_closure() -> None:
    fd = os.open(RUNTIME_PINS, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NOATIME)
    try:
        value = os.fstat(fd)
        if (value.st_uid != 0 or value.st_gid != 0 or stat.S_IMODE(value.st_mode) != 0o400
                or value.st_nlink != 1):
            raise Refused("RUNTIME_PINS_IDENTITY")
        payload = os.read(fd, 65537)
        if len(payload) > 65536:
            raise Refused("RUNTIME_PINS_TOO_LARGE")
    finally:
        os.close(fd)
    pins = json.loads(payload)
    if pins.get("schema") != "cal-python314-isolated-runtime-pins/v1":
        raise Refused("RUNTIME_PINS_SCHEMA")
    entries = pins.get("files")
    if not isinstance(entries, dict) or not entries:
        raise Refused("RUNTIME_PINS_EMPTY")
    for path, digest in entries.items():
        if (not isinstance(path, str) or not path.startswith("/usr/lib/")
                or not re.fullmatch(r"[0-9a-f]{64}", digest)
                or _sha_file(path) != digest):
            raise Refused("RUNTIME_FILE_CHANGED")
    for module in list(sys.modules.values()):
        for attribute in ("__file__", "__cached__"):
            path = getattr(module, attribute, None)
            if path and os.path.isfile(path):
                real = os.path.realpath(path)
                if real == DEPLOYED:
                    continue
                if not real.startswith("/usr/lib/") or real not in entries:
                    raise Refused("UNPINNED_IMPORTED_MODULE")


def _open_ancestors(pins: HostPins) -> tuple[int, int, int]:
    held = []
    try:
        current = os.open("/", O_DIR)
        held.append(current)
        _check_directory(current, pins.ancestors["/"])
        for name, path in (("var", "/var"), ("lib", "/var/lib")):
            current = os.open(name, O_DIR, dir_fd=current)
            held.append(current)
            _check_directory(current, pins.ancestors[path])
        return tuple(held)
    except BaseException:
        for fd in reversed(held):
            os.close(fd)
        raise


def _require_absent(parent: int, name: str) -> None:
    try:
        os.stat(name, dir_fd=parent, follow_symlinks=False)
    except FileNotFoundError:
        return
    raise Refused("ONE_SHOT_NAME_ALREADY_PRESENT")


def _new_directory(parent: int, name: str, device: int, mount: int) -> int:
    _require_absent(parent, name)
    os.mkdir(name, mode=0o700, dir_fd=parent)
    os.fsync(parent)
    fd = os.open(name, O_DIR, dir_fd=parent)
    value = os.fstat(fd)
    named = os.stat(name, dir_fd=parent, follow_symlinks=False)
    if (not stat.S_ISDIR(value.st_mode) or value.st_uid != 0 or value.st_gid != 0
            or stat.S_IMODE(value.st_mode) != 0o700 or value.st_dev != device
            or _mount_id(fd) != mount or (named.st_dev, named.st_ino) != (value.st_dev, value.st_ino)):
        os.close(fd)
        raise Refused("NEW_DIRECTORY_IDENTITY_UNKNOWN")
    os.fsync(fd)
    return fd


def _new_record(parent: int, name: str, body: dict) -> None:
    payload = _canonical(body)
    fd = os.open(name, O_NEW, 0o600, dir_fd=parent)
    try:
        value = os.fstat(fd)
        if (not stat.S_ISREG(value.st_mode) or value.st_uid != 0 or value.st_gid != 0
                or stat.S_IMODE(value.st_mode) != 0o600):
            raise Refused("NEW_RECORD_IDENTITY_UNKNOWN")
        if os.write(fd, payload) != len(payload):
            raise Refused("SHORT_RECORD_WRITE")
        os.fsync(fd)
    finally:
        os.close(fd)
    os.fsync(parent)


def _linked_directory(parent: int, name: str, held: int, mode: int,
                      device: int, mount: int) -> None:
    value = os.fstat(held)
    named = os.stat(name, dir_fd=parent, follow_symlinks=False)
    if (not stat.S_ISDIR(value.st_mode) or not stat.S_ISDIR(named.st_mode)
            or (value.st_dev, value.st_ino) != (named.st_dev, named.st_ino)
            or value.st_nlink < 2 or value.st_uid != 0 or value.st_gid != 0
            or stat.S_IMODE(value.st_mode) != mode or value.st_dev != device
            or _mount_id(held) != mount):
        raise Refused("FINAL_LINKED_DIRECTORY_REFUSED")


def _preflight(pins: HostPins) -> tuple[int, int, int]:
    ancestors = _open_ancestors(pins)
    try:
        _check_mounts(pins)
        _require_absent(ancestors[2], PATH_NAMES[0])
        # Recheck exact held ancestry immediately before the first mutation.
        for fd, path in zip(ancestors, ("/", "/var", "/var/lib")):
            _check_directory(fd, pins.ancestors[path])
        return ancestors
    except BaseException:
        for fd in reversed(ancestors):
            os.close(fd)
        raise


def _apply_storage(pins: HostPins) -> dict:
    """Internal exact-path transaction; callers supply no parent FD or path."""
    if os.getuid() != 0 or os.geteuid() != 0:
        raise Refused("ROOT_IDENTITY_REQUIRED")
    root_fd, var_fd, lib_fd = _preflight(pins)
    opened = [root_fd, var_fd, lib_fd]
    old_umask = os.umask(0o077)
    try:
        device, mount = pins.ancestors["/var/lib"][0], pins.ancestors["/var/lib"][5]
        top = _new_directory(lib_fd, PATH_NAMES[0], device, mount)
        opened.append(top)
        preimage = _canonical({"ancestors": pins.ancestors,
                               "source": pins.primary_source, "fstype": pins.primary_fstype})
        preimage_sha = hashlib.sha256(preimage).hexdigest()
        _new_record(top, CLAIM, {"schema": VERSION, "state": "CONSUMED_NO_RETRY",
                                 "preimage_sha256": preimage_sha})
        storage = _new_directory(top, PATH_NAMES[1], device, mount)
        opened.append(storage)
        leaf_witnesses = {}
        for name in PATH_NAMES[2:]:
            leaf = _new_directory(storage, name, device, mount)
            value = os.fstat(leaf)
            leaf_witnesses[name] = {"device": value.st_dev, "inode": value.st_ino}
            os.close(leaf)
        if set(os.listdir(storage)) != set(PATH_NAMES[2:]):
            raise Refused("STORAGE_NAMESPACE_CHANGED")
        if set(os.listdir(top)) != {CLAIM, PATH_NAMES[1]}:
            raise Refused("TOP_NAMESPACE_CHANGED")
        os.fchmod(top, 0o755)
        os.fsync(top)
        if stat.S_IMODE(os.fstat(top).st_mode) != 0o755:
            raise Refused("TOP_FINAL_MODE_UNKNOWN")
        prepared_body = {"schema": VERSION, "state": "STORAGE_PREPARED_ONLY",
                         "preimage_sha256": preimage_sha,
                         "top_inode": os.fstat(top).st_ino,
                         "storage_inode": os.fstat(storage).st_ino,
                         "leaves": leaf_witnesses}
        _new_record(top, PREPARED, prepared_body)
        if set(os.listdir(top)) != {CLAIM, PREPARED, PATH_NAMES[1]}:
            raise Refused("FINAL_NAMESPACE_CHANGED")
        _linked_directory(lib_fd, PATH_NAMES[0], top, 0o755, device, mount)
        _linked_directory(top, PATH_NAMES[1], storage, 0o700, device, mount)
        for name in PATH_NAMES[2:]:
            leaf = os.open(name, O_DIR, dir_fd=storage)
            try:
                observed = os.fstat(leaf)
                if (observed.st_dev, observed.st_ino) != (
                        leaf_witnesses[name]["device"], leaf_witnesses[name]["inode"]):
                    raise Refused("FINAL_LEAF_INODE_CHANGED")
                _linked_directory(storage, name, leaf, 0o700, device, mount)
                if os.listdir(leaf):
                    raise Refused("FINAL_LEAF_NOT_EMPTY")
            finally:
                os.close(leaf)
        if _sha_file(f"{TARGET}/{CLAIM}") != hashlib.sha256(_canonical({
                "schema": VERSION, "state": "CONSUMED_NO_RETRY",
                "preimage_sha256": preimage_sha})).hexdigest():
            raise Refused("FINAL_CLAIM_CHANGED")
        if _sha_file(f"{TARGET}/{PREPARED}") != hashlib.sha256(_canonical(prepared_body)).hexdigest():
            raise Refused("FINAL_PREPARED_CHANGED")
        for fd, path in zip((root_fd, var_fd, lib_fd), ("/", "/var", "/var/lib")):
            _check_directory(fd, pins.ancestors[path])
        _linked_directory(lib_fd, PATH_NAMES[0], top, 0o755, device, mount)
        _linked_directory(top, PATH_NAMES[1], storage, 0o700, device, mount)
        return {"status": "STORAGE_PREPARED_ONLY", "top_inode": os.fstat(top).st_ino,
                "storage_inode": os.fstat(storage).st_ino,
                "preimage_sha256": preimage_sha}
    finally:
        for fd in reversed(opened):
            os.close(fd)
        os.umask(old_umask)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--plan", action="store_true", help="read-only local preimage inspection")
    actions.add_argument("--apply-reviewed-one-shot", metavar="RECEIPT_SHA256",
                         help="root-owned installed copy and exact pinned host only")
    args = parser.parse_args()
    try:
        if args.apply_reviewed_one_shot:
            _deployed_code()
            _reviewed_receipt(args.apply_reviewed_one_shot)
            print(json.dumps(_apply_storage(LIVE), sort_keys=True))
            return 0
        held = _preflight(LIVE)
        for fd in reversed(held):
            os.close(fd)
        state = {"schema": VERSION, "status": "CURRENT_PINNED_PREFLIGHT_ONLY",
                 "target": TARGET, "deployed_code": DEPLOYED,
                 "pinned_ancestors": PINNED, "effect": "none"}
        print(json.dumps(state, sort_keys=True, indent=2))
        return 0
    except (OSError, Refused, ValueError) as error:
        print("REFUSED:" + str(error), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
