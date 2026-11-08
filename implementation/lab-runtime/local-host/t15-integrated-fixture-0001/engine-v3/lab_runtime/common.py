from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path


class RuntimeFault(Exception):
    """An explicit fail-closed protocol or integrity failure."""


def require(condition, message):
    if not condition:
        raise RuntimeFault(message)


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def byte_digest(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    def pairs(items):
        result = {}
        for k, v in items:
            require(k not in result, f"duplicate JSON key: {k}")
            result[k] = v
        return result
    try:
        return json.loads(Path(path).read_text(), object_pairs_hook=pairs,
                          parse_constant=lambda v: (_ for _ in ()).throw(RuntimeFault(f"nonfinite JSON: {v}")))
    except (ValueError, OSError) as exc:
        raise RuntimeFault(f"cannot read {path}: {exc}") from exc


def under(root, relative):
    require(isinstance(relative, str) and bool(relative), "empty material path")
    value = Path(relative)
    require(not value.is_absolute() and ".." not in value.parts, "material path must stay within its root")
    resolved = (root / value).resolve()
    require(resolved.is_relative_to(root.resolve()), "material symlink escapes its root")
    return resolved


def fsync_dir(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
        fsync_dir(path.parent)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def pointer(document, selector):
    if not selector or selector == "#":
        return document
    require(selector.startswith("/") or selector.startswith("#/"), "invalid JSON pointer")
    value = document
    for part in selector.removeprefix("#").split("/")[1:]:
        part = part.replace("~1", "/").replace("~0", "~")
        try:
            value = value[int(part)] if isinstance(value, list) else value[part]
        except (KeyError, ValueError, IndexError, TypeError) as exc:
            raise RuntimeFault(f"unresolved pointer {selector}") from exc
    return value


def sealed(value):
    return {**value, "digest": digest(value)}


def verify_seal(value):
    require(value.get("digest") == digest({k: v for k, v in value.items() if k != "digest"}), "invalid envelope digest")


def identity(record, field=None):
    if field:
        require(field in record and isinstance(record[field], str), f"missing identity field: {field}")
        return record[field]
    for key in ("definition_id", "artifact_type_ref", "node_id", "record_id", "migration_manifest_id", "product_id", "project_id"):
        if key in record:
            return record[key]
    raise RuntimeFault("record has no declared supported identity field")
