#!/usr/bin/env python3
"""Preflight or atomically apply Decision 0071."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
PROPOSAL = HERE / "proposal"
AUTHORIZATION = HERE / "authorization.json"
FINAL = LAB / "authority/admissions/cyberalchemy-lab-operational-foundation/v1"
DECISION = "CAL-DECISION-0071-CYBERALCHEMY-LAB-OPERATIONAL-FOUNDATION-ADMISSION"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> tuple[dict[str, Any], dict[str, Any]]:
    run = subprocess.run([sys.executable, str(PROPOSAL / "validate.py")], cwd=LAB, check=False)
    if run.returncode != 0:
        raise RuntimeError("proposal validation failed")
    validation = load(PROPOSAL / "validation.json")
    proposal = load(PROPOSAL / "proposal.json")
    if validation["result"] != "PASS" or validation["materials"]["proposal_sha256"] != sha(PROPOSAL / "proposal.json"):
        raise RuntimeError("proposal validation is stale")
    authorization = load(AUTHORIZATION)
    required = {
        "schema_version": "cyberalchemy-lab-owner-authorization/v1",
        "decision_id": DECISION,
        "authorized": True,
        "proposal_path": str((PROPOSAL / "proposal.json").relative_to(LAB)),
        "proposal_sha256": sha(PROPOSAL / "proposal.json"),
    }
    for key, value in required.items():
        if authorization.get(key) != value:
            raise RuntimeError(f"authorization mismatch at {key}: {authorization.get(key)!r} != {value!r}")
    expected_effects = {"artifact_instances_admitted": 9, "typed_relation_instances_admitted": 13, "history_streams_declared": 2, "runtime_activations": 0}
    if authorization.get("interpreted_scope") != expected_effects or proposal["proposed_effects"] != expected_effects:
        raise RuntimeError("authorization scope does not equal proposal effects")
    if not authorization.get("verbatim_user_authorization", "").strip():
        raise RuntimeError("verbatim owner authorization is empty")
    return proposal, authorization


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    proposal, authorization = verify()
    if not args.apply:
        print(json.dumps({"result": "PASS", "mode": "preflight", "proposal_sha256": sha(PROPOSAL / "proposal.json"), "bundle_sha256": sha(PROPOSAL / "bundle-postimage/bundle.json")}, sort_keys=True))
        return 0

    if FINAL.exists():
        if sha(FINAL / "bundle.json") != proposal["postimage"]["sha256"]:
            raise RuntimeError("final admission path exists with different bytes")
    else:
        FINAL.parent.mkdir(parents=True, exist_ok=True)
        stage_root = Path(tempfile.mkdtemp(prefix=".decision-0071-", dir=str(FINAL.parent)))
        stage = stage_root / "v1"
        try:
            shutil.copytree(PROPOSAL / "bundle-postimage", stage)
            if sha(stage / "bundle.json") != proposal["postimage"]["sha256"]:
                raise RuntimeError("staged bundle digest mismatch")
            os.replace(stage, FINAL)
        finally:
            shutil.rmtree(stage_root, ignore_errors=True)

    decision = {
        "schema_version": "cyberalchemy-lab-operational-foundation-decision/v1",
        "decision_id": DECISION,
        "title": "Admit the smallest real CyberAlchemy Lab operational foundation",
        "status": "owner-admitted",
        "decided_at": "2026-10-06",
        "owner_ref": "role:repository-owner",
        "authority_effect": "operational-foundation-instance-admission-only",
        "authorization": {"path": str(AUTHORIZATION.relative_to(LAB)), "sha256": sha(AUTHORIZATION), "verbatim_user_authorization": authorization["verbatim_user_authorization"]},
        "proposal": {"path": str((PROPOSAL / "proposal.json").relative_to(LAB)), "sha256": sha(PROPOSAL / "proposal.json")},
        "admission_bundle": {"path": str((FINAL / "bundle.json").relative_to(LAB)), "sha256": sha(FINAL / "bundle.json")},
        "effects": proposal["proposed_effects"],
        "decision_effect": [
            "Admit nine exact operational foundation artifact instances.",
            "Admit thirteen exact Typed Relation instances connecting those roots.",
            "Declare the two Project history streams initialized empty at cursor zero.",
            "Require Decision 0071 and this bundle to enter the first successor Project State through governed events.",
        ],
        "excluded_effects": proposal["excluded_effects"],
        "claim_ceiling": "Decision 0071 establishes durable operational roots and generation rules only. It does not create real work records, an Agent Session, evidence, ontology projections, implementation adoption, or runtime activation.",
    }
    dump(HERE / "decision.json", decision)
    lines = [
        "# Decision 0071: CyberAlchemy Lab operational foundation admission",
        "",
        "Status: **owner-admitted**",
        "",
        "The repository now has one admitted operational root from which real future work can generate successor Project State, bounded Agent context, evidence, and ontology projections.",
        "",
        "## Admitted",
        "",
        "- `9` exact artifact instances",
        "- `13` exact Typed Relation instances",
        "- `2` initialized-empty Project history stream declarations",
        "- `0` runtime activations",
        "",
        "The initial Project State is fixed at Decision 0070. This decision and bundle must appear in its first governed successor.",
        "",
        "## Claim ceiling",
        "",
        decision["claim_ceiling"],
        "",
    ]
    (HERE / "DECISION.md").write_text("\n".join(lines), encoding="utf-8")
    receipt = {
        "schema_version": "cyberalchemy-lab-operational-foundation-application-receipt/v1",
        "result": "PASS",
        "decision_id": DECISION,
        "applied_at": "2026-10-06",
        "materials": {"decision_sha256": sha(HERE / "decision.json"), "bundle_sha256": sha(FINAL / "bundle.json"), "authorization_sha256": sha(AUTHORIZATION), "proposal_sha256": sha(PROPOSAL / "proposal.json")},
        "effects": proposal["proposed_effects"],
        "claim_ceiling": decision["claim_ceiling"],
    }
    dump(HERE / "receipts/application.json", receipt)
    print(json.dumps({"result": "PASS", "mode": "applied", "decision_sha256": receipt["materials"]["decision_sha256"], "bundle_sha256": receipt["materials"]["bundle_sha256"], **proposal["proposed_effects"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
