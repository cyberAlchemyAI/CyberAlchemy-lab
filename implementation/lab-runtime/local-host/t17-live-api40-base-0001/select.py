"""Cold-select the observed API40 lab.status positive and wrong-scope pair."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PINS = {
    "implementation/lab-runtime/local-host/t23-paperclip-api40-local-0001/RUN-0007.json": "6ee0499a0464954413d72013ba5c7ba7f4fa90a7a2aa63be8edec634c07c8ff5",
    "implementation/lab-runtime/local-host/t23-paperclip-api40-local-0001/run.py": "b07b95b838cdb42793cbe7af6391ff939036986e928bee9ca96f5081150d4ff6",
    "implementation/lab-runtime/local-host/t23-paperclip-api40-local-0001/reader.py": "7272b5ce7e728834e2a8efd71d6d255144798e227b01a5251ad03945c9ddac46",
    "implementation/lab-runtime/local-host/t23-paperclip-api40-local-0001/adapter.mjs": "5729352a220318cdc2e690062e68fd16e74c71bb4841b05643a7919bade5c356",
    "implementation/lab-runtime/local-host/t23-paperclip-api40-local-0001/read-plan.json": "585e223a079d7bfedf2d5cd5fd6d3ea2870b39fb3510dad0e5e2c32573a49298",
    "implementation/lab-runtime/local-host/working/t23-three-journeys-independent-review-0001/REVIEW.md": "a5b0fccc51daade9405cb468edeaf87006cb832f161d41f1d1a56cc7ac0e2493",
    "implementation/lab-runtime/local-host/t17-live-api40-slice-0001/RESULT.json": "a63c6e3229f0bcbfd9ad5a6d6eb5cb553cf40339de93bb583e3b49de74feb353",
    "product/lab/release-candidates/v1/interface/api-integration-v40-current-t06-0001/source-manifest.json": "45412c382dc0cc9c807dd2bf4ec67037c7ae58854fcbb42cb15a96f0f7f3a219",
    "product/lab/release-candidates/v1/interface/api-integration-v40-current-t06-0001/contract-profile.json": "cbfd53a80f41a2ffd7ac28b88fa9e19a232ad291c8cb3791a302a4e8349c7614",
}
RECEIPT = next(path for path in PINS if path.endswith("RUN-0007.json"))


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def exact(relative: str, expected: str, root: Path = ROOT) -> bytes:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != relative:
        raise ValueError("unsafe selected path")
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in path.parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        leaf = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        try:
            if not stat.S_ISREG(os.fstat(leaf).st_mode):
                raise ValueError("selected file is not regular")
            with os.fdopen(os.dup(leaf), "rb") as stream:
                raw = stream.read(8 * 1024 * 1024 + 1)
            if len(raw) > 8 * 1024 * 1024 or sha(raw) != expected:
                raise ValueError("selected bytes differ")
            return raw
        finally:
            os.close(leaf)
    except OSError as error:
        raise ValueError("selected path differs") from error
    finally:
        os.close(fd)


def validate(receipt: dict, prior: dict) -> dict:
    if (receipt.get("schema_version") != "lab-T23-paperclip-api40-local-journey/v1" or
            receipt.get("status") != "PASS" or
            receipt.get("api40_child_exit_code") != 0 or
            receipt.get("paperclip_process_exit_code") != 0 or
            receipt.get("api_source_sha256") != PINS[next(p for p in PINS if p.endswith("api-integration-v40-current-t06-0001/source-manifest.json"))] or
            receipt.get("api_profile_sha256") != PINS[next(p for p in PINS if p.endswith("api-integration-v40-current-t06-0001/contract-profile.json"))] or
            receipt.get("orchestrator_sha256") != PINS[next(p for p in PINS if p.endswith("t23-paperclip-api40-local-0001/run.py"))] or
            receipt.get("reader_sha256") != PINS[next(p for p in PINS if p.endswith("t23-paperclip-api40-local-0001/reader.py"))] or
            receipt.get("adapter_invoker_sha256") != PINS[next(p for p in PINS if p.endswith("t23-paperclip-api40-local-0001/adapter.mjs"))] or
            receipt.get("process_agent_invoked") is not True or
            receipt.get("disposable_control_removed") is not True or
            receipt.get("lab_mutations_requested") != 0 or
            receipt.get("workspace_before") != {"objects": 0, "effect_journal": 0, "session_custody_lock": 0} or
            receipt.get("workspace_after") != {"objects": 0, "effect_journal": 0, "session_custody_lock": 1} or
            prior.get("qualified_operation_slice") != ["action.dispatch"] or
            prior.get("T17_complete") is not False):
        raise ValueError("selected live cut differs")
    rows = receipt.get("actual_lab_calls")
    if not isinstance(rows, list) or len(rows) != 3:
        raise ValueError("actual Lab call inventory differs")
    expected = [("lab.status", "positive", "result", None),
                ("catalog.get", "positive", "result", None),
                ("lab.status", "wrong-scope", "error", "unauthorized")]
    if [(r.get("operation"), r.get("case"), r.get("kind"), r.get("code")) for r in rows] != expected:
        raise ValueError("positive/refusal pair differs")
    if (rows[0].get("request_sha256") == rows[2].get("request_sha256") or
            rows[0].get("reply_sha256") == rows[2].get("reply_sha256") or
            any(len(r.get("request_sha256", "")) != 64 or len(r.get("reply_sha256", "")) != 64 for r in rows)):
        raise ValueError("request/response byte bindings differ")
    return {"schema_version": "lab-T17-api40-base-status-live-slice/v1",
            "api_source_sha256": receipt["api_source_sha256"],
            "api_profile_sha256": receipt["api_profile_sha256"],
            "paperclip_receipt_sha256": PINS[RECEIPT],
            "previous_action_slice_sha256": PINS[next(p for p in PINS if p.endswith("t17-live-api40-slice-0001/RESULT.json"))],
            "operation": "lab.status", "positive_request_sha256": rows[0]["request_sha256"],
            "positive_reply_sha256": rows[0]["reply_sha256"],
            "negative_request_sha256": rows[2]["request_sha256"],
            "negative_reply_sha256": rows[2]["reply_sha256"],
            "negative_code": "unauthorized", "same_child": True,
            "effect_journal_before": 0, "effect_journal_after": 0,
            "cumulative_live_operation_count": 2,
            "remaining_live_operation_count": 32,
            "T17_complete": False, "authority_effect": "none"}


def select() -> dict:
    bodies = {name: exact(name, digest) for name, digest in PINS.items()}
    return validate(json.loads(bodies[RECEIPT]), json.loads(bodies[next(p for p in PINS if p.endswith("t17-live-api40-slice-0001/RESULT.json"))]))


if __name__ == "__main__":
    print(json.dumps(select(), sort_keys=True, indent=2))
