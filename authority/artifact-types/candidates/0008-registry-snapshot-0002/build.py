#!/usr/bin/env python3
"""Build immutable Registry/v2 Snapshot 0002 from admitted Snapshot 0001."""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
BASE = LAB / "authority/artifact-types/candidates/0006-effective-state-registry/registry.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_registry() -> dict:
    registry = copy.deepcopy(load(BASE))
    contract_path = "authority/artifact-types/candidates/0006-effective-state-registry/artifact-type-candidate.json"
    schema_path = "authority/artifact-types/candidates/0006-effective-state-registry/schema.json"
    decision_path = "docs/decisions/0068-artifact-type-registry-v2-admission/decision.json"
    decision = load(LAB / decision_path)
    contract = load(LAB / contract_path)

    registry["registry_id"] = "CAL-ARTIFACT-TYPE-EFFECTIVE-STATE-REGISTRY-0002"
    registry["version"] = "2.0.0-candidate.2"
    registry["status"] = "candidate-postimage"
    registry["authority_effect"] = "none"
    registry["claim_ceiling"] = (
        "This candidate snapshot resolves 57 visible Artifact Type descriptors and 34 admitted contract entries after "
        "ingesting Decision 0068. It does not admit this snapshot, alter Snapshot 0001, admit any remaining candidate "
        "Artifact Type or instance, perform a semantic rebind, admit a relation, or activate a consumer or runtime."
    )
    registry["source_direction"] = {
        "canonical": "registry.json",
        "generator_ref": "cal.generator.artifact-type-registry-snapshot-0002/v1",
        "human_projection": "REGISTRY.md",
        "projection_policy": "generated-only",
    }

    definition_refs = list(contract["semantic_definition_refs"])
    registry["descriptors"].append({
        "activation_state": "not-activated",
        "artifact_type_id": contract["artifact_type_id"],
        "artifact_type_ref": contract["artifact_type_ref"],
        "descriptor_path": contract_path,
        "descriptor_sha256": sha(LAB / contract_path),
        "descriptor_version": contract["version"],
        "effective_decision_refs": [decision["decision_id"]],
        "effective_state": "admitted-current",
        "embedded_status": contract["status"],
        "instance_discriminator": copy.deepcopy(decision["admitted_artifact_type"]["instance_discriminator"]),
        "proposed_primary_definition_ref": None,
        "resolution_target_ref": None,
        "schema_path": schema_path,
        "schema_sha256": sha(LAB / schema_path),
        "semantic_binding_posture": "current-as-declared",
        "semantic_definition_refs": definition_refs,
    })
    registry["admitted_contracts"].append({
        "admission_decision_ref": decision["decision_id"],
        "artifact_path": contract_path,
        "artifact_sha256": sha(LAB / contract_path),
        "artifact_type_ref": contract["artifact_type_ref"],
        "instance_discriminator": copy.deepcopy(decision["admitted_artifact_type"]["instance_discriminator"]),
        "lifecycle_state": "admitted-current",
        "schema_path": schema_path,
        "schema_selector": None,
        "schema_sha256": sha(LAB / schema_path),
        "semantic_definition_refs": definition_refs,
        "semantic_kind": contract["classification"]["semantic_kind"],
    })
    registry["current_by_identity"][contract["artifact_type_id"]] = contract["artifact_type_ref"]
    registry["overlay_sources"].append({
        "path": decision_path,
        "role": "decision-overlay",
        "sha256": sha(LAB / decision_path),
    })

    states = Counter(item["effective_state"] for item in registry["descriptors"])
    bindings = Counter(item["semantic_binding_posture"] for item in registry["descriptors"])
    declared_refs = {
        item["artifact_type_ref"] for item in registry["descriptors"]
        if item["effective_state"] != "resolved-duplicate"
    }
    registry["inventory"] = {
        "admitted_contract_count": len(registry["admitted_contracts"]),
        "admitted_current_count": sum(item["lifecycle_state"] == "admitted-current" for item in registry["admitted_contracts"]),
        "admitted_historical_count": sum(item["lifecycle_state"] == "admitted-historical" for item in registry["admitted_contracts"]),
        "descriptor_count": len(registry["descriptors"]),
        "descriptor_declared_ref_count": len(declared_refs),
        "descriptor_identity_count": len({item["artifact_type_id"] for item in registry["descriptors"]}),
        "descriptor_resolved_ref_count": len({item["artifact_type_ref"] for item in registry["descriptors"]}),
        "duplicate_resolution_count": len(registry["duplicate_resolutions"]),
        "semantic_binding_counts": dict(sorted(bindings.items())),
        "state_counts": dict(sorted(states.items())),
    }
    return registry


def write_projection(registry: dict) -> None:
    lines = [
        "<!-- GENERATED FILE: canonical data is registry.json. -->",
        "",
        "# Artifact Type effective-state registry — Snapshot 0002",
        "",
        f"- Registry: `{registry['registry_id']}`",
        f"- Version: `{registry['version']}`",
        f"- Status: `{registry['status']}`",
        f"- Authority effect: `{registry['authority_effect']}`",
        "- Predecessor: `CAL-ARTIFACT-TYPE-EFFECTIVE-STATE-REGISTRY-0001`",
        "- Exact delta: Registry/v2 descriptor, admitted contract, current identity mapping, and Decision 0068 overlay",
        "",
        "## Inventory",
        "",
    ]
    for key, value in registry["inventory"].items():
        rendered = json.dumps(value, sort_keys=True) if isinstance(value, dict) else str(value)
        lines.append(f"- {key.replace('_', ' ').title()}: `{rendered}`")
    lines += [
        "",
        "## Added current carrier",
        "",
        "| Artifact Type ref | Effective state | Decision |",
        "| --- | --- | --- |",
        "| `cal.artifact-type.artifact-type-registry/v2` | `admitted-current` | `CAL-DECISION-0068-ARTIFACT-TYPE-REGISTRY-V2-ADMISSION` |",
        "",
        "## Realistic example",
        "",
        "A consumer asks which Artifact Type contract governs effective-state registry instances. Snapshot 0002 resolves the identity `cal.artifact-type.artifact-type-registry` to `cal.artifact-type.artifact-type-registry/v2`, and the exact instance discriminator remains `/schema_version = cyberalchemy-lab-artifact-type-effective-state-registry/v2`.",
        "",
        "## Claim ceiling",
        "",
        registry["claim_ceiling"],
    ]
    (ROOT / "REGISTRY.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    built = build_registry()
    dump(ROOT / "registry.json", built)
    write_projection(built)
