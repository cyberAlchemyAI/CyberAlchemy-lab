#!/usr/bin/env python3
"""Apply the approved Typed Connection Extension Rule Definition admission."""

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
CANDIDATE = LAB / "authority/definitions/candidates/0012-typed-connection-extension-rule"
DEFINITION = CANDIDATE / "definitions/typed-connection-extension-rule/v1/definition.json"
VALIDATION = CANDIDATE / "receipts/validation.json"
REGISTRY = LAB / "authority/definitions/registry.json"
INDEX = LAB / "authority/definitions/DEFINITIONS-INDEX.md"
DRIFT = LAB / "authority/definitions/drift-audit.json"
DRIFT_MD = LAB / "authority/definitions/DEFINITION-DRIFT-AUDIT.md"
DECISION_ID = "CAL-DECISION-0064-TYPED-CONNECTION-EXTENSION-RULE-ADMISSION"
DEFINITION_ID = "cal.definition.typed-connection-extension-rule"
DEFINITION_VERSION = "1.0.0-candidate.1"


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
    definition = load(DEFINITION)
    validation = load(VALIDATION)
    live = load(REGISTRY)

    if definition["definition_id"] != DEFINITION_ID or definition["version"] != DEFINITION_VERSION:
        raise RuntimeError("reviewed Definition identity or version changed")
    if sha(DEFINITION) != "9ceb0da5a4a71c375d3191ad6b05077182e1dbaea8e618cabc60127a5fb9c962":
        raise RuntimeError("reviewed Definition digest changed")
    if validation.get("result") != "PASS" or validation.get("summary") != {"failed": 0, "passed": 19, "total": 19}:
        raise RuntimeError("candidate validation must pass 19/19 before admission")

    existing = [
        item for item in live["entries"]
        if item["definition_id"] == DEFINITION_ID and item["version"] == DEFINITION_VERSION
    ]
    if existing:
        if existing[0].get("admission_decision_ref") != DECISION_ID or existing[0].get("lifecycle_state") != "admitted":
            raise RuntimeError("Definition identity/version already exists under a different posture")
        return subprocess.run([sys.executable, str(ROOT / "validate.py")], cwd=LAB, check=False).returncode

    if len(live["entries"]) != 118 or len(live["current_lookup"]) != 112:
        raise RuntimeError("Definition registry preimage counts changed")

    authorization = {
        "schema_version": "cyberalchemy-lab-definition-admission-authorization/v1",
        "authorization_id": "CAL-AUTHORIZATION-0064-TYPED-CONNECTION-EXTENSION-RULE",
        "recorded_on": "2026-10-06",
        "principal_id": "person:<vrondelli>",
        "selected_role": "definition-owner",
        "user_instruction_verbatim": "Admited",
        "interpreted_scope": "Admit the exact revised Typed Connection Extension Rule Definition shown immediately before this instruction. Continue steps 2 through 8 through their separate review and decision gates.",
        "authorized_effect": f"Admit {DEFINITION_ID}@{DEFINITION_VERSION} at the exact reviewed digest and select it as current.",
        "candidate": exact(CANDIDATE / "candidate.json"),
        "definition": exact(DEFINITION),
        "validation_receipt": exact(VALIDATION),
        "registry_preimage": exact(REGISTRY),
        "excluded_effects": [
            "No Relation Kind, endpoint pair, qualifier schema, endpoint carrier, Typed Relation, ontology-local edge, or relation instance is admitted.",
            "No Artifact Type, consumer, runtime, migration, implementation, or control is activated.",
            "No later step in the integrated-model admission sequence is pre-approved.",
            "No commit, push, publication, release, or deployment is authorized.",
        ],
    }
    atomic_write(ROOT / "authorization.json", encode(authorization))

    registry = deepcopy(live)
    registry["entries"].append({
        "admission_decision_ref": DECISION_ID,
        "definition_id": DEFINITION_ID,
        "lifecycle_state": "admitted",
        "path": rel(DEFINITION),
        "sha256": sha(DEFINITION),
        "term": definition["term"],
        "version": DEFINITION_VERSION,
    })
    registry["entries"].sort(key=lambda item: (item["definition_id"], item["version"]))
    registry["current_lookup"][DEFINITION_ID] = f"{DEFINITION_ID}@{DEFINITION_VERSION}"
    registry["current_lookup"] = dict(sorted(registry["current_lookup"].items()))
    registry["status"] = "owner-admitted"
    registry["authority_effect"] = "one-hundred-nineteen-exact-definition-versions-canonical"
    registry["admission_decision_ref"] = DECISION_ID
    registry["predecessor"] = {
        "path": rel(REGISTRY),
        "sha256": sha(REGISTRY),
        "entry_count": len(live["entries"]),
        "current_count": len(live["current_lookup"]),
        "admission_decision_ref": live["admission_decision_ref"],
    }
    registry["source_direction"] = {
        "canonical": "registry.json",
        "human_projection": "DEFINITIONS-INDEX.md",
        "projection_policy": "generated-only",
        "generator_ref": "cal.generator.typed-connection-extension-rule-admission/v1",
    }
    registry["claim_ceiling"] = (
        "This registry contains 119 admitted Definition versions and selects 113 current identities, including the exact "
        "Typed Connection Extension Rule admitted by CAL-DECISION-0064. It does not admit Relation Kinds, endpoint pairs, "
        "qualifier schemas, endpoint carriers, Typed Relations, ontology-local edges, instances, consumers, or runtimes."
    )

    drift = deepcopy(load(DRIFT))
    drift["admission_decision_ref"] = DECISION_ID
    drift["record_id"] = "CAL-DEFINITION-DRIFT-AUDIT-POST-TCER-V1"
    drift["findings"].append({
        "finding_id": "TCER-POST-001",
        "severity": "resolved",
        "status": "admitted",
        "condition": "The Typed Connection Extension Rule is admitted at its exact reviewed digest and selected as the current Definition identity.",
        "target": f"{DEFINITION_ID}@{DEFINITION_VERSION}",
        "remediation": "Use this rule for every global pair extension and for every global-versus-ontology-local scope decision; keep Relation Kind and carrier admission separate.",
    })
    drift["summary"]["current_definition_terms"] = 113
    drift["summary"]["definition_versions"] = 119
    drift["summary"]["typed_connection_extension_rule"] = "admitted-current"
    drift["source_direction"] = {
        "canonical": "drift-audit.json",
        "human_projection": "DEFINITION-DRIFT-AUDIT.md",
        "projection_policy": "generated-only",
        "generator_ref": "cal.generator.typed-connection-extension-rule-admission/v1",
    }
    drift["claim_ceiling"] = (
        "This audit establishes admission of the exact Typed Connection Extension Rule and records remaining semantic "
        "boundaries. It does not establish Relation Kind, endpoint, qualifier, carrier, relation-instance, consumer, or runtime conformance."
    )

    backups = {path: path.read_bytes() for path in [REGISTRY, INDEX, DRIFT, DRIFT_MD]}
    created = [ROOT / name for name in ["authorization.json", "decision.json", "DECISION.md"]]
    try:
        atomic_write(REGISTRY, encode(registry))
        atomic_write(INDEX, render_index(registry).encode())
        drift["registry_sha256"] = sha(REGISTRY)
        atomic_write(DRIFT, encode(drift))
        atomic_write(DRIFT_MD, render_drift(drift).encode())

        decision = {
            "schema_version": "cyberalchemy-lab-definition-admission-decision/v1",
            "decision_id": DECISION_ID,
            "title": "Typed Connection Extension Rule Definition admission",
            "status": "owner-admitted",
            "authority_effect": "exact-typed-connection-extension-rule-definition-admitted",
            "authorization": exact(ROOT / "authorization.json"),
            "admitted_definition": {
                "definition_ref": f"{DEFINITION_ID}@{DEFINITION_VERSION}",
                "path": rel(DEFINITION),
                "sha256": sha(DEFINITION),
                "decision_overlay_status": "admitted-current",
            },
            "registry_postimage": exact(REGISTRY),
            "index_postimage": exact(INDEX),
            "drift_audit_postimage": exact(DRIFT),
            "admission_result": {
                "definitions_admitted": 1,
                "canonical_definition_versions": 119,
                "current_definition_identities": 113,
                "relation_kinds_admitted": 0,
                "endpoint_pairs_admitted": 0,
                "consumer_activations": 0,
                "result": "complete",
            },
            "excluded_effects": authorization["excluded_effects"],
            "claim_ceiling": registry["claim_ceiling"],
            "source_direction": {
                "canonical": "decision.json",
                "human_projection": "DECISION.md",
                "projection_policy": "generated-only",
                "generator": "apply.py",
            },
        }
        atomic_write(ROOT / "decision.json", encode(decision))
        decision_md = "\n".join([
            "<!-- GENERATED FILE: canonical data is decision.json. -->",
            "",
            "# Typed Connection Extension Rule Definition admission",
            "",
            f"- Decision: `{DECISION_ID}`",
            "- Status: `owner-admitted`",
            f"- Definition: `{DEFINITION_ID}@{DEFINITION_VERSION}`",
            f"- Digest: `{sha(DEFINITION)}`",
            "- Relation Kinds admitted: `0`",
            "- Endpoint pairs admitted: `0`",
            "",
            "## Claim ceiling",
            "",
            registry["claim_ceiling"],
            "",
        ])
        atomic_write(ROOT / "DECISION.md", decision_md.encode())
        result = subprocess.run([sys.executable, str(ROOT / "validate.py")], cwd=LAB, check=False)
        if result.returncode:
            raise RuntimeError("post-admission validation failed")
    except Exception:
        for path, data in backups.items():
            atomic_write(path, data)
        for path in created + [ROOT / "receipts/validation.json"]:
            path.unlink(missing_ok=True)
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
