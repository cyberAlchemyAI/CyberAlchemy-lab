#!/usr/bin/env python3
"""Local, unprivileged operational provisioning slice for the API16 reader.

This controller owns a new store and stages a fresh policy for each run. It
does not initialize an authority store or grant an operator capability.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import fcntl
from contextlib import contextmanager
import re
from datetime import datetime, timezone
from pathlib import Path
import secrets
import stat

VERSION = "lab-local-operational-provision-plan/v1"
STATE_VERSION = "lab-local-operational-provision-state/v1"
ROOT = Path(__file__).resolve().parents[4]
FIELDS = {
    "schema_version", "store_id", "operator_ref", "scope_ref", "owner_uid",
    "engine_path", "engine_sha256", "profile_path", "profile_sha256",
    "base_head_path", "base_head_sha256", "store_path", "rollback_path",
    "private_key_path", "private_key_sha256", "custody_policy_path", "custody_policy_sha256",
    "channel_root_path", "source_name", "source_expires_at",
}
O_FILE = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
RUN_ID = re.compile(r"run-[0-9a-f]{32}\Z")
OP_ID = re.compile(r"op:[A-Za-z0-9._-]{1,64}\Z")
MAX_OPERATIONS = 1024


class Refused(RuntimeError):
    pass


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise Refused(reason)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _instant(value: str) -> datetime:
    require(type(value) is str, "INVALID_EXPIRY")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as error:
        raise Refused("INVALID_EXPIRY") from error
    require(parsed.tzinfo is not None, "EXPIRY_REQUIRES_TIMEZONE")
    return parsed.astimezone(timezone.utc)


def _path(raw: str, *, present: bool, kind: str = "file") -> Path:
    require(type(raw) is str and raw.startswith("/") and ".." not in Path(raw).parts,
            "UNSAFE_PATH")
    path = Path(raw)
    require(not path.is_relative_to(ROOT), "REPOSITORY_PATH_REFUSED")
    for part in (path, *path.parents):
        if part.is_symlink():
            raise Refused("SYMLINK_PATH_REFUSED")
    if present:
        require(path.is_file() if kind == "file" else path.is_dir(), "INPUT_MISSING")
    else:
        require(not path.exists(), "OUTPUT_ALREADY_EXISTS")
    return path


def _owned_dir(path: Path, mode: int = 0o700) -> os.stat_result:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        value = os.fstat(fd)
        named = os.stat(path, follow_symlinks=False)
        require((value.st_dev, value.st_ino) == (named.st_dev, named.st_ino)
                and stat.S_ISDIR(value.st_mode) and value.st_uid == os.getuid()
                and stat.S_IMODE(value.st_mode) == mode, "DIRECTORY_IDENTITY_REFUSED")
        return value
    finally:
        os.close(fd)


def _read_owned(path: Path, expected: str | None = None) -> bytes:
    _path(str(path), present=True)
    fd = os.open(path, O_FILE)
    try:
        value = os.fstat(fd)
        named = os.stat(path, follow_symlinks=False)
        require(stat.S_ISREG(value.st_mode) and value.st_uid == os.getuid()
                and (value.st_dev, value.st_ino) == (named.st_dev, named.st_ino),
                "FILE_IDENTITY_REFUSED")
        require(value.st_size <= 1024 * 1024, "FILE_TOO_LARGE")
        chunks = []
        total = 0
        while True:
            part = os.read(fd, min(65536, 1024 * 1024 + 1 - total))
            if not part:
                break
            total += len(part)
            require(total <= 1024 * 1024, "FILE_TOO_LARGE")
            chunks.append(part)
        raw = b"".join(chunks)
        if expected is not None:
            require(digest(raw) == expected, "PIN_CHANGED")
        return raw
    finally:
        os.close(fd)


def _read_plan(path: str) -> bytes:
    selected = _path(path, present=True)
    raw = _read_owned(selected)
    value = os.stat(selected, follow_symlinks=False)
    require(stat.S_IMODE(value.st_mode) == 0o600, "PLAN_MODE_REFUSED")
    _owned_dir(selected.parent)
    return raw


def _write_all(fd: int, raw: bytes) -> None:
    cursor = 0
    while cursor < len(raw):
        count = os.write(fd, raw[cursor:])
        require(type(count) is int and count > 0, "SHORT_WRITE_REFUSED")
        cursor += count


def _sync_json(path: Path, value: dict) -> None:
    raw = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
    temporary = path.parent / (".state-" + secrets.token_hex(12))
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        _write_all(fd, raw)
        os.fsync(fd)
    finally:
        os.close(fd)
    os.replace(temporary, path)
    parent = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(parent)
    finally:
        os.close(parent)


class Controller:
    def __init__(self, plan_path: str):
        self.plan_path = _path(plan_path, present=True)
        raw = _read_plan(str(self.plan_path))
        self.plan_sha256 = digest(raw)
        try:
            self.plan = json.loads(raw)
        except (ValueError, UnicodeError) as error:
            raise Refused("PLAN_INVALID") from error
        p = self.plan
        require(type(p) is dict and set(p) == FIELDS and p["schema_version"] == VERSION,
                "PLAN_SHAPE_REFUSED")
        require(type(p["owner_uid"]) is int and p["owner_uid"] == os.getuid()
                and type(p["store_id"]) is str and p["store_id"].replace("-", "").isalnum()
                and type(p["operator_ref"]) is str and ":" in p["operator_ref"]
                and type(p["scope_ref"]) is str and ":" in p["scope_ref"],
                "OPERATOR_SCOPE_REFUSED")
        self.store = _path(p["store_path"], present=True, kind="directory")
        self.channel_root = _path(p["channel_root_path"], present=True, kind="directory")
        require(self.channel_root.is_relative_to(Path("/tmp"))
                and not self.store.is_relative_to(self.channel_root)
                and not self.channel_root.is_relative_to(self.store), "STAGING_BOUNDARY_REFUSED")
        _owned_dir(self.store)
        _owned_dir(self.channel_root)
        self.state_path = self.store / "provision-state.json"
        self.lock_path = self.store / ".provision.lock"
        self.state = self._state()

    @staticmethod
    def initialize(plan_path: str) -> "Controller":
        raw = _read_plan(plan_path)
        try:
            p = json.loads(raw)
        except (ValueError, UnicodeError) as error:
            raise Refused("PLAN_INVALID") from error
        require(type(p) is dict and set(p) == FIELDS and p["schema_version"] == VERSION,
                "PLAN_SHAPE_REFUSED")
        require(type(p["owner_uid"]) is int and p["owner_uid"] == os.getuid()
                and type(p["store_id"]) is str and p["store_id"].replace("-", "").isalnum()
                and type(p["operator_ref"]) is str and ":" in p["operator_ref"]
                and type(p["scope_ref"]) is str and ":" in p["scope_ref"],
                "OPERATOR_SCOPE_REFUSED")
        store = _path(p["store_path"], present=False)
        channel = _path(p["channel_root_path"], present=False)
        _owned_dir(store.parent)
        require(channel.is_relative_to(Path("/tmp")), "STAGING_BOUNDARY_REFUSED")
        require(not store.is_relative_to(channel) and not channel.is_relative_to(store),
                "STAGING_BOUNDARY_REFUSED")
        probe = Controller.__new__(Controller)
        probe.plan = p
        probe.store = store
        probe.channel_root = channel
        probe._validate_inputs()
        # /tmp is sticky world-writable; unique absent names and exclusive mkdir
        # avoid accidental collision. This is not hostile same-UID isolation.
        os.mkdir(store, 0o700)
        try:
            os.mkdir(channel, 0o700)
            try:
                _owned_dir(store)
                _owned_dir(channel)
                initial = {"schema_version": STATE_VERSION, "plan_sha256": digest(raw),
                           "generation": 0, "pending": None, "active": None,
                           "operations": {},
                           "retained_rollback_path": p["rollback_path"]}
                _sync_json(store / "provision-state.json", initial)
                return Controller(plan_path)
            except BaseException:
                if not os.listdir(channel):
                    os.rmdir(channel)
                raise
        except BaseException:
            if not os.listdir(store):
                os.rmdir(store)
            raise

    def _validate_inputs(self) -> bytes:
        p = self.plan
        if hasattr(self, "plan_path"):
            require(digest(_read_plan(str(self.plan_path))) == self.plan_sha256, "PIN_CHANGED")
        for name in ("engine", "profile", "base_head"):
            _read_owned(_path(p[name + "_path"], present=True), p[name + "_sha256"])
        key = _path(p["private_key_path"], present=True)
        _owned_dir(key.parent)
        key_stat = os.stat(key, follow_symlinks=False)
        require(key_stat.st_uid == os.getuid() and stat.S_IMODE(key_stat.st_mode) == 0o600,
                "KEY_CUSTODY_REFUSED")
        _read_owned(key, p["private_key_sha256"])
        require(not key.is_relative_to(self.store) and not key.is_relative_to(ROOT),
                "KEY_CUSTODY_REFUSED")
        policy_path = _path(p["custody_policy_path"], present=True)
        _owned_dir(policy_path.parent)
        require(stat.S_IMODE(os.stat(policy_path, follow_symlinks=False).st_mode) == 0o600,
                "POLICY_CUSTODY_REFUSED")
        policy_raw = _read_owned(policy_path, p["custody_policy_sha256"])
        require(len(policy_raw) <= 16384, "POLICY_TOO_LARGE")
        try:
            policy = json.loads(policy_raw)
        except (ValueError, UnicodeError) as error:
            raise Refused("POLICY_INVALID") from error
        require(type(policy) is dict and policy.get("host_uid") == os.getuid()
                and policy.get("principal_ref") == p["operator_ref"]
                and policy.get("source_name") == p["source_name"]
                and policy.get("scope_refs") == [p["scope_ref"]]
                and policy.get("revoked") is False
                and policy.get("authority_effect") == "none"
                and _instant(policy.get("expires_at")) <= _instant(p["source_expires_at"])
                and _instant(policy.get("expires_at")) > datetime.now(timezone.utc)
                and _instant(p["source_expires_at"]) > datetime.now(timezone.utc),
                "POLICY_SCOPE_OR_PERIOD_REFUSED")
        rollback = _path(p["rollback_path"], present=True, kind="directory")
        _owned_dir(rollback)
        require(not rollback.is_relative_to(self.store)
                and not self.store.is_relative_to(rollback), "ROLLBACK_BOUNDARY_REFUSED")
        return policy_raw

    def _state(self) -> dict:
        raw = _read_owned(self.state_path)
        try:
            state = json.loads(raw)
        except (ValueError, UnicodeError) as error:
            raise Refused("STATE_INVALID") from error
        require(type(state) is dict and set(state) == {"schema_version", "plan_sha256",
                "generation", "pending", "active", "operations", "retained_rollback_path"}
                and state["schema_version"] == STATE_VERSION
                and state["plan_sha256"] == self.plan_sha256
                and state["retained_rollback_path"] == self.plan["rollback_path"]
                and type(state["generation"]) is int and state["generation"] >= 0
                and type(state["operations"]) is dict
                and len(state["operations"]) <= MAX_OPERATIONS,
                "STATE_BINDING_REFUSED")
        value = os.stat(self.state_path, follow_symlinks=False)
        require(stat.S_IMODE(value.st_mode) == 0o600, "STATE_MODE_REFUSED")
        for item, fields in ((state["pending"], {"run_id", "policy_sha256",
                                                  "operation_id", "request_sha256"}),
                             (state["active"], {"run_id", "policy_sha256",
                                                "directory_inode", "policy_inode",
                                                "operation_id", "request_sha256"})):
            if item is None:
                continue
            require(type(item) is dict and set(item) == fields
                    and type(item["run_id"]) is str and RUN_ID.fullmatch(item["run_id"])
                    and type(item["policy_sha256"]) is str
                    and HEX64.fullmatch(item["policy_sha256"]), "STATE_RUN_REFUSED")
            require(type(item["operation_id"]) is str and OP_ID.fullmatch(item["operation_id"])
                    and type(item["request_sha256"]) is str
                    and HEX64.fullmatch(item["request_sha256"]), "STATE_OPERATION_REFUSED")
            for key in ("directory_inode", "policy_inode"):
                if key in fields:
                    pair = item[key]
                    require(type(pair) is list and len(pair) == 2
                            and all(type(n) is int and n > 0 for n in pair),
                            "STATE_INODE_REFUSED")
        for operation_id, record in state["operations"].items():
            require(type(operation_id) is str and OP_ID.fullmatch(operation_id)
                    and type(record) is dict
                    and set(record) == {"request_sha256", "run_id", "generation"}
                    and type(record["request_sha256"]) is str
                    and HEX64.fullmatch(record["request_sha256"])
                    and type(record["run_id"]) is str and RUN_ID.fullmatch(record["run_id"])
                    and type(record["generation"]) is int
                    and 1 <= record["generation"] <= state["generation"],
                    "STATE_OPERATION_REFUSED")
        active = state["active"]
        if active is not None:
            record = state["operations"].get(active["operation_id"])
            require(record is not None and record["request_sha256"] == active["request_sha256"]
                    and record["run_id"] == active["run_id"]
                    and record["generation"] == state["generation"],
                    "STATE_OPERATION_REFUSED")
        return state

    def _save(self) -> None:
        _sync_json(self.state_path, self.state)

    @contextmanager
    def _locked(self):
        _owned_dir(self.store)
        fd = os.open(self.lock_path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
        try:
            value = os.fstat(fd)
            named = os.stat(self.lock_path, follow_symlinks=False)
            require(stat.S_ISREG(value.st_mode) and value.st_uid == os.getuid()
                    and stat.S_IMODE(value.st_mode) == 0o600
                    and (value.st_dev, value.st_ino) == (named.st_dev, named.st_ino),
                    "LOCK_IDENTITY_REFUSED")
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise Refused("STORE_BUSY") from error
            yield
        finally:
            os.close(fd)

    def _remove_active(self) -> None:
        active = self.state["active"]
        if active is None:
            return
        path = self.channel_root / active["run_id"]
        require(set(os.listdir(self.channel_root)) <= {active["run_id"]},
                "UNKNOWN_CHANNEL_RETAINED")
        if not os.path.lexists(path):
            # Interrupted after rmdir but before the state transition. No
            # other channel entry exists, so this exact active run is gone.
            self.state["active"] = None
            self._save()
            return
        _path(str(path), present=True, kind="directory")
        run_stat = _owned_dir(path)
        require([run_stat.st_dev, run_stat.st_ino] == active["directory_inode"],
                "CHANNEL_IDENTITY_REFUSED")
        entries = os.listdir(path)
        if not entries:
            # Interrupted after unlink but before rmdir. The recorded run
            # inode is empty; never delete unknown contents.
            os.rmdir(path)
            self.state["active"] = None
            self._save()
            return
        require(entries == ["policy.json"], "CHANNEL_PREIMAGE_REFUSED")
        policy = path / "policy.json"
        raw = _read_owned(policy, active["policy_sha256"])
        value = os.stat(policy, follow_symlinks=False)
        require(stat.S_IMODE(value.st_mode) == 0o600 and len(raw) <= 16384
                and [value.st_dev, value.st_ino] == active["policy_inode"]
                and os.listdir(path) == ["policy.json"], "CHANNEL_PREIMAGE_REFUSED")
        os.unlink(policy)
        os.rmdir(path)
        self.state["active"] = None
        self._save()

    def _restart_locked(self) -> dict:
        require(digest(_read_plan(str(self.plan_path))) == self.plan_sha256, "PIN_CHANGED")
        self.state = self._state()
        pending = self.state["pending"]
        if pending is not None:
            entries = os.listdir(self.channel_root)
            require(set(entries) <= {pending["run_id"]}, "UNCERTAIN_CHANNEL_RETAINED")
            path = self.channel_root / pending["run_id"]
            if os.path.lexists(path):
                # Only a private, exact-shape run from the durable intent can
                # be cleared. A dangling symlink, changed bytes, or foreign
                # entry keeps the intent and all bytes for inspection.
                try:
                    _path(str(path), present=True, kind="directory")
                    _owned_dir(path)
                    contents = os.listdir(path)
                    require(contents in ([], ["policy.json"]), "UNCERTAIN_CHANNEL_RETAINED")
                    if contents:
                        policy = path / "policy.json"
                        raw = _read_owned(policy, pending["policy_sha256"])
                        value = os.stat(policy, follow_symlinks=False)
                        require(len(raw) <= 16384 and stat.S_IMODE(value.st_mode) == 0o600,
                                "UNCERTAIN_CHANNEL_RETAINED")
                        require(os.listdir(path) == ["policy.json"],
                                "UNCERTAIN_CHANNEL_RETAINED")
                        os.unlink(policy)
                    os.rmdir(path)
                except (Refused, OSError) as error:
                    raise Refused("UNCERTAIN_CHANNEL_RETAINED") from error
            require(not os.listdir(self.channel_root), "UNCERTAIN_CHANNEL_RETAINED")
            self.state["pending"] = None
            self._save()
        self._remove_active()
        require(os.listdir(self.channel_root) == [], "UNKNOWN_CHANNEL_RETAINED")
        return {"status": "fresh-channel-required", "generation": self.state["generation"]}

    def restart(self) -> dict:
        """Invalidate the previous channel and reconcile only evidenced intent."""
        with self._locked():
            return self._restart_locked()

    def _replay_active(self, operation_id: str, record: dict) -> dict:
        active = self.state["active"]
        require(active is not None and active["operation_id"] == operation_id
                and active["run_id"] == record["run_id"], "OPERATION_RETIRED")
        require(os.listdir(self.channel_root) == [active["run_id"]],
                "ACTIVE_CHANNEL_UNAVAILABLE")
        directory = self.channel_root / active["run_id"]
        _path(str(directory), present=True, kind="directory")
        value = _owned_dir(directory)
        require([value.st_dev, value.st_ino] == active["directory_inode"]
                and os.listdir(directory) == ["policy.json"], "ACTIVE_CHANNEL_UNAVAILABLE")
        policy = directory / "policy.json"
        _read_owned(policy, active["policy_sha256"])
        value = os.stat(policy, follow_symlinks=False)
        require(stat.S_IMODE(value.st_mode) == 0o600
                and [value.st_dev, value.st_ino] == active["policy_inode"],
                "ACTIVE_CHANNEL_UNAVAILABLE")
        return {"policy_path": str(policy), "policy_sha256": active["policy_sha256"],
                "generation": record["generation"], "run_id": active["run_id"],
                "operation_id": operation_id, "replayed": True}

    def stage(self, operation_id: str | None = None, intent: str = "reader-channel") -> dict:
        if operation_id is None:
            operation_id = "op:" + secrets.token_hex(16)
        require(type(operation_id) is str and OP_ID.fullmatch(operation_id),
                "OPERATION_ID_REFUSED")
        require(type(intent) is str and 1 <= len(intent) <= 128 and "\x00" not in intent,
                "OPERATION_INTENT_REFUSED")
        with self._locked():
            require(digest(_read_plan(str(self.plan_path))) == self.plan_sha256, "PIN_CHANGED")
            self.state = self._state()
            try:
                raw = self._validate_inputs()
            except Refused:
                self._restart_locked()
                raise
            request_sha256 = digest(json.dumps({"plan_sha256": self.plan_sha256,
                "policy_sha256": digest(raw), "intent": intent}, sort_keys=True,
                separators=(",", ":")).encode())
            pending = self.state["pending"]
            if pending is not None and pending["operation_id"] == operation_id:
                require(pending["request_sha256"] == request_sha256,
                        "OPERATION_CONFLICT")
            previous = self.state["operations"].get(operation_id)
            if previous is not None:
                require(previous["request_sha256"] == request_sha256,
                        "OPERATION_CONFLICT")
                return self._replay_active(operation_id, previous)
            self._restart_locked()
            raw = self._validate_inputs()
            require(len(self.state["operations"]) < MAX_OPERATIONS,
                    "OPERATION_HISTORY_FULL")
            run_id = "run-" + secrets.token_hex(16)
            self.state["pending"] = {"run_id": run_id, "policy_sha256": digest(raw),
                                     "operation_id": operation_id,
                                     "request_sha256": request_sha256}
            self._save()
            directory = self.channel_root / run_id
            os.mkdir(directory, 0o700)
            policy = directory / "policy.json"
            fd = os.open(policy, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            try:
                _write_all(fd, raw)
                os.fsync(fd)
            finally:
                os.close(fd)
            dir_stat = _owned_dir(directory)
            file_stat = os.stat(policy, follow_symlinks=False)
            require(_read_owned(policy, digest(raw)) == raw
                    and stat.S_IMODE(file_stat.st_mode) == 0o600, "CHANNEL_WRITE_REFUSED")
            self.state["generation"] += 1
            self.state["active"] = {"run_id": run_id, "policy_sha256": digest(raw),
                                    "directory_inode": [dir_stat.st_dev, dir_stat.st_ino],
                                    "policy_inode": [file_stat.st_dev, file_stat.st_ino],
                                    "operation_id": operation_id,
                                    "request_sha256": request_sha256}
            self.state["operations"][operation_id] = {
                "request_sha256": request_sha256, "run_id": run_id,
                "generation": self.state["generation"]}
            self.state["pending"] = None
            self._save()
            try:
                self._validate_inputs()
            except BaseException:
                self._remove_active()
                raise
            return {"policy_path": str(policy), "policy_sha256": digest(raw),
                    "generation": self.state["generation"], "run_id": run_id,
                    "operation_id": operation_id, "replayed": False}

    def rollback(self) -> dict:
        with self._locked():
            self._restart_locked()
            return {"status": "inactive", "retained_rollback_path": self.plan["rollback_path"],
                    "store_path": str(self.store)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, help="Absolute path to a private, versioned plan")
    parser.add_argument("--operation-id", help="Stable idempotency key for stage")
    parser.add_argument("--intent", default="reader-channel", help="Bounded stage request intent")
    parser.add_argument("action", choices=("initialize", "stage", "restart", "rollback"))
    args = parser.parse_args()
    try:
        if args.action == "initialize":
            ctrl = Controller.initialize(args.plan)
            result = {"status": "initialized", "store_path": str(ctrl.store),
                      "plan_sha256": ctrl.plan_sha256}
        else:
            ctrl = Controller(args.plan)
            result = (ctrl.stage(args.operation_id, args.intent) if args.action == "stage"
                      else getattr(ctrl, args.action)())
    except (Refused, OSError) as error:
        print(json.dumps({"status": "refused", "reason": str(error)}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
