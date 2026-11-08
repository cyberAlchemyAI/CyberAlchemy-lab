"""Synthetic same-UID interposition probes in separate Docker containers."""

import errno
import json
import os
import sys


run_id, mode = sys.argv[1:3]
if (os.getuid(), os.geteuid(), os.getgid(), os.getegid()) != (20001, 20001, 20001, 20001):
    raise SystemExit("ATTACKER_ID_CHANGED")
parent = "/lab/instances"
child = parent + "/run-" + run_id
if mode == "rw_counterexample":
    child = parent + "/not-present-" + run_id
results = {}
for name, action in (
    ("rename", lambda: os.rename(child, parent + "/stolen-" + run_id)),
    ("create_sibling", lambda: os.mkdir(parent + "/rogue-" + run_id, 0o700)),
):
    try:
        action()
    except OSError as exc:
        results[name] = exc.errno
    else:
        results[name] = 0
if mode == "readonly" and results != {"rename": errno.EROFS,
                                     "create_sibling": errno.EROFS}:
    raise SystemExit("READONLY_MOUNT_DID_NOT_DENY " + repr(results))
if mode == "no_mount" and results != {"rename": errno.ENOENT,
                                     "create_sibling": errno.ENOENT}:
    raise SystemExit("ABSENT_MOUNT_DID_NOT_DENY " + repr(results))
if mode == "rw_counterexample" and results != {"rename": errno.ENOENT,
                                               "create_sibling": 0}:
    raise SystemExit("RW_COUNTEREXAMPLE_CHANGED " + repr(results))
print(json.dumps({"event": "ATTACK_RESULT", "run_id": run_id,
                  "mode": mode, "syscalls": results}, sort_keys=True), flush=True)
