#!/usr/bin/env python3
"""Build Registry Snapshot 0003 and the resolved endpoint inventory for Step 5."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
CANDIDATE = ROOT / "candidate.json"


def load(path: Path) -> Any: return json.loads(path.read_text(encoding="utf-8"))
def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path: Path, value: Any) -> None: path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def infer_discriminator(artifact: dict, schema: dict) -> dict:
    explicit = artifact.get("instance_contract", {}).get("instance_discriminator")
    if explicit: return explicit
    properties = schema.get("properties", {})
    if "schema_version" in properties and "const" in properties["schema_version"]:
        return {"path": "/schema_version", "value": properties["schema_version"]["const"]}
    if "kind" in properties and "const" in properties["kind"]:
        return {"path": "/kind", "value": properties["kind"]["const"]}
    raise ValueError(f"no discriminator for {artifact['artifact_type_ref']}")


def descriptor(path: str) -> dict:
    artifact_path = LAB / path
    artifact = load(artifact_path)
    schema_path = artifact_path.parent / "schema.json"
    return {
        "activation_state": "not-activated",
        "artifact_type_id": artifact["artifact_type_id"],
        "artifact_type_ref": artifact["artifact_type_ref"],
        "descriptor_path": path,
        "descriptor_sha256": sha(artifact_path),
        "descriptor_version": artifact["version"],
        "effective_decision_refs": [],
        "effective_state": "candidate-unadmitted",
        "embedded_status": artifact["status"],
        "instance_discriminator": infer_discriminator(artifact, load(schema_path)),
        "proposed_primary_definition_ref": None,
        "resolution_target_ref": None,
        "schema_path": str(schema_path.relative_to(LAB)),
        "schema_sha256": sha(schema_path),
        "semantic_binding_posture": "current-as-declared",
        "semantic_definition_refs": artifact["semantic_definition_refs"],
    }


def build_registry(candidate: dict) -> tuple[dict, list[dict]]:
    base = load(LAB / candidate["inputs"]["predecessor_registry"])
    hard = load(LAB / candidate["inputs"]["hard_corrections"])
    endpoints = load(LAB / candidate["inputs"]["endpoint_carriers"])
    legacy = load(LAB / candidate["inputs"]["legacy_successors"])
    meta = load(LAB / candidate["inputs"]["metamodel_successors"])
    relation_hardening = load(LAB / candidate["inputs"]["relation_carrier_hardening"])
    registry = copy.deepcopy(base)

    revised_paths = {row["artifact_type_ref"]: row["artifact_path"] for row in hard["postimages"] if row["artifact_type_ref"] != "cal.artifact-type.capability-realization-binding/v2"}
    for index, current in enumerate(registry["descriptors"]):
        path = revised_paths.get(current["artifact_type_ref"])
        if path and current["effective_state"] == "candidate-unadmitted":
            registry["descriptors"][index] = descriptor(path)

    additions = []
    hard_successor = next(row for row in hard["postimages"] if row["artifact_type_ref"] == "cal.artifact-type.capability-realization-binding/v2")
    for row in [hard_successor, *legacy["entries"], *meta["entries"], *endpoints["entries"], *relation_hardening["entries"]]:
        additions.append(descriptor(row["artifact_path"]))
    registry["descriptors"].extend(additions)

    successor_rows = [hard_successor, *legacy["entries"], *meta["entries"]]
    predecessor_by_successor = {
        "cal.artifact-type.capability-realization-binding/v2": "authority/artifact-types/capability-realization-binding/v1/artifact.json",
        **{row["artifact_type_ref"]: load(LAB / row["artifact_path"])["predecessor_contract"]["path"] for row in [*legacy["entries"], *meta["entries"]]},
    }
    for row in successor_rows:
        registry["candidate_lineage"].append({
            "artifact_type_ref": row["artifact_type_ref"],
            "posture": "candidate-successor-unadmitted",
            "predecessor_descriptor": predecessor_by_successor[row["artifact_type_ref"]],
            "successor_descriptor": row["artifact_path"],
        })

    registry["registry_id"] = "CAL-ARTIFACT-TYPE-EFFECTIVE-STATE-REGISTRY-0003"
    registry["version"] = "2.0.0-candidate.3"
    registry["status"] = "candidate-postimage"
    registry["authority_effect"] = "none"
    registry["claim_ceiling"] = "This candidate snapshot indexes 90 visible Artifact Type descriptors after complete Step 5 materialization and pre-admission hardening of the two relation carriers, while preserving 34 admitted contract entries and every current mapping from Snapshot 0002. It does not admit a candidate, transition a predecessor, admit a relation, or activate a consumer or runtime."
    registry["source_direction"] = {"canonical": "registry.json", "generator_ref": "cal.generator.step5-postimage-registry/v1", "human_projection": "REGISTRY.md", "projection_policy": "generated-only"}
    states = Counter(row["effective_state"] for row in registry["descriptors"])
    bindings = Counter(row["semantic_binding_posture"] for row in registry["descriptors"])
    registry["inventory"] = {
        "admitted_contract_count": len(registry["admitted_contracts"]),
        "admitted_current_count": sum(row["lifecycle_state"] == "admitted-current" for row in registry["admitted_contracts"]),
        "admitted_historical_count": sum(row["lifecycle_state"] == "admitted-historical" for row in registry["admitted_contracts"]),
        "descriptor_count": len(registry["descriptors"]),
        "descriptor_declared_ref_count": len({row["artifact_type_ref"] for row in registry["descriptors"] if row["effective_state"] != "resolved-duplicate"}),
        "descriptor_identity_count": len({row["artifact_type_id"] for row in registry["descriptors"]}),
        "descriptor_resolved_ref_count": len({row["artifact_type_ref"] for row in registry["descriptors"]}),
        "duplicate_resolution_count": len(registry["duplicate_resolutions"]),
        "semantic_binding_counts": {
            "admitted-successor-required": bindings.get("admitted-successor-required", 0),
            "candidate-rebind-required": bindings.get("candidate-rebind-required", 0),
            "current-as-declared": bindings.get("current-as-declared", 0),
        },
        "state_counts": dict(sorted(states.items())),
    }
    return registry, additions


def build_endpoint_inventory(candidate: dict, additions: list[dict]) -> dict:
    source = load(LAB / candidate["inputs"]["relation_endpoint_inventory"])
    carrier_by_kind = {row["artifact_type_id"].removeprefix("cal.artifact-type."): row for row in additions}
    result = copy.deepcopy(source)
    for entry in result["entries"]:
        if entry["lifecycle_state"] == "referenced-no-canonical-carrier":
            carrier = carrier_by_kind[entry["endpoint_kind"]]
            entry["carrier_ref"] = carrier["artifact_type_ref"]
            entry["lifecycle_state"] = "candidate-materialized"
            entry["path"] = carrier["descriptor_path"]
            entry["lifecycle_evidence_path"] = "authority/artifact-types/candidates/0010-step5-postimage-registry/registry.json"
            entry["note"] = "Step 5 candidate carrier materialized; admission remains absent."
    result["counts"] = {
        "admitted-current": sum(row["lifecycle_state"] == "admitted-current" for row in result["entries"]),
        "candidate-materialized": sum(row["lifecycle_state"] == "candidate-materialized" for row in result["entries"]),
        "declared_endpoint_pairs": source["counts"]["declared_endpoint_pairs"],
        "named_endpoint_kinds": len(result["entries"]),
        "referenced-no-canonical-carrier": sum(row["lifecycle_state"] == "referenced-no-canonical-carrier" for row in result["entries"]),
        "wildcard_tokens": source["counts"]["wildcard_tokens"],
    }
    result["claim_ceiling"] = "This postimage proves candidate carrier material exists for all 50 named endpoint kinds. It does not admit the 37 candidate carriers, admit Relation Kinds or Typed Relations, validate real relation instances, or activate a consumer or runtime."
    return result


def write_projection(registry: dict, endpoint_inventory: dict) -> None:
    lines = ["<!-- GENERATED FILE: canonical data is registry.json and endpoint-inventory.json. -->", "", "# Step 5 complete materialized postimage", "", f"- Registry: `{registry['registry_id']}`", f"- Descriptors: `{registry['inventory']['descriptor_count']}`", f"- Admitted contracts preserved: `{registry['inventory']['admitted_contract_count']}`", f"- Candidate descriptors: `{registry['inventory']['state_counts']['candidate-unadmitted']}`", f"- Relation endpoint kinds with carriers: `{endpoint_inventory['counts']['named_endpoint_kinds']}`", f"- Missing endpoint carriers: `{endpoint_inventory['counts']['referenced-no-canonical-carrier']}`", f"- Authority effect: `{registry['authority_effect']}`", "", "## Step 5 additions", "", "- 5 existing unadmitted candidates repaired", "- 9 immutable successors materialized", "- 22 new endpoint carrier identities materialized", "- Relation Kind and Typed Relation hardened to complete v2 carriers before admission", "", "## Realistic integrated example", "", "`implementation:registry-validator` may be the source of `relation.realizes` targeting `product-capability:effective-state-resolution`. The Implementation carrier, Product Capability carrier, Relation Kind contract, Typed Relation instance, and Capability Realization Binding remain separate artifacts and lifecycle states.", "", "## Claim ceiling", "", registry["claim_ceiling"]]
    (ROOT / "REGISTRY.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    candidate = load(CANDIDATE)
    registry, additions = build_registry(candidate)
    endpoint_inventory = build_endpoint_inventory(candidate, additions)
    dump(ROOT / "registry.json", registry)
    dump(ROOT / "endpoint-inventory.json", endpoint_inventory)
    write_projection(registry, endpoint_inventory)


if __name__ == "__main__": main()
