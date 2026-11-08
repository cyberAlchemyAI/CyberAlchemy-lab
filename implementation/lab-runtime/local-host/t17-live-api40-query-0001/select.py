"""Select the live API40 artifact.query positive and causal refusal pair."""

import hashlib
import json
import os
from pathlib import Path
import stat

ROOT = Path(__file__).resolve().parents[4]
PINS = {
    "implementation/lab-runtime/local-host/t17-live-api40-query-0001/RUN-0002.json": "1aeb4480d47a538fb639af8dcfea93ae0b64943dd3e5df7461a63ecf16dcca9b",
    "implementation/lab-runtime/local-host/t17-live-api40-query-0001/run.py": "a8a19b2ac251e883141b1f0e869a3f28cf84eb363c6dea43eee36502622f4b9a",
    "implementation/lab-runtime/local-host/t17-live-api40-query-0001/reader.py": "2eb8a2ee79f7eb86025fc79def425f7f838abd45cc5624302a0a90a64d0dbdf3",
    "implementation/lab-runtime/local-host/t17-live-api40-query-0001/adapter.mjs": "8da73160ffc1d5116699e66a0622b365ea60236b40e6d01bd29eadf1c3b0fba2",
    "implementation/lab-runtime/local-host/t17-live-api40-query-0001/read-plan.json": "243f26363db6d55d452d9f4e5ff7a35eddfe98d07e96fb8b02e359cfb340cfe5",
    "implementation/lab-runtime/local-host/t17-live-api40-catalog-0001/RESULT.json": "278bc8eb3e85437ae76278ce43afcac516ea98c51da3b084ae408efab9b0eb6e",
    "product/lab/release-candidates/v1/interface/api-integration-v40-current-t06-0001/source-manifest.json": "45412c382dc0cc9c807dd2bf4ec67037c7ae58854fcbb42cb15a96f0f7f3a219",
    "product/lab/release-candidates/v1/interface/api-integration-v40-current-t06-0001/contract-profile.json": "cbfd53a80f41a2ffd7ac28b88fa9e19a232ad291c8cb3791a302a4e8349c7614",
}
RECEIPT = next(name for name in PINS if name.endswith("RUN-0002.json"))
PRIOR = next(name for name in PINS if name.endswith("t17-live-api40-catalog-0001/RESULT.json"))


def exact(name, digest, root=ROOT):
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts or relative.as_posix() != name:
        raise ValueError("unsafe selected path")
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in relative.parts[:-1]:
            next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        leaf = os.open(relative.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        try:
            if not stat.S_ISREG(os.fstat(leaf).st_mode):
                raise ValueError("selected file is not regular")
            with os.fdopen(os.dup(leaf), "rb") as source:
                raw = source.read(8 * 1024 * 1024 + 1)
            if len(raw) > 8 * 1024 * 1024 or hashlib.sha256(raw).hexdigest() != digest:
                raise ValueError("selected bytes differ")
            return raw
        finally:
            os.close(leaf)
    except OSError as error:
        raise ValueError("selected path differs") from error
    finally:
        os.close(fd)


def validate(receipt, prior):
    source = PINS[next(name for name in PINS if name.endswith("api-integration-v40-current-t06-0001/source-manifest.json"))]
    profile = PINS[next(name for name in PINS if name.endswith("api-integration-v40-current-t06-0001/contract-profile.json"))]
    runner = PINS[next(name for name in PINS if name.endswith("t17-live-api40-query-0001/run.py"))]
    reader = PINS[next(name for name in PINS if name.endswith("t17-live-api40-query-0001/reader.py"))]
    adapter = PINS[next(name for name in PINS if name.endswith("t17-live-api40-query-0001/adapter.mjs"))]
    if (receipt.get("schema_version") != "lab-T17-paperclip-api40-local-journey/v1" or
            receipt.get("status") != "PASS" or receipt.get("api_source_sha256") != source or
            receipt.get("api_profile_sha256") != profile or
            receipt.get("orchestrator_sha256") != runner or
            receipt.get("reader_sha256") != reader or
            receipt.get("adapter_invoker_sha256") != adapter or
            receipt.get("api40_child_exit_code") != 0 or
            receipt.get("paperclip_process_exit_code") != 0 or
            receipt.get("process_agent_invoked") is not True or
            receipt.get("disposable_control_removed") is not True or
            receipt.get("lab_mutations_requested") != 0 or
            receipt.get("workspace_before") != {"objects": 0, "effect_journal": 0, "session_custody_lock": 0} or
            receipt.get("workspace_after") != {"objects": 0, "effect_journal": 0, "session_custody_lock": 1} or
            prior.get("cumulative_live_operation_count") != 3 or
            prior.get("remaining_live_operation_count") != 31 or
            prior.get("T17_complete") is not False or
            prior.get("api_source_sha256") != source or
            prior.get("api_profile_sha256") != profile):
        raise ValueError("selected live cut differs")
    rows = receipt.get("actual_lab_calls")
    expected = [("lab.status", "positive", "result", None),
                ("catalog.get", "positive", "result", None),
                ("lab.status", "wrong-scope", "error", "unauthorized"),
                ("catalog.get", "wrong-context", "error", "unauthorized"),
                ("artifact.query", "positive", "result", None),
                ("artifact.query", "wrong-scope", "error", "unauthorized")]
    if (not isinstance(rows, list) or len(rows) != 6 or
            [(row.get("operation"), row.get("case"), row.get("kind"), row.get("code")) for row in rows] != expected):
        raise ValueError("query positive/refusal pair differs")
    if (any(not isinstance(row.get(key), str) or len(row[key]) != 64
            for row in rows for key in ("request_sha256", "reply_sha256")) or
            rows[4]["request_sha256"] == rows[5]["request_sha256"] or
            rows[4]["reply_sha256"] == rows[5]["reply_sha256"]):
        raise ValueError("query request/response bindings differ")
    return {"schema_version": "lab-T17-api40-base-query-live-slice/v1",
            "api_source_sha256": source, "api_profile_sha256": profile,
            "live_receipt_sha256": PINS[RECEIPT], "previous_catalog_slice_sha256": PINS[PRIOR],
            "operation": "artifact.query", "positive_request_sha256": rows[4]["request_sha256"],
            "positive_reply_sha256": rows[4]["reply_sha256"],
            "negative_request_sha256": rows[5]["request_sha256"],
            "negative_reply_sha256": rows[5]["reply_sha256"],
            "negative_code": "unauthorized", "negative_case": "wrong-scope", "same_child": True,
            "effect_journal_before": 0, "effect_journal_after": 0,
            "cumulative_live_operation_count": 4, "remaining_live_operation_count": 30,
            "T17_complete": False, "authority_effect": "none"}


def select():
    bodies = {name: exact(name, digest) for name, digest in PINS.items()}
    return validate(json.loads(bodies[RECEIPT]), json.loads(bodies[PRIOR]))


if __name__ == "__main__":
    print(json.dumps(select(), sort_keys=True, indent=2))
