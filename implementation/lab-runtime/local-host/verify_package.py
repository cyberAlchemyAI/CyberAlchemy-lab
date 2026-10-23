#!/usr/bin/env python3
"""Refuse missing, changed, or extra image inputs before starting a fixture."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import sys


class PackageRefused(ValueError):
    pass


def require(ok: bool, code: str) -> None:
    if not ok:
        raise PackageRefused(code)


def path_of(root: Path, name: str) -> Path:
    value = PurePosixPath(name)
    require(type(name) is str and name and not value.is_absolute() and
            value.as_posix() == name and all(p not in ("", ".", "..") for p in value.parts),
            "INVALID_PATH")
    return root.joinpath(*value.parts)


def verify(workspace: Path, manifest_path: Path, build_inputs: Path | None = None) -> None:
    raw = manifest_path.read_bytes()
    def no_duplicates(rows):
        result = {}
        for key, value in rows:
            require(key not in result, "DUPLICATE_MANIFEST_KEY")
            result[key] = value
        return result
    manifest = json.loads(raw, object_pairs_hook=no_duplicates)
    require(type(manifest) is dict and manifest.get("schema") ==
            "lab-local-image-source-manifest/v1", "INVALID_MANIFEST")
    require(set(manifest) == {"schema", "materials", "runtime_code", "build_inputs",
                              "namespace_only", "epoch_inventory", "snapshot_digest",
                              "builder_sha256"}, "INVALID_MANIFEST")
    require(type(manifest["build_inputs"]) is dict and
            set(manifest["build_inputs"]) ==
            {"Dockerfile", "requirements.lock", "compose.yaml", "run-local-product.sh"},
            "INVALID_BUILD_INPUTS")
    if build_inputs is None:
        build_inputs = manifest_path.parent
    for name, sha in sorted(manifest["build_inputs"].items()):
        require(type(sha) is str and len(sha) == 64, "INVALID_BUILD_DIGEST:" + name)
        path = path_of(build_inputs, name)
        item = path.lstat()
        expected_mode = 0o755 if name.endswith(".sh") else 0o644
        require(stat.S_ISREG(item.st_mode) and item.st_mode & 0o777 == expected_mode
                and item.st_nlink == 1, "UNSAFE_BUILD_INPUT:" + name)
        require(hashlib.sha256(path.read_bytes()).hexdigest() == sha,
                "CHANGED_BUILD_INPUT:" + name)
    expected = dict(manifest["materials"])
    expected.update(manifest["runtime_code"])
    empty = hashlib.sha256(b"").hexdigest()
    for name in manifest["namespace_only"]:
        require(name not in expected, "DUPLICATE_PACKAGE_PATH")
        expected[name] = empty
    require(len(expected) == len(manifest["materials"]) +
            len(manifest["runtime_code"]) + len(manifest["namespace_only"]),
            "DUPLICATE_PACKAGE_PATH")
    found = set()
    for directory, directories, files in os.walk(workspace, followlinks=False):
        base = Path(directory)
        for name in directories:
            require(not (base / name).is_symlink(), "PACKAGE_SYMLINK")
        for name in files:
            path = base / name
            relative = path.relative_to(workspace).as_posix()
            require(relative in expected, "EXTRA_PACKAGE_FILE:" + relative)
            found.add(relative)
    require(found == set(expected), "MISSING_PACKAGE_FILE")
    for name, sha in sorted(expected.items()):
        path = path_of(workspace, name)
        item = path.lstat()
        require(stat.S_ISREG(item.st_mode) and item.st_mode & 0o777 == 0o644
                and item.st_nlink == 1, "UNSAFE_PACKAGE_FILE:" + name)
        require(hashlib.sha256(path.read_bytes()).hexdigest() == sha,
                "CHANGED_PACKAGE_BYTE:" + name)
    current_inventory = {
        "admission_bundles": sorted(p.relative_to(workspace).as_posix()
                                    for p in workspace.glob("authority/admissions/*/v*/bundle.json")),
        "recorded_decisions": sorted(p.relative_to(workspace).as_posix()
                                     for p in workspace.glob("docs/decisions/*/decision.json")),
    }
    require(current_inventory == manifest["epoch_inventory"], "PACKAGE_EPOCH_INVENTORY")


def main() -> int:
    try:
        if sys.argv[1:2] == ["--verify-context"]:
            require(len(sys.argv) == 3, "INVALID_CONTEXT_COMMAND")
            context = Path(sys.argv[2])
            verify(context / "workspace", context / "package-manifest.json", context)
            return 0
        require("--" in sys.argv[1:], "MISSING_COMMAND")
        separator = sys.argv.index("--")
        command = sys.argv[separator + 1:]
        require(command and command[0] == "python" and command[1:3] == ["-B", "implementation/lab-runtime/local-host/chain-fixture/chain.py"] or
                command and command[0] == "python" and command[1:3] == ["-B", "implementation/lab-runtime/local-product/run.py"],
                "UNEXPECTED_COMMAND")
        verify(Path("/workspace"), Path("/package-manifest.json"), Path("/build-inputs"))
        os.execvp(command[0], command)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("PACKAGE_REFUSED:" + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
