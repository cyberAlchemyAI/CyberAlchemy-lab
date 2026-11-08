"""Freeze the disjoint v3 engine's executable closure and exact pins."""

import hashlib
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
OLD = ROOT / "product/lab/release-candidates/v1/interface/custody-correction-v4"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binding(path):
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path)}


def write_new(path, value):
    raw = (json.dumps(value, sort_keys=True, indent=2) + "\n").encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(raw)


def main():
    old = json.loads((OLD / "engine-manifest.json").read_bytes())
    files = sorted((p for p in (HERE / "runtime").rglob("*") if p.is_file() and
                    "__pycache__" not in p.parts), key=lambda p: p.as_posix())
    old["files"] = [binding(path) for path in files]
    old["profile_binding"] = binding(HERE / "runtime/profile.json")
    old["changed_files"] = [
        {"candidate_binding": binding(path),
         "parent_binding": binding(OLD / "runtime" / path.relative_to(HERE / "runtime"))
         if (OLD / "runtime" / path.relative_to(HERE / "runtime")).is_file() else None}
        for path in files if not (OLD / "runtime" / path.relative_to(HERE / "runtime")).is_file() or
        sha(path) != sha(OLD / "runtime" / path.relative_to(HERE / "runtime"))]
    write_new(HERE / "engine-manifest.json", old)
    pins = {"manifest_sha256": sha(HERE / "engine-manifest.json"),
            "engine_id": old["engine_id"],
            "mapping_sha256": old["mapping_binding"]["sha256"],
            "profile_sha256": old["profile_binding"]["sha256"],
            "correction_profile_sha256": old["correction_profile_binding"]["sha256"]}
    write_new(HERE / "pins.json", pins)
    print(json.dumps({"manifest_sha256": pins["manifest_sha256"],
                      "profile_sha256": pins["profile_sha256"], "files": len(files)}))


if __name__ == "__main__":
    main()
