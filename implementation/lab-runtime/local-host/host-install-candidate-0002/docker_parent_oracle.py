"""Disposable container oracle for root-owned parent denial only.

Run by run-docker-oracle.sh. No host path is mounted. This is not an installed
WSL namespace, Root/slot, proc/FD, or protected-runtime qualification.
"""

import errno
import json
import os
import tempfile


SERVICE_UID = SERVICE_GID = 20001


def attempt(label, action):
    try:
        action()
        return {"action": label, "result": "UNEXPECTED_SUCCESS"}
    except OSError as error:
        return {"action": label, "result": errno.errorcode.get(error.errno, "UNKNOWN"),
                "errno": error.errno}


def main():
    if os.geteuid() != 0 or not os.path.ismount("/tmp"):
        raise SystemExit("DISPOSABLE_CONTAINER_ROOT_AND_TMPFS_REQUIRED")
    parent = tempfile.mkdtemp(prefix="cal-root-owned-parent-", dir="/tmp")
    os.chmod(parent, 0o700)
    child = os.path.join(parent, "i-selected")
    os.mkdir(child, 0o700)
    held_child = os.open(child, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    os.chown(child, SERVICE_UID, SERVICE_GID)
    root_pid = os.getpid()
    read_fd, write_fd = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(read_fd)
        os.close(held_child)  # no inherited parent/child authority in outsider
        os.setgroups([])
        os.setgid(SERVICE_GID)
        os.setuid(SERVICE_UID)
        with open("/proc/self/status", encoding="utf-8") as status_file:
            cap_eff = next(line.split(":", 1)[1].strip() for line in status_file
                           if line.startswith("CapEff:"))
        if (os.geteuid(), os.getegid(), os.getgroups(), int(cap_eff, 16)) != (
                SERVICE_UID, SERVICE_GID, [], 0):
            os._exit(7)
        cases = [
            attempt("rename_selected_child", lambda: os.rename(child, child + "-moved")),
            attempt("create_sibling", lambda: os.mkdir(os.path.join(parent, "i-alien"))),
            attempt("open_root_parent", lambda: os.open(parent, os.O_RDONLY | os.O_DIRECTORY)),
            attempt("stat_selected_child", lambda: os.stat(child)),
            attempt("open_root_held_child_fd", lambda: os.open(
                f"/proc/{root_pid}/fd/{held_child}", os.O_RDONLY | os.O_DIRECTORY)),
        ]
        os.write(write_fd, json.dumps(cases, sort_keys=True).encode())
        os.close(write_fd)
        os._exit(0)
    os.close(write_fd)
    body = os.read(read_fd, 65536)
    os.close(read_fd)
    _, status = os.waitpid(pid, 0)
    try:
        cases = json.loads(body)
        if not os.WIFEXITED(status) or os.WEXITSTATUS(status) != 0:
            raise SystemExit("HOSTILE_CHILD_FAILED")
        if any(row["result"] not in ("EACCES", "EPERM") for row in cases):
            raise SystemExit("DENIAL_ORACLE_FAILED " + json.dumps(cases, sort_keys=True))
        print(json.dumps({"verdict": "PASS_BOUNDED_CONTAINER_ONLY",
                          "root_parent_mode": "0700", "root_parent_uid": 0,
                          "selected_child_uid": SERVICE_UID,
                          "hostile_uid": SERVICE_UID, "cases": cases}, sort_keys=True))
    finally:
        os.close(held_child)
        os.rmdir(child)
        os.rmdir(parent)


if __name__ == "__main__":
    main()
