"""Synthetic sole writer in a dedicated Docker PID/mount namespace."""

import errno
import fcntl
import hashlib
import json
import os
import stat
import sys
import time


run_id, volume_token, dev_text, ino_text = sys.argv[1:5]
volume_identity = (int(dev_text), int(ino_text))
instance_name = "run-" + run_id
root = "/lab"
instances = root + "/instances"
if (os.getuid(), os.geteuid(), os.getgid(), os.getegid()) != (20001, 20001, 20001, 20001):
    raise SystemExit("SERVICE_ID_REQUIRED")
root_stat = os.stat(root, follow_symlinks=False)
parent_stat = os.stat(instances, follow_symlinks=False)
if ((root_stat.st_dev, root_stat.st_ino) != volume_identity
        or root_stat.st_uid != 0 or root_stat.st_gid != 0
        or stat.S_IMODE(root_stat.st_mode) & 0o022
        or parent_stat.st_uid != 20001 or parent_stat.st_gid != 20001
        or stat.S_IMODE(parent_stat.st_mode) != 0o700):
    raise SystemExit("VOLUME_IDENTITY_CHANGED")
with open(root + "/.volume-token", "rb") as stream:
    token_body = stream.read(1024)
if json.loads(token_body) != {"schema": "cal-docker-source8-probe/v1",
                              "run_id": run_id, "volume_token": volume_token}:
    raise SystemExit("VOLUME_TOKEN_CHANGED")
parent_fd = os.open(instances, os.O_RDONLY | os.O_DIRECTORY |
                    os.O_NOFOLLOW | os.O_CLOEXEC)
lock_fd = os.open(".slot-lock", os.O_RDONLY | os.O_NOFOLLOW |
                  os.O_CLOEXEC, dir_fd=parent_fd)
try:
    fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    lock = os.fstat(lock_fd)
    named_lock = os.stat(".slot-lock", dir_fd=parent_fd, follow_symlinks=False)
    if ((lock.st_dev, lock.st_ino) != (named_lock.st_dev, named_lock.st_ino)
            or lock.st_uid != 20001 or stat.S_IMODE(lock.st_mode) != 0o600):
        raise SystemExit("SLOT_LOCK_CHANGED")
    try:
        os.stat(instance_name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        pass
    else:
        raise SystemExit("ONE_SHOT_NAME_CONSUMED")
    prior_umask = os.umask(0o077)
    try:
        os.mkdir(instance_name, 0o700, dir_fd=parent_fd)
    finally:
        os.umask(prior_umask)
    created = os.stat(instance_name, dir_fd=parent_fd, follow_symlinks=False)
    print(json.dumps({"event": "GAP_READY", "run_id": run_id,
                      "instance_dev": created.st_dev,
                      "instance_ino": created.st_ino}, sort_keys=True), flush=True)
    time.sleep(35)
    child_fd = os.open(instance_name, os.O_RDONLY | os.O_DIRECTORY |
                       os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=parent_fd)
    try:
        held = os.fstat(child_fd)
        named = os.stat(instance_name, dir_fd=parent_fd, follow_symlinks=False)
        if ((held.st_dev, held.st_ino) != (created.st_dev, created.st_ino)
                or (named.st_dev, named.st_ino) != (held.st_dev, held.st_ino)
                or held.st_uid != 20001 or stat.S_IMODE(held.st_mode) != 0o700):
            raise SystemExit("FIRST_OPEN_IDENTITY_CHANGED")
        payload = (json.dumps({"public_probe": True, "run_id": run_id},
                              sort_keys=True, separators=(",", ":")) + "\n").encode()
        out_fd = os.open("public-probe.json", os.O_WRONLY | os.O_CREAT |
                         os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                         0o600, dir_fd=child_fd)
        try:
            if os.write(out_fd, payload) != len(payload):
                raise SystemExit("SHORT_PUBLIC_WRITE")
            os.fsync(out_fd)
        finally:
            os.close(out_fd)
        os.fsync(child_fd)
        os.fsync(parent_fd)
        after = os.stat(instance_name, dir_fd=parent_fd, follow_symlinks=False)
        if (after.st_dev, after.st_ino) != (held.st_dev, held.st_ino):
            raise SystemExit("FINAL_INSTANCE_NAME_CHANGED")
        if os.stat(instances, follow_symlinks=False).st_ino != parent_stat.st_ino:
            raise SystemExit("PARENT_LINK_CHANGED")
        print(json.dumps({"event": "WRITER_DONE", "run_id": run_id,
                          "instance_dev": held.st_dev, "instance_ino": held.st_ino,
                          "payload_sha256": hashlib.sha256(payload).hexdigest(),
                          "lock_dev": lock.st_dev, "lock_ino": lock.st_ino},
                         sort_keys=True), flush=True)
    finally:
        os.close(child_fd)
finally:
    os.close(lock_fd)
    os.close(parent_fd)
