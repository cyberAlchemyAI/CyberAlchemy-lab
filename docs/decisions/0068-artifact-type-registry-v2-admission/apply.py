#!/usr/bin/env python3
"""Apply the owner-approved Registry/v2 contract and initial-instance admission."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


LAB = Path(__file__).resolve().parents[3]
ROOT = Path(__file__).resolve().parent
PACKAGE = LAB / "authority/artifact-types/candidates/0006-effective-state-registry"
ARTIFACT = PACKAGE / "artifact-type-candidate.json"
SCHEMA = PACKAGE / "schema.json"
INSTANCE = PACKAGE / "registry.json"
SOURCE_RECEIPT = PACKAGE / "receipts/validation.json"
ADMISSION = LAB / "authority/artifact-types/admissions/artifact-surface/v2/artifact-type-registry.json"
DECISION_ID = "CAL-DECISION-0068-ARTIFACT-TYPE-REGISTRY-V2-ADMISSION"
EXPECTED = {
    "artifact": "6e00cda2f484e41b9ac9c5ba027a858d179de9424e90b5c523a9df933ceafcbe",
    "candidate": "ed3cb6e18930d90f413f15e7a4523266b8293ca2791f4dcd27d5a3f0560a405a",
    "schema": "5140e341541582fec1711e3645d86c1545872f953ff4d2366e0efb18f7fed707",
    "instance": "4f77443384a734acc9a1bd668f87941c45ae78291ecba1d420d3ac4eda2c578c",
    "content_audit": "9272eb31bd5db08ac9b9a0ca41863c2730631c7945bffe3e7ef3bfd8daf4541d",
    "hostile_matrix": "6a90764336a55ee8f5a070f77e93fb3f2264b1da38050c5a61d850e561ace69a",
    "review": "5efb074306ea9acabc67fdfcc912f9d3f99be7b3892c3eac7d3128c8274f5297",
    "receipt": "3c8c849863644c59bc1448ad18f15a9b0079abdd2fb5dfa9da416e053083f13e",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(LAB))


def exact(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": sha(path)}


def atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
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


def main() -> int:
    if (ROOT / "decision.json").exists():
        return subprocess.run([sys.executable, str(ROOT / "validate.py")], cwd=LAB).returncode

    actual = {
        "artifact": sha(ARTIFACT),
        "candidate": sha(PACKAGE / "candidate.json"),
        "schema": sha(SCHEMA),
        "instance": sha(INSTANCE),
        "content_audit": sha(PACKAGE / "content-audit.json"),
        "hostile_matrix": sha(PACKAGE / "hostile-cases.json"),
        "review": sha(PACKAGE / "REVIEW.md"),
        "receipt": sha(SOURCE_RECEIPT),
    }
    if actual != EXPECTED:
        raise RuntimeError(f"reviewed Step 4 envelope changed: {actual}")

    artifact = load(ARTIFACT)
    instance = load(INSTANCE)
    receipt = load(SOURCE_RECEIPT)
    if artifact["artifact_type_ref"] != "cal.artifact-type.artifact-type-registry/v2" or artifact["version"] != "2.0.0-candidate.2":
        raise RuntimeError("reviewed Registry/v2 contract is not current")
    if receipt.get("result") != "PASS" or receipt.get("summary") != {"failed": 0, "passed": 23, "total": 23}:
        raise RuntimeError("Registry/v2 validation must pass 23/23 before admission")
    if instance["current_by_identity"].get("cal.artifact-type.artifact-type-registry") is not None:
        raise RuntimeError("the initial snapshot must not self-admit")

    excluded = [
        "No Artifact Type other than the exact Registry/v2 contract is admitted.",
        "No descriptor or contract listed as candidate-unadmitted becomes admitted.",
        "No semantic rebind, duplicate resolution, activation state, or historical state is changed.",
        "No Relation Kind, endpoint pair, qualifier, Typed Relation, consumer, implementation, or runtime is admitted or activated.",
        "The exact initial registry instance is not rewritten to include its own admission decision.",
    ]
    authorization = {
        "schema_version": "cyberalchemy-lab-artifact-type-registry-admission-authorization/v1",
        "authorization_id": "CAL-AUTHORIZATION-0068-ARTIFACT-TYPE-REGISTRY-V2",
        "recorded_on": "2026-10-06",
        "principal_id": "person:<vrondelli>",
        "selected_role": "artifact-type-owner",
        "user_instruction_verbatim": "admit",
        "interpreted_scope": "Admit the exact reviewed Artifact Type Registry/v2 candidate.2 contract and its exact 56-descriptor, 33-contract initial registry instance as one bounded Step 4 decision.",
        "authorized_effect": "Admit cal.artifact-type.artifact-type-registry/v2 as admitted-current and admit CAL-ARTIFACT-TYPE-EFFECTIVE-STATE-REGISTRY-0001 as its exact initial instance.",
        "artifact_type_contract": exact(ARTIFACT),
        "schema": exact(SCHEMA),
        "initial_registry_instance": exact(INSTANCE),
        "candidate_envelope": exact(PACKAGE / "candidate.json"),
        "content_audit": exact(PACKAGE / "content-audit.json"),
        "hostile_matrix": exact(PACKAGE / "hostile-cases.json"),
        "review": exact(PACKAGE / "REVIEW.md"),
        "validation_receipt": exact(SOURCE_RECEIPT),
        "unadmitted_predecessor_lineage": [
            exact(LAB / "authority/artifact-types/artifact-type-registry/v1/artifact.json"),
            exact(LAB / "authority/artifact-types/artifact-type-registry/v1/candidates/0002-executable-surface/artifact.json"),
        ],
        "excluded_effects": excluded,
    }
    atomic(ROOT / "authorization.json", authorization)

    admission = {
        "schema_version": "cyberalchemy-lab-artifact-type-registry-admission/v1",
        "admission_decision_ref": DECISION_ID,
        "artifact_type": {
            "artifact_type_id": artifact["artifact_type_id"],
            "artifact_type_ref": artifact["artifact_type_ref"],
            "artifact_version": artifact["version"],
            "lifecycle_state": "admitted-current",
            "artifact": exact(ARTIFACT),
            "schema": exact(SCHEMA),
            "instance_discriminator": {"path": "/schema_version", "value": "cyberalchemy-lab-artifact-type-effective-state-registry/v2"},
            "semantic_definition_refs": artifact["semantic_definition_refs"],
        },
        "initial_instance": {
            "registry_id": instance["registry_id"],
            "registry_version": instance["version"],
            "lifecycle_state": "admitted-current",
            "artifact_type_ref": artifact["artifact_type_ref"],
            "registry": exact(INSTANCE),
            "descriptor_count": instance["inventory"]["descriptor_count"],
            "admitted_contract_count": instance["inventory"]["admitted_contract_count"],
            "snapshot_policy": "immutable-bootstrap-snapshot; Decision 0068 enters only a later registry refresh",
        },
        "predecessor_posture": {
            "artifact_type_ref": "cal.artifact-type.artifact-type-registry/v1",
            "lifecycle_state": "candidate-unadmitted",
            "transitioned_to_historical": False,
        },
        "other_artifact_type_admissions": 0,
        "consumer_activations": 0,
        "claim_ceiling": "This overlay admits the exact Artifact Type Registry/v2 candidate.2 contract and the exact initial effective-state registry instance. It does not admit any other Artifact Type or instance, change any state represented inside the snapshot, perform a semantic rebind, admit a relation, or activate a consumer or runtime.",
    }
    atomic(ADMISSION, admission)

    decision = {
        "schema_version": "cyberalchemy-lab-artifact-type-registry-admission-decision/v1",
        "decision_id": DECISION_ID,
        "title": "Artifact Type Registry/v2 and initial registry instance admission",
        "status": "owner-admitted",
        "authority_effect": "artifact-type-registry-v2-and-exact-initial-instance-admitted",
        "authorization": exact(ROOT / "authorization.json"),
        "admission_record": exact(ADMISSION),
        "admitted_artifact_type": admission["artifact_type"],
        "admitted_initial_instance": admission["initial_instance"],
        "admission_result": {
            "artifact_types_admitted": 1,
            "registry_instances_admitted": 1,
            "predecessors_transitioned_to_historical": 0,
            "other_artifact_types_admitted": 0,
            "consumer_activations": 0,
            "result": "complete",
        },
        "transaction_model": {
            "kind": "decision-overlay-only",
            "reviewed_contract_bytes_preserved": True,
            "initial_instance_bytes_preserved": True,
            "bootstrap_self_inclusion_deferred": True,
        },
        "successor_obligation": "Create a separately reviewed Registry/v2 snapshot to ingest Decision 0068 and later admissions; do not mutate the admitted initial snapshot.",
        "excluded_effects": excluded,
        "claim_ceiling": admission["claim_ceiling"],
        "source_direction": {"canonical": "decision.json", "human_projection": "DECISION.md", "projection_policy": "generated-only", "generator": "apply.py"},
    }
    atomic(ROOT / "decision.json", decision)
    (ROOT / "DECISION.md").write_text("\n".join([
        "<!-- GENERATED FILE: canonical data is decision.json. -->",
        "",
        "# Artifact Type Registry/v2 and initial registry admission",
        "",
        f"- Decision: `{DECISION_ID}`",
        "- Status: `owner-admitted`",
        "- Artifact Type: `cal.artifact-type.artifact-type-registry/v2` — `admitted-current`",
        f"- Initial registry: `{instance['registry_id']}` — `admitted-current`",
        "- Descriptor snapshot: `56`",
        "- Admitted-contract snapshot: `33`",
        "- Other Artifact Types admitted: `0`",
        "- Consumer activations: `0`",
        "",
        "## Bootstrap rule",
        "",
        "Decision 0068 enters a later registry refresh. The admitted initial snapshot remains byte-for-byte unchanged.",
        "",
        "## Claim ceiling",
        "",
        admission["claim_ceiling"],
        "",
    ]), encoding="utf-8")
    return subprocess.run([sys.executable, str(ROOT / "validate.py")], cwd=LAB).returncode


if __name__ == "__main__":
    raise SystemExit(main())
