#!/usr/bin/env python3
"""Resolve the migration Project candidate to the admitted Project Identity carrier."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parent
CANDIDATE = LAB / "authority/artifact-types/project/v1"
EXISTING = LAB / "authority/artifact-types/project-identity/v1"
DEFINITION = LAB / "authority/definitions/candidates/0006-craft-identity/definitions/project/v1/definition.json"
EXISTING_DECISION = LAB / "docs/decisions/0030-cml07-s2-artifact-types-v1/decision.json"
RESOLUTION = LAB / "authority/artifact-types/resolutions/migration-26/v1/project.json"
DECISION_ID = "CAL-DECISION-0061-PROJECT-ARTIFACT-TYPE-DUPLICATE-RESOLUTION"


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
    definition = load(DEFINITION)
    admitted = next(
        item for item in existing_decision["admitted_artifact_types"]
        if item["artifact_type_ref"] == existing["artifact_type_ref"]
    )
    if admitted["artifact_sha256"] != sha(EXISTING / "artifact.json") or admitted["schema_sha256"] != sha(EXISTING / "schema.json"):
        raise RuntimeError("existing admitted Project Identity package has drifted")
    if candidate["semantic_definition_refs"] != ["CAV2-D60@1.0.0-candidate.1"]:
        raise RuntimeError("migration Project candidate no longer has the reviewed semantic binding")
    if "CAV2-D60@1.0.0-candidate.1" not in existing["semantic_definition_refs"]:
        raise RuntimeError("Project Identity/v1 no longer binds the Project Definition")

    authorization = {
        "schema_version": "cyberalchemy-lab-artifact-type-resolution-authorization/v1",
        "authorization_id": "CAL-AUTHORIZATION-0061-PROJECT-DUPLICATE-RESOLUTION",
        "recorded_on": "2026-10-05",
        "principal_id": "person:<vrondelli>",
        "selected_role": "artifact-type-owner",
        "user_instruction_verbatim": "yes",
        "interpreted_scope": "Close type.project as duplicate-overlap and retain the already admitted Project Identity/v1 as the authoritative Project carrier. Do not admit the duplicate candidate or any Project instance.",
        "authorized_effect": "Resolve cal.artifact-type.project/v1 as duplicate-overlap and retain cal.artifact-type.project-identity/v1 as the authoritative carrier.",
        "excluded_effects": [
            "No new Artifact Type is admitted.",
            "No Project instance is admitted or activated.",
            "No coordinated work, consumer, implementation, or runtime is authorized or activated.",
            "No claim of complete CAV2-D60 field coverage is established.",
        ],
    }
    dump(ROOT / "authorization.json", authorization)

    resolution = {
        "schema_version": "cyberalchemy-lab-artifact-type-queue-resolution/v1",
        "target_id": "type.project",
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
        "semantic_definition": {
            "definition_ref": f"{definition['definition_id']}@{definition['version']}",
            "path": rel(DEFINITION),
            "sha256": sha(DEFINITION),
        },
        "rationale": "Both contracts carry durable Project coordination identity under CAV2-D60. Project Identity/v1 is already admitted and has dedicated project_id identity, explicit coordination scope, evidence, claim ceiling, and identity-collapse safeguards.",
        "typed_residue": [
            {
                "residue_id": "PROJECT-RESOLUTION-R1",
                "missing": "Project Identity/v1 does not carry every CAV2-D60 element as a first-class field, including goal_refs, purpose_refs, lifecycle_state, owner_routes, and evidence_index structure.",
                "owner_ref": "role:artifact-type-owner",
                "consequence": "The resolution establishes one authoritative carrier but does not establish complete field-level conformance to the admitted Project Definition; a separately reviewed successor may be needed.",
            }
        ],
        "admission_decision_ref": DECISION_ID,
        "artifact_types_admitted": 0,
        "claim_ceiling": "This resolution closes the migration Project candidate as duplicate-overlap and retains the already admitted Project Identity/v1 carrier. It does not merge instance data, admit or activate a Project, authorize coordinated work, or establish complete field-level conformance to CAV2-D60.",
    }
    dump(RESOLUTION, resolution)

    decision = {
        "schema_version": "cyberalchemy-lab-artifact-type-resolution-decision/v1",
        "decision_id": DECISION_ID,
        "title": "Project Artifact Type duplicate resolution",
        "status": "owner-resolved",
        "authority_effect": "migration-project-candidate-resolved-to-existing-admitted-carrier",
        "authorization": {"path": rel(ROOT / "authorization.json"), "sha256": sha(ROOT / "authorization.json")},
        "resolution_record": {"path": rel(RESOLUTION), "sha256": sha(RESOLUTION)},
        "result": {
            "queue_items_resolved": 1,
            "artifact_types_admitted": 0,
            "instances_admitted": 0,
            "consumer_activations": 0,
        },
        "typed_residue": resolution["typed_residue"],
        "excluded_effects": authorization["excluded_effects"],
        "claim_ceiling": resolution["claim_ceiling"],
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
                "# Project Artifact Type duplicate resolution",
                "",
                f"- Decision: `{DECISION_ID}`",
                "- Status: `owner-resolved`",
                "- Candidate: `cal.artifact-type.project/v1`",
                "- Authoritative carrier: `cal.artifact-type.project-identity/v1`",
                "- New Artifact Types admitted: `0`",
                "",
                "## Rationale",
                "",
                resolution["rationale"],
                "",
                "## Recorded residue",
                "",
                "Project Identity/v1 remains the authoritative carrier, but complete field-level coverage of CAV2-D60 requires a separately reviewed successor decision.",
                "",
                "## Claim ceiling",
                "",
                resolution["claim_ceiling"],
                "",
            ]
        ),
        encoding="utf-8",
    )
    return subprocess.run([sys.executable, str(ROOT / "validate.py")], cwd=LAB, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
