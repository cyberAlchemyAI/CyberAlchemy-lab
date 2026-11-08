"""Verify a typed mixed release closure without making proof rows graph edges."""

from __future__ import annotations

import hashlib
import os
import stat
from pathlib import Path

SCHEMA = "cal-typed-release-closure/v1"
KINDS = {"semantic-artifact", "provenance-evidence", "public-package", "protected-host"}


class Refused(ValueError):
    pass


def need(value, code):
    if not value:
        raise Refused(code)


def read_hash(path: Path, *, protected: bool, repository: Path):
    need(path.is_absolute(), "ABSOLUTE_PATH_REQUIRED")
    need(".." not in path.parts, "PATH_TRAVERSAL_REFUSED")
    need(not path.is_relative_to(repository) if protected else path.is_relative_to(repository),
         "PUBLIC_PROTECTED_BOUNDARY")
    directory = os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        for component in path.parts[1:-1]:
            next_directory = os.open(component, os.O_RDONLY | os.O_DIRECTORY |
                                     os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=directory)
            os.close(directory)
            directory = next_directory
        parent = os.fstat(directory)
        if protected:
            need(parent.st_uid == os.getuid() and stat.S_IMODE(parent.st_mode) & 0o077 == 0,
                 "PROTECTED_PARENT_REFUSED")
        fd = os.open(path.name, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC,
                     dir_fd=directory)
        try:
            opened = os.fstat(fd)
            named = os.stat(path.name, dir_fd=directory, follow_symlinks=False)
            need(stat.S_ISREG(opened.st_mode) and
                 (opened.st_dev, opened.st_ino) == (named.st_dev, named.st_ino),
                 "FILE_IDENTITY_REFUSED")
            if protected:
                need(opened.st_uid == os.getuid() and stat.S_IMODE(opened.st_mode) & 0o077 == 0,
                     "PROTECTED_CUSTODY_REFUSED")
            hashed = hashlib.sha256()
            size = 0
            while True:
                part = os.read(fd, 1024 * 1024)
                if not part:
                    break
                hashed.update(part)
                size += len(part)
            after = os.fstat(fd)
            named_after = os.stat(path.name, dir_fd=directory, follow_symlinks=False)
            absolute_after = os.stat(path, follow_symlinks=False)
            parent_after = os.fstat(directory)
            parent_named_after = os.stat(path.parent, follow_symlinks=False)
            identity = (opened.st_dev, opened.st_ino)
            fingerprint = lambda value: (value.st_dev, value.st_ino, value.st_size,
                                         value.st_mtime_ns, value.st_ctime_ns,
                                         value.st_mode, value.st_uid)
            need(fingerprint(opened) == fingerprint(after) and
                 size == opened.st_size and
                 identity == (named_after.st_dev, named_after.st_ino) ==
                 (absolute_after.st_dev, absolute_after.st_ino) and
                 fingerprint(named_after) == fingerprint(after) and
                 fingerprint(absolute_after) == fingerprint(after) and
                 (parent.st_dev, parent.st_ino, parent.st_mode, parent.st_uid) ==
                 (parent_after.st_dev, parent_after.st_ino, parent_after.st_mode, parent_after.st_uid) ==
                 (parent_named_after.st_dev, parent_named_after.st_ino,
                  parent_named_after.st_mode, parent_named_after.st_uid),
                 "FILE_CHANGED_DURING_READ")
            return hashed.hexdigest(), size
        finally:
            os.close(fd)
    except OSError as error:
        raise Refused("SYMLINK_OR_PATH_REFUSED") from error
    finally:
        os.close(directory)


def verify(manifest: dict, repository: Path):
    need(type(manifest) is dict and set(manifest) == {"schema", "roots", "bindings"}
         and manifest["schema"] == SCHEMA and type(manifest["roots"]) is list
         and type(manifest["bindings"]) is list, "MANIFEST_SHAPE_REFUSED")
    repository = repository.resolve(strict=True)
    by_ref = {}
    for row in manifest["bindings"]:
        need(type(row) is dict and set(row) == {"kind", "ref", "path", "sha256", "depends_on"},
             "BINDING_SHAPE_REFUSED")
        kind, ref = row["kind"], row["ref"]
        need(kind in KINDS and type(ref) is str and ref and ref not in by_ref,
             "KIND_OR_DUPLICATE_REFUSED")
        need(type(row["sha256"]) is str and len(row["sha256"]) == 64 and
             all(c in "0123456789abcdef" for c in row["sha256"]), "DIGEST_SHAPE_REFUSED")
        need(type(row["path"]) is str and type(row["depends_on"]) is list,
             "PATH_OR_EDGES_REFUSED")
        need(kind == "semantic-artifact" or not row["depends_on"],
             "PROOF_EDGE_REFUSED")
        if kind == "protected-host":
            path = Path(row["path"])
            need(path.is_absolute(), "PROTECTED_PATH_REFUSED")
        else:
            path = repository / row["path"]
            need(not Path(row["path"]).is_absolute() and ".." not in Path(row["path"]).parts,
                 "PUBLIC_PATH_REFUSED")
        observed, size = read_hash(path, protected=kind == "protected-host",
                                   repository=repository)
        need(observed == row["sha256"], "BYTES_SUBSTITUTED")
        by_ref[ref] = (row, size)
    roots = manifest["roots"]
    need(all(type(ref) is str and ref for ref in roots), "ROOTS_REFUSED")
    need(len(roots) == len(set(roots)) and roots, "ROOTS_REFUSED")
    for ref in roots:
        need(ref in by_ref and by_ref[ref][0]["kind"] == "semantic-artifact",
             "ROOT_KIND_REFUSED")
    visiting, visited = set(), set()

    def walk(ref):
        need(ref in by_ref and by_ref[ref][0]["kind"] == "semantic-artifact",
             "SEMANTIC_TARGET_REFUSED")
        need(ref not in visiting, "SEMANTIC_CYCLE_REFUSED")
        if ref in visited:
            return
        visiting.add(ref)
        row = by_ref[ref][0]
        need(all(type(target) is str and target for target in row["depends_on"]),
             "SEMANTIC_TARGET_REFUSED")
        need(len(row["depends_on"]) == len(set(row["depends_on"])),
             "DUPLICATE_SEMANTIC_EDGE")
        for target in row["depends_on"]:
            walk(target)
        visiting.remove(ref)
        visited.add(ref)

    for root in roots:
        walk(root)
    return {"schema": SCHEMA, "verified_bindings": len(by_ref),
            "semantic_nodes": len(visited),
            "semantic_edges": sum(len(by_ref[ref][0]["depends_on"]) for ref in visited),
            "protected_bytes_exposed": 0}
