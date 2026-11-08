#!/usr/bin/env python3
"""Read-only preflight for a proposed root-owned storage-code installation.

There is deliberately no apply route. This module does not confer authority to
run code from a user-writable checkout as root.
"""

from __future__ import annotations

import argparse
import errno
import fcntl
import hashlib
import json
import os
import stat
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parent.parent / "host-storage-release-candidate-0001" / "release.py"
SOURCE_SHA256 = "dcbf8d6c8ddad7f77a2f55ba6f95a77f5936456853cb8145b517ef3e22ff53c4"
DESTINATION = "/usr/local/libexec/cal-host-storage-release-0001/release.py"
PACKAGE = "/usr/local/libexec/cal-host-storage-release-0001"
O_DIRECTORY = os.O_PATH | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC


class Refused(RuntimeError):
    pass


def source_bytes(path: Path, expected_hash: str) -> tuple[bytes, dict]:
    """Pin copied bytes without changing a relatime source's access time."""
    noatime = getattr(os, "O_NOATIME", None)
    if noatime is None:
        raise Refused("O_NOATIME_UNAVAILABLE")
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | noatime)
    except OSError as error:
        raise Refused("SOURCE_NOATIME_OPEN_REFUSED") from error
    try:
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        if not flags & noatime:
            raise Refused("SOURCE_NOATIME_NOT_HELD")
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise Refused("SOURCE_NOT_SINGLE_REGULAR_FILE")
        with os.fdopen(os.dup(fd), "rb") as stream:
            payload = stream.read()
        after = os.fstat(fd)
        fields = ("st_dev", "st_ino", "st_uid", "st_gid", "st_mode", "st_size",
                  "st_mtime_ns", "st_ctime_ns", "st_atime_ns", "st_nlink")
        if any(getattr(before, field) != getattr(after, field) for field in fields):
            raise Refused("SOURCE_CHANGED_DURING_READ")
        digest = hashlib.sha256(payload).hexdigest()
        if digest != expected_hash:
            raise Refused("SOURCE_HASH_CHANGED")
        return payload, {"device": before.st_dev, "inode": before.st_ino,
                         "uid": before.st_uid, "gid": before.st_gid,
                         "mode": oct(stat.S_IMODE(before.st_mode)),
                         "size": len(payload), "sha256": digest,
                         "atime_ns": before.st_atime_ns}
    finally:
        os.close(fd)


def destination_preimage(prefix: str = "/", expected_uid: int = 0) -> dict:
    """Inspect each held ancestor; refuse occupied package name and ACLs."""
    if not os.path.isabs(prefix):
        raise Refused("ABSOLUTE_PREFIX_REQUIRED")
    held = []
    rows = {}
    try:
        current = os.open(prefix, O_DIRECTORY)
        held.append(current)
        root = os.fstat(current)
        if (not stat.S_ISDIR(root.st_mode) or root.st_uid != expected_uid
                or root.st_gid != expected_uid
                or stat.S_IMODE(root.st_mode) & 0o022):
            raise Refused("DESTINATION_ANCESTOR_UNTRUSTED")
        for name in ("usr", "local", "libexec"):
            current = os.open(name, O_DIRECTORY, dir_fd=current)
            held.append(current)
            value = os.fstat(current)
            if (not stat.S_ISDIR(value.st_mode) or value.st_uid != expected_uid
                    or value.st_gid != expected_uid
                    or stat.S_IMODE(value.st_mode) & 0o022):
                raise Refused("DESTINATION_ANCESTOR_UNTRUSTED")
            for attr in ("system.posix_acl_access", "system.posix_acl_default"):
                try:
                    os.getxattr(f"/proc/self/fd/{current}", attr)
                except OSError as error:
                    if error.errno == errno.ENODATA:
                        continue
                    raise Refused("DESTINATION_ACL_UNKNOWN") from error
                raise Refused("DESTINATION_ACL_PRESENT")
            rows[name] = {"device": value.st_dev, "inode": value.st_ino,
                          "uid": value.st_uid, "gid": value.st_gid,
                          "mode": oct(stat.S_IMODE(value.st_mode))}
        try:
            os.stat("cal-host-storage-release-0001", dir_fd=current,
                    follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise Refused("CODE_PACKAGE_NAME_ALREADY_CONSUMED")
        return rows
    finally:
        for fd in reversed(held):
            os.close(fd)


def preflight(source: Path = SOURCE, prefix: str = "/",
              expected_uid: int = 0, expected_hash: str = SOURCE_SHA256) -> dict:
    payload, witness = source_bytes(source, expected_hash)
    ancestors = destination_preimage(prefix, expected_uid)
    return {"status": "INACTIVE_PREFLIGHT_ONLY", "source": str(source),
            "source_witness": witness, "copied_bytes": len(payload),
            "destination": DESTINATION, "ancestor_witnesses": ancestors,
            "apply_enabled": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.apply:
        print("REFUSED:HOST_CODE_INSTALL_NOT_RELEASED", file=sys.stderr)
        return 3
    try:
        print(json.dumps(preflight(), sort_keys=True, indent=2))
        return 0
    except (OSError, Refused) as error:
        print("REFUSED:" + str(error), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
