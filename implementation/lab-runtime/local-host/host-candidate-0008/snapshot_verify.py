#!/usr/bin/env python3
"""Read-only exact snapshot verifier candidate; no protected closure is selected."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys

from broker import Refused, mount_id

COMPONENT = re.compile(r"[A-Za-z0-9._+-]+\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


def _relative(value: str) -> tuple[str, ...]:
    parts = value.split("/")
    if not parts or any(not COMPONENT.fullmatch(part) or part in (".", "..") for part in parts):
        raise Refused("invalid snapshot member")
    return tuple(parts)


def _mode(value: str) -> int:
    if not isinstance(value, str) or not re.fullmatch(r"0[0-7]{3}", value):
        raise Refused("invalid snapshot mode")
    return int(value, 8)


def verify(root: Path, manifest: dict) -> dict:
    if set(manifest) != {"schema", "root_uid", "root_gid", "root_mode", "root_device",
                         "root_mount_id", "members"} or manifest["schema"] != "cal-snapshot-0005":
        raise Refused("snapshot schema mismatch")
    if type(manifest["root_uid"]) is not int or type(manifest["root_gid"]) is not int:
        raise Refused("invalid owner")
    if type(manifest["root_device"]) is not int or type(manifest["root_mount_id"]) is not int:
        raise Refused("invalid root identity")
    if not isinstance(manifest["members"], list):
        raise Refused("members must be a list")
    expected: dict[str, dict] = {}
    for member in manifest["members"]:
        if not isinstance(member, dict) or set(member) not in (
            {"path", "kind", "mode"}, {"path", "kind", "mode", "sha256"}):
            raise Refused("invalid member fields")
        path = member["path"]
        if not isinstance(path, str):
            raise Refused("invalid member path")
        _relative(path)
        if path in expected:
            raise Refused("duplicate member")
        kind = member["kind"]
        if kind not in ("directory", "file") or (kind == "file") != ("sha256" in member):
            raise Refused("member kind or digest mismatch")
        mode = _mode(member["mode"])
        if mode & 0o222 or mode & 0o6000:
            raise Refused("writable or special snapshot member")
        if kind == "file" and (not isinstance(member["sha256"], str)
                               or not HEX64.fullmatch(member["sha256"])):
            raise Refused("invalid file digest")
        expected[path] = member
    root_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        root_st = os.fstat(root_fd)
        if (root_st.st_uid, root_st.st_gid, stat.S_IMODE(root_st.st_mode), root_st.st_dev,
            mount_id(root_fd)) != (manifest["root_uid"], manifest["root_gid"],
                                   _mode(manifest["root_mode"]), manifest["root_device"],
                                   manifest["root_mount_id"]):
            raise Refused("snapshot root identity mismatch")
        if stat.S_IMODE(root_st.st_mode) & 0o222:
            raise Refused("writable snapshot root")
        observed: set[str] = set()

        def visit(directory_fd: int, prefix: str) -> None:
            with os.scandir(directory_fd) as iterator:
                entries = list(iterator)
            for entry in entries:
                path = prefix + entry.name
                wanted = expected.get(path)
                if wanted is None:
                    raise Refused("unexpected snapshot member")
                observed.add(path)
                flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC
                if wanted["kind"] == "directory":
                    flags |= os.O_DIRECTORY
                fd = os.open(entry.name, flags, dir_fd=directory_fd)
                try:
                    st = os.fstat(fd)
                    if (st.st_uid, st.st_gid, stat.S_IMODE(st.st_mode), st.st_dev,
                        mount_id(fd)) != (manifest["root_uid"], manifest["root_gid"],
                                          _mode(wanted["mode"]), manifest["root_device"],
                                          manifest["root_mount_id"]):
                        raise Refused("snapshot member identity mismatch")
                    if wanted["kind"] == "directory":
                        if not stat.S_ISDIR(st.st_mode):
                            raise Refused("expected directory")
                        visit(fd, path + "/")
                    else:
                        if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
                            raise Refused("expected unique regular file")
                        digest = hashlib.sha256()
                        while chunk := os.read(fd, 1024 * 1024):
                            digest.update(chunk)
                        after = os.fstat(fd)
                        if (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns) != (
                            st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns):
                            raise Refused("snapshot file changed during read")
                        if digest.hexdigest() != wanted["sha256"]:
                            raise Refused("snapshot digest mismatch")
                finally:
                    os.close(fd)

        visit(root_fd, "")
        if observed != set(expected):
            raise Refused("missing snapshot member")
        return {"schema": "cal-snapshot-verified-0005", "member_count": len(observed)}
    finally:
        os.close(root_fd)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: snapshot_verify.py SNAPSHOT_ROOT MANIFEST_JSON")
    try:
        print(json.dumps(verify(Path(sys.argv[1]), json.loads(Path(sys.argv[2]).read_text()))))
    except (OSError, ValueError, Refused) as exc:
        raise SystemExit(f"snapshot refused: {type(exc).__name__}") from exc
