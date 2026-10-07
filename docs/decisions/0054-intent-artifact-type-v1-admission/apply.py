#!/usr/bin/env python3
"""Apply the user-approved Intent Artifact Type admission overlay."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parent
PACKAGE = LAB / "authority/artifact-types/intent/v1"
ADMISSION = LAB / "authority/artifact-types/admissions/migration-26/v1/intent.json"
REFINEMENT = LAB / "authority/artifact-types/candidates/0004-remaining-26-materialization/refinements/type.intent.json"
DECISION_ID = "CAL-DECISION-0054-INTENT-ARTIFACT-TYPE-V1-ADMISSION"


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
    receipt = load(PACKAGE / "receipts/validation.json")
    if receipt["result"] != "PASS":
        raise RuntimeError("Intent package validation must pass before admission")
    artifact = load(PACKAGE / "artifact.json")
    if artifact["version"] != "1.0.0-candidate.2":
        raise RuntimeError("the reviewed Intent refinement is not current")

    authorization = {
        "schema_version": "cyberalchemy-lab-artifact-type-admission-authorization/v1",
        "authorization_id": "CAL-AUTHORIZATION-0054-INTENT-ARTIFACT-TYPE-V1",
        "recorded_on": "2026-10-05",
        "principal_id": "person:<vrondelli>",
        "selected_role": "artifact-type-owner",
        "user_instruction_verbatim": "yes, review the next and show me with example lets do this process for all",
        "interpreted_scope": "Admit the exact refined Intent Artifact Type shown immediately before this instruction. Continue review one item at a time; future items are not pre-approved.",
        "authorized_effect": "Admit cal.artifact-type.intent/v1 at the exact reviewed artifact and schema digests by decision overlay.",
        "artifact": {"path": rel(PACKAGE / "artifact.json"), "sha256": sha(PACKAGE / "artifact.json")},
        "schema": {"path": rel(PACKAGE / "schema.json"), "sha256": sha(PACKAGE / "schema.json")},
        "validation_receipt": {"path": rel(PACKAGE / "receipts/validation.json"), "sha256": sha(PACKAGE / "receipts/validation.json")},
        "review_refinement": {"path": rel(REFINEMENT), "sha256": sha(REFINEMENT)},
        "excluded_effects": [
            "No Intent instance is admitted.",
            "No consumer or runtime is activated.",
            "No later Artifact Type in the 26-item queue is pre-approved.",
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
        "instance_discriminator": {"path": "/kind", "value": "intent"},
        "semantic_definition_refs": artifact["semantic_definition_refs"],
        "review_refinement": authorization["review_refinement"],
        "instance_admissions": 0,
        "consumer_activations": 0,
        "claim_ceiling": "This overlay admits the exact refined Intent Artifact Type contract only. It does not admit an Intent instance, authenticate a reference, satisfy an Intent, or activate a consumer or runtime.",
    }
    dump(ADMISSION, admission)

    decision = {
        "schema_version": "cyberalchemy-lab-artifact-type-admission-decision/v1",
        "decision_id": DECISION_ID,
        "title": "Intent Artifact Type v1 admission",
        "status": "owner-admitted",
        "authority_effect": "exact-intent-artifact-type-admitted-by-decision-overlay",
        "authorization": {"path": rel(ROOT / "authorization.json"), "sha256": sha(ROOT / "authorization.json")},
        "admitted_artifact_type": {
            "artifact_type_ref": artifact["artifact_type_ref"],
            "decision_overlay_status": "admitted-current",
            "path": rel(PACKAGE / "artifact.json"),
            "sha256": sha(PACKAGE / "artifact.json"),
            "schema_path": rel(PACKAGE / "schema.json"),
            "schema_sha256": sha(PACKAGE / "schema.json"),
        },
        "admission_record": {"path": rel(ADMISSION), "sha256": sha(ADMISSION)},
        "review_refinement": authorization["review_refinement"],
        "admission_result": {"artifact_types_admitted": 1, "instances_admitted": 0, "consumer_activations": 0, "result": "complete"},
        "excluded_effects": authorization["excluded_effects"],
        "claim_ceiling": admission["claim_ceiling"],
        "source_direction": {"canonical": "decision.json", "human_projection": "DECISION.md", "projection_policy": "generated-only", "generator": "apply.py"},
    }
    dump(ROOT / "decision.json", decision)
    (ROOT / "DECISION.md").write_text(
        "\n".join(
            [
                "<!-- GENERATED FILE: canonical data is decision.json. -->",
                "",
                "# Intent Artifact Type v1 admission",
                "",
                f"- Decision: `{DECISION_ID}`",
                "- Status: `owner-admitted`",
                "- Artifact Type: `cal.artifact-type.intent/v1`",
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
