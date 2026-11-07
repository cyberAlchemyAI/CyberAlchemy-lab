"""Bounded original-byte IO and deterministic new-record encoding."""
from __future__ import annotations

from collections.abc import Mapping
import ctypes
import hashlib
import json
import os
import re
import stat
import tempfile
from pathlib import Path

MAX_SAFE = 2**53 - 1
HEX = re.compile(r"[a-f0-9]{64}\Z")
IDENT = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")


class Refusal(Exception):
    def __init__(self, code, message, exit_code=2):
        super().__init__(message)
        self.code, self.exit_code = code, exit_code


def require(condition, code, message=None, exit_code=2):
    if not condition:
        raise Refusal(code, message or code, exit_code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def shape(value, required, optional=(), *, label="record"):
    require(isinstance(value, dict), "invalid-shape", label + " must be an object")
    require(set(required) <= value.keys() and value.keys() <= set(required) | set(optional),
            "invalid-fields", label + " has missing or undeclared fields")


def tree(value, *, source=False, depth=0):
    require(depth <= 64, "json-depth", "JSON nesting exceeds 64")
    if isinstance(value, str):
        require("\0" not in value and not any(0xD800 <= ord(c) <= 0xDFFF for c in value),
                "invalid-unicode", "NUL or unpaired surrogate")
    elif isinstance(value, dict):
        for k, v in value.items():
            require(isinstance(k, str), "invalid-key")
            tree(k, source=source, depth=depth + 1)
            tree(v, source=source, depth=depth + 1)
    elif isinstance(value, list):
        for v in value:
            tree(v, source=source, depth=depth + 1)
    elif type(value) is int:
        require(source or abs(value) <= MAX_SAFE, "unsupported-number", "New records require exact safe integers", 4)
    elif value is not None and type(value) is not bool:
        raise Refusal("unsupported-number", "Floating/nonfinite numbers require an explicit representation contract", 4)


def decode(raw, *, source=False, maximum=16 * 1024 * 1024):
    require(isinstance(raw, bytes) and len(raw) <= maximum, "input-budget")
    def pairs(items):
        result = {}
        for k, v in items:
            require(k not in result, "duplicate-key", "Duplicate JSON object key")
            result[k] = v
        return result
    def unsupported(_):
        raise Refusal("unsupported-number", "Unsupported numeric representation", 4)
    try:
        value = json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=pairs,
                           parse_constant=unsupported, parse_float=unsupported)
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise Refusal("invalid-json", "Malformed UTF-8/JSON") from exc
    tree(value, source=source)
    return value


def encode(value):
    tree(value)
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode()


def logical(path):
    require(isinstance(path, str) and 0 < len(path) <= 512, "unsafe-path")
    parts = path.split("/")
    require(all(IDENT.fullmatch(p) and p not in (".", "..") and not p.endswith(".")
                and p.split(".")[0].upper() not in {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
                for p in parts), "unsafe-path", "Noncanonical member path")
    return parts


def member_paths(paths):
    """A member collection must also be representable as an on-disk directory."""
    names = set(paths)
    for name in names:
        parts = logical(name)
        require(not any("/".join(parts[:i]) in names for i in range(1, len(parts))), "member-prefix-collision")
    return names


def read(path, *, maximum=16 * 1024 * 1024, private=False):
    """Anchor every path component; never follow a directory or leaf symlink."""
    path = Path(os.path.abspath(path))
    directory = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[1:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            os.close(directory)
            directory = child
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
        try:
            before = os.fstat(fd)
            require(stat.S_ISREG(before.st_mode) and before.st_size <= maximum, "input-budget", "Expected bounded regular file")
            if private:
                require(before.st_uid == os.getuid() and not before.st_mode & 0o077, "unsafe-mode", "Expected owned private file")
            chunks, total = [], 0
            while True:
                chunk = os.read(fd, min(65536, maximum + 1 - total))
                if not chunk:
                    break
                chunks.append(chunk); total += len(chunk)
                require(total <= maximum, "input-budget")
            after = os.fstat(fd)
            require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) ==
                    (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns), "changed-during-read")
            return b"".join(chunks)
        finally:
            os.close(fd)
    except OSError as exc:
        raise Refusal("source-unavailable", "Required original file is unavailable or unsafe", 3) from exc
    finally:
        os.close(directory)


def binding(raw, path):
    return {"path": path, "sha256": sha(raw), "bytes": len(raw), "digest_kind": "original-file-sha256"}


def bound(root, item):
    shape(item, ("path", "sha256", "bytes", "digest_kind"), label="byte binding")
    logical(item["path"])
    require(item["digest_kind"] == "original-file-sha256" and HEX.fullmatch(item["sha256"]), "invalid-binding")
    if isinstance(root, Mapping):
        require(item["path"] in root and isinstance(root[item["path"]], bytes), "source-unavailable", "Required captured member is absent", 3)
        raw = root[item["path"]]
    else:
        raw = read(Path(root) / item["path"])
    require(len(raw) == item["bytes"] and sha(raw) == item["sha256"], "binding-mismatch", "Selected original bytes differ", 3)
    return raw


def pointer(value, selector):
    require(isinstance(selector, str) and (selector == "" or selector.startswith("/")), "invalid-selector")
    for part in selector.split("/")[1:] if selector else []:
        require(not re.search(r"~(?![01])", part), "invalid-selector")
        key = part.replace("~1", "/").replace("~0", "~")
        try:
            if isinstance(value, list):
                require(bool(re.fullmatch(r"0|[1-9][0-9]*", key)), "invalid-selector")
                value = value[int(key)]
            else:
                value = value[key]
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise Refusal("unresolved-selector", "Exact selector does not resolve") from exc
    return value


def fsync_dir(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def exclusive(path, raw):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(raw); handle.flush(); os.fsync(handle.fileno())
    except BaseException:
        raise


def publish_directory(staged, destination):
    libc = ctypes.CDLL(None, use_errno=True)
    rename = getattr(libc, "renameat2", None)
    require(rename is not None, "unsupported-filesystem", "Atomic no-replace directory publication required", 4)
    rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    rename.restype = ctypes.c_int
    result = rename(-100, os.fsencode(staged), -100, os.fsencode(destination), 1)
    require(result == 0, "output-exists-or-unavailable", "Output publication refused; existing destinations are preserved", 3)
    try:
        fsync_dir(Path(destination).parent)
    except BaseException as exc:
        # rename already succeeded: failure or interruption cannot imply no output.
        raise Refusal("publication-outcome-unknown", "Output may have been published; inspect the requested destination before retrying", 3) from exc


def write_package(destination, members, *, empty_directories=()):
    member_paths(members)
    destination = Path(destination).absolute()
    require(destination.parent.is_dir(), "output-parent-missing", exit_code=3)
    # Anchor the parent before creating anything, including for paths containing symlinks.
    require(destination.parent.resolve() == destination.parent, "unsafe-output-parent")
    staged = Path(tempfile.mkdtemp(prefix=".define-v2-", dir=destination.parent))
    try:
        for directory in empty_directories:
            logical(directory);(staged / directory).mkdir(parents=True, exist_ok=True, mode=0o700)
        for path, raw in members.items():
            logical(path)
            target = staged / path
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            exclusive(target, raw)
        for directory in sorted((f for f in staged.rglob("*") if f.is_dir()), key=lambda f: len(f.parts), reverse=True):
            fsync_dir(directory)
        fsync_dir(staged)
        publish_directory(staged, destination)
    finally:
        if staged.exists():
            import shutil
            shutil.rmtree(staged)
