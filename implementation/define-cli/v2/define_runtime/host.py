"""Exact local host boundary. Configuration is not an authority grant.

The independently installed native verifier owns nonce authentication, current
issuer/principal/scope validation and revocation. No test issuer is installed here.
"""
import os
from pathlib import Path
import secrets
import subprocess
import sys
from datetime import datetime, timezone

from .exact import binding, bound, decode, encode, read, require, sha, shape

SELECTION_FIELDS = ("schema_version", "selection_id", "revision", "host_binding", "extension_binding", "protocol_binding",
                    "source_profile_binding", "schema_bindings", "dependency_selection_binding", "source_selection_contract_binding",
                    "operation_mapping", "credential_locators", "authority_posture", "limits", "authority_effect")


class NativeHost:
    """One explicitly installed local Lab selection; no discovery or fallback."""
    def __init__(self, selection_path):
        require(selection_path is not None, "host-selection-required", "Select the actual independently configured Lab host; no permission is inferred", 3)
        self.path = Path(selection_path).absolute()
        self.raw = read(self.path, maximum=1048576, private=True)
        self.selection = decode(self.raw)
        shape(self.selection, SELECTION_FIELDS)
        self.root = self.path.parent
        require(self.selection["schema_version"] == "cal.define.lab-adapter-selection/v1" and self.selection["authority_effect"] == "none", "unsupported-host-selection", exit_code=4)
        require(self.selection["authority_posture"] == "native-current-verifier-required", "authority-unavailable", exit_code=3)
        qualified = decode(read(Path(__file__).resolve().parents[1] / "qualified-hosts.json", maximum=1048576))
        require(any(h["host_sha256"] == self.selection["host_binding"]["sha256"] and h["extension_sha256"] == self.selection["extension_binding"]["sha256"] and h["protocol_sha256"] == self.selection["protocol_binding"]["sha256"] for h in qualified["qualified_hosts"]),
                "host-successor-unqualified", "No independently qualified scoped host successor matches this selection; caller configuration cannot establish qualification", 3)
        self.guard()

    def guard(self):
        require(read(self.path, maximum=1048576, private=True) == self.raw, "host-selection-changed", exit_code=3)
        s = self.selection
        for b in [s[k] for k in ("host_binding", "extension_binding", "protocol_binding", "source_profile_binding", "dependency_selection_binding", "source_selection_contract_binding")] + s["schema_bindings"]:
            bound(self.root, b)
        dependencies = decode(bound(self.root, s["dependency_selection_binding"]))
        shape(dependencies, ("schema_version", "files", "authority_effect"))
        require(dependencies["schema_version"] == "cal.define.host-dependencies/v1" and dependencies["authority_effect"] == "none" and len(dependencies["files"]) <= 1024, "invalid-host-dependencies")
        for b in dependencies["files"]:bound(self.root, b)

    def call(self, operation, payload):
        self.guard()
        require(operation in self.selection["operation_mapping"], "host-operation-unavailable", operation + " is not selected", 3)
        nonce = secrets.token_hex(32)
        message = {"schema_version": "cal.define.host-call/v1", "operation": self.selection["operation_mapping"][operation],
                   "selection_binding": binding(self.raw, self.path.name), "nonce": nonce, "payload": payload, "authority_effect": "none"}
        raw = encode(message);require(len(raw) <= min(1048576, self.selection["limits"]["max_frame_bytes"]), "host-frame-budget")
        # Only the externally installed/pinned host entrypoint executes. No executable is accepted in a Pack or request.
        entrypoint = self.root / self.selection["host_binding"]["path"]
        with subprocess.Popen([sys.executable, "-I", "-B", str(entrypoint), "--selection", str(self.path)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, cwd=self.root) as process:
            try:
                stdout, _ = process.communicate(raw, timeout=60)
            except KeyboardInterrupt:
                process.kill();process.communicate()
                require(False, "host-outcome-unknown", "Interrupted host operation; inspect the original operation before retrying", 130)
            except subprocess.TimeoutExpired:
                process.kill();process.communicate()
                require(False, "host-outcome-unknown", "Host timeout; inspect the original operation before retrying", 3)
            require(process.returncode == 0 and len(stdout) <= 1048576, "host-refused", "Selected host refused; no successful effect is inferred", 3)
        response = decode(stdout, maximum=1048576)
        shape(response, ("schema_version", "nonce", "request_sha256", "result", "authority_effect"))
        require(response["schema_version"] == "cal.define.host-reply/v1" and response["nonce"] == nonce and response["request_sha256"] == sha(raw) and response["authority_effect"] == "none", "host-reply-binding-mismatch", exit_code=3)
        self.guard()
        return response["result"]

    def permit(self, operation, scope, subject):
        result = self.call("verify-scoped-operator", {"operation": operation, "scope_ref": scope, "subject_sha256": subject})
        shape(result, ("verified", "operation", "scope_ref", "subject_sha256", "principal_ref", "policy_observation_binding", "expires_at", "authority_effect"))
        require(result["verified"] is True and result["operation"] == operation and result["scope_ref"] == scope and result["subject_sha256"] == subject and result["authority_effect"] == "none", "authority-unavailable", exit_code=3)
        try:expiry = datetime.fromisoformat(result["expires_at"].replace("Z", "+00:00"))
        except (ValueError, TypeError):require(False, "invalid-host-expiry", exit_code=3)
        require(expiry.tzinfo is not None and datetime.now(timezone.utc) < expiry, "permission-expired", exit_code=3)
        return result
