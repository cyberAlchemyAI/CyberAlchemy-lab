#!/usr/bin/env python3
"""Apply the approved 60-Definition integrated Lab model admission."""

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
CANDIDATE_ROOT = LAB / "authority/definitions/candidates/0013-integrated-lab-definition-model"
CANDIDATE = CANDIDATE_ROOT / "candidate.json"
SOURCE_RECEIPT = CANDIDATE_ROOT / "receipts/validation.json"
REGISTRY = LAB / "authority/definitions/registry.json"
INDEX = LAB / "authority/definitions/DEFINITIONS-INDEX.md"
DRIFT = LAB / "authority/definitions/drift-audit.json"
DRIFT_MD = LAB / "authority/definitions/DEFINITION-DRIFT-AUDIT.md"
DECISION_ID = "CAL-DECISION-0065-INTEGRATED-LAB-DEFINITION-MODEL-ADMISSION"
CANDIDATE_SHA256 = "a355adf57079efb45a5e0c8431e6cb2b9e7b57536264465ad69c02af53296994"
RECEIPT_SHA256 = "890bd18595c8b0a4e52c830df8507ba3c1d5c366a7e0c43aa99d3fbde5c4f0f3"
REGISTRY_PREIMAGE_SHA256 = "b0445231b42ba37b436e876242e779ec1d2921ef424edceced0d8e78f59dc561"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def encode(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(LAB))


def exact(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": sha(path)}


def atomic_write(path: Path, data: bytes) -> None:
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


def render_index(registry: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED FILE: edit machine sources and run the bound admission builder. -->",
        "",
        "# CyberAlchemy Lab Definition Index",
        "",
        f"- Status: `{registry['status']}`",
        f"- Admission decision: `{registry['admission_decision_ref']}`",
        "",
        "| ID | Version | Term | Lifecycle | Path |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in registry["entries"]:
        lines.append(
            f"| `{item['definition_id']}` | `{item['version']}` | {item['term']} | "
            f"`{item['lifecycle_state']}` | `{item['path']}` |"
        )
    lines.extend(["", "## Current lookup", ""])
    lines.extend(f"- `{key}` -> `{value}`" for key, value in registry["current_lookup"].items())
    lines.extend(["", "## Claim ceiling", "", registry["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


def render_drift(data: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED FILE: edit drift-audit.json through its bound admission builder. -->",
        "",
        "# Definition Drift Audit",
        "",
        "> Post-admission explanatory projection; machine JSON is canonical.",
        "",
    ]
    for item in data["findings"]:
        lines.extend([
            f"## {item['finding_id']} — {item['status']}",
            "",
            item["condition"],
            "",
            f"Remediation: {item['remediation']}",
            "",
        ])
    lines.extend(["## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    candidate = load(CANDIDATE)
    source_receipt = load(SOURCE_RECEIPT)
    live = load(REGISTRY)
    if sha(CANDIDATE) != CANDIDATE_SHA256:
        raise RuntimeError("reviewed candidate digest changed")
    if sha(SOURCE_RECEIPT) != RECEIPT_SHA256:
        raise RuntimeError("reviewed candidate validation receipt changed")
    if source_receipt.get("result") != "PASS" or source_receipt.get("summary") != {"failed": 0, "passed": 19, "total": 19}:
        raise RuntimeError("candidate validation must pass 19/19")
    if len(candidate["definitions"]) != 60 or len({x["definition_id"] for x in candidate["definitions"]}) != 60:
        raise RuntimeError("approval binds exactly 60 unique Definition identities")

    definition_digests = source_receipt["materials"]["definition_digests"]
    records = []
    for item in candidate["definitions"]:
        path = LAB / item["path"]
        record = load(path)
        if record["definition_id"] != item["definition_id"] or record["version"] != item["version"]:
            raise RuntimeError(f"candidate identity mismatch: {item['definition_id']}")
        if sha(path) != definition_digests.get(record["definition_id"]):
            raise RuntimeError(f"reviewed Definition digest changed: {record['definition_id']}")
        records.append((item, record, path))

    already = [x for x in live["entries"] if x["definition_id"] in {r[1]["definition_id"] for r in records}]
    if already:
        if len(already) == 60 and all(x.get("admission_decision_ref") == DECISION_ID and x["lifecycle_state"] == "admitted" for x in already):
            return subprocess.run([sys.executable, str(ROOT / "validate.py")], cwd=LAB, check=False).returncode
        raise RuntimeError("one or more Definition identities already exist under another posture")
    if sha(REGISTRY) != REGISTRY_PREIMAGE_SHA256 or len(live["entries"]) != 119 or len(live["current_lookup"]) != 113:
        raise RuntimeError("Definition registry preimage changed")

    authorization = {
        "schema_version": "cyberalchemy-lab-definition-admission-authorization/v1",
        "authorization_id": "CAL-AUTHORIZATION-0065-INTEGRATED-LAB-DEFINITION-MODEL",
        "recorded_on": "2026-10-06",
        "principal_id": "person:<vrondelli>",
        "selected_role": "definition-owner",
        "user_instruction_verbatim": "Admitted",
        "interpreted_scope": "Admit the exact revised 60-Definition Step 2 batch shown immediately before this instruction.",
        "authorized_effect": "Admit exactly 60 digest-bound Definition versions and select each as its current identity.",
        "candidate": exact(CANDIDATE),
        "validation_receipt": exact(SOURCE_RECEIPT),
        "registry_preimage": exact(REGISTRY),
        "definition_digests": definition_digests,
        "excluded_effects": [
            "No Artifact Type or artifact instance is admitted.",
            "No Relation Kind, endpoint pair, qualifier schema, Typed Relation, or ontology-local edge is admitted.",
            "No Policy instance, Decision beyond this admission, runtime, adapter, consumer, migration, publication, release, or deployment is activated.",
            "No later step in the integrated-model admission sequence is pre-approved.",
        ],
    }
    atomic_write(ROOT / "authorization.json", encode(authorization))

    registry = deepcopy(live)
    for item, record, path in records:
        registry["entries"].append({
            "admission_decision_ref": DECISION_ID,
            "definition_id": record["definition_id"],
            "lifecycle_state": "admitted",
            "path": rel(path),
            "sha256": sha(path),
            "term": record["term"],
            "version": record["version"],
        })
        registry["current_lookup"][record["definition_id"]] = f"{record['definition_id']}@{record['version']}"
    registry["entries"].sort(key=lambda x: (x["definition_id"], x["version"]))
    registry["current_lookup"] = dict(sorted(registry["current_lookup"].items()))
    registry["status"] = "owner-admitted"
    registry["authority_effect"] = "one-hundred-seventy-nine-exact-definition-versions-canonical"
    registry["admission_decision_ref"] = DECISION_ID
    registry["predecessor"] = {
        "path": rel(REGISTRY), "sha256": sha(REGISTRY), "entry_count": 119, "current_count": 113,
        "admission_decision_ref": live["admission_decision_ref"],
    }
    registry["source_direction"] = {
        "canonical": "registry.json", "human_projection": "DEFINITIONS-INDEX.md",
        "projection_policy": "generated-only", "generator_ref": "cal.generator.integrated-lab-definition-admission/v1",
    }
    registry["claim_ceiling"] = (
        "This registry contains 179 admitted Definition versions and selects 173 current identities, including the exact "
        "60-Definition integrated Lab model admitted by CAL-DECISION-0065. It does not admit Artifact Types, instances, "
        "Relation Kinds, endpoint pairs, qualifier schemas, Typed Relations, ontology edges, Policies, runtimes, or consumers."
    )

    drift = deepcopy(load(DRIFT))
    drift["admission_decision_ref"] = DECISION_ID
    drift["record_id"] = "CAL-DEFINITION-DRIFT-AUDIT-POST-INTEGRATED-LAB-MODEL-V1"
    drift["findings"].append({
        "finding_id": "INTEGRATED-LAB-DEFINITIONS-POST-001",
        "severity": "resolved",
        "status": "admitted",
        "condition": "All 60 exact missing Definition identities identified by the integrated Lab semantic gap audit are admitted and current.",
        "target": "CAL-DEFINITION-CANDIDATE-INTEGRATED-LAB-MODEL-0013",
        "remediation": "Use the admitted meanings for specialization resolution, carrier design, Relation Kind closure, qualifiers, Ontology integration, and runtime work while preserving their separate authority gates.",
    })
    drift["summary"]["current_definition_terms"] = 173
    drift["summary"]["definition_versions"] = 179
    drift["summary"]["new_definition_identities"] = 141
    drift["summary"]["new_definition_versions_admitted"] = 145
    drift["summary"]["integrated_lab_model_definitions"] = "60-admitted-current"
    drift["source_direction"] = {
        "canonical": "drift-audit.json", "human_projection": "DEFINITION-DRIFT-AUDIT.md",
        "projection_policy": "generated-only", "generator_ref": "cal.generator.integrated-lab-definition-admission/v1",
    }
    drift["claim_ceiling"] = (
        "This audit establishes admission of the exact 60-Definition integrated Lab semantic model. It does not establish "
        "carrier, relation-pair, qualifier, ontology, governance-instance, runtime, or consumer conformance."
    )

    backups = {p: p.read_bytes() for p in [REGISTRY, INDEX, DRIFT, DRIFT_MD]}
    created = [ROOT / x for x in ["authorization.json", "decision.json", "DECISION.md", "receipts/validation.json"]]
    try:
        atomic_write(REGISTRY, encode(registry))
        atomic_write(INDEX, render_index(registry).encode())
        drift["registry_sha256"] = sha(REGISTRY)
        atomic_write(DRIFT, encode(drift))
        atomic_write(DRIFT_MD, render_drift(drift).encode())
        decision = {
            "schema_version": "cyberalchemy-lab-definition-admission-decision/v1",
            "decision_id": DECISION_ID,
            "title": "Integrated Lab 60-Definition model admission",
            "status": "owner-admitted",
            "authority_effect": "exact-sixty-definition-versions-admitted-current",
            "authorization": exact(ROOT / "authorization.json"),
            "admitted_definitions": [
                {"definition_ref": f"{record['definition_id']}@{record['version']}", "path": rel(path), "sha256": sha(path)}
                for _, record, path in records
            ],
            "registry_postimage": exact(REGISTRY),
            "index_postimage": exact(INDEX),
            "drift_audit_postimage": exact(DRIFT),
            "admission_result": {
                "definitions_admitted": 60, "canonical_definition_versions": 179,
                "current_definition_identities": 173, "artifact_types_admitted": 0,
                "relation_kinds_admitted": 0, "endpoint_pairs_admitted": 0,
                "consumer_activations": 0, "result": "complete",
            },
            "excluded_effects": authorization["excluded_effects"],
            "claim_ceiling": registry["claim_ceiling"],
            "source_direction": {"canonical": "decision.json", "human_projection": "DECISION.md", "projection_policy": "generated-only", "generator": "apply.py"},
        }
        atomic_write(ROOT / "decision.json", encode(decision))
        atomic_write(ROOT / "DECISION.md", ("\n".join([
            "<!-- GENERATED FILE: canonical data is decision.json. -->", "", "# Integrated Lab 60-Definition model admission", "",
            f"- Decision: `{DECISION_ID}`", "- Status: `owner-admitted`", "- Definitions admitted: `60`",
            "- Registry versions: `179`", "- Current identities: `173`", "- Artifact Types admitted: `0`",
            "- Relation Kinds admitted: `0`", "", "## Claim ceiling", "", registry["claim_ceiling"], "",
        ])).encode())
        result = subprocess.run([sys.executable, str(ROOT / "validate.py")], cwd=LAB, check=False)
        if result.returncode:
            raise RuntimeError("post-admission validation failed")
    except Exception:
        for path, data in backups.items():
            atomic_write(path, data)
        for path in created:
            path.unlink(missing_ok=True)
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
