"""Disposable Docker-volume initializer. Runs as container root, never on host."""

import hashlib
import json
import os
import stat
import sys


run_id = sys.argv[1]
volume_token = sys.argv[2]
root = "/lab"
before = os.stat(root, follow_symlinks=False)
if not stat.S_ISDIR(before.st_mode) or before.st_uid != 0 or before.st_gid != 0:
    raise SystemExit("VOLUME_ROOT_UNTRUSTED")
if os.listdir(root):
    raise SystemExit("VOLUME_NOT_NEW")
old_umask = os.umask(0o077)
try:
    marker = (json.dumps({"schema": "cal-docker-source8-probe/v1",
                          "run_id": run_id, "volume_token": volume_token},
                         sort_keys=True, separators=(",", ":")) + "\n").encode()
    fd = os.open(root + "/.volume-token", os.O_WRONLY | os.O_CREAT |
                 os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o400)
    try:
        if os.write(fd, marker) != len(marker):
            raise SystemExit("SHORT_MARKER_WRITE")
        os.fsync(fd)
    finally:
        os.close(fd)
    os.chmod(root + "/.volume-token", 0o444)
    os.mkdir(root + "/instances", 0o700)
    lock_fd = os.open(root + "/instances/.slot-lock", os.O_WRONLY |
                      os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    os.close(lock_fd)
    instances_fd = os.open(root + "/instances", os.O_RDONLY |
                           os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.chown(root + "/instances/.slot-lock", 20001, 20001)
        os.chown(root + "/instances", 20001, 20001)
        os.fsync(instances_fd)
    finally:
        os.close(instances_fd)
    root_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(root_fd)
    finally:
        os.close(root_fd)
finally:
    os.umask(old_umask)
after = os.stat(root, follow_symlinks=False)
leaf = os.stat(root + "/instances", follow_symlinks=False)
if ((after.st_dev, after.st_ino) != (before.st_dev, before.st_ino)
        or leaf.st_uid != 20001 or leaf.st_gid != 20001
        or stat.S_IMODE(leaf.st_mode) != 0o700
        or set(os.listdir(root)) != {".volume-token", "instances"}):
    raise SystemExit("INITIALIZED_TREE_CHANGED")
print(json.dumps({"event": "INIT_DONE", "run_id": run_id,
                  "volume_dev": after.st_dev, "volume_ino": after.st_ino,
                  "instances_dev": leaf.st_dev, "instances_ino": leaf.st_ino,
                  "marker_sha256": hashlib.sha256(marker).hexdigest()}, sort_keys=True),
      flush=True)
