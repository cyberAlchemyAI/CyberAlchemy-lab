"""Scoped host-owned retained objects, complete receipts and cold reconstruction."""
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import os
from pathlib import Path
import re
import tempfile
import secrets
import stat

from .exact import HEX, binding, decode, encode, exclusive, fsync_dir, read, require, sha, shape, write_package
from .package import verify_package

STORE_ID = r"[a-z][a-z0-9-]{0,63}"
LOCATOR = re.compile(r"lab-retained://(" + STORE_ID + r")/sha256/([a-f0-9]{64})(?:#/members/([A-Za-z0-9][A-Za-z0-9_-]{0,127}))?\Z")
RECEIPT = re.compile(r"retention-receipt:(" + STORE_ID + r"):([a-f0-9]{64}):sha256:([a-f0-9]{64})\Z")


class Custody:
    def __init__(self, root, store_id, scope_ref, gate):
        self.root = Path(root).absolute()
        require(re.fullmatch(STORE_ID, store_id), "invalid-store-id")
        require(self.root.is_dir() and self.root.resolve() == self.root and not self.root.is_symlink(), "store-not-provisioned", exit_code=3)
        st = self.root.stat()
        require(st.st_uid == os.getuid() and st.st_mode & 0o077 == 0, "unsafe-store-root", exit_code=3)
        self.identity = (st.st_dev, st.st_ino)
        self._fd = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        self.store_id, self.scope, self.gate = store_id, scope_ref, gate

    def close(self):
        if self._fd is not None:
            os.close(self._fd);self._fd = None

    def __del__(self):
        if getattr(self, "_fd", None) is not None:self.close()

    def guard(self):
        st = self.root.stat()
        require(self.root.resolve() == self.root and (st.st_dev, st.st_ino) == self.identity and st.st_uid == os.getuid() and st.st_mode & 0o077 == 0, "store-identity-changed", exit_code=3)

    def directory(self, relative):
        with self.directory_fd(relative, create=True):pass
        return self.root / relative

    @contextmanager
    def directory_fd(self, relative, *, create=False):
        from .exact import logical
        self.guard();parts = logical(relative)
        fd = os.dup(self._fd)
        try:
            for component in parts:
                if create:
                    try:os.mkdir(component, mode=0o700, dir_fd=fd);os.fsync(fd)
                    except FileExistsError:pass
                child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                os.close(fd);fd = child
                st = os.fstat(fd)
                require(st.st_uid == os.getuid() and st.st_mode & 0o077 == 0, "unsafe-store-directory", exit_code=3)
            yield fd
        except OSError as exc:
            from .exact import Refusal
            raise Refusal("unsafe-or-missing-store-directory", "Store directory unavailable or unsafe", 3) from exc
        finally:os.close(fd)

    def leaf_read(self, fd, name):
        handle = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        try:
            before = os.fstat(handle)
            require(stat.S_ISREG(before.st_mode) and before.st_uid == os.getuid() and not before.st_mode & 0o077 and before.st_size <= 16777216, "unsafe-store-object", exit_code=3)
            chunks, total = [], 0
            while True:
                chunk = os.read(handle, min(65536, 16777217 - total))
                if not chunk:break
                chunks.append(chunk);total += len(chunk)
                require(total <= 16777216, "store-object-budget")
            after = os.fstat(handle)
            require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) ==
                    (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns), "changed-store-object", exit_code=3)
            return b"".join(chunks)
        finally:os.close(handle)

    def selected_read(self, path):
        relative = path.relative_to(self.root)
        with self.directory_fd(str(relative.parent)) as fd:return self.leaf_read(fd, relative.name)

    def permit(self, operation, root_digest):
        # A grant for one store/root identity cannot be reused for another owned directory.
        subject = sha(encode({"store_id": self.store_id, "root_identity": list(self.identity), "package_root": root_digest}))
        return self.gate.permit(operation, self.scope, subject)

    @contextmanager
    def lock(self):
        self.guard()
        fd = os.open(".custody.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600, dir_fd=self._fd)
        try:
            st = os.fstat(fd);require(st.st_uid == os.getuid() and not st.st_mode & 0o077, "unsafe-lock")
            fcntl.flock(fd, fcntl.LOCK_EX);self.guard();yield
        finally:
            os.close(fd)

    def object_path(self, digest):
        require(HEX.fullmatch(digest), "invalid-object-digest")
        return self.root / "objects/sha256" / digest[:2] / digest

    def object_read(self, digest):
        self.guard()
        try:raw = self.selected_read(self.object_path(digest))
        except OSError as exc:
            from .exact import Refusal
            raise Refusal("reconstruction-incomplete", "Required retained object unavailable: " + digest, 3) from exc
        require(sha(raw) == digest, "reconstruction-incomplete", "Retained object digest differs", 3)
        self.guard();return raw

    def install(self, path, raw):
        self.guard()
        with self.directory_fd(str(path.parent.relative_to(self.root)), create=True) as directory:
            name = ".pending-" + secrets.token_hex(16)
            fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=directory)
            try:
                with os.fdopen(fd, "wb") as f:
                    f.write(raw);f.flush();os.fsync(f.fileno())
                try:os.link(name, path.name, src_dir_fd=directory, dst_dir_fd=directory, follow_symlinks=False)
                except FileExistsError:require(self.leaf_read(directory, path.name) == raw, "stored-object-conflict", exit_code=3)
                os.fsync(directory)
            finally:os.unlink(name, dir_fd=directory)

    def retain(self, manifest_raw, buffers, idempotency_key):
        root_digest = sha(manifest_raw)
        observation = self.permit("retain-package", root_digest)
        m, required, verified = verify_package(manifest_raw, lambda _, row: buffers[row["path"]], all_members=True)
        capture = decode(verified["capture.json"])
        require(all(r["retention_posture"] == "permitted" for r in capture["input_rows"]), "retention-rights-unresolved", exit_code=3)
        fingerprint = sha(encode({"operation": "retain-package", "principal": observation["principal_ref"], "scope": self.scope, "root": root_digest}))
        operation = sha(encode({"key": idempotency_key, "scope": self.scope, "principal": observation["principal_ref"]}))
        with self.lock():
            journal = self.directory("journal") / (operation + ".json")
            if journal.exists():
                prior = decode(self.selected_read(journal));require(prior["fingerprint"] == fingerprint, "idempotency-conflict", exit_code=3)
            else:
                self.install(journal, encode({"fingerprint": fingerprint, "root_sha256": root_digest, "authority_effect": "none"}))
            receipt_path = self.root / "packages" / root_digest / "complete.json"
            if receipt_path.exists():
                receipt_raw = self.selected_read(receipt_path)
                self.verify_receipt(receipt_raw, root_digest)
                self.verify_retained(root_digest)
                self.permit("retain-package", root_digest)
                return self.receipt_result(root_digest, receipt_raw)
            for raw in [manifest_raw, *verified.values()]:self.install(self.object_path(sha(raw)), raw)
            self.verify_retained(root_digest)
            fresh = self.permit("retain-package", root_digest)
            receipt = {"schema_version": "cal.define.custody-completion/v1", "root_binding": {"sha256": root_digest, "bytes": len(manifest_raw)},
                       "stored_member_bindings": {i: {"sha256": r["sha256"], "bytes": r["bytes"]} for i, r in m["members"].items()},
                       "required_member_ids": sorted(required), "total_bytes": len(manifest_raw) + sum(len(r) for r in verified.values()),
                       "store_id": self.store_id, "scope_ref": self.scope, "store_selection_binding": {"store_id": self.store_id, "directory_identity": list(self.identity)},
                       "request_binding": {"sha256": fingerprint}, "policy_observation_binding": fresh["policy_observation_binding"],
                       "completed_at": datetime.now(timezone.utc).isoformat(), "claim_ceiling": "Exact retained byte custody only; no admission or continuing read permission.", "authority_effect": "none"}
            raw = encode(receipt);self.guard();self.install(receipt_path, raw)
            return self.receipt_result(root_digest, raw)

    def receipt_result(self, root_digest, raw):
        return {"locator": f"lab-retained://{self.store_id}/sha256/{root_digest}", "content_digest": "sha256:" + root_digest,
                "receipt_ref": f"retention-receipt:{self.store_id}:{root_digest}:sha256:{sha(raw)}", "authority_effect": "none"}

    def verify_receipt(self, raw, root_digest):
        r = decode(raw)
        shape(r, ("schema_version", "root_binding", "stored_member_bindings", "required_member_ids", "total_bytes", "store_id", "scope_ref", "store_selection_binding", "request_binding", "policy_observation_binding", "completed_at", "claim_ceiling", "authority_effect"))
        require(r["schema_version"] == "cal.define.custody-completion/v1" and r["root_binding"]["sha256"] == root_digest and r["store_id"] == self.store_id and r["scope_ref"] == self.scope and r["store_selection_binding"] == {"store_id": self.store_id, "directory_identity": list(self.identity)} and r["authority_effect"] == "none", "receipt-identity-mismatch", exit_code=3)
        m, required, _ = self.verify_retained(root_digest)
        require(r["stored_member_bindings"] == {i: {"sha256": row["sha256"], "bytes": row["bytes"]} for i, row in m["members"].items()} and r["required_member_ids"] == sorted(required) and r["root_binding"]["bytes"] == len(self.object_read(root_digest)) and r["total_bytes"] == r["root_binding"]["bytes"] + sum(v["bytes"] for v in r["stored_member_bindings"].values()), "receipt-members-mismatch", exit_code=3)
        return r

    def verify_retained(self, root_digest):
        return verify_package(self.object_read(root_digest), lambda _, row: self.object_read(row["sha256"]))

    def reconstruct(self, locator, receipt_ref, *, destination=None):
        loc, pin = LOCATOR.fullmatch(locator), RECEIPT.fullmatch(receipt_ref)
        require(loc is not None and pin is not None and loc[3] is None, "noncanonical-retained-reference")
        require(loc[1] == pin[1] == self.store_id and loc[2] == pin[2], "retained-reference-mismatch")
        root_digest = loc[2];self.permit("read-retained", root_digest)
        raw = self.selected_read(self.root / "packages" / root_digest / "complete.json")
        require(sha(raw) == pin[3], "receipt-digest-mismatch", exit_code=3)
        self.verify_receipt(raw, root_digest)
        m, required, buffers = self.verify_retained(root_digest)
        permission = self.permit("read-retained", root_digest);self.guard()
        if destination is not None:write_package(destination, {**buffers, "manifest.json": self.object_read(root_digest)})
        return {"schema_version": "cal.define.reconstruction-observation/v1", "observation_id": "reconstruction:" + root_digest,
                "root_binding": binding(self.object_read(root_digest), "manifest.json"), "pack_binding": binding(buffers["pack.json"], "pack.json"),
                "source_cut": {"posture": "authorized-candidate-package-inspection", "scope_ref": self.scope}, "input_record_refs": [],
                "consumer_binding": {"principal_ref": permission["principal_ref"]}, "permission_observation_binding": permission["policy_observation_binding"],
                "verified_member_ids": sorted(required), "outcome": "complete-frozen-reconstruction",
                "limitations": ["Current operational readiness and governing standing are not established.", "Session memory is not retained or restored.",
                                "Unselected optional members are not claimed as reconstructed: " + ",".join(sorted(set(m["members"]) - required))], "authority_effect": "none"}
