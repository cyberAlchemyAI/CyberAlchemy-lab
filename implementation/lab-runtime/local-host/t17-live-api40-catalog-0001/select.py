"""Select the live API40 catalog positive and causal refusal pair."""

import hashlib
import json
import os
from pathlib import Path
import stat

ROOT = Path(__file__).resolve().parents[4]
PINS = {
    "implementation/lab-runtime/local-host/t17-live-api40-catalog-0001/RUN-0002.json": "2cf9f606bb7c7b62c974846c7868e4d1bef9dd994711427a0f6b20242f495127",
    "implementation/lab-runtime/local-host/t17-live-api40-catalog-0001/run.py": "76916ae9ff5a4fffd0af5b540e4c5e34529ab188ce8afc50b553e8004d635a67",
    "implementation/lab-runtime/local-host/t17-live-api40-catalog-0001/reader.py": "c8da81aecd6323391e96c67f2511837946fb86dd3f6da56663d9e9d2f29010de",
    "implementation/lab-runtime/local-host/t17-live-api40-catalog-0001/adapter.mjs": "8da73160ffc1d5116699e66a0622b365ea60236b40e6d01bd29eadf1c3b0fba2",
    "implementation/lab-runtime/local-host/t17-live-api40-catalog-0001/read-plan.json": "585e223a079d7bfedf2d5cd5fd6d3ea2870b39fb3510dad0e5e2c32573a49298",
    "implementation/lab-runtime/local-host/t17-live-api40-base-0001/RESULT.json": "9e60dcb6f0e9fe303b6c368ecc95530063a61bde5ec56fc9a3652620321b2df1",
    "product/lab/release-candidates/v1/interface/api-integration-v40-current-t06-0001/source-manifest.json": "45412c382dc0cc9c807dd2bf4ec67037c7ae58854fcbb42cb15a96f0f7f3a219",
    "product/lab/release-candidates/v1/interface/api-integration-v40-current-t06-0001/contract-profile.json": "cbfd53a80f41a2ffd7ac28b88fa9e19a232ad291c8cb3791a302a4e8349c7614",
}
RECEIPT = next(name for name in PINS if name.endswith("RUN-0002.json"))
PRIOR = next(name for name in PINS if name.endswith("t17-live-api40-base-0001/RESULT.json"))


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
    runner = PINS[next(name for name in PINS if name.endswith("t17-live-api40-catalog-0001/run.py"))]
    reader = PINS[next(name for name in PINS if name.endswith("t17-live-api40-catalog-0001/reader.py"))]
    adapter = PINS[next(name for name in PINS if name.endswith("t17-live-api40-catalog-0001/adapter.mjs"))]
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
            prior.get("cumulative_live_operation_count") != 2 or
            prior.get("remaining_live_operation_count") != 32 or
            prior.get("T17_complete") is not False or
            prior.get("api_source_sha256") != source or
            prior.get("api_profile_sha256") != profile):
        raise ValueError("selected live cut differs")
    rows = receipt.get("actual_lab_calls")
    expected = [("lab.status", "positive", "result", None),
                ("catalog.get", "positive", "result", None),
                ("lab.status", "wrong-scope", "error", "unauthorized"),
                ("catalog.get", "wrong-context", "error", "unauthorized")]
    if (not isinstance(rows, list) or len(rows) != 4 or
            [(row.get("operation"), row.get("case"), row.get("kind"), row.get("code")) for row in rows] != expected):
        raise ValueError("catalog positive/refusal pair differs")
    if (any(not isinstance(row.get(key), str) or len(row[key]) != 64
            for row in rows for key in ("request_sha256", "reply_sha256")) or
            rows[1]["request_sha256"] == rows[3]["request_sha256"] or
            rows[1]["reply_sha256"] == rows[3]["reply_sha256"]):
        raise ValueError("catalog request/response bindings differ")
    return {"schema_version": "lab-T17-api40-base-catalog-live-slice/v1",
            "api_source_sha256": source, "api_profile_sha256": profile,
            "live_receipt_sha256": PINS[RECEIPT], "previous_status_slice_sha256": PINS[PRIOR],
            "operation": "catalog.get", "positive_request_sha256": rows[1]["request_sha256"],
            "positive_reply_sha256": rows[1]["reply_sha256"],
            "negative_request_sha256": rows[3]["request_sha256"],
            "negative_reply_sha256": rows[3]["reply_sha256"],
            "negative_code": "unauthorized", "negative_case": "wrong-context", "same_child": True,
            "effect_journal_before": 0, "effect_journal_after": 0,
            "cumulative_live_operation_count": 3, "remaining_live_operation_count": 31,
            "T17_complete": False, "authority_effect": "none"}


def select():
    bodies = {name: exact(name, digest) for name, digest in PINS.items()}
    return validate(json.loads(bodies[RECEIPT]), json.loads(bodies[PRIOR]))


if __name__ == "__main__":
    print(json.dumps(select(), sort_keys=True, indent=2))
