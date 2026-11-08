"""Scan seven exact retained public Machine replies without retaining private inputs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import stat
import types


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PRIVACY_PATH = ROOT / "implementation/lab-runtime/local-host/t20-local-privacy-0001/scan.py"
PRIVACY_SHA = "8d01bcb71ade520f9fc8a168e4708bf3509a1a4cbdba1424ade2eddd0296e76b"
T05_PATH = ROOT / "implementation/lab-runtime/local-host/working/t05-api33-local-result-0001/RESULT.json"
T05_SHA = "38286bb9a53f768c50f751e6705e4afa177775f11759c814069fa089a1978668"
OPERATIONS = ("lab.status", "catalog.get", "artifact.query", "artifact.inspect",
              "context.get", "session.inspect", "operation.inspect")
PROFILE_REF = "product/lab/release-candidates/v1/interface/api-integration-v33-current-0001/contract-profile.json"
TEST_REF = "_cal_api30_current_source8_successor_0001.test_machine_transport.MachineTransport.test_02_all_seven_public_read_operations_with_actual_Actor"
CREDENTIAL_SCHEME = re.compile(rb"\b(?:Bearer|Basic|Token)\s+\S+", re.I)
SENSITIVE_FRAGMENT = ("privatekey", "secret", "credential", "password", "apikey",
                      "accesstoken", "refreshtoken", "bearertoken", "signingkey",
                      "keymaterial", "cookie")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def need(value: bool, reason: str) -> None:
    if not value:
        raise ValueError(reason)


def selected(path: Path, expected: str) -> bytes:
    need(path.is_relative_to(ROOT) and stat.S_ISREG(path.lstat().st_mode),
         "selected output path unavailable")
    for ancestor in (path, *path.parents):
        if ancestor == ROOT.parent:
            break
        need(not ancestor.is_symlink(), "selected output linked")
    raw = path.read_bytes()
    need(sha(raw) == expected, "selected output bytes changed")
    return raw


def scanner():
    raw = selected(PRIVACY_PATH, PRIVACY_SHA)
    module = types.ModuleType("_cal_t20_selected_scanner")
    module.__file__ = str(PRIVACY_PATH)
    exec(compile(raw, str(PRIVACY_PATH), "exec"), module.__dict__)
    need(sha(PRIVACY_PATH.read_bytes()) == PRIVACY_SHA, "selected scanner changed")
    return module


def inspect_public(raw: bytes, old) -> None:
    value = old.strict_json(raw)
    old.scan_json(value)
    need(not old.PRIVATE_BLOCK.search(raw), "private key block in public reply")
    need(not old.PRIVATE_LOCATOR.search(raw), "owned private locator in public reply")
    need(not old.SECRET_ASSIGNMENT.search(raw), "secret assignment in public reply")
    need(not CREDENTIAL_SCHEME.search(raw), "credential scheme in public reply")

    def visit(item):
        if isinstance(item, dict):
            for key, child in item.items():
                normalized = re.sub(r"[^a-z0-9]", "", str(key).lower())
                sensitive = normalized in ("token", "authtoken", "authorization") or any(
                    fragment in normalized for fragment in SENSITIVE_FRAGMENT)
                empty = child is None or child is False or child == "" or child == [] or child == {}
                need(not sensitive or empty, "populated credential-like field in public reply")
                visit(child)
        elif isinstance(item, list):
            for child in item:
                visit(child)
    visit(value)


def verify_observation(body: dict, operation: str, profile_sha: str) -> None:
    need(body["test_ref"] == TEST_REF and body["authority_effect"] == "none" and
         body["actual_owner_outcome"] is None and body["task_complete"] is False,
         "public observation provenance or claim differs")
    reply = body["actual_public_reply"]
    need(reply["kind"] == "result" and reply["operation"] == operation and
         body["request_sha256"] == reply["request_binding"]["sha256"] and
         reply["contract_profile_binding"] ==
         {"ref": PROFILE_REF, "sha256": profile_sha},
         "public observation request/profile join differs")


def run() -> dict:
    old = scanner()
    result = old.strict_json(selected(T05_PATH, T05_SHA))
    need(result["result"] == "PASS-LOCAL" and
         result["machine_cases_passed"] == result["machine_cases_selected"] == 14 and
         len(result["seven_actual_read_result_receipts"]) == 7,
         "selected seven-reply source differs")
    observed = []
    for expected_op, row in zip(OPERATIONS, result["seven_actual_read_result_receipts"], strict=True):
        need(row["operation"] == expected_op and isinstance(row["sha256"], str),
             "selected reply order differs")
        path = ROOT / row["path"]
        raw = selected(path, row["sha256"])
        inspect_public(raw, old)
        body = old.strict_json(raw)
        verify_observation(body, expected_op, result["profile_sha256"])
        observed.append({"operation": expected_op, "public_observation_sha256": row["sha256"],
                         "public_bytes": len(raw)})
    return {"schema_version": "lab-T20-seven-machine-replies/v1",
            "status": "PASS-BOUNDED", "selected_t05_result_sha256": T05_SHA,
            "selected_scanner_sha256": PRIVACY_SHA, "replies": observed,
            "private_key_blocks": 0, "credential_fields": 0,
            "credential_schemes": 0, "private_runtime_locators": 0,
            "protected_source8_scanned": False, "final_family_privacy_qualified": False,
            "authority_effect": "none", "runner_sha256": sha(Path(__file__).read_bytes())}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
