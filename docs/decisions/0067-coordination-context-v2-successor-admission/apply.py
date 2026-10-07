#!/usr/bin/env python3
"""Apply the owner-approved Coordination Context/v2 successor admission."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parent
CURRENT = LAB / "authority/artifact-types/coordination-context/v2"
PREDECESSOR = LAB / "authority/artifact-types/coordination-context/v1"
PREDECESSOR_DECISION = LAB / "docs/decisions/0021-ctx01-artifact-type-promotion/decision.json"
NON_COLLAPSE_AUDIT = LAB / "authority/artifact-types/candidates/0007-coordination-context-non-collapse/audit.json"
ADMISSION = LAB / "authority/artifact-types/admissions/context-metamodel/v2/coordination-context.json"
REGISTRY_ROOT = LAB / "authority/artifact-types/candidates/0006-effective-state-registry"
REGISTRY = REGISTRY_ROOT / "registry.json"
CANDIDATE = REGISTRY_ROOT / "candidate.json"
DECISION_ID = "CAL-DECISION-0067-COORDINATION-CONTEXT-V2-SUCCESSOR-ADMISSION"
EXPECTED_PREIMAGE = {
    "artifact": "41965229bcbc57fbad6a2701ed34752e838dfc498d5d09dc22e6161afc4036ac",
    "schema": "6b13f5afed37dbd8d7134c877d6ff484cc9b2ad259fbd8c7b7a5bbc57a8ea7b9",
    "package_receipt": "33e86d94647356c5014c12f9a7a27801ba72181905237471a111b327a675351b",
    "predecessor_artifact": "22e2b5b9aef41517a7ee6417a2d4fe7a06ae0a1ab98744cb5a13b4a90bbc99d1",
    "predecessor_schema": "44d92e3d241b674f2adc79b716ae87e9891772bda99aa67126ea4491a52ae036",
    "predecessor_decision": "dd9907c6622568525eb0a237938cc88ee1958546816b60d0127212068528cc23",
    "registry": "3ca50c8513c3c04aa5014f1d642ff4b21a6a6003163dc3932bc417e2e8f06b1b",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def encode(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(LAB))


def exact(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": sha(path)}


def main() -> int:
    if (ROOT / "decision.json").exists():
        return subprocess.run([sys.executable, str(ROOT / "validate.py")], cwd=LAB).returncode

    actual = {
        "artifact": sha(CURRENT / "artifact.json"),
        "schema": sha(CURRENT / "schema.json"),
        "package_receipt": sha(CURRENT / "receipts/validation.json"),
        "predecessor_artifact": sha(PREDECESSOR / "artifact.json"),
        "predecessor_schema": sha(PREDECESSOR / "schema.json"),
        "predecessor_decision": sha(PREDECESSOR_DECISION),
        "registry": sha(REGISTRY),
    }
    if actual != EXPECTED_PREIMAGE:
        raise RuntimeError(f"reviewed admission envelope changed: {actual}")

    artifact = load(CURRENT / "artifact.json")
    receipt = load(CURRENT / "receipts/validation.json")
    predecessor_decision = load(PREDECESSOR_DECISION)
    registry = load(REGISTRY)
    if artifact["artifact_type_ref"] != "cal.artifact-type.coordination-context/v2":
        raise RuntimeError("reviewed Coordination Context/v2 package is not current")
    if receipt.get("result") != "PASS" or receipt.get("summary") != {
        "failed": 0,
        "hostile_cases": 18,
        "lifecycle_cases": 6,
        "passed": 14,
        "positive_cases": 4,
        "total": 14,
    }:
        raise RuntimeError("Coordination Context/v2 package validation must pass the reviewed matrix")
    predecessor_entry = next(
        item for item in predecessor_decision["admitted_artifact_types"]
        if item["artifact_type_ref"] == "cal.artifact-type.coordination-context/v1"
    )
    if registry["current_by_identity"][artifact["artifact_type_id"]] != predecessor_entry["artifact_type_ref"]:
        raise RuntimeError("Coordination Context/v1 is not the effective current predecessor")

    excluded = [
        "No Coordination Context instance is admitted, created, migrated, or activated.",
        "No Product, Project, Goal, Bounded Context, owner, consumer, implementation, or runtime is activated.",
        "No Relation Kind, ordered endpoint pair, qualifier schema, Typed Relation, or relation projection is admitted.",
        "No Coordination Context/v1 bytes are rewritten or deleted.",
        "No Artifact Type other than the exact Coordination Context/v2 successor is admitted.",
    ]
    authorization = {
        "schema_version": "cyberalchemy-lab-artifact-type-successor-admission-authorization/v1",
        "authorization_id": "CAL-AUTHORIZATION-0067-COORDINATION-CONTEXT-V2-SUCCESSOR",
        "recorded_on": "2026-10-06",
        "principal_id": "person:<vrondelli>",
        "selected_role": "artifact-type-owner",
        "user_instruction_verbatim": "admit",
        "interpreted_scope": "Admit the exact reviewed Coordination Context/v2 Artifact Type as current and transition Coordination Context/v1 to historical while keeping the separately governed relation endpoint extensions unadmitted.",
        "authorized_effect": "Admit cal.artifact-type.coordination-context/v2 as admitted-current and mark cal.artifact-type.coordination-context/v1 admitted-historical by decision overlay.",
        "current_artifact": exact(CURRENT / "artifact.json"),
        "current_schema": exact(CURRENT / "schema.json"),
        "current_validation_receipt": exact(CURRENT / "receipts/validation.json"),
        "predecessor_artifact": exact(PREDECESSOR / "artifact.json"),
        "predecessor_schema": exact(PREDECESSOR / "schema.json"),
        "predecessor_admission_decision": exact(PREDECESSOR_DECISION),
        "non_collapse_audit": exact(NON_COLLAPSE_AUDIT),
        "excluded_effects": excluded,
    }
    atomic(ROOT / "authorization.json", encode(authorization))

    admission = {
        "schema_version": "cyberalchemy-lab-artifact-type-successor-admission/v1",
        "artifact_type_id": artifact["artifact_type_id"],
        "admission_decision_ref": DECISION_ID,
        "lifecycle": {
            "current": {
                "artifact_type_ref": artifact["artifact_type_ref"],
                "artifact_version": artifact["version"],
                "lifecycle_state": "admitted-current",
                "artifact": exact(CURRENT / "artifact.json"),
                "schema": exact(CURRENT / "schema.json"),
                "instance_discriminator": {"path": "/schema_version", "value": "cyberalchemy-lab-coordination-context/v2"},
                "semantic_definition_refs": artifact["semantic_definition_refs"],
            },
            "predecessor": {
                "artifact_type_ref": predecessor_entry["artifact_type_ref"],
                "artifact_version": load(PREDECESSOR / "artifact.json")["version"],
                "lifecycle_state": "admitted-historical",
                "previous_lifecycle_state": "admitted-current",
                "original_admission_decision_ref": "CAL-DECISION-0021-CTX01-ARTIFACT-TYPE-PROMOTION",
                "artifact": exact(PREDECESSOR / "artifact.json"),
                "schema": exact(PREDECESSOR / "schema.json"),
            },
        },
        "instance_admissions": 0,
        "consumer_activations": 0,
        "relation_endpoint_pairs_admitted": 0,
        "claim_ceiling": "This overlay admits the exact Coordination Context/v2 Artifact Type as current and records Coordination Context/v1 as historical. It does not admit or migrate an instance, admit any relation endpoint extension or projection, grant authority, activate work, or activate a consumer or runtime.",
    }
    atomic(ADMISSION, encode(admission))

    decision = {
        "schema_version": "cyberalchemy-lab-artifact-type-successor-admission-decision/v1",
        "decision_id": DECISION_ID,
        "title": "Coordination Context/v2 successor admission",
        "status": "owner-admitted",
        "authority_effect": "coordination-context-v2-admitted-current-and-v1-transitioned-to-admitted-historical",
        "authorization": exact(ROOT / "authorization.json"),
        "admission_record": exact(ADMISSION),
        "lifecycle_result": admission["lifecycle"],
        "admission_result": {
            "artifact_types_admitted": 1,
            "predecessors_transitioned_to_historical": 1,
            "instances_admitted": 0,
            "consumer_activations": 0,
            "relation_endpoint_pairs_admitted": 0,
            "result": "complete",
        },
        "transaction_model": {
            "kind": "decision-overlay-only",
            "candidate_bytes_preserved": True,
            "predecessor_bytes_preserved": True,
        },
        "excluded_effects": excluded,
        "claim_ceiling": admission["claim_ceiling"],
        "source_direction": {
            "canonical": "decision.json",
            "human_projection": "DECISION.md",
            "projection_policy": "generated-only",
            "generator": "apply.py",
        },
    }
    atomic(ROOT / "decision.json", encode(decision))
    atomic(
        ROOT / "DECISION.md",
        ("\n".join([
            "<!-- GENERATED FILE: canonical data is decision.json. -->",
            "",
            "# Coordination Context/v2 successor admission",
            "",
            f"- Decision: `{DECISION_ID}`",
            "- Status: `owner-admitted`",
            "- Current: `cal.artifact-type.coordination-context/v2` — `admitted-current`",
            "- Predecessor: `cal.artifact-type.coordination-context/v1` — `admitted-historical`",
            "- Instances admitted: `0`",
            "- Relation endpoint pairs admitted: `0`",
            "- Consumer activations: `0`",
            "",
            "## Claim ceiling",
            "",
            admission["claim_ceiling"],
            "",
        ])).encode(),
    )

    post = deepcopy(registry)
    current_contract = next(
        item for item in post["admitted_contracts"]
        if item["artifact_type_ref"] == "cal.artifact-type.coordination-context/v1"
    )
    current_contract["lifecycle_state"] = "admitted-historical"
    current_contract["successor_decision_ref"] = DECISION_ID
    post["admitted_contracts"].append({
        "admission_decision_ref": DECISION_ID,
        "artifact_path": rel(CURRENT / "artifact.json"),
        "artifact_sha256": sha(CURRENT / "artifact.json"),
        "artifact_type_ref": artifact["artifact_type_ref"],
        "instance_discriminator": {"path": "/schema_version", "value": "cyberalchemy-lab-coordination-context/v2"},
        "lifecycle_state": "admitted-current",
        "schema_path": rel(CURRENT / "schema.json"),
        "schema_selector": None,
        "schema_sha256": sha(CURRENT / "schema.json"),
        "semantic_definition_refs": artifact["semantic_definition_refs"],
        "semantic_kind": "coordination-context",
    })
    post["admitted_contracts"].sort(key=lambda item: (item["artifact_type_ref"], item["artifact_path"]))
    post["current_by_identity"][artifact["artifact_type_id"]] = artifact["artifact_type_ref"]
    for item in post["descriptors"]:
        if item["artifact_type_ref"] == "cal.artifact-type.coordination-context/v1":
            item["effective_state"] = "admitted-historical"
            item["effective_decision_refs"] = ["CAL-DECISION-0021-CTX01-ARTIFACT-TYPE-PROMOTION", DECISION_ID]
        elif item["artifact_type_ref"] == artifact["artifact_type_ref"]:
            item["effective_state"] = "admitted-current"
            item["effective_decision_refs"] = [DECISION_ID]
    post["candidate_lineage"] = [
        item for item in post["candidate_lineage"]
        if item["artifact_type_ref"] != artifact["artifact_type_ref"]
    ]
    post["overlay_sources"].append({
        "path": rel(ROOT / "decision.json"),
        "role": "decision-overlay",
        "sha256": sha(ROOT / "decision.json"),
    })
    post["overlay_sources"].sort(key=lambda item: item["path"])
    post["inventory"].update({
        "admitted_contract_count": 33,
        "admitted_current_count": 28,
        "admitted_historical_count": 5,
    })
    post["inventory"]["state_counts"] = {
        "admitted-current": 21,
        "admitted-historical": 5,
        "candidate-unadmitted": 28,
        "resolved-duplicate": 2,
    }
    post["claim_ceiling"] = "This candidate resolves the effective state of all 56 visible Artifact Type descriptors and 33 admitted contract entries, including the Coordination Context/v2 successor admission. It does not admit this registry, any remaining candidate Artifact Type, any instance, any semantic rebind, any relation endpoint extension, any consumer, or any runtime."
    atomic(REGISTRY, encode(post))

    subprocess.run([sys.executable, str(REGISTRY_ROOT / "audit_content.py")], cwd=LAB, check=True)
    candidate = load(CANDIDATE)
    audit = load(REGISTRY_ROOT / "content-audit.json")
    candidate["content_audit"].update({
        "actionable_descriptor_count": audit["summary"]["actionable_descriptor_count"],
        "descriptor_count": audit["summary"]["descriptor_count"],
        "sha256": sha(REGISTRY_ROOT / "content-audit.json"),
    })
    candidate["claim_ceiling"] = post["claim_ceiling"]
    atomic(CANDIDATE, encode(candidate))
    subprocess.run([sys.executable, str(REGISTRY_ROOT / "build.py")], cwd=LAB, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
