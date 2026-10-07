#!/usr/bin/env python3
"""Apply the owner-approved Research Inquiry/v1 Artifact Type admission."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parent
PACKAGE = LAB / "authority/artifact-types/research-inquiry/v1"
ADMISSION = LAB / "authority/artifact-types/admissions/migration-26/v1/research-inquiry.json"
REFINEMENT = LAB / "authority/artifact-types/candidates/0004-remaining-26-materialization/refinements/type.research-inquiry.json"
MATERIALIZATION = PACKAGE / "materialization.json"
DECISION_ID = "CAL-DECISION-0062-RESEARCH-INQUIRY-V1-ADMISSION"


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
    refinement = load(REFINEMENT)
    materialization = load(MATERIALIZATION)
    if receipt["result"] != "PASS" or receipt["summary"] != {"blocked": 0, "passed": 12, "total": 12}:
        raise RuntimeError("Research Inquiry/v1 package validation must pass 12/12 before admission")
    if artifact["artifact_type_ref"] != "cal.artifact-type.research-inquiry/v1" or artifact["version"] != "1.0.0-candidate.2":
        raise RuntimeError("the reviewed Research Inquiry/v1 refinement is not current")
    if refinement["review_state"] != "revision-authorized-before-admission":
        raise RuntimeError("Research Inquiry refinement authorization is missing")
    if materialization["target_id"] != "type.research-inquiry" or materialization["status"] != "candidate-refined":
        raise RuntimeError("Research Inquiry package materialization is not the reviewed refinement")

    authorization = {
        "schema_version": "cyberalchemy-lab-artifact-type-admission-authorization/v1",
        "authorization_id": "CAL-AUTHORIZATION-0062-RESEARCH-INQUIRY-V1",
        "recorded_on": "2026-10-05",
        "principal_id": "person:<vrondelli>",
        "selected_role": "artifact-type-owner",
        "user_instruction_verbatim": "yes",
        "interpreted_scope": "Admit the exact revised Research Inquiry/v1 Artifact Type shown immediately before this instruction. Preserve its example as an unadmitted fixture and do not start research or establish a Finding.",
        "authorized_effect": "Admit cal.artifact-type.research-inquiry/v1 at the exact reviewed artifact and schema digests by decision overlay.",
        "artifact": exact(PACKAGE / "artifact.json"),
        "schema": exact(PACKAGE / "schema.json"),
        "validation_receipt": exact(PACKAGE / "receipts/validation.json"),
        "review_refinement": exact(REFINEMENT),
        "package_materialization": exact(MATERIALIZATION),
        "migration_contract": exact(PACKAGE / "migration-contract.json"),
        "excluded_effects": [
            "No Research Inquiry instance is admitted or launched.",
            "No Research Run is executed.",
            "No evidence, Finding, conclusion, decision, Definition, or proof is established.",
            "No consumer, implementation, or runtime is activated.",
            "No later migration queue item is pre-approved.",
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
        "instance_discriminator": {"path": "/kind", "value": "research-inquiry"},
        "semantic_definition_refs": artifact["semantic_definition_refs"],
        "review_refinement": authorization["review_refinement"],
        "migration_contract": authorization["migration_contract"],
        "instance_admissions": 0,
        "consumer_activations": 0,
        "claim_ceiling": "This overlay admits the exact Research Inquiry/v1 Artifact Type contract only. It does not admit or launch an inquiry, execute research, or establish evidence, a Finding, conclusion, decision, Definition, proof, or runtime authority.",
    }
    dump(ADMISSION, admission)

    decision = {
        "schema_version": "cyberalchemy-lab-artifact-type-admission-decision/v1",
        "decision_id": DECISION_ID,
        "title": "Research Inquiry/v1 Artifact Type admission",
        "status": "owner-admitted",
        "authority_effect": "exact-research-inquiry-v1-artifact-type-admitted-by-decision-overlay",
        "authorization": exact(ROOT / "authorization.json"),
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
        "package_materialization": exact(MATERIALIZATION),
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
                "# Research Inquiry/v1 Artifact Type admission",
                "",
                f"- Decision: `{DECISION_ID}`",
                "- Status: `owner-admitted`",
                "- Artifact Type: `cal.artifact-type.research-inquiry/v1`",
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
