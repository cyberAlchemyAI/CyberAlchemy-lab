#!/usr/bin/env python3
"""Resolve the migration Product candidate to the admitted Product Identity carrier."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parent
CANDIDATE = LAB / "authority/artifact-types/product/v1"
EXISTING = LAB / "authority/artifact-types/product-identity/v1"
EXISTING_DECISION = LAB / "docs/decisions/0030-cml07-s2-artifact-types-v1/decision.json"
RESOLUTION = LAB / "authority/artifact-types/resolutions/migration-26/v1/product.json"
DECISION_ID = "CAL-DECISION-0055-PRODUCT-ARTIFACT-TYPE-DUPLICATE-RESOLUTION"


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
    candidate = load(CANDIDATE / "artifact.json")
    existing = load(EXISTING / "artifact.json")
    existing_decision = load(EXISTING_DECISION)
    admitted = next(item for item in existing_decision["admitted_artifact_types"] if item["artifact_type_ref"] == existing["artifact_type_ref"])
    if admitted["artifact_sha256"] != sha(EXISTING / "artifact.json") or admitted["schema_sha256"] != sha(EXISTING / "schema.json"):
        raise RuntimeError("existing admitted Product Identity package has drifted")

    authorization = {
        "schema_version": "cyberalchemy-lab-artifact-type-resolution-authorization/v1",
        "authorization_id": "CAL-AUTHORIZATION-0055-PRODUCT-DUPLICATE-RESOLUTION",
        "recorded_on": "2026-10-05",
        "principal_id": "person:<vrondelli>",
        "selected_role": "artifact-type-owner",
        "user_instruction_verbatim": "yes next",
        "interpreted_scope": "Accept the immediately preceding recommendation to resolve type.product into the existing admitted Product Identity carrier, without admitting the duplicate candidate, then continue to the next item.",
        "authorized_effect": "Resolve cal.artifact-type.product/v1 as duplicate-overlap and retain cal.artifact-type.product-identity/v1 as the authoritative carrier.",
        "excluded_effects": ["No new Artifact Type is admitted.", "No Product instance is admitted.", "No consumer or runtime is activated."],
    }
    dump(ROOT / "authorization.json", authorization)

    resolution = {
        "schema_version": "cyberalchemy-lab-artifact-type-queue-resolution/v1",
        "target_id": "type.product",
        "candidate_artifact_type_ref": candidate["artifact_type_ref"],
        "resolution": "resolved-to-existing-admitted-artifact-type",
        "queue_state": "closed-without-duplicate-admission",
        "candidate": {
            "artifact_path": rel(CANDIDATE / "artifact.json"),
            "artifact_sha256": sha(CANDIDATE / "artifact.json"),
            "schema_path": rel(CANDIDATE / "schema.json"),
            "schema_sha256": sha(CANDIDATE / "schema.json"),
        },
        "authoritative_carrier": {
            "artifact_type_ref": existing["artifact_type_ref"],
            "artifact_path": rel(EXISTING / "artifact.json"),
            "artifact_sha256": sha(EXISTING / "artifact.json"),
            "schema_path": rel(EXISTING / "schema.json"),
            "schema_sha256": sha(EXISTING / "schema.json"),
            "admission_decision_ref": existing_decision["decision_id"],
        },
        "rationale": "Both contracts carry durable Product identity under cal.definition.product. Product Identity/v1 is already admitted and has stronger lineage, evidence, scope, and identity-collapse safeguards.",
        "admission_decision_ref": DECISION_ID,
        "artifact_types_admitted": 0,
        "claim_ceiling": "This resolution closes the migration Product candidate as duplicate-overlap and selects the already admitted Product Identity carrier. It does not merge instance data, admit a Product instance, or activate a consumer.",
    }
    dump(RESOLUTION, resolution)

    decision = {
        "schema_version": "cyberalchemy-lab-artifact-type-resolution-decision/v1",
        "decision_id": DECISION_ID,
        "title": "Product Artifact Type duplicate resolution",
        "status": "owner-resolved",
        "authority_effect": "migration-product-candidate-resolved-to-existing-admitted-carrier",
        "authorization": {"path": rel(ROOT / "authorization.json"), "sha256": sha(ROOT / "authorization.json")},
        "resolution_record": {"path": rel(RESOLUTION), "sha256": sha(RESOLUTION)},
        "result": {"queue_items_resolved": 1, "artifact_types_admitted": 0, "instances_admitted": 0, "consumer_activations": 0},
        "excluded_effects": authorization["excluded_effects"],
        "claim_ceiling": resolution["claim_ceiling"],
        "source_direction": {"canonical": "decision.json", "human_projection": "DECISION.md", "projection_policy": "generated-only", "generator": "apply.py"},
    }
    dump(ROOT / "decision.json", decision)
    (ROOT / "DECISION.md").write_text(
        "\n".join([
            "<!-- GENERATED FILE: canonical data is decision.json. -->", "", "# Product Artifact Type duplicate resolution", "",
            f"- Decision: `{DECISION_ID}`", "- Status: `owner-resolved`", "- Candidate: `cal.artifact-type.product/v1`",
            "- Authoritative carrier: `cal.artifact-type.product-identity/v1`", "- New Artifact Types admitted: `0`", "",
            "## Rationale", "", resolution["rationale"], "", "## Claim ceiling", "", resolution["claim_ceiling"], "",
        ]), encoding="utf-8"
    )
    return subprocess.run([sys.executable, str(ROOT / "validate.py")], cwd=LAB, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
