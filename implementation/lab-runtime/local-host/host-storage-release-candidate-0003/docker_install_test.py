"""Disposable container-only code-install transaction test; never host-bind."""

import importlib.util
import hashlib
import json
import os
import stat
import sys


path = "/tmp/candidate/install_code.py"
spec = importlib.util.spec_from_file_location("installer", path)
installer = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = installer
spec.loader.exec_module(installer)
installer.SOURCE = "/tmp/candidate"


def pin(path):
    fd = os.open(path, installer.O_DIR)
    try:
        value = os.fstat(fd)
        return (value.st_dev, value.st_ino, value.st_uid, value.st_gid,
                stat.S_IMODE(value.st_mode), installer.mount_id(fd))
    finally:
        os.close(fd)


installer.ANCESTORS = {path: pin(path) for path in installer.ANCESTORS}
sys.modules["__main__"].__file__ = "<stdin>"  # actual installer launch is verified stdin
# The image has different pyc bytes; bind a test-only root-runtime pin payload.
pins_path = installer.SOURCE + "/runtime-pins.json"
with open(pins_path, encoding="utf-8") as stream:
    pins = json.load(stream)
for module in list(sys.modules.values()):
    for attr in ("__file__", "__cached__"):
        candidate = getattr(module, attr, None)
        if candidate and os.path.isfile(candidate):
            resolved = os.path.realpath(candidate)
            if resolved.startswith("/usr/lib/"):
                pins["files"][resolved] = ""
pins["files"] = {name: hashlib.sha256(open(name, "rb").read()).hexdigest()
                 for name in pins["files"]}
with open(pins_path, "w", encoding="utf-8") as stream:
    json.dump(pins, stream, sort_keys=True)
    stream.write("\n")
    stream.flush()
    os.fsync(stream.fileno())
digest = hashlib.sha256(open(pins_path, "rb").read()).hexdigest()
installer.FILES["runtime-pins.json"] = (digest, 0o400)
assert not os.path.lexists(installer.PARENT + "/" + installer.NAME)
good_payload = open(pins_path, "rb").read()
bad_pins = json.loads(good_payload)
first_path = next(iter(bad_pins["files"]))
bad_pins["files"][first_path] = "0" * 64
with open(pins_path, "w", encoding="utf-8") as stream:
    json.dump(bad_pins, stream, sort_keys=True)
    stream.write("\n")
installer.FILES["runtime-pins.json"] = (
    hashlib.sha256(open(pins_path, "rb").read()).hexdigest(), 0o400)
try:
    installer.install()
except installer.Refused as exc:
    assert str(exc) == "RUNTIME_FILE_HASH_CHANGED"
else:
    raise AssertionError("mismatched runtime accepted")
assert not os.path.lexists(installer.PARENT + "/" + installer.NAME)
with open(pins_path, "wb") as stream:
    stream.write(good_payload)
installer.FILES["runtime-pins.json"] = (digest, 0o400)
try:
    result = installer.install()
except installer.Refused:
    for module in list(sys.modules.values()):
        if module is sys.modules[installer.__name__]:
            continue
        for attr in ("__file__", "__cached__"):
            candidate = getattr(module, attr, None)
            if candidate and os.path.isfile(candidate):
                resolved = os.path.realpath(candidate)
                if not resolved.startswith("/usr/lib/") or resolved not in pins["files"]:
                    print("DOCKER_INSTALL_UNPINNED", resolved)
    raise
assert result["status"] == "CODE_INSTALLED_REVIEW_RECEIPT_ABSENT"
for name, (digest, mode) in installer.FILES.items():
    installed = installer.PARENT + "/" + installer.NAME + "/" + name
    assert stat.S_IMODE(os.lstat(installed).st_mode) == mode
    assert installer.read_source(name, digest) == open(installed, "rb").read()
try:
    installer.install()
except installer.Refused as exc:
    assert str(exc) == "ONE_SHOT_PACKAGE_NAME_CONSUMED"
else:
    raise AssertionError("replay accepted")
print(json.dumps({"verdict": "PASS_DISPOSABLE_CONTAINER_CODE_INSTALL_ONLY",
                  "files": sorted(installer.FILES)}, sort_keys=True))
