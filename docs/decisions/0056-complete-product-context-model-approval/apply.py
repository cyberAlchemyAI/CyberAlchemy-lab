#!/usr/bin/env python3
"""Apply approval of the complete Product context as the admission-sequence model."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parent
MODEL_ROOT = LAB / "authority/product-context/candidates/0001-complete-product-model"
SELECTION = LAB / "authority/product-context/selected/v1/selection.json"
DECISION_ID = "CAL-DECISION-0056-COMPLETE-PRODUCT-CONTEXT-MODEL-APPROVAL"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(LAB))


def main() -> int:
    receipt = load(MODEL_ROOT / "receipts/validation.json")
    if receipt["result"] != "PASS":
        raise RuntimeError("complete Product context validation must pass before approval")
    model = load(MODEL_ROOT / "model.json")
    authorization = {
        "schema_version": "cyberalchemy-lab-product-context-approval-authorization/v1",
        "authorization_id": "CAL-AUTHORIZATION-0056-COMPLETE-PRODUCT-CONTEXT",
        "recorded_on": "2026-10-05",
        "principal_id": "person:<vrondelli>",
        "selected_role": "product-model-owner",
        "user_instruction_verbatim": "approved",
        "interpreted_scope": "Approve the exact complete Product model shown immediately before this instruction as the governing structure for the Product admission sequence.",
        "authorized_effect": "Select CAL-PRODUCT-CONTEXT-COMPLETE-0001 as the governing Product context model for subsequent separately approved Artifact Type admissions.",
        "model": {"path": rel(MODEL_ROOT / "model.json"), "sha256": sha(MODEL_ROOT / "model.json")},
        "example": {"path": rel(MODEL_ROOT / "example.json"), "sha256": sha(MODEL_ROOT / "example.json")},
        "validation_receipt": {"path": rel(MODEL_ROOT / "receipts/validation.json"), "sha256": sha(MODEL_ROOT / "receipts/validation.json")},
        "excluded_effects": [
            "No Artifact Type or instance is admitted by this approval.",
            "Product Identity/v1 is not superseded by this approval.",
            "No profile, relation kind, projection, consumer, realization, or runtime is activated.",
        ],
    }
    dump(ROOT / "authorization.json", authorization)
    selection = {
        "schema_version": "cyberalchemy-lab-product-context-selection/v1",
        "selection_id": "CAL-PRODUCT-CONTEXT-SELECTION-V1",
        "model_id": model["model_id"],
        "status": "owner-approved-governing-model",
        "authority_effect": "governing-structure-selected-for-separate-admission-sequence",
        "model": authorization["model"],
        "example": authorization["example"],
        "validation_receipt": authorization["validation_receipt"],
        "approval_decision_ref": DECISION_ID,
        "admission_sequence": [
            "cal.artifact-type.product-identity/v2",
            "cal.artifact-type.product-thesis/v1",
            "cal.artifact-type.product-capability/v1",
            "cal.artifact-type.capability-realization-binding/v1",
        ],
        "separate_decision_required_per_item": True,
        "claim_ceiling": "This selection governs the Product context structure and admission order. It does not itself admit, supersede, instantiate, adopt, or activate any component.",
    }
    dump(SELECTION, selection)
    decision = {
        "schema_version": "cyberalchemy-lab-product-context-approval-decision/v1",
        "decision_id": DECISION_ID,
        "title": "Complete Product context model approval",
        "status": "owner-approved",
        "authority_effect": "complete-product-context-selected-as-governing-model",
        "authorization": {"path": rel(ROOT / "authorization.json"), "sha256": sha(ROOT / "authorization.json")},
        "selected_model": authorization["model"],
        "selected_example": authorization["example"],
        "validation_receipt": authorization["validation_receipt"],
        "selection_record": {"path": rel(SELECTION), "sha256": sha(SELECTION)},
        "result": {"models_approved": 1, "artifact_types_admitted": 0, "instances_admitted": 0, "consumer_activations": 0},
        "excluded_effects": authorization["excluded_effects"],
        "claim_ceiling": selection["claim_ceiling"],
        "source_direction": {"canonical": "decision.json", "human_projection": "DECISION.md", "projection_policy": "generated-only", "generator": "apply.py"},
    }
    dump(ROOT / "decision.json", decision)
    (ROOT / "DECISION.md").write_text(
        "\n".join([
            "<!-- GENERATED FILE: canonical data is decision.json. -->", "", "# Complete Product context model approval", "",
            f"- Decision: `{DECISION_ID}`", "- Status: `owner-approved`", f"- Model: `{model['model_id']}`",
            "- Artifact Types admitted: `0`", "- Consumer activations: `0`", "", "## Admission sequence", "",
            *[f"{index}. `{ref}`" for index, ref in enumerate(selection["admission_sequence"], 1)], "", "## Claim ceiling", "", selection["claim_ceiling"], "",
        ]), encoding="utf-8"
    )
    return subprocess.run([sys.executable, str(ROOT / "validate.py")], cwd=LAB, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
