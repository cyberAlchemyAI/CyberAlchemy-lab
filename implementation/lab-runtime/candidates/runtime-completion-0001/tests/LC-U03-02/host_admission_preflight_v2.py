"""Read-only LC-U03-02 host admission preflight; never qualifies a runtime.

The disposable cgroup oracle demonstrates mechanics. This preflight prevents
that evidence from being mistaken for selected exclusive host custody. It does
not create cgroups, start processes, signal PIDs, or inspect protected data.
"""
import json
import os
from pathlib import Path
import pwd
import stat
import sys


REQUIRED_CONTROLLERS = frozenset({"cpu", "memory", "pids"})


def snapshot():
    root = Path("/sys/fs/cgroup")
    mounts = Path("/proc/self/mountinfo").read_text().splitlines()
    cgroup2_root = any(" - cgroup2 " in line and line.split()[4] == "/sys/fs/cgroup" for line in mounts)
    membership = Path("/proc/self/cgroup").read_text().strip().splitlines()
    # getpwall is NSS-backed; no local-only or authority claim follows.
    accounts = sorted({entry.pw_uid for entry in pwd.getpwall() if 0 < entry.pw_uid < 65534})
    return {
        "broker_uid": os.getuid(),
        "self_cgroup": membership[0] if len(membership) == 1 else None,
        "cgroup2_root_mounted": cgroup2_root,
        "root_uid": root.stat().st_uid,
        "root_mode": root.stat().st_mode & 0o7777,
        "root_writable_by_current_uid": os.access(root, os.W_OK),
        "controllers": sorted((root / "cgroup.controllers").read_text().split()),
        "nss_observed_account_uids": accounts,
    }


def assess(observation, selection=None):
    reasons = []
    if not observation["cgroup2_root_mounted"]:
        reasons.append("CGROUP2_ROOT_NOT_OBSERVED")
    if not REQUIRED_CONTROLLERS.issubset(observation["controllers"]):
        reasons.append("REQUIRED_CONTROLLERS_NOT_OBSERVED")
    if not isinstance(observation["self_cgroup"], str) or not observation["self_cgroup"].startswith("0::/"):
        reasons.append("UNEXPECTED_CGROUP_MEMBERSHIP")
    if selection is None:
        reasons.append("NO_INDEPENDENT_HOST_SELECTION")
    else:
        if set(selection) != {"broker_uid", "worker_uid", "scope_cgroup", "administrator_binding"}:
            reasons.append("SELECTION_SHAPE")
        else:
            if type(selection["broker_uid"]) is not int or selection["broker_uid"] != observation["broker_uid"]:
                reasons.append("BROKER_UID_MISMATCH")
            if type(selection["worker_uid"]) is not int or selection["worker_uid"] <= 0 or selection["worker_uid"] == observation["broker_uid"]:
                reasons.append("NO_SEPARATE_WORKER_UID")
            elif selection["worker_uid"] not in observation["nss_observed_account_uids"]:
                reasons.append("WORKER_ACCOUNT_NOT_OBSERVED")
            scope = selection["scope_cgroup"]
            if (not isinstance(scope, str) or not scope.startswith("/user.slice/") or
                    not scope.endswith(".scope") or not scope.isascii() or not scope.isprintable() or
                    "\\" in scope or len(scope) > 4096 or
                    any(part in ("", ".", "..") or len(part) > 255 for part in scope[1:].split("/"))):
                reasons.append("SCOPE_NOT_NOMINATED")
            if not isinstance(selection["administrator_binding"], str) or len(selection["administrator_binding"]) != 64 or any(c not in "0123456789abcdef" for c in selection["administrator_binding"]):
                reasons.append("ADMINISTRATOR_BINDING_MISSING")
    return {
        "schema_version": "lab-lcu0302-host-admission-preflight/v1",
        "result": "BLOCKED" if reasons else "SELECTION_SHAPE_ONLY",
        "reasons": reasons,
        "observation": observation,
        "host_qualified": False,
        "effect_state": "none",
        "claim_ceiling": "Read-only observed capability and selection shape only; no delegated-scope custody, worker isolation, clone3 launch, historical-family oracle, or LC-U03-02 acceptance.",
    }


def open_parent_nofollow(path):
    if (type(path) is not str or not path.startswith("/") or "\0" in path or
            len(path) > 4096 or any(part in ("", ".", "..") or len(part) > 255
                                  for part in path[1:].split("/"))):
        raise ValueError("SELECTION_PATH")
    parts = path[1:].split("/")
    fd = os.open("/", os.O_PATH | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        for part in parts[:-1]:
            next_fd = os.open(part, os.O_PATH | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                              dir_fd=fd)
            os.close(fd)
            fd = next_fd
        return fd, parts[-1]
    except BaseException:
        os.close(fd)
        raise


def file_identity(st):
    return (st.st_dev, st.st_ino, st.st_mode, st.st_uid, st.st_gid,
            st.st_size, st.st_mtime_ns, st.st_ctime_ns)


def read_selected_file(path):
    """4096-byte maximum, held no-follow regular file and pre/post attachment."""
    parent_fd, leaf = open_parent_nofollow(path)
    try:
        path_fd = os.open(leaf, os.O_PATH | os.O_NOFOLLOW | os.O_CLOEXEC,
                          dir_fd=parent_fd)
        try:
            before = os.fstat(path_fd)
            if not stat.S_ISREG(before.st_mode):
                raise ValueError("SELECTION_NOT_REGULAR")
            if before.st_size > 4096:
                raise ValueError("SELECTION_TOO_LARGE")
            # Reopen only the held regular inode, never a raced pathname/device.
            fd = os.open(f"/proc/self/fd/{path_fd}", os.O_RDONLY | os.O_NONBLOCK | os.O_CLOEXEC)
            try:
                if file_identity(os.fstat(fd)) != file_identity(before):
                    raise ValueError("SELECTION_CHANGED")
                chunks = []
                count = 0
                while count <= 4096:
                    chunk = os.read(fd, 4097 - count)
                    if not chunk:
                        break
                    chunks.append(chunk)
                    count += len(chunk)
                if count > 4096:
                    raise ValueError("SELECTION_TOO_LARGE")
                if file_identity(os.fstat(fd)) != file_identity(before):
                    raise ValueError("SELECTION_CHANGED")
            finally:
                os.close(fd)
            leaf_fd = os.open(leaf, os.O_PATH | os.O_NOFOLLOW | os.O_CLOEXEC,
                              dir_fd=parent_fd)
            try:
                if file_identity(os.fstat(leaf_fd)) != file_identity(before):
                    raise ValueError("SELECTION_DETACHED")
            finally:
                os.close(leaf_fd)
            reopened_parent, reopened_leaf = open_parent_nofollow(path)
            try:
                if (reopened_leaf != leaf or
                        (os.fstat(parent_fd).st_dev, os.fstat(parent_fd).st_ino) !=
                        (os.fstat(reopened_parent).st_dev, os.fstat(reopened_parent).st_ino)):
                    raise ValueError("SELECTION_PARENT_DETACHED")
            finally:
                os.close(reopened_parent)
            return b"".join(chunks)
        finally:
            os.close(path_fd)
    finally:
        os.close(parent_fd)


def parse_selection(raw):
    def unique_pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("SELECTION_DUPLICATE_KEY")
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=unique_pairs)


def main():
    if len(sys.argv) not in (1, 3) or (len(sys.argv) == 3 and sys.argv[1] != "--selection"):
        raise SystemExit("usage: host_admission_preflight_v2.py [--selection ABSOLUTE_JSON_FILE]")
    selection = None
    if len(sys.argv) == 3:
        try:
            selection = parse_selection(read_selected_file(sys.argv[2]))
        except (OSError, ValueError, UnicodeError) as exc:
            raise SystemExit(f"selection rejected: {type(exc).__name__}") from None
        if not isinstance(selection, dict):
            raise SystemExit("selection must be object")
    print(json.dumps(assess(snapshot(), selection), sort_keys=True))


if __name__ == "__main__":
    main()
