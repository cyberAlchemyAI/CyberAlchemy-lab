"""Disposable exact-byte local bundle importer with a durable HEAD boundary."""

from __future__ import annotations

import fcntl
import json
import os
import stat
import uuid
from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
from typing import Callable


class ImportError(ValueError):
    pass


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def encoded(value: dict) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _sha(value: str) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def _private_dir(fd: int) -> None:
    info = os.fstat(fd)
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise ImportError("unsafe local import directory")


def _regular_at(directory_fd: int, name: str) -> bytes:
    try:
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory_fd)
    except OSError as exc:
        raise ImportError(f"cannot open regular file: {name}") from exc
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_uid != os.getuid():
            raise ImportError(f"non-regular or linked file: {name}")
        with os.fdopen(fd, "rb", closefd=False) as stream:
            return stream.read()
    finally:
        os.close(fd)


def _atomic_new_at(directory_fd: int, name: str, data: bytes) -> None:
    temporary = f".{name}.{uuid.uuid4().hex}.tmp"
    fd = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW,
                 0o600, dir_fd=directory_fd)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, name, src_dir_fd=directory_fd,
                    dst_dir_fd=directory_fd, follow_symlinks=False)
        except FileExistsError:
            if _regular_at(directory_fd, name) != data:
                raise ImportError(f"occupied path has different bytes: {name}")
        os.fsync(directory_fd)
    finally:
        os.unlink(temporary, dir_fd=directory_fd)
        os.fsync(directory_fd)


def _atomic_replace_at(directory_fd: int, name: str, data: bytes) -> None:
    temporary = f".{name}.{uuid.uuid4().hex}.tmp"
    fd = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW,
                 0o600, dir_fd=directory_fd)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, name, src_dir_fd=directory_fd, dst_dir_fd=directory_fd)
        os.fsync(directory_fd)
    finally:
        try:
            os.unlink(temporary, dir_fd=directory_fd)
        except FileNotFoundError:
            pass


class LocalImporter:
    def __init__(self, root: Path):
        self.root = Path(root)
        self._root_fd = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        self._bundles_fd = -1
        try:
            _private_dir(self._root_fd)
            try:
                os.mkdir("bundles", mode=0o700, dir_fd=self._root_fd)
            except FileExistsError:
                pass
            self._bundles_fd = os.open("bundles", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                       dir_fd=self._root_fd)
            _private_dir(self._bundles_fd)
            self._check_attachment()
            try:
                os.stat("HEAD.json", dir_fd=self._root_fd, follow_symlinks=False)
            except FileNotFoundError:
                if os.listdir(self._bundles_fd):
                    raise ImportError("HEAD missing while bundle residue exists")
                _atomic_new_at(self._root_fd, "HEAD.json",
                               encoded({"schema": "lab-local-import-head/v1", "sequence": 0,
                                        "bundle_digest": None, "previous_head_digest": None}))
            self._check_attachment()
        except BaseException:
            self.close()
            raise
        self.bundles = self.root / "bundles"
        self.head = self.root / "HEAD.json"

    def close(self) -> None:
        for name in ("_bundles_fd", "_root_fd"):
            fd = getattr(self, name, -1)
            if fd >= 0:
                os.close(fd)
                setattr(self, name, -1)

    def __del__(self) -> None:
        self.close()

    def _check_attachment(self) -> None:
        try:
            selected = os.stat(self.root, follow_symlinks=False)
        except FileNotFoundError as exc:
            raise ImportError("selected import root was detached") from exc
        held = os.fstat(self._root_fd)
        if (not stat.S_ISDIR(selected.st_mode)
                or (selected.st_dev, selected.st_ino) != (held.st_dev, held.st_ino)):
            raise ImportError("selected import root was replaced")

    @contextmanager
    def _lock(self):
        self._check_attachment()
        fd = os.open(".lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600,
                     dir_fd=self._root_fd)
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_uid != os.getuid():
                raise ImportError("unsafe lock file")
            fcntl.flock(fd, fcntl.LOCK_EX)
            self._check_attachment()
            yield
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)

    def read_head(self) -> tuple[dict, str]:
        self._check_attachment()
        raw = _regular_at(self._root_fd, "HEAD.json")
        try:
            value = json.loads(raw)
        except (ValueError, UnicodeDecodeError) as exc:
            raise ImportError("invalid HEAD JSON") from exc
        if (not isinstance(value, dict) or set(value) != {"schema", "sequence", "bundle_digest", "previous_head_digest"}
                or value["schema"] != "lab-local-import-head/v1"
                or type(value["sequence"]) is not int or value["sequence"] < 0
                or (value["bundle_digest"] is not None and not _sha(value["bundle_digest"]))
                or (value["previous_head_digest"] is not None and not _sha(value["previous_head_digest"]))
                or raw != encoded(value)):
            raise ImportError("invalid HEAD shape or bytes")
        if value["sequence"] == 0 and (value["bundle_digest"] is not None or value["previous_head_digest"] is not None):
            raise ImportError("invalid initial HEAD")
        if value["sequence"] > 0 and (value["bundle_digest"] is None or value["previous_head_digest"] is None):
            raise ImportError("incomplete committed HEAD")
        if value["sequence"] > 0:
            committed = _regular_at(self._bundles_fd, f"{value['bundle_digest']}.bin")
            if digest(committed) != value["bundle_digest"]:
                raise ImportError("committed bundle bytes changed")
        return value, digest(raw)

    def import_bundle(
        self, *, body: bytes, selected_digest: str, expected_head_digest: str,
        approved: Callable[[bytes], bool], after_stage: Callable[[], None] | None = None,
    ) -> dict:
        if not isinstance(body, bytes) or not _sha(selected_digest) or digest(body) != selected_digest:
            raise ImportError("selected bundle bytes changed")
        if not _sha(expected_head_digest):
            raise ImportError("invalid expected HEAD digest")
        if not approved(body):
            raise ImportError("exact local decision is not approved")
        with self._lock():
            current, current_digest = self.read_head()
            bundle_name = f"{selected_digest}.bin"
            if current_digest != expected_head_digest:
                if (current["bundle_digest"] == selected_digest
                        and current["previous_head_digest"] == expected_head_digest
                        and _regular_at(self._bundles_fd, bundle_name) == body):
                    return {"idempotent": True, "head_digest": current_digest,
                            "sequence": current["sequence"]}
                raise ImportError("wrong HEAD; exact predecessor changed")
            self._check_attachment()
            _atomic_new_at(self._bundles_fd, bundle_name, body)
            if after_stage is not None:
                after_stage()
            successor = {"schema": "lab-local-import-head/v1",
                         "sequence": current["sequence"] + 1,
                         "bundle_digest": selected_digest,
                         "previous_head_digest": current_digest}
            self._check_attachment()
            _atomic_replace_at(self._root_fd, "HEAD.json", encoded(successor))
            self._check_attachment()
            return {"idempotent": False, "head_digest": digest(encoded(successor)),
                    "sequence": successor["sequence"]}

    def import_decided_bundle(self, *, target, decision_state, body: bytes,
                              expected_head_digest: str,
                              after_stage: Callable[[], None] | None = None) -> dict:
        """Connect an exact local T26 bundle decision to this import boundary."""
        if (getattr(target, "scope", None) != "local-import"
                or getattr(target, "body_digest", None) != getattr(target, "bundle_digest", None)
                or getattr(target, "base_digest", None) != expected_head_digest):
            raise ImportError("target is not the selected whole local-import bundle")
        return self.import_bundle(
            body=body, selected_digest=target.body_digest,
            expected_head_digest=expected_head_digest,
            approved=lambda data: decision_state.can_import(target, body=data),
            after_stage=after_stage,
        )
