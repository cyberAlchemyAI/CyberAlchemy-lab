#!/usr/bin/env python3
"""Stage only pinned public fixture inputs into a disposable Docker context."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
MANIFEST = HERE / "source-manifest.json"
RELEASE_PIN = HERE / "package-release.json"
PUBLIC_REGISTRY = (
    "authority/admissions/governance-transaction-surface/v1/"
    "registries/definition-registry.json"
)
CANONICAL_REGISTRY = "authority/definitions/registry.json"
EMPTY_SHA = hashlib.sha256(b"").hexdigest()
MAX_FILE = 1 << 20


class PackageRefused(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PackageRefused(message)


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False, allow_nan=False) + "\n").encode()


def safe_relative(name: str) -> Path:
    value = PurePosixPath(name)
    require(type(name) is str and name and not value.is_absolute()
            and value.as_posix() == name and all(p not in ("", ".", "..") for p in value.parts),
            "INVALID_PATH")
    return Path(*value.parts)


def read_regular(root: Path, name: str, *, expected_mode: int) -> bytes:
    relative = safe_relative(name)
    current = root
    for component in relative.parts[:-1]:
        current = current / component
        item = current.lstat()
        require(stat.S_ISDIR(item.st_mode) and not stat.S_ISLNK(item.st_mode), "UNSAFE_PARENT:" + name)
    path = root / relative
    before = path.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_mode & 0o777 == expected_mode
            and before.st_size <= MAX_FILE and before.st_nlink == 1, "UNSAFE_FILE:" + name)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        opened = os.fstat(fd)
        require(stat.S_ISREG(opened.st_mode) and (opened.st_dev, opened.st_ino) ==
                (before.st_dev, before.st_ino) and opened.st_size <= MAX_FILE,
                "FILE_REPLACED:" + name)
        chunks = []
        remaining = MAX_FILE + 1
        while remaining:
            part = os.read(fd, min(65536, remaining))
            if not part:
                break
            chunks.append(part)
            remaining -= len(part)
        raw = b"".join(chunks)
        after = os.fstat(fd)
        require(len(raw) <= MAX_FILE and len(raw) == opened.st_size and
                (after.st_size, after.st_mtime_ns, after.st_ctime_ns) ==
                (opened.st_size, opened.st_mtime_ns, opened.st_ctime_ns),
                "FILE_CHANGED_DURING_READ:" + name)
        return raw
    finally:
        os.close(fd)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def inventory(repo: Path) -> dict[str, list[str]]:
    return {
        "admission_bundles": sorted(p.relative_to(repo).as_posix()
                                    for p in repo.glob("authority/admissions/*/v*/bundle.json")),
        "recorded_decisions": sorted(p.relative_to(repo).as_posix()
                                     for p in repo.glob("docs/decisions/*/decision.json")),
    }


def load_manifest(path: Path) -> dict:
    raw = path.read_bytes()
    try:
        manifest = json.loads(raw)
    except (ValueError, UnicodeError) as error:
        raise PackageRefused("INVALID_MANIFEST") from error
    require(raw == canonical(manifest) and type(manifest) is dict and set(manifest) ==
            {"schema", "materials", "runtime_code", "build_inputs", "namespace_only",
             "epoch_inventory", "snapshot_digest", "builder_sha256"} and
            manifest["schema"] == "lab-local-image-source-manifest/v1", "INVALID_MANIFEST")
    require(type(manifest["materials"]) is dict and type(manifest["runtime_code"]) is dict
            and type(manifest["build_inputs"]) is dict and
            set(manifest["build_inputs"]) ==
            {"Dockerfile", "requirements.lock", "compose.yaml", "run-local-product.sh"}
            and type(manifest["namespace_only"]) is list and
            type(manifest["epoch_inventory"]) is dict, "INVALID_MANIFEST")
    return manifest


def verify_release_pin(manifest: dict) -> None:
    raw = RELEASE_PIN.read_bytes()
    try:
        release = json.loads(raw)
    except (ValueError, UnicodeError) as error:
        raise PackageRefused("INVALID_RELEASE_PIN") from error
    require(raw == canonical(release) and type(release) is dict and
            set(release) == {"schema", "source_manifest_sha256", "build_inputs"} and
            release["schema"] == "lab-local-package-release/v1" and
            release["source_manifest_sha256"] == digest(canonical(manifest)) and
            release["build_inputs"] == manifest["build_inputs"],
            "PACKAGE_RELEASE_CHANGED")


def stage(repo: Path, context: Path, manifest: dict) -> None:
    require(context.is_dir() and not any(context.iterdir()), "CONTEXT_NOT_EMPTY")
    require(inventory(repo) == manifest["epoch_inventory"], "EPOCH_INVENTORY_CHANGED")
    materials = manifest["materials"]
    code = manifest["runtime_code"]
    namespace = manifest["namespace_only"]
    require(type(manifest["builder_sha256"]) is str and
            digest(read_regular(repo, "implementation/lab-runtime/local-host/package_runtime.py",
                                expected_mode=0o644)) == manifest["builder_sha256"],
            "BUILDER_CHANGED")
    require(set(materials).isdisjoint(code) and
            set(namespace).isdisjoint(set(materials) | set(code)) and
            set(namespace) == (set(manifest["epoch_inventory"]["admission_bundles"])
                               | set(manifest["epoch_inventory"]["recorded_decisions"])) - set(materials),
            "MANIFEST_CLOSURE")
    require(materials[CANONICAL_REGISTRY] == materials[PUBLIC_REGISTRY],
            "REGISTRY_PUBLIC_POSTIMAGE_MISMATCH")
    build_files = {}
    for name, expected in sorted(manifest["build_inputs"].items()):
        require(type(expected) is str and len(expected) == 64,
                "INVALID_BUILD_DIGEST:" + name)
        raw = read_regular(HERE, name, expected_mode=0o755 if name.endswith(".sh") else 0o644)
        require(digest(raw) == expected, "BUILD_INPUT_CHANGED:" + name)
        build_files[name] = raw
    files = {}
    for name, expected in sorted({**materials, **code}.items()):
        safe_relative(name)
        require(type(expected) is str and len(expected) == 64, "INVALID_DIGEST:" + name)
        mode = 0o600 if name == CANONICAL_REGISTRY else 0o644
        raw = read_regular(repo, name, expected_mode=mode)
        require(digest(raw) == expected, "CHANGED_BYTE:" + name)
        if name != CANONICAL_REGISTRY:
            files[name] = raw
    # The owner-only canonical lookup is byte-identical to the selected public
    # immutable postimage. Never copy its owner-only host inode into Docker.
    files[CANONICAL_REGISTRY] = files[PUBLIC_REGISTRY]
    for name in namespace:
        safe_relative(name)
        path = repo / name
        item = path.lstat()
        require(stat.S_ISREG(item.st_mode) and item.st_nlink == 1, "NAMESPACE_CHANGED:" + name)
        files[name] = b""  # capture() consumes only the name for these paths.
    require(inventory(repo) == manifest["epoch_inventory"], "EPOCH_INVENTORY_CHANGED")
    for name, raw in sorted(files.items()):
        destination = context / "workspace" / safe_relative(name)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
        destination.chmod(0o644)
    for name, raw in sorted(build_files.items()):
        (context / name).write_bytes(raw)
        (context / name).chmod(0o755 if name.endswith(".sh") else 0o644)
    (context / "package-manifest.json").write_bytes(canonical(manifest))
    (context / ".dockerignore").write_text(
        "*\n!Dockerfile\n!requirements.lock\n!compose.yaml\n!run-local-product.sh\n"
        "!package-manifest.json\n!workspace/\n!workspace/**\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context", required=True, type=Path)
    options = parser.parse_args()
    try:
        manifest = load_manifest(MANIFEST)
        verify_release_pin(manifest)
        stage(REPO, options.context, manifest)
    except (OSError, PackageRefused, KeyError, TypeError) as error:
        print("PACKAGE_REFUSED:" + str(error), file=__import__("sys").stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
