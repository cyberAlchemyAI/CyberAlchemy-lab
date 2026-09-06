#!/usr/bin/env python3
"""Verify, rehearse, or explicitly execute the exact additive copy allowlist."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[4]
SOURCE = Path("/home/vrondelli/projects/domainspec-core/cyberAlchemy-v2")


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_target(relative: str, root: Path = LAB) -> Path:
    candidate = (root / relative).resolve()
    if not candidate.is_relative_to(root.resolve()):
        raise ValueError(f"target traversal: {relative}")
    return candidate


def verify() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    allowlist = load(ROOT / "copy-allowlist.json")
    checks: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for entry in allowlist["entries"]:
        source = SOURCE / entry["source_path"]
        target = safe_target(entry["target_path"])
        actual_source = sha(source) if source.is_file() else "missing"
        source_ok = actual_source == entry["source_sha256"]
        if entry["action"] == "create":
            target_ok = not target.exists()
        elif entry["action"] == "preserve-existing":
            target_ok = target.is_file() and sha(target) == entry["source_sha256"]
        else:
            target_ok = False
        result = {"source_path": entry["source_path"], "target_path": entry["target_path"], "action": entry["action"], "source_current": source_ok, "target_precondition": target_ok}
        checks.append(result)
        if not (source_ok and target_ok):
            failures.append(result)
    return checks, failures


def rehearse() -> dict[str, Any]:
    allowlist = load(ROOT / "copy-allowlist.json")
    by_rule: dict[str, list[dict[str, Any]]] = {}
    for entry in allowlist["entries"]:
        by_rule.setdefault(entry["mapping_rule_id"], []).append(entry)
    samples = [min(items, key=lambda item: (item["size"], item["source_path"])) for _, items in sorted(by_rule.items())]
    results: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="cal-migration-rehearsal-") as temporary:
        rehearsal_root = Path(temporary)
        for entry in samples:
            source = SOURCE / entry["source_path"]
            target = safe_target(entry["target_path"], rehearsal_root)
            target.parent.mkdir(parents=True, exist_ok=True)
            with source.open("rb") as source_handle, target.open("xb") as target_handle:
                shutil.copyfileobj(source_handle, target_handle)
            os.chmod(target, entry["mode"])
            results.append({"mapping_rule_id": entry["mapping_rule_id"], "source_path": entry["source_path"], "target_path": entry["target_path"], "digest_match": sha(target) == entry["source_sha256"], "mode_match": (target.stat().st_mode & 0o7777) == entry["mode"]})
    return {"sample_count": len(samples), "results": results, "temporary_tree_removed": True, "result": "PASS" if all(item["digest_match"] and item["mode_match"] for item in results) else "BLOCK"}


def execute(authorization_path: Path) -> int:
    authorization = load(authorization_path)
    receipt_path = ROOT / "receipts/validation.json"
    expected = {
        "candidate_manifest_sha256": sha(ROOT / "manifest.json"),
        "validation_receipt_sha256": sha(receipt_path),
        "execution_authorized": True,
    }
    if authorization != expected:
        print("EXECUTION=BLOCK")
        print("REASON=authorization-envelope-mismatch")
        return 1
    validation = load(receipt_path)
    if validation.get("result") != "PASS" or validation.get("assessment", {}).get("product_approval") != "granted-by-exact-owner-decision":
        print("EXECUTION=BLOCK")
        print("REASON=product-approval-not-bound")
        return 1
    _, failures = verify()
    if failures:
        print("EXECUTION=BLOCK")
        print(f"PRECONDITION_FAILURES={len(failures)}")
        return 1
    journal: list[dict[str, Any]] = []
    for entry in load(ROOT / "copy-allowlist.json")["entries"]:
        if entry["action"] == "preserve-existing":
            journal.append({"target_path": entry["target_path"], "action": "preserved-existing", "sha256": entry["source_sha256"]})
            continue
        source = SOURCE / entry["source_path"]
        target = safe_target(entry["target_path"])
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            with source.open("rb") as source_handle, target.open("xb") as target_handle:
                shutil.copyfileobj(source_handle, target_handle)
            os.chmod(target, entry["mode"])
        except Exception as error:
            dump(ROOT / "receipts/execution-partial.json", {"schema_version": "cyberalchemy-lab-migration-execution-receipt/v1", "result": "PARTIAL-STOPPED", "authority_effect": "partial-target-copy", "journal": journal, "failure": {"target_path": entry["target_path"], "error": str(error)}, "rollback_authorized": False})
            raise
        journal.append({"target_path": entry["target_path"], "action": "created", "sha256": entry["source_sha256"]})
    dump(ROOT / "receipts/execution.json", {"schema_version": "cyberalchemy-lab-migration-execution-receipt/v1", "result": "PASS", "authority_effect": "exact-additive-copy-completed", "manifest_sha256": expected["candidate_manifest_sha256"], "validation_receipt_sha256": expected["validation_receipt_sha256"], "journal": journal, "source_mutated": False, "rollback_authorized": False, "claim_ceiling": "Records exact additive copy only; imported artifacts remain unadmitted and inactive."})
    print("EXECUTION=PASS")
    print(f"JOURNAL_ENTRIES={len(journal)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--rehearse-sample", action="store_true")
    mode.add_argument("--execute", action="store_true")
    parser.add_argument("--authorization", type=Path)
    args = parser.parse_args()
    if args.execute:
        if args.authorization is None:
            print("EXECUTION=BLOCK\nREASON=missing-authorization-file")
            return 1
        return execute(args.authorization)
    if args.rehearse_sample:
        result = rehearse()
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["result"] == "PASS" else 1
    checks, failures = verify()
    result = {"schema_version": "cyberalchemy-lab-migration-dry-run/v1", "result": "PASS" if not failures else "BLOCK", "authority_effect": "none", "checked": len(checks), "failures": failures, "target_mutated": False, "source_mutated": False}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
