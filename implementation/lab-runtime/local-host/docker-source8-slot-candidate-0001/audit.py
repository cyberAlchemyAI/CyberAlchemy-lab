"""Read-only synthetic volume audit before resource cleanup."""

import hashlib
import json
import os
import stat
import sys


run_id, volume_token = sys.argv[1:3]
root = "/lab"
instances = root + "/instances"
family = instances + "/run-" + run_id
rogue = instances + "/rogue-" + run_id
if set(os.listdir(root)) != {".volume-token", "instances"}:
    raise SystemExit("VOLUME_ENTRIES_UNKNOWN")
if set(os.listdir(instances)) != {".slot-lock", "run-" + run_id,
                                 "rogue-" + run_id}:
    raise SystemExit("INSTANCE_ENTRIES_UNKNOWN")
if os.listdir(rogue):
    raise SystemExit("ROGUE_COUNTEREXAMPLE_NOT_EMPTY")
if os.listdir(family) != ["public-probe.json"]:
    raise SystemExit("FAMILY_ENTRIES_UNKNOWN")
with open(root + "/.volume-token", "rb") as stream:
    marker = stream.read()
if json.loads(marker) != {"schema": "cal-docker-source8-probe/v1",
                          "run_id": run_id, "volume_token": volume_token}:
    raise SystemExit("MARKER_CHANGED")
with open(family + "/public-probe.json", "rb") as stream:
    payload = stream.read()
if json.loads(payload) != {"public_probe": True, "run_id": run_id}:
    raise SystemExit("PAYLOAD_CHANGED")
for path, owner, mode in ((root + "/.volume-token", 0, 0o444),
                          (instances, 20001, 0o700),
                          (instances + "/.slot-lock", 20001, 0o600),
                          (family, 20001, 0o700),
                          (rogue, 20001, 0o700),
                          (family + "/public-probe.json", 20001, 0o600)):
    item = os.stat(path, follow_symlinks=False)
    if item.st_uid != owner or stat.S_IMODE(item.st_mode) != mode:
        raise SystemExit("AUDIT_IDENTITY_CHANGED " + path)
print(json.dumps({"event": "AUDIT_DONE", "run_id": run_id,
                  "marker_sha256": hashlib.sha256(marker).hexdigest(),
                  "payload_sha256": hashlib.sha256(payload).hexdigest(),
                  "family_ino": os.stat(family, follow_symlinks=False).st_ino,
                  "scope": "SYNTHETIC_ONLY_SAFE_TO_DISCARD"}, sort_keys=True),
      flush=True)
