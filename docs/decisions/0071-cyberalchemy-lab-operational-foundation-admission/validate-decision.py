#!/usr/bin/env python3
"""Validate applied Decision 0071 and its immutable admission bundle."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
FINAL = LAB / "authority/admissions/cyberalchemy-lab-operational-foundation/v1"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[dict[str, Any]] = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    required = [HERE / "authorization.json", HERE / "decision.json", HERE / "receipts/application.json", FINAL / "bundle.json"]
    missing = [str(path.relative_to(LAB)) for path in required if not path.is_file()]
    if missing:
        print(json.dumps({"result": "FAIL", "missing": missing}, sort_keys=True))
        return 1
    authorization = load(HERE / "authorization.json")
    decision = load(HERE / "decision.json")
    receipt = load(HERE / "receipts/application.json")
    bundle = load(FINAL / "bundle.json")
    proposal = load(HERE / "proposal/proposal.json")

    check("authorization-exact", authorization["authorized"] is True and authorization["decision_id"] == decision["decision_id"] and authorization["proposal_sha256"] == sha(HERE / "proposal/proposal.json"), authorization)
    check("decision-bundle-binding", decision["admission_bundle"]["sha256"] == sha(FINAL / "bundle.json") == proposal["postimage"]["sha256"] and bundle["decision_id"] == decision["decision_id"], decision["admission_bundle"])
    files = [{"path": item["path"], "current": sha(FINAL / item["path"]) == item["sha256"]} for item in bundle["files"]]
    check("immutable-bundle-closure", all(item["current"] for item in files), files)
    artifacts = load(FINAL / "artifact-instance-admission.json")
    relations = load(FINAL / "typed-relation-admission.json")
    foundation = load(FINAL / "foundation-admission.json")
    counts = {"artifact_instances_admitted": 9, "typed_relation_instances_admitted": 13, "history_streams_declared": 2, "runtime_activations": 0}
    check("exact-effective-state", bundle["counts"] == decision["effects"] == receipt["effects"] == foundation["counts"] == counts and artifacts["count"] == 9 and relations["count"] == 13, {"bundle": bundle["counts"], "artifacts": artifacts["count"], "relations": relations["count"]})
    copied = []
    for item in artifacts["entries"] + relations["entries"]:
        path = LAB / item["admitted_instance_path"]
        copied.append({"identity": item.get("identity_ref") or item.get("relation_id"), "current": path.is_file() and sha(path) == item["admitted_instance_sha256"] == item["source_sha256"]})
    check("admitted-instance-bytes", all(item["current"] for item in copied), copied)
    histories = load(FINAL / "history-declarations.json")
    history_ok = len(histories["streams"]) == 2 and all(item["cursor"] == 0 and item["state"] == "initialized-empty" and item["runtime_active"] is False for item in histories["streams"])
    check("history-bootstrap-boundary", history_ok, histories)
    check("application-receipt-current", receipt["result"] == "PASS" and receipt["materials"]["decision_sha256"] == sha(HERE / "decision.json") and receipt["materials"]["bundle_sha256"] == sha(FINAL / "bundle.json"), receipt["materials"])

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL"
    output = {
        "schema_version": "cyberalchemy-lab-operational-foundation-decision-validation/v1",
        "result": result,
        "checks": checks,
        "materials": {"decision_sha256": sha(HERE / "decision.json"), "bundle_sha256": sha(FINAL / "bundle.json")},
        "claim_ceiling": "PASS proves Decision 0071 and its immutable operational foundation bundle remain exact. It does not establish a runtime or future generated records.",
    }
    dump(HERE / "receipts/decision-validation.json", output)
    print(json.dumps({"result": result, "checks": len(checks), **output["materials"]}, sort_keys=True))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
