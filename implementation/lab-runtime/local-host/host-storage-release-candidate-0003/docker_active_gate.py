"""Synthetic receipt gate in a no-host-bind Docker tmpfs; stdin execution only."""

import hashlib
import importlib.util
import json
import os
import sys


path = "/usr/local/libexec/cal-host-storage-release-0003/release.py"
spec = importlib.util.spec_from_file_location("release", path)
release = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = release
spec.loader.exec_module(release)


def pin(name):
    fd = os.open(name, release.O_DIR)
    try:
        value = os.fstat(fd)
        return (value.st_dev, value.st_ino, value.st_uid, value.st_gid,
                value.st_mode & 0o777, release._mount_id(fd))
    finally:
        os.close(fd)


rows = release._mount_rows()
lib_mount = pin("/var/lib")[5]
selected = [row for row in rows if row["id"] == lib_mount]
if len(selected) != 1 or selected[0]["point"] != "/var/lib" or selected[0]["fstype"] != "tmpfs":
    raise SystemExit("DOCKER_TMPFS_REQUIRED")
release.LIVE = release.HostPins({name: pin(name) for name in ("/", "/var", "/var/lib")},
                                selected[0]["source"], selected[0]["fstype"])
release._deployed_code()
# This disposable image has different .pyc bytes from WSL. Build a container-only
# pin set, preserving the selected path set, before exercising the receipt gate.
with open(release.RUNTIME_PINS, encoding="utf-8") as stream:
    runtime_pins = json.load(stream)
for module in list(sys.modules.values()):
    for attr in ("__file__", "__cached__"):
        candidate = getattr(module, attr, None)
        if candidate and os.path.isfile(candidate):
            resolved = os.path.realpath(candidate)
            if resolved.startswith("/usr/lib/"):
                runtime_pins["files"][resolved] = release._sha_file(resolved)
runtime_pins["files"] = {name: release._sha_file(name)
                         for name in runtime_pins["files"]}
os.chmod(release.RUNTIME_PINS, 0o600)
with open(release.RUNTIME_PINS, "wb") as stream:
    stream.write(release._canonical(runtime_pins))
    stream.flush()
    os.fsync(stream.fileno())
os.chmod(release.RUNTIME_PINS, 0o400)
receipt = {"schema": "cal-host-storage-reviewed-receipt/v1",
           "verdict": "PASS_FOR_ONE_SHOT_STORAGE_ONLY",
           "release_sha256": release._sha_file(path),
           "runtime_pins_sha256": release._sha_file(release.RUNTIME_PINS),
           "target": release.TARGET,
           "preimage_sha256": hashlib.sha256(release._canonical({
               "ancestors": release.LIVE.ancestors, "source": release.LIVE.primary_source,
               "fstype": release.LIVE.primary_fstype})).hexdigest(),
           "reviewer": "SYNTHETIC_DOCKER_TEST_ONLY"}
def create_receipt(body):
    payload = release._canonical(body)
    fd = os.open(release.RECEIPT, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                 os.O_NOFOLLOW, 0o400)
    try:
        if os.write(fd, payload) != len(payload):
            raise AssertionError("short synthetic receipt write")
        os.fsync(fd)
    finally:
        os.close(fd)
    return hashlib.sha256(payload).hexdigest()


for invalid_reviewer in (None, "", 0, "../spoof"):
    invalid = dict(receipt)
    if invalid_reviewer is None:
        del invalid["reviewer"]
    else:
        invalid["reviewer"] = invalid_reviewer
    invalid_sha = create_receipt(invalid)
    try:
        release._reviewed_receipt(invalid_sha)
    except release.Refused as exc:
        if str(exc) != "REVIEW_RECEIPT_SCOPE_REFUSED":
            raise
    else:
        raise AssertionError("invalid reviewer accepted")
    os.unlink(release.RECEIPT)

receipt_sha = create_receipt(receipt)
try:
    release._reviewed_receipt(receipt_sha)
except release.Refused:
    with open(release.RUNTIME_PINS, encoding="utf-8") as stream:
        installed_pins = json.load(stream)["files"]
    for module in list(sys.modules.values()):
        for attr in ("__file__", "__cached__"):
            candidate = getattr(module, attr, None)
            if candidate and os.path.isfile(candidate):
                resolved = os.path.realpath(candidate)
                if resolved != release.DEPLOYED and (not resolved.startswith("/usr/lib/")
                                                     or resolved not in installed_pins):
                    print("DOCKER_UNPINNED_IMPORTED_MODULE", resolved)
    raise
print(json.dumps({"verdict": "PASS_SYNTHETIC_DOCKER_RECEIPT_GATE_ONLY",
                  "rejected_reviewer_cases": 4,
                  "receipt_sha256": receipt_sha}, sort_keys=True))
