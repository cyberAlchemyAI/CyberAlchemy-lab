"""Disposable cgroup-v2 mechanism oracle; not a protected host admission.

Run only inside a uniquely named, delegated user systemd scope. It creates two
child cgroups, then kills and reaps only processes it forked into its attempt.
"""
import ctypes
import json
import os
from pathlib import Path
import re
import select
import sys
import time


def read(path):
    return path.read_text().strip()


def write(path, value):
    with path.open("w") as handle:
        handle.write(value)


def populated(group):
    return dict(line.split() for line in read(group / "cgroup.events").splitlines())["populated"] == "1"


def wait_pipe(fd, seconds=5):
    ready, _, _ = select.select([fd], [], [], seconds)
    if not ready:
        raise RuntimeError("child readiness timeout")
    value = os.read(fd, 256)
    if not value:
        raise RuntimeError("child readiness missing")
    return value


def wait_empty(group, seconds=5):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if not populated(group):
            return True
        time.sleep(0.02)
    return False


def main():
    if len(sys.argv) != 2 or not re.fullmatch(r"cal-lcu0302-oracle-[0-9]{8}-[0-9a-f]{8}\.scope", sys.argv[1]):
        raise RuntimeError("exact disposable scope name required")
    unit = sys.argv[1]
    relative = Path(read(Path("/proc/self/cgroup")).split("::", 1)[1])
    expected = Path("/user.slice/user-1000.slice/user@1000.service/app.slice") / unit
    if relative != expected or os.getuid() != 1000:
        raise RuntimeError("not inside selected delegated user scope")
    root = Path("/sys/fs/cgroup") / relative.relative_to("/")
    if root.stat().st_uid != os.getuid() or read(root / "cgroup.type") != "domain":
        raise RuntimeError("scope custody/type")
    if {p.name for p in root.iterdir() if p.is_dir()} or read(root / "cgroup.procs") != str(os.getpid()):
        raise RuntimeError("scope is not exclusively occupied")
    if not {"cpu", "memory", "pids"}.issubset(read(root / "cgroup.controllers").split()):
        raise RuntimeError("required controllers not delegated")
    if read(root / "cgroup.subtree_control"):
        raise RuntimeError("unexpected initial controllers")

    before = {"root": str(root), "root_inode": root.stat().st_ino,
              "root_procs": read(root / "cgroup.procs"),
              "root_controllers": read(root / "cgroup.controllers")}
    broker = root / "broker"
    attempt = root / "attempt"
    child_pid = None
    grandchild_pid = None
    direct_reaped = False
    grandchild_reaped = False
    broker.mkdir(mode=0o700)
    try:
        write(broker / "cgroup.procs", f"{os.getpid()}\n")
        if read(root / "cgroup.procs"):
            raise RuntimeError("scope root remained populated")
        write(root / "cgroup.subtree_control", "+cpu +memory +pids\n")
        attempt.mkdir(mode=0o700)
        write(attempt / "pids.max", "16\n")
        write(attempt / "memory.max", "67108864\n")
        write(attempt / "cpu.max", "100000 100000\n")
        if (read(attempt / "pids.max"), read(attempt / "memory.max"), read(attempt / "cpu.max")) != ("16", "67108864", "100000 100000"):
            raise RuntimeError("attempt limits did not take")
        if ctypes.CDLL(None, use_errno=True).prctl(36, 1, 0, 0, 0) != 0:
            raise RuntimeError("subreaper setup failed")

        ready_r, ready_w = os.pipe()
        start_r, start_w = os.pipe()
        child_pid = os.fork()
        if child_pid == 0:
            try:
                os.close(ready_r)
                os.close(start_w)
                if os.read(start_r, 1) != b"G":
                    os._exit(91)
                grandchild = os.fork()
                if grandchild == 0:
                    os.setsid()
                    os.write(ready_w, f"{os.getpid()} {os.getsid(0)} {os.getpgid(0)}\n".encode())
                    while True:
                        time.sleep(60)
                os._exit(0)
            except BaseException:
                os._exit(92)
        os.close(ready_w)
        os.close(start_r)
        write(attempt / "cgroup.procs", f"{child_pid}\n")
        if read(Path(f"/proc/{child_pid}/cgroup")).split("::", 1)[1] != str(relative / "attempt"):
            raise RuntimeError("child was not attached to exact attempt")
        os.write(start_w, b"G")
        os.close(start_w)
        grandchild_pid, sid, pgid = map(int, wait_pipe(ready_r).split())
        os.close(ready_r)
        if not (grandchild_pid == sid == pgid):
            raise RuntimeError("descendant did not setsid")
        waited, status = os.waitpid(child_pid, 0)
        direct_reaped = True
        if waited != child_pid or status != 0:
            raise RuntimeError("direct child failed")
        if read(Path(f"/proc/{grandchild_pid}/cgroup")).split("::", 1)[1] != str(relative / "attempt"):
            raise RuntimeError("reparented descendant left attempt")
        if os.waitpid(grandchild_pid, os.WNOHANG) != (0, 0):
            raise RuntimeError("descendant not alive/adopted")
        if not populated(attempt):
            raise RuntimeError("direct exit incorrectly emptied group")
        negative = {"direct_child_reaped": True, "setsid_reparented_descendant_alive": True,
                    "attempt_populated_after_direct_reap": True}
        write(attempt / "cgroup.kill", "1\n")
        waited, status = os.waitpid(grandchild_pid, 0)
        grandchild_reaped = waited == grandchild_pid and os.WIFSIGNALED(status) and os.WTERMSIG(status) == 9
        if not grandchild_reaped or not wait_empty(attempt):
            raise RuntimeError("descendant kill/reap/empty failed")
        result = {"schema_version": "lab-lcu0302-disposable-cgroup-oracle/v1",
                  "result": "PASS", "claim": "disposable user-scope cgroup mechanism only",
                  "before": before,
                  "negative": negative,
                  "after": {"attempt_populated": False, "grandchild_reaped_sigkill": True,
                            "direct_child_reaped": True, "limits": {"pids.max": 16, "memory.max": 67108864, "cpu.max": "100000 100000"}}}
    finally:
        if attempt.exists():
            try:
                write(attempt / "cgroup.kill", "1\n")
            except OSError:
                pass
            if child_pid and not direct_reaped:
                try:
                    os.waitpid(child_pid, 0)
                except ChildProcessError:
                    pass
            if grandchild_pid and not grandchild_reaped:
                try:
                    os.waitpid(grandchild_pid, 0)
                except ChildProcessError:
                    pass
            if not wait_empty(attempt):
                raise RuntimeError("attempt still populated during cleanup")
            attempt.rmdir()
        if read(root / "cgroup.subtree_control"):
            write(root / "cgroup.subtree_control", "-cpu -memory -pids\n")
        write(root / "cgroup.procs", f"{os.getpid()}\n")
        broker.rmdir()
    result["after"].update({"attempt_removed": not attempt.exists(), "broker_removed": not broker.exists(),
                            "scope_root_procs": read(root / "cgroup.procs")})
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
