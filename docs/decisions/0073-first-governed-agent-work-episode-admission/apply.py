#!/usr/bin/env python3
"""Preflight or atomically apply Decision 0073."""
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


HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
PROPOSAL = HERE / "proposal"
AUTHORIZATION = HERE / "authorization.json"
FINAL = LAB / "authority/admissions/first-governed-agent-work-episode/v1"
DECISION = "CAL-DECISION-0073-FIRST-GOVERNED-AGENT-WORK-EPISODE-ADMISSION"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> tuple[dict, dict]:
    run = subprocess.run([sys.executable, str(PROPOSAL / "validate.py")], cwd=LAB, check=False)
    if run.returncode:
        raise RuntimeError("proposal validation failed")
    validation = load(PROPOSAL / "validation.json")
    proposal = load(PROPOSAL / "proposal.json")
    authorization = load(AUTHORIZATION)
    if validation["result"] != "PASS" or validation["materials"]["proposal_sha256"] != sha(PROPOSAL / "proposal.json"):
        raise RuntimeError("proposal validation is stale")
    required = {
        "schema_version": "cyberalchemy-lab-owner-authorization/v1",
        "decision_id": DECISION,
        "authorized": True,
        "proposal_path": str((PROPOSAL / "proposal.json").relative_to(LAB)),
        "proposal_sha256": sha(PROPOSAL / "proposal.json"),
        "admission_candidate_sha256": proposal["inputs"]["candidate"]["sha256"],
    }
    for key, value in required.items():
        if authorization.get(key) != value:
            raise RuntimeError(f"authorization mismatch at {key}")
    if authorization["interpreted_scope"] != proposal["proposed_effects"] or not authorization.get("verbatim_user_authorization", "").strip():
        raise RuntimeError("authorization scope mismatch")
    return proposal, authorization


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    proposal, authorization = verify()
    if not args.apply:
        print(json.dumps({"result": "PASS", "mode": "preflight", "proposal_sha256": sha(PROPOSAL / "proposal.json"), "bundle_sha256": sha(PROPOSAL / "bundle-postimage/bundle.json")}, sort_keys=True))
        return 0

    created = False
    try:
        if FINAL.exists():
            if sha(FINAL / "bundle.json") != proposal["postimage"]["sha256"]:
                raise RuntimeError("different final admission bundle already exists")
        else:
            FINAL.parent.mkdir(parents=True, exist_ok=True)
            stage_root = Path(tempfile.mkdtemp(prefix=".decision-0073-", dir=FINAL.parent))
            stage = stage_root / "v1"
            try:
                shutil.copytree(PROPOSAL / "bundle-postimage", stage)
                if sha(stage / "bundle.json") != proposal["postimage"]["sha256"]:
                    raise RuntimeError("staged bundle digest mismatch")
                os.replace(stage, FINAL)
                created = True
            finally:
                shutil.rmtree(stage_root, ignore_errors=True)

        decision = {
            "schema_version": "cyberalchemy-lab-first-governed-agent-work-episode-decision/v1",
            "decision_id": DECISION,
            "title": "Admit the first governed Agent work episode and Decision 0072 Project State successor",
            "status": "owner-admitted",
            "decided_at": "2026-10-06",
            "owner_ref": "role:repository-owner",
            "authority_effect": "first-governed-agent-work-episode-admission-only",
            "authorization": {"path": str(AUTHORIZATION.relative_to(LAB)), "sha256": sha(AUTHORIZATION), "verbatim_user_authorization": authorization["verbatim_user_authorization"]},
            "proposal": {"path": str((PROPOSAL / "proposal.json").relative_to(LAB)), "sha256": sha(PROPOSAL / "proposal.json")},
            "admission_bundle": {"path": str((FINAL / "bundle.json").relative_to(LAB)), "sha256": sha(FINAL / "bundle.json")},
            "admission_correction": proposal["admission_correction"],
            "effects": proposal["proposed_effects"],
            "current_project_state_ref": "project-state:cyberalchemy-v2-to-lab-migration:decision-0072",
            "historical_project_state_ref": "project-state:cyberalchemy-v2-to-lab-migration:decision-0071",
            "operational_closure": load(FINAL / "operational-closure.json"),
            "next_successor_obligation": "Decision 0073 and this admission bundle must enter the next immutable Project State through semantic and governance events; the Decision 0072 state remains byte-immutable.",
            "excluded_effects": proposal["excluded_effects"],
            "claim_ceiling": "Decision 0073 admits the exact first governed Agent work episode, its Context and Ontology projections, and the Decision 0072 Project State successor. It closes the ephemeral Agent Session, retains no session memory, and activates no runtime.",
        }
        dump(HERE / "decision.json", decision)
        (HERE / "DECISION.md").write_text(
            "# Decision 0073: First governed Agent work episode admission\n\n"
            "Status: **owner-admitted**\n\n"
            "Current Project State: `project-state:cyberalchemy-v2-to-lab-migration:decision-0072`\n\n"
            "- Artifact instances admitted: `22`\n"
            "- Typed Relations admitted: `23`\n"
            "- Semantic events admitted: `1`\n"
            "- Governance events admitted: `1`\n"
            "- Ephemeral Agent instances closed: `1`\n"
            "- Ephemeral Agent Sessions closed: `1`\n"
            "- Runtime activations: `0`\n\n"
            "Session memory expired at the owner review boundary. Durable continuity remains in the admitted Project State, immutable Context View, and purpose-bounded Ontology View. Decision 0073 belongs in the next immutable successor.\n\n"
            "## Claim ceiling\n\n"
            + decision["claim_ceiling"]
            + "\n",
            encoding="utf-8",
        )
        receipt = {
            "schema_version": "cyberalchemy-lab-first-governed-agent-work-episode-application-receipt/v1",
            "decision_id": DECISION,
            "result": "PASS",
            "applied_at": "2026-10-06",
            "effects": proposal["proposed_effects"],
            "materials": {"decision_sha256": sha(HERE / "decision.json"), "bundle_sha256": sha(FINAL / "bundle.json"), "authorization_sha256": sha(AUTHORIZATION), "proposal_sha256": sha(PROPOSAL / "proposal.json"), "candidate_sha256": proposal["inputs"]["candidate"]["sha256"]},
            "claim_ceiling": decision["claim_ceiling"],
        }
        dump(HERE / "receipts/application.json", receipt)
        print(json.dumps({"result": "PASS", "mode": "applied", **receipt["materials"], **proposal["proposed_effects"]}, sort_keys=True))
        return 0
    except Exception:
        if created:
            shutil.rmtree(FINAL, ignore_errors=True)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
