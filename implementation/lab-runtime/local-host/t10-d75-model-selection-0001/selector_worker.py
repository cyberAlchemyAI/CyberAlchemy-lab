#!/usr/bin/env python3
"""Isolated child that runs the original pinned source-profile selector."""
import hashlib
import json
from pathlib import Path
import sys


def main():
    root = Path(sys.argv[1]).resolve(strict=True)
    expected_source = sys.argv[2]
    package = root / "implementation/lab-runtime/candidates/repeatable-operation"
    profile_source = package / "lab_runtime/profiles.py"
    if hashlib.sha256(profile_source.read_bytes()).hexdigest() != expected_source:
        raise ValueError("original selector source changed before import")
    sys.path.insert(0, str(package))
    from lab_runtime import profiles
    if (Path(profiles.__file__).resolve(strict=True) != profile_source or
            Path(profiles.select.__code__.co_filename).resolve(strict=True) != profile_source):
        raise ValueError("wrong original selector module or function origin")
    choices = json.loads(sys.stdin.buffer.read())
    if [item["name"] for item in choices["selections"]] != ["d74", "d75"]:
        raise ValueError("wrong pinned source choices")
    observed = {}
    for item in choices["selections"]:
        kwargs = {key: value for key, value in item.items()
                  if key not in ("name", "source_materials", "source_bytes")}
        selection = profiles.select(root, **kwargs)
        if (selection.profile_sha256 != item["profile_sha256"] or
                selection.profile["expected_cut"] != "decision:00" + item["name"][1:]):
            raise ValueError("selector returned wrong source cut")
        observed[item["name"]] = {
            "profile_sha256": selection.profile_sha256,
            "profile_path": selection.controls["profile"]["path"],
            "profile_id": selection.profile["profile_id"],
            "expected_cut": selection.profile["expected_cut"],
            "executable_manifest_sha256": selection.profile["executable_manifest_sha256"],
            "content_manifest_sha256": selection.controls["content_manifest"]["sha256"],
            "policy_sha256": selection.controls["policy"]["sha256"],
            "review_sha256": selection.controls["selection_review"]["sha256"],
        }
    if hashlib.sha256(profile_source.read_bytes()).hexdigest() != expected_source:
        raise ValueError("original selector source changed after call")
    print(json.dumps(observed, sort_keys=True))


if __name__ == "__main__":
    main()
