#!/usr/bin/env python3
"""Apply the owner-approved Product Thesis/v1 Artifact Type admission."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parent
PACKAGE = LAB / "authority/artifact-types/product-thesis/v1"
ADMISSION = LAB / "authority/artifact-types/admissions/migration-26/v1/product-thesis.json"
REFINEMENT = LAB / "authority/artifact-types/candidates/0004-remaining-26-materialization/refinements/type.product-thesis.json"
MODEL_SELECTION = LAB / "authority/product-context/selected/v1/selection.json"
PRODUCT_IDENTITY_DECISION = LAB / "docs/decisions/0057-product-identity-v2-successor-admission/decision.json"
DECISION_ID = "CAL-DECISION-0058-PRODUCT-THESIS-V1-ADMISSION"


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
    receipt = load(PACKAGE / "receipts/validation.json")
    artifact = load(PACKAGE / "artifact.json")
    selection = load(MODEL_SELECTION)
    identity_decision = load(PRODUCT_IDENTITY_DECISION)
    if receipt["result"] != "PASS" or receipt["summary"] != {"blocked": 0, "passed": 12, "total": 12}:
        raise RuntimeError("Product Thesis/v1 package validation must pass 12/12 before admission")
    if artifact["artifact_type_ref"] != "cal.artifact-type.product-thesis/v1" or artifact["version"] != "1.0.0-candidate.3":
        raise RuntimeError("the reviewed Product Thesis/v1 refinement is not current")
    if selection["admission_sequence"][1] != artifact["artifact_type_ref"]:
        raise RuntimeError("Product Thesis/v1 is not second in the approved Product admission sequence")
    if identity_decision["status"] != "owner-admitted":
        raise RuntimeError("Product Identity/v2 successor admission is not current")

    authorization = {
        "schema_version": "cyberalchemy-lab-artifact-type-admission-authorization/v1",
        "authorization_id": "CAL-AUTHORIZATION-0058-PRODUCT-THESIS-V1",
        "recorded_on": "2026-10-05",
        "principal_id": "person:<vrondelli>",
        "selected_role": "artifact-type-owner",
        "user_instruction_verbatim": "yes",
        "interpreted_scope": "Admit the exact refined Product Thesis/v1 Artifact Type shown immediately before this instruction. Preserve its fixture as candidate-only and continue the approved Product sequence one item at a time.",
        "authorized_effect": "Admit cal.artifact-type.product-thesis/v1 at the exact reviewed artifact and schema digests by decision overlay.",
        "artifact": exact(PACKAGE / "artifact.json"),
        "schema": exact(PACKAGE / "schema.json"),
        "validation_receipt": exact(PACKAGE / "receipts/validation.json"),
        "review_refinement": exact(REFINEMENT),
        "governing_model_selection": exact(MODEL_SELECTION),
        "product_identity_prerequisite": exact(PRODUCT_IDENTITY_DECISION),
        "excluded_effects": [
            "No Product Thesis instance is admitted or committed.",
            "No hypothesis, intended outcome, value claim, or effectiveness claim is proven.",
            "No consumer, capability, realization, implementation, or runtime is activated.",
            "No later item in the approved Product admission sequence is pre-approved.",
        ],
    }
    dump(ROOT / "authorization.json", authorization)

    admission = {
        "schema_version": "cyberalchemy-lab-artifact-type-admission/v1",
        "artifact_type_ref": artifact["artifact_type_ref"],
        "artifact_version": artifact["version"],
        "semantic_kind": artifact["classification"]["semantic_kind"],
        "lifecycle_state": "admitted-current",
        "decision_overlay_status": "admitted-current",
        "admission_decision_ref": DECISION_ID,
        "artifact_path": rel(PACKAGE / "artifact.json"),
        "artifact_sha256": sha(PACKAGE / "artifact.json"),
        "schema_path": rel(PACKAGE / "schema.json"),
        "schema_sha256": sha(PACKAGE / "schema.json"),
        "instance_discriminator": {"path": "/kind", "value": "product-thesis"},
        "semantic_definition_refs": artifact["semantic_definition_refs"],
        "review_refinement": authorization["review_refinement"],
        "prerequisite_decision": authorization["product_identity_prerequisite"],
        "instance_admissions": 0,
        "consumer_activations": 0,
        "claim_ceiling": "This overlay admits the exact Product Thesis/v1 Artifact Type contract only. It does not admit or commit a Product Thesis instance, prove any hypothesis or intended outcome, or activate a capability, realization, implementation, or runtime.",
    }
    dump(ADMISSION, admission)

    decision = {
        "schema_version": "cyberalchemy-lab-artifact-type-admission-decision/v1",
        "decision_id": DECISION_ID,
        "title": "Product Thesis/v1 Artifact Type admission",
        "status": "owner-admitted",
        "authority_effect": "exact-product-thesis-v1-artifact-type-admitted-by-decision-overlay",
        "authorization": exact(ROOT / "authorization.json"),
        "governing_model_selection": exact(MODEL_SELECTION),
        "product_identity_prerequisite": exact(PRODUCT_IDENTITY_DECISION),
        "admitted_artifact_type": {
            "artifact_type_ref": artifact["artifact_type_ref"],
            "decision_overlay_status": "admitted-current",
            "path": rel(PACKAGE / "artifact.json"),
            "sha256": sha(PACKAGE / "artifact.json"),
            "schema_path": rel(PACKAGE / "schema.json"),
            "schema_sha256": sha(PACKAGE / "schema.json"),
        },
        "admission_record": exact(ADMISSION),
        "review_refinement": authorization["review_refinement"],
        "admission_result": {
            "artifact_types_admitted": 1,
            "instances_admitted": 0,
            "consumer_activations": 0,
            "result": "complete",
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
                "# Product Thesis/v1 Artifact Type admission",
                "",
                f"- Decision: `{DECISION_ID}`",
                "- Status: `owner-admitted`",
                "- Artifact Type: `cal.artifact-type.product-thesis/v1`",
                "- Lifecycle: `admitted-current`",
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
