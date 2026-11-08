#!/usr/bin/python3.14 -I
"""One-shot fixed-path root code installer; never run without separate review."""

import argparse
import errno
import hashlib
import json
import os
import re
import stat
import sys


SOURCE = ("/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/"
          "local-host/host-storage-release-candidate-0003")
PARENT = "/usr/local/libexec"
NAME = "cal-host-storage-release-0003"
FILES = {
    "release.py": ("59f05a264b6f2ea068062ec44c32a730aa70b03528651ddf8f9c17f52e9644e3", 0o500),
    "runtime-pins.json": ("69a086a7d8ad7aa6eee2733bedd67b512902612c4e045e76869e123c49bfd5af", 0o400),
}
INTERPRETER_SHA256 = "52e0a13e60a981d8c4b6478be2ba5176f69da07948a056bf49cf6f077e30cb41"
ANCESTORS = {
    "/": (2096, 2, 0, 0, 0o755, 82),
    "/usr": (2096, 65537, 0, 0, 0o755, 82),
    "/usr/local": (2096, 15982, 0, 0, 0o755, 82),
    PARENT: (2096, 15990, 0, 0, 0o755, 82),
}
O_DIR = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
O_NEW = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC


class Refused(RuntimeError):
    pass


def mount_id(fd):
    with open(f"/proc/self/fdinfo/{fd}", encoding="ascii") as stream:
        rows = [row.partition(":")[2].strip() for row in stream if row.startswith("mnt_id:")]
    if len(rows) != 1 or not rows[0].isdecimal():
        raise Refused("MOUNT_ID_UNKNOWN")
    return int(rows[0])


def checked_dir(fd, expected):
    item = os.fstat(fd)
    actual = (item.st_dev, item.st_ino, item.st_uid, item.st_gid,
              stat.S_IMODE(item.st_mode), mount_id(fd))
    if not stat.S_ISDIR(item.st_mode) or actual != expected:
        raise Refused("ANCESTOR_PREIMAGE_CHANGED")
    for attr in ("system.posix_acl_access", "system.posix_acl_default"):
        try:
            os.getxattr(fd, attr)
        except OSError as exc:
            if exc.errno == errno.ENODATA:
                continue
            raise Refused("ACL_UNKNOWN") from exc
        raise Refused("ACL_PRESENT")


def opened_ancestry():
    held = []
    try:
        fd = os.open("/", O_DIR)
        held.append(fd)
        checked_dir(fd, ANCESTORS["/"])
        for name, path in (("usr", "/usr"), ("local", "/usr/local"),
                           ("libexec", PARENT)):
            fd = os.open(name, O_DIR, dir_fd=fd)
            held.append(fd)
            checked_dir(fd, ANCESTORS[path])
        for parent, name, child in zip(held, ("usr", "local", "libexec"), held[1:]):
            actual = os.stat(name, dir_fd=parent, follow_symlinks=False)
            held_stat = os.fstat(child)
            if (actual.st_dev, actual.st_ino) != (held_stat.st_dev, held_stat.st_ino):
                raise Refused("ANCESTOR_NAME_CHANGED")
        try:
            os.stat(NAME, dir_fd=held[-1], follow_symlinks=False)
        except FileNotFoundError:
            return held
        raise Refused("ONE_SHOT_PACKAGE_NAME_CONSUMED")
    except BaseException:
        for handle in reversed(held):
            os.close(handle)
        raise


def read_source(name, expected):
    fd = os.open(os.path.join(SOURCE, name), os.O_RDONLY | os.O_NOFOLLOW |
                 os.O_CLOEXEC | os.O_NOATIME)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise Refused("SOURCE_IDENTITY_UNKNOWN")
        data = bytearray()
        while piece := os.read(fd, 65536):
            data.extend(piece)
        after = os.fstat(fd)
        if ((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns,
             before.st_ctime_ns, before.st_atime_ns) !=
            (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns,
             after.st_ctime_ns, after.st_atime_ns)):
            raise Refused("SOURCE_CHANGED_DURING_READ")
        if hashlib.sha256(data).hexdigest() != expected:
            raise Refused("SOURCE_HASH_CHANGED")
        return bytes(data)
    finally:
        os.close(fd)


def verify_interpreter():
    fd = os.open("/usr/bin/python3.14", os.O_RDONLY | os.O_NOFOLLOW |
                 os.O_CLOEXEC | os.O_NOATIME)
    try:
        value = os.fstat(fd)
        if not stat.S_ISREG(value.st_mode) or value.st_uid != 0 or value.st_gid != 0:
            raise Refused("INTERPRETER_IDENTITY_UNKNOWN")
        digest = hashlib.sha256()
        while piece := os.read(fd, 65536):
            digest.update(piece)
        if digest.hexdigest() != INTERPRETER_SHA256:
            raise Refused("INTERPRETER_HASH_CHANGED")
    finally:
        os.close(fd)


def verify_runtime_closure(payload):
    if sys.path != ["/usr/lib/python314.zip", "/usr/lib/python3.14",
                    "/usr/lib/python3.14/lib-dynload"]:
        raise Refused("IMPORT_PATH_CHANGED")
    pins = json.loads(payload)
    if pins.get("schema") != "cal-python314-isolated-runtime-pins/v1":
        raise Refused("RUNTIME_PINS_SCHEMA")
    entries = pins.get("files")
    if not isinstance(entries, dict) or not entries:
        raise Refused("RUNTIME_PINS_EMPTY")
    for path, expected in entries.items():
        if (not isinstance(path, str) or not path.startswith("/usr/lib/")
                or not isinstance(expected, str)
                or not re.fullmatch(r"[0-9a-f]{64}", expected)):
            raise Refused("RUNTIME_PIN_INVALID")
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC |
                     os.O_NOATIME)
        try:
            before = os.fstat(fd)
            if not stat.S_ISREG(before.st_mode) or before.st_uid != 0 or before.st_gid != 0:
                raise Refused("RUNTIME_FILE_UNTRUSTED")
            digest = hashlib.sha256()
            while piece := os.read(fd, 65536):
                digest.update(piece)
            after = os.fstat(fd)
            if ((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns,
                 before.st_ctime_ns, before.st_atime_ns) !=
                (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns,
                 after.st_ctime_ns, after.st_atime_ns)):
                raise Refused("RUNTIME_FILE_CHANGED_DURING_READ")
            if digest.hexdigest() != expected:
                raise Refused("RUNTIME_FILE_HASH_CHANGED")
        finally:
            os.close(fd)
    for module in list(sys.modules.values()):
        if module is sys.modules[__name__]:
            continue
        for attribute in ("__file__", "__cached__"):
            path = getattr(module, attribute, None)
            if path and os.path.isfile(path):
                real = os.path.realpath(path)
                if not real.startswith("/usr/lib/") or real not in entries:
                    raise Refused("UNPINNED_IMPORTED_MODULE")


def linked(parent, name, held, mode):
    named = os.stat(name, dir_fd=parent, follow_symlinks=False)
    value = os.fstat(held)
    if (not stat.S_ISDIR(named.st_mode) or
        (named.st_dev, named.st_ino) != (value.st_dev, value.st_ino) or
        value.st_uid != 0 or value.st_gid != 0 or value.st_nlink < 2 or
        stat.S_IMODE(value.st_mode) != mode or mount_id(held) != ANCESTORS[PARENT][5]):
        raise Refused("PACKAGE_LINK_CHANGED")


def install():
    if os.getuid() != 0 or os.geteuid() != 0 or os.getgid() != 0 or os.getegid() != 0:
        raise Refused("ROOT_REQUIRED")
    if (os.path.realpath(sys.executable) != "/usr/bin/python3.14" or
        not sys.flags.isolated or not sys.flags.no_site or
        not sys.flags.dont_write_bytecode or not sys.flags.ignore_environment):
        raise Refused("ISOLATED_PYTHON_REQUIRED")
    verify_interpreter()
    payloads = {name: read_source(name, digest) for name, (digest, _) in FILES.items()}
    verify_runtime_closure(payloads["runtime-pins.json"])
    held = opened_ancestry()
    package = None
    prior_umask = os.umask(0o077)
    try:
        for handle, path in zip(held, ANCESTORS):
            checked_dir(handle, ANCESTORS[path])
        os.mkdir(NAME, 0o700, dir_fd=held[-1])
        os.fsync(held[-1])
        package = os.open(NAME, O_DIR, dir_fd=held[-1])
        linked(held[-1], NAME, package, 0o700)
        for name, (digest, mode) in FILES.items():
            fd = os.open(name, O_NEW, mode, dir_fd=package)
            try:
                data = payloads[name]
                if os.write(fd, data) != len(data):
                    raise Refused("SHORT_WRITE")
                os.fsync(fd)
                value = os.fstat(fd)
                if (not stat.S_ISREG(value.st_mode) or value.st_uid != 0 or
                    value.st_gid != 0 or value.st_nlink != 1 or
                    stat.S_IMODE(value.st_mode) != mode):
                    raise Refused("INSTALLED_FILE_IDENTITY_UNKNOWN")
            finally:
                os.close(fd)
            os.fsync(package)
        if set(os.listdir(package)) != set(FILES):
            raise Refused("PACKAGE_ENTRIES_CHANGED")
        linked(held[-1], NAME, package, 0o700)
        for name, (digest, mode) in FILES.items():
            fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC |
                         os.O_NOATIME, dir_fd=package)
            try:
                value = os.fstat(fd)
                named = os.stat(name, dir_fd=package, follow_symlinks=False)
                if ((named.st_dev, named.st_ino) != (value.st_dev, value.st_ino) or
                    value.st_uid != 0 or value.st_gid != 0 or value.st_nlink != 1 or
                    stat.S_IMODE(value.st_mode) != mode or
                    hashlib.sha256(os.read(fd, len(payloads[name]) + 1)).hexdigest() != digest):
                    raise Refused("INSTALLED_FILE_CHANGED")
            finally:
                os.close(fd)
        for handle, path in zip(held, ANCESTORS):
            checked_dir(handle, ANCESTORS[path])
        linked(held[-1], NAME, package, 0o700)
        return {"status": "CODE_INSTALLED_REVIEW_RECEIPT_ABSENT", "path": PARENT + "/" + NAME}
    finally:
        if package is not None:
            os.close(package)
        for handle in reversed(held):
            os.close(handle)
        os.umask(prior_umask)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--plan", action="store_true")
    actions.add_argument("--install-code-one-shot", action="store_true")
    args = parser.parse_args()
    try:
        if args.install_code_one_shot:
            result = install()
        else:
            held = opened_ancestry()
            for handle in reversed(held):
                os.close(handle)
            result = {"status": "ABSENT_PACKAGE_PREFLIGHT_ONLY", "source_hashes": FILES,
                      "effect": "none"}
        print(json.dumps(result, sort_keys=True))
        return 0
    except (OSError, Refused) as exc:
        print("REFUSED:" + str(exc), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
