"""Run internal storage transaction only in a disposable no-host-bind Docker tmpfs."""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
from unittest import mock


DEPLOYED = Path("/usr/local/libexec/cal-host-storage-release-0003/release.py")
spec = importlib.util.spec_from_file_location("release", DEPLOYED)
release = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = release
spec.loader.exec_module(release)


def pin(path):
    fd = os.open(path, release.O_DIR)
    try:
        value = os.fstat(fd)
        return (value.st_dev, value.st_ino, value.st_uid, value.st_gid,
                value.st_mode & 0o777, release._mount_id(fd))
    finally:
        os.close(fd)


def main():
    if os.geteuid() != 0 or not os.path.ismount("/var/lib"):
        raise SystemExit("ISOLATED_ROOT_TMPFS_REQUIRED")
    if os.path.exists(release.TARGET):
        raise SystemExit("FRESH_TARGET_REQUIRED")
    live_cli = subprocess.run([sys.executable, "-I", "-B", "-S", str(DEPLOYED),
                               "--apply-reviewed-one-shot", "0" * 64],
                              capture_output=True, text=True, check=False)
    if live_cli.returncode != 3 or os.path.exists(release.TARGET):
        raise SystemExit("PINNED_LIVE_CLI_FAILED_TO_REFUSE")
    rows = release._mount_rows()
    lib_id = pin("/var/lib")[5]
    selected = [row for row in rows if row["id"] == lib_id]
    if len(selected) != 1 or selected[0]["point"] != "/var/lib" or selected[0]["fstype"] != "tmpfs":
        raise SystemExit("ISOLATED_TMPFS_MOUNT_REQUIRED")
    pins = release.HostPins({name: pin(name) for name in ("/", "/var", "/var/lib")},
                            selected[0]["source"], selected[0]["fstype"])
    bad_ancestors = dict(pins.ancestors)
    bad_ancestors["/var/lib"] = (bad_ancestors["/var/lib"][0],
                                 bad_ancestors["/var/lib"][1] + 1,
                                 *bad_ancestors["/var/lib"][2:])
    try:
        release._preflight(release.HostPins(bad_ancestors, pins.primary_source,
                                            pins.primary_fstype))
    except release.Refused as error:
        if str(error) != "PINNED_ANCESTOR_CHANGED":
            raise
    else:
        raise SystemExit("WRONG_PREIMAGE_ACCEPTED")
    original_xattr = release.os.getxattr

    def injected_acl(fd, attribute):
        if attribute == "system.posix_acl_access":
            return b"present"
        return original_xattr(fd, attribute)

    with mock.patch.object(release.os, "getxattr", side_effect=injected_acl):
        try:
            release._preflight(pins)
        except release.Refused as error:
            if str(error) != "ACL_PRESENT":
                raise
        else:
            raise SystemExit("ACL_PRESENT_ACCEPTED")
    alias = dict(selected[0], id=999999, point="/tmp/alias", root="/", options=["rw"])
    with mock.patch.object(release, "_mount_rows", return_value=rows + [alias]):
        try:
            release._preflight(pins)
        except release.Refused as error:
            if str(error) != "WRITABLE_ALIAS":
                raise
        else:
            raise SystemExit("WRITABLE_ALIAS_ACCEPTED")
    result = release._apply_storage(pins)
    if result["status"] != "STORAGE_PREPARED_ONLY":
        raise SystemExit("STORAGE_RESULT_UNEXPECTED")
    root = Path(release.TARGET)
    if not (root / release.CLAIM).is_file() or not (root / release.PREPARED).is_file():
        raise SystemExit("RECORDS_MISSING")
    if set(path.name for path in (root / "source8-v1").iterdir()) != {
            "instances", "custody", "retained"}:
        raise SystemExit("STORAGE_SHAPE_CHANGED")
    try:
        release._apply_storage(pins)
    except release.Refused as error:
        if str(error) != "ONE_SHOT_NAME_ALREADY_PRESENT":
            raise
    else:
        raise SystemExit("REPLAY_NOT_REFUSED")
    read_fd, write_fd = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(read_fd)
        os.setgroups([])
        os.setgid(20001)
        os.setuid(20001)
        cases = []
        for name, action in (
            ("rename_top", lambda: os.rename(root, root.with_name("cyberalchemy-alien"))),
            ("create_sibling", lambda: os.mkdir("/var/lib/cyberalchemy-alien")),
            ("read_private_root", lambda: os.listdir(root / "source8-v1")),
        ):
            try:
                action()
                cases.append((name, "UNEXPECTED_SUCCESS"))
            except OSError as error:
                cases.append((name, error.errno))
        os.write(write_fd, json.dumps(cases).encode())
        os.close(write_fd)
        os._exit(0)
    os.close(write_fd)
    cases = json.loads(os.read(read_fd, 4096))
    os.close(read_fd)
    _, status = os.waitpid(pid, 0)
    if not os.WIFEXITED(status) or os.WEXITSTATUS(status) != 0:
        raise SystemExit("HOSTILE_CHILD_FAILED")
    if any(value not in (1, 13) for _, value in cases):
        raise SystemExit("HOSTILE_DENIAL_FAILED " + json.dumps(cases))
    print(json.dumps({"verdict": "PASS_BOUNDED_DOCKER_TMPFS_ONLY",
                      "storage": result, "hostile_cases": cases}, sort_keys=True))


if __name__ == "__main__":
    main()
