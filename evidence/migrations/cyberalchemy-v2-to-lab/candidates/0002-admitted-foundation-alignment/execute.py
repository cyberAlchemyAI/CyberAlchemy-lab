#!/usr/bin/env python3
"""Verify/rehearse successor 0002 or execute from a separate admitted decision record."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[4]
PREDECESSOR_EXECUTOR = ROOT.parent / "0001-full-migration-architecture/execute.py"
spec = importlib.util.spec_from_file_location("migration_candidate_0001_executor", PREDECESSOR_EXECUTOR)
mechanics = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mechanics)
mechanics.ROOT = ROOT


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_decision_record(path: Path) -> list[str]:
    failures: list[str] = []
    record = load(path)
    errors = sorted(error.message for error in jsonschema.Draft202012Validator(load(ROOT / "decision-record.schema.json")).iter_errors(record))
    failures.extend(f"schema:{error}" for error in errors)
    request_path = ROOT / "receipts/decision-request/decision-request-set.json"
    receipt_path = ROOT / "receipts/validation.json"
    expected = {
        "decision_request_set_path": request_path.relative_to(LAB).as_posix(),
        "decision_request_set_sha256": sha(request_path) if request_path.is_file() else "missing",
        "candidate_manifest_sha256": sha(ROOT / "manifest.json"),
        "validation_receipt_sha256": sha(receipt_path),
    }
    for key, value in expected.items():
        if record.get(key) != value:
            failures.append(f"binding-mismatch:{key}")
    request_set = load(request_path) if request_path.is_file() else {"requests": []}
    expected_requests = {item["request_id"]: item for item in request_set["requests"]}
    observed = {item.get("request_id"): item for item in record.get("decisions", [])}
    if set(observed) != set(expected_requests):
        failures.append("decision-request-set-not-closed")
    for request_id, request in expected_requests.items():
        decision = observed.get(request_id, {})
        if decision.get("decision_kind") != request["decision_kind"] or decision.get("owner_ref") != request["owner_ref"] or decision.get("outcome") != "approved" or decision.get("authorized_effect") != request["requested_effect"]:
            failures.append(f"decision-mismatch:{request_id}")
    if record.get("copy_boundary") != {"additive_only": True, "overwrite": False, "source_mutation": False, "source_deletion": False, "publication": False}:
        failures.append("copy-boundary-mismatch")
    if load(receipt_path).get("result") != "PASS":
        failures.append("validation-receipt-not-pass")
    return failures


def execute(path: Path) -> int:
    failures = validate_decision_record(path)
    if failures:
        print("EXECUTION=BLOCK")
        print("REASONS=" + ",".join(failures))
        return 1
    _, precondition_failures = mechanics.verify()
    if precondition_failures:
        print("EXECUTION=BLOCK")
        print(f"PRECONDITION_FAILURES={len(precondition_failures)}")
        return 1
    record_sha = sha(path)
    journal: list[dict[str, Any]] = []
    for entry in load(ROOT / "copy-allowlist.json")["entries"]:
        if entry["action"] == "preserve-existing":
            journal.append({"target_path": entry["target_path"], "action": "preserved-existing", "sha256": entry["source_sha256"]})
            continue
        source = mechanics.SOURCE / entry["source_path"]
        target = mechanics.safe_target(entry["target_path"])
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            with source.open("rb") as source_handle, target.open("xb") as target_handle:
                shutil.copyfileobj(source_handle, target_handle)
            os.chmod(target, entry["mode"])
        except Exception as error:
            dump(ROOT / "receipts/execution-partial.json", {"schema_version": "cyberalchemy-lab-migration-execution-receipt/v2", "result": "PARTIAL-STOPPED", "decision_record_sha256": record_sha, "journal": journal, "failure": {"target_path": entry["target_path"], "error": str(error)}, "rollback_authorized": False})
            print("EXECUTION=PARTIAL-STOPPED")
            return 1
        journal.append({"target_path": entry["target_path"], "action": "created", "sha256": entry["source_sha256"]})
    dump(ROOT / "receipts/execution.json", {"schema_version": "cyberalchemy-lab-migration-execution-receipt/v2", "result": "PASS", "authority_effect": "exact-additive-copy-completed", "decision_record_sha256": record_sha, "candidate_manifest_sha256": sha(ROOT / "manifest.json"), "validation_receipt_sha256": sha(ROOT / "receipts/validation.json"), "journal": journal, "source_mutated": False, "rollback_authorized": False, "claim_ceiling": "Records exact additive copy only; imports remain unadmitted and inactive."})
    print("EXECUTION=PASS")
    print(f"JOURNAL_ENTRIES={len(journal)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--rehearse-sample", action="store_true")
    mode.add_argument("--execute", action="store_true")
    parser.add_argument("--decision-record", type=Path)
    args = parser.parse_args()
    if args.execute:
        if args.decision_record is None:
            print("EXECUTION=BLOCK\nREASON=missing-separate-decision-record")
            return 1
        return execute(args.decision_record.resolve())
    if args.rehearse_sample:
        result = mechanics.rehearse()
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["result"] == "PASS" else 1
    checks, failures = mechanics.verify()
    result = {"schema_version": "cyberalchemy-lab-migration-dry-run/v2", "result": "PASS" if not failures else "BLOCK", "authority_effect": "none", "checked": len(checks), "failures": failures, "target_mutated": False, "source_mutated": False, "decision_record_required_for_execution": True}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
