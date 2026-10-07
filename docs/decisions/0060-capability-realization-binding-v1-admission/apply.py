#!/usr/bin/env python3
"""Apply the approved Capability Realization Binding/v1 Artifact Type admission."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parent
PACKAGE = LAB / "authority/artifact-types/capability-realization-binding/v1"
ADMISSION = LAB / "authority/artifact-types/admissions/migration-26/v1/capability-realization-binding.json"
REFINEMENT = LAB / "authority/artifact-types/candidates/0004-remaining-26-materialization/refinements/type.capability-realization-binding.json"
MODEL_SELECTION = LAB / "authority/product-context/selected/v1/selection.json"
SEQUENCE_STATUS = LAB / "authority/product-context/selected/v1/admission-status.json"
PREREQUISITES = [
    LAB / "docs/decisions/0057-product-identity-v2-successor-admission/decision.json",
    LAB / "docs/decisions/0058-product-thesis-v1-admission/decision.json",
    LAB / "docs/decisions/0059-product-capability-v1-admission/decision.json",
]
DECISION_ID = "CAL-DECISION-0060-CAPABILITY-REALIZATION-BINDING-V1-ADMISSION"


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
    prerequisite_decisions = [load(path) for path in PREREQUISITES]
    if receipt["result"] != "PASS" or receipt["summary"] != {"blocked": 0, "passed": 12, "total": 12}:
        raise RuntimeError("Capability Realization Binding/v1 package validation must pass 12/12 before admission")
    if artifact["artifact_type_ref"] != "cal.artifact-type.capability-realization-binding/v1" or artifact["version"] != "1.0.0-candidate.2":
        raise RuntimeError("the reviewed Capability Realization Binding/v1 refinement is not current")
    if selection["admission_sequence"][3] != artifact["artifact_type_ref"]:
        raise RuntimeError("Capability Realization Binding/v1 is not fourth in the approved Product admission sequence")
    if any(decision["status"] != "owner-admitted" for decision in prerequisite_decisions):
        raise RuntimeError("one or more Product model prerequisites are not admitted")

    authorization = {
        "schema_version": "cyberalchemy-lab-artifact-type-admission-authorization/v1",
        "authorization_id": "CAL-AUTHORIZATION-0060-CAPABILITY-REALIZATION-BINDING-V1",
        "recorded_on": "2026-10-05",
        "principal_id": "person:<vrondelli>",
        "selected_role": "artifact-type-owner",
        "user_instruction_verbatim": "yes",
        "interpreted_scope": "Admit the exact refined Capability Realization Binding/v1 Artifact Type shown immediately before this instruction. Preserve its fixture as a candidate binding and complete the four-item Product model Artifact Type sequence without adopting or activating a realization.",
        "authorized_effect": "Admit cal.artifact-type.capability-realization-binding/v1 at the exact reviewed artifact and schema digests by decision overlay.",
        "artifact": exact(PACKAGE / "artifact.json"),
        "schema": exact(PACKAGE / "schema.json"),
        "validation_receipt": exact(PACKAGE / "receipts/validation.json"),
        "review_refinement": exact(REFINEMENT),
        "governing_model_selection": exact(MODEL_SELECTION),
        "prerequisite_decisions": [exact(path) for path in PREREQUISITES],
        "excluded_effects": [
            "No Capability Realization Binding instance is admitted or adopted.",
            "No workflow, service, application, repository, implementation, or runtime is activated.",
            "No conformance, observation, operational, effectiveness, or Product value claim is established.",
            "No remaining Artifact Type in the 26-item migration queue is pre-approved.",
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
        "instance_discriminator": {"path": "/kind", "value": "capability-realization-binding"},
        "semantic_definition_refs": artifact["semantic_definition_refs"],
        "review_refinement": authorization["review_refinement"],
        "prerequisite_decisions": authorization["prerequisite_decisions"],
        "instance_admissions": 0,
        "consumer_activations": 0,
        "claim_ceiling": "This overlay admits the exact Capability Realization Binding/v1 Artifact Type contract only. It does not admit or adopt a binding instance, activate a realization, or establish conformance, observation, operation, effectiveness, or Product value.",
    }
    dump(ADMISSION, admission)

    sequence_items = [
        {
            "artifact_type_ref": "cal.artifact-type.product-identity/v2",
            "decision_ref": "CAL-DECISION-0057-PRODUCT-IDENTITY-V2-SUCCESSOR-ADMISSION",
            "decision": exact(PREREQUISITES[0]),
            "lifecycle_state": "admitted-current",
        },
        {
            "artifact_type_ref": "cal.artifact-type.product-thesis/v1",
            "decision_ref": "CAL-DECISION-0058-PRODUCT-THESIS-V1-ADMISSION",
            "decision": exact(PREREQUISITES[1]),
            "lifecycle_state": "admitted-current",
        },
        {
            "artifact_type_ref": "cal.artifact-type.product-capability/v1",
            "decision_ref": "CAL-DECISION-0059-PRODUCT-CAPABILITY-V1-ADMISSION",
            "decision": exact(PREREQUISITES[2]),
            "lifecycle_state": "admitted-current",
        },
        {
            "artifact_type_ref": artifact["artifact_type_ref"],
            "decision_ref": DECISION_ID,
            "decision": {"path": rel(ROOT / "decision.json"), "sha256": "pending-self-digest"},
            "lifecycle_state": "admitted-current",
        },
    ]

    decision = {
        "schema_version": "cyberalchemy-lab-artifact-type-admission-decision/v1",
        "decision_id": DECISION_ID,
        "title": "Capability Realization Binding/v1 Artifact Type admission",
        "status": "owner-admitted",
        "authority_effect": "exact-capability-realization-binding-v1-artifact-type-admitted-by-decision-overlay",
        "authorization": exact(ROOT / "authorization.json"),
        "governing_model_selection": exact(MODEL_SELECTION),
        "prerequisite_decisions": [exact(path) for path in PREREQUISITES],
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
        "product_model_sequence_result": {
            "expected_items": 4,
            "admitted_current_items": 4,
            "result": "complete",
        },
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

    # The status projection points to Decision 0060 by stable ID rather than its
    # own digest, avoiding a circular decision/status digest dependency.
    sequence_items[-1]["decision"] = {"path": rel(ROOT / "decision.json"), "decision_id": DECISION_ID}
    sequence_status = {
        "schema_version": "cyberalchemy-lab-product-context-admission-status/v1",
        "selection": exact(MODEL_SELECTION),
        "status": "artifact-type-sequence-complete",
        "items": sequence_items,
        "summary": {
            "expected_items": 4,
            "admitted_current_items": 4,
            "instances_admitted_by_sequence": 0,
            "consumer_activations_by_sequence": 0,
        },
        "claim_ceiling": "All four Artifact Types in the approved Product model sequence are admitted-current. This status does not admit Product, thesis, capability, or binding instances and does not activate consumers, realizations, implementations, or runtimes.",
    }
    dump(SEQUENCE_STATUS, sequence_status)

    (ROOT / "DECISION.md").write_text(
        "\n".join(
            [
                "<!-- GENERATED FILE: canonical data is decision.json. -->",
                "",
                "# Capability Realization Binding/v1 Artifact Type admission",
                "",
                f"- Decision: `{DECISION_ID}`",
                "- Status: `owner-admitted`",
                "- Artifact Type: `cal.artifact-type.capability-realization-binding/v1`",
                "- Lifecycle: `admitted-current`",
                "- Product model Artifact Type sequence: `complete (4/4)`",
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
