#!/usr/bin/env python3
"""Validate the approval and admission boundary audit."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    tracked = [ROOT / "audit.json", ROOT / "AUDIT.md"]
    before = {path.name: sha(path) for path in tracked}
    run = subprocess.run([sys.executable, str(ROOT / "build.py")], cwd=LAB, capture_output=True, text=True, check=False)
    after = {path.name: sha(path) for path in tracked}
    audit = load(ROOT / "audit.json")
    checks = []

    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    check("deterministic-build", run.returncode == 0 and before == after, {"returncode": run.returncode, "stable": before == after})
    sources = audit["source_bindings"]
    source_pairs = [sources["definition_registry"], sources["artifact_type_registry"], sources["pending_successor"]]
    source_pairs.extend({"path": item["decision_path"], "sha256": item["decision_sha256"]} for item in sources["decisions"])
    source_pairs.extend({"path": item["authorization_path"], "sha256": item["authorization_sha256"]} for item in sources["decisions"])
    source_pairs.extend({"path": item["path"], "sha256": item["sha256"]} for item in sources["definitions"])
    current = [{"path": item["path"], "current": sha(LAB / item["path"]) == item["sha256"]} for item in source_pairs]
    check("source-bindings-current", all(item["current"] for item in current), current)
    definition_ids = {item["definition_id"] for item in sources["definitions"]}
    expected_definitions = {"cal.definition.authority-boundary", "cal.definition.decision-bundle", "cal.definition.decision-checkpoint", "cal.definition.user-decision-preference", "cal.definition.workflow-decision-profile", "cal.definition.decision", "cal.definition.decision-scope", "cal.definition.derived-refresh"}
    check("admitted-definition-basis", definition_ids == expected_definitions and all(item["lifecycle_state"] == "admitted" for item in sources["definitions"]), sorted(definition_ids))
    missing = set(audit["carrier_gap"]["missing"])
    expected_missing = {"cal.artifact-type.authority-boundary/v1", "cal.artifact-type.decision-bundle/v1", "cal.artifact-type.decision-checkpoint/v1", "cal.artifact-type.user-decision-preference/v1", "cal.artifact-type.workflow-decision-profile/v1", "cal.artifact-type.admission-transaction/v1"}
    check("carrier-gap-exact", missing == expected_missing, sorted(missing))
    check("decision-chain-reviewed", [item["number"] for item in sources["decisions"]] == [70, 71, 72, 73] and all(item["verbatim_user_authorization"] for item in sources["decisions"]), sources["decisions"])
    assessment = {item["boundary"]: item for item in audit["current_boundary_assessment"]}
    d74 = assessment["Proposed D74 admission of the D73 Project State successor"]
    check("approval-loop-rejected", d74["decision_identity"] == "unnecessary" and d74["separate_human_checkpoint"] == "reject" and audit["history_disposition"]["pending_decision_0074"] == "do-not-admit-under-the-old-boundary-pattern", d74)
    model = audit["revised_model"]
    check("single-checkpoint-separate-authority", "one human Decision Checkpoint" in model["human_checkpoint_rule"] and "independently scoped Decision members" in model["human_checkpoint_rule"] and "retains its own Decision identity" in model["decision_identity_rule"], {"checkpoint": model["human_checkpoint_rule"], "identity": model["decision_identity_rule"]})
    check("deterministic-consequences-no-reapproval", "require no second approval" in model["project_state_rule"] and any("deterministic Project State successor" in item for item in model["no_new_checkpoint_for"]), model["no_new_checkpoint_for"])
    check("history-preserved", audit["history_disposition"]["rewrite_or_merge"] is False and audit["history_disposition"]["decisions_0070_through_0073"] == "preserve-as-admitted-history", audit["history_disposition"])
    check("authority-effect-none", audit["authority_effect"] == "none" and audit["status"] == "candidate-awaiting-owner-review", {"authority_effect": audit["authority_effect"], "status": audit["status"]})
    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL"
    receipt = {"schema_version": "cyberalchemy-lab-approval-admission-boundary-audit-validation/v1", "result": result, "checks": checks, "materials": {"audit_sha256": sha(ROOT / "audit.json")}, "claim_ceiling": audit["claim_ceiling"]}
    receipt_path = ROOT / "receipts/validation.json"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"result": result, "checks": len(checks), **receipt["materials"]}, sort_keys=True))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
