#!/usr/bin/env python3
"""Apply the owner-approved Product Identity/v2 successor admission."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parent
CURRENT = LAB / "authority/artifact-types/product-identity/v2"
PREDECESSOR = LAB / "authority/artifact-types/product-identity/v1"
SUCCESSOR = CURRENT / "successor.json"
PREDECESSOR_DECISION = LAB / "docs/decisions/0030-cml07-s2-artifact-types-v1/decision.json"
MODEL_SELECTION = LAB / "authority/product-context/selected/v1/selection.json"
ADMISSION = LAB / "authority/artifact-types/admissions/migration-26/v1/product-identity.json"
DECISION_ID = "CAL-DECISION-0057-PRODUCT-IDENTITY-V2-SUCCESSOR-ADMISSION"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(LAB))


def exact(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": sha(path)}


def main() -> int:
    receipt = load(CURRENT / "receipts/validation.json")
    artifact = load(CURRENT / "artifact.json")
    successor = load(SUCCESSOR)
    selection = load(MODEL_SELECTION)
    predecessor_decision = load(PREDECESSOR_DECISION)
    if receipt["result"] != "PASS" or receipt["summary"] != {"blocked": 0, "passed": 17, "total": 17}:
        raise RuntimeError("Product Identity/v2 package validation must pass 17/17 before admission")
    if artifact["artifact_type_ref"] != "cal.artifact-type.product-identity/v2" or artifact["version"] != "2.0.0-candidate.1":
        raise RuntimeError("the reviewed Product Identity/v2 package is not current")
    if selection["admission_sequence"][0] != artifact["artifact_type_ref"]:
        raise RuntimeError("Product Identity/v2 is not first in the approved Product admission sequence")
    predecessor_entry = next(
        item for item in predecessor_decision["admitted_artifact_types"]
        if item["artifact_type_ref"] == "cal.artifact-type.product-identity/v1"
    )
    if predecessor_entry["decision_overlay_status"] != "admitted-current":
        raise RuntimeError("Product Identity/v1 is not the admitted-current predecessor")
    if successor["predecessor_ref"] != predecessor_entry["artifact_type_ref"]:
        raise RuntimeError("successor record does not bind the admitted predecessor")

    authorization = {
        "schema_version": "cyberalchemy-lab-artifact-type-successor-admission-authorization/v1",
        "authorization_id": "CAL-AUTHORIZATION-0057-PRODUCT-IDENTITY-V2-SUCCESSOR",
        "recorded_on": "2026-10-05",
        "principal_id": "person:<vrondelli>",
        "selected_role": "artifact-type-owner",
        "user_instruction_verbatim": "yes",
        "interpreted_scope": "Admit the exact Product Identity/v2 package shown immediately before this instruction as current and transition Product Identity/v1 from admitted-current to admitted-historical. Continue the approved Product sequence one item at a time.",
        "authorized_effect": "Admit cal.artifact-type.product-identity/v2 as admitted-current and mark cal.artifact-type.product-identity/v1 admitted-historical by decision overlay.",
        "current_artifact": exact(CURRENT / "artifact.json"),
        "current_schema": exact(CURRENT / "schema.json"),
        "current_validation_receipt": exact(CURRENT / "receipts/validation.json"),
        "successor_record": exact(SUCCESSOR),
        "predecessor_artifact": exact(PREDECESSOR / "artifact.json"),
        "predecessor_schema": exact(PREDECESSOR / "schema.json"),
        "predecessor_admission_decision": exact(PREDECESSOR_DECISION),
        "governing_model_selection": exact(MODEL_SELECTION),
        "excluded_effects": [
            "No Product instance, Product Thesis, Product Capability, or Capability Realization Binding is admitted.",
            "No Product Identity/v1 bytes are rewritten or deleted.",
            "No consumer, implementation, realization, or runtime is activated.",
            "No later item in the approved Product admission sequence is pre-approved.",
        ],
    }
    dump(ROOT / "authorization.json", authorization)

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
                "instance_discriminator": {"path": "/schema_version", "value": "cyberalchemy-lab-product-identity/v2"},
                "semantic_definition_refs": artifact["semantic_definition_refs"],
            },
            "predecessor": {
                "artifact_type_ref": predecessor_entry["artifact_type_ref"],
                "artifact_version": load(PREDECESSOR / "artifact.json")["version"],
                "lifecycle_state": "admitted-historical",
                "previous_lifecycle_state": "admitted-current",
                "original_admission_decision_ref": "CAL-DECISION-0030-CML07-S2-IDENTITY-ARTIFACT-TYPES-V1",
                "artifact": exact(PREDECESSOR / "artifact.json"),
                "schema": exact(PREDECESSOR / "schema.json"),
            },
        },
        "successor_record": exact(SUCCESSOR),
        "instance_admissions": 0,
        "consumer_activations": 0,
        "claim_ceiling": "This overlay admits the exact Product Identity/v2 Artifact Type as current and records Product Identity/v1 as historical. It does not admit or migrate a Product instance, commit a thesis, adopt a Capability, prove value, or activate an implementation or runtime.",
    }
    dump(ADMISSION, admission)

    decision = {
        "schema_version": "cyberalchemy-lab-artifact-type-successor-admission-decision/v1",
        "decision_id": DECISION_ID,
        "title": "Product Identity/v2 successor admission",
        "status": "owner-admitted",
        "authority_effect": "product-identity-v2-admitted-current-and-v1-transitioned-to-admitted-historical",
        "authorization": exact(ROOT / "authorization.json"),
        "governing_model_selection": exact(MODEL_SELECTION),
        "admission_record": exact(ADMISSION),
        "lifecycle_result": admission["lifecycle"],
        "admission_result": {
            "artifact_types_admitted": 1,
            "predecessors_transitioned_to_historical": 1,
            "instances_admitted": 0,
            "consumer_activations": 0,
            "result": "complete",
        },
        "transaction_model": {
            "kind": "decision-overlay-only",
            "candidate_bytes_preserved": True,
            "predecessor_bytes_preserved": True,
        },
        "excluded_effects": authorization["excluded_effects"],
        "claim_ceiling": admission["claim_ceiling"],
        "source_direction": {
            "canonical": "decision.json",
            "human_projection": "DECISION.md",
            "projection_policy": "generated-only",
            "generator": "apply.py",
        },
    }
    dump(ROOT / "decision.json", decision)
    (ROOT / "DECISION.md").write_text(
        "\n".join(
            [
                "<!-- GENERATED FILE: canonical data is decision.json. -->",
                "",
                "# Product Identity/v2 successor admission",
                "",
                f"- Decision: `{DECISION_ID}`",
                "- Status: `owner-admitted`",
                "- Current: `cal.artifact-type.product-identity/v2` — `admitted-current`",
                "- Predecessor: `cal.artifact-type.product-identity/v1` — `admitted-historical`",
                "- Instances admitted: `0`",
                "- Consumer activations: `0`",
                "",
                "## Claim ceiling",
                "",
                admission["claim_ceiling"],
                "",
            ]
        ),
        encoding="utf-8",
    )
    return subprocess.run([sys.executable, str(ROOT / "validate.py")], cwd=LAB, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
