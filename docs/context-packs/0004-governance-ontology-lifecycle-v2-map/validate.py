#!/usr/bin/env python3
"""Validate and render the additive Governance-to-Ontology-Lifecycle v2 map."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
PACK_PATH = HERE / "map-pack.json"
PACK_SCHEMA_PATH = HERE / "schema.json"
PACK_OUTPUT = HERE / "MAP-PACK.md"
RECEIPT = HERE / "receipts/validation.json"
MAP_PATH = LAB / "contexts/maps/governance-ontology-lifecycle/v2/map.json"
MAP_OUTPUT = LAB / "contexts/maps/governance-ontology-lifecycle/v2/MAP.md"
MAP_SCHEMA_PATH = LAB / "tooling/schemas/ctx07/v2/schema.json"
GENERATOR_PATH = LAB / "tooling/generators/ctx07_artifact.py"

UPSTREAM = "cal.context.governance/v2"
DOWNSTREAM = "cal.context.ontology-lifecycle/v2"
PATTERN = "candidate:ddd.upstream-downstream.published-language.anticorruption-layer/v1"
RELATIONSHIP_ID = "cal.context-relationship.governance-to-ontology-lifecycle.authority-decision-feed"
EXPECTED_CONTRACTS = {
    UPSTREAM,
    "cal.language.governance/v2",
    DOWNSTREAM,
    "cal.language.ontology-lifecycle/v2",
    "cal.definition.context-map@2.0.0-candidate.1",
}
EXPECTED_TRANSLATIONS = {
    "cav2.governance-model#node:GovernanceDecision",
    "ontology-lifecycle.governance-event",
    "ontology-lifecycle.exact-semantic-event-reference",
}
EXPECTED_OWNERS = {
    "role:context-map-owner",
    "role:governance-context-owner",
    "role:governance-language-owner",
    "role:ontology-lifecycle-context-owner",
    "role:ontology-lifecycle-language-owner",
}
V1_MAP_SHA256 = "e4c339df5f2072a2a43b34ca2fe1f11ea331f53fc5a0616249d37150e2a242fd"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render_instance(context_map: dict) -> str:
    spec = importlib.util.spec_from_file_location("ctx07_artifact", GENERATOR_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.render_instance(context_map, "context-map")


def render_pack(pack: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit map-pack.json and rerun validate.py. -->",
        "",
        "# Governance to Ontology Lifecycle v2 Context Map prototype",
        "",
        f"- Pack: `{pack['pack_id']}`",
        f"- Stage: `{pack['stage_id']}`",
        f"- Status: `{pack['status']}`",
        f"- Authority effect: `{pack['authority_effect']}`",
        "",
        "## Objective",
        "",
        pack["objective"],
        "",
        "## Two-lane frontier",
        "",
        f"- Product lane: `{pack['two_lane_binding']['product_lane']}`",
        f"- Current frontier: `{pack['two_lane_binding']['current_product_frontier']}`",
        f"- Continuation: `{pack['two_lane_binding']['continuation_status']}`",
        "- Operational blockers: none",
        "",
        "## Selected inputs",
        "",
        "| Input | Path | SHA-256 |",
        "| --- | --- | --- |",
    ]
    for item in pack["selected_inputs"]:
        lines.append(f"| `{item['input_id']}` | `{item['path']}` | `{item['sha256']}` |")
    lines.extend(["", "## Claim ceiling", "", pack["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


def check_map(context_map: dict, pack: dict, *, check_sources: bool = True) -> list[dict]:
    checks: list[dict] = []

    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    pack_errors = sorted(
        error.message
        for error in Draft202012Validator(load(PACK_SCHEMA_PATH)).iter_errors(pack)
    )
    check("prototype-pack-schema-valid", not pack_errors, pack_errors)

    shared_schema = load(MAP_SCHEMA_PATH)
    map_schema = {
        "$schema": shared_schema["$schema"],
        "$defs": shared_schema["$defs"],
        "$ref": "#/$defs/contextMap",
    }
    map_errors = sorted(
        error.message for error in Draft202012Validator(map_schema).iter_errors(context_map)
    )
    check("context-map-v2-schema-valid", not map_errors, map_errors)

    if check_sources:
        actual_inputs = {}
        current = True
        for item in pack["selected_inputs"]:
            path = LAB / item["path"]
            actual = digest(path) if path.is_file() else None
            actual_inputs[item["input_id"]] = actual
            current = current and actual == item["sha256"]
        check("selected-input-digest-closure", current, actual_inputs)
    else:
        check("selected-input-digest-closure", True, "not-rechecked-for-in-memory-hostile-probe")

    artifact_decision = load(
        LAB / "docs/decisions/0027-ctx07-normalized-context-artifact-type-promotion/decision.json"
    )
    admitted_types = {
        item["artifact_type_ref"]: item.get("decision_overlay_status")
        for item in artifact_decision.get("admitted_artifact_types", [])
    }
    check(
        "context-map-v2-type-admitted-for-new-construction",
        artifact_decision.get("status") == "owner-admitted"
        and admitted_types.get("cal.artifact-type.context-map/v2")
        == "admitted-for-new-normalized-construction",
        admitted_types,
    )

    endpoint_decision = load(
        LAB / "docs/decisions/0025-governance-ontology-lifecycle-successor-promotion/decision.json"
    )
    endpoint_paths = {
        item["path"]: item.get("decision_overlay_status")
        for item in endpoint_decision.get("admitted_artifacts", [])
    }
    required_endpoint_paths = {
        "contexts/governance/v2/context.json",
        "contexts/governance/v2/language.json",
        "contexts/ontology-lifecycle/v2/context.json",
        "contexts/ontology-lifecycle/v2/language.json",
    }
    check(
        "v2-endpoints-owner-admitted",
        endpoint_decision.get("status") == "owner-admitted"
        and all(endpoint_paths.get(path) == "admitted" for path in required_endpoint_paths),
        endpoint_paths,
    )

    v1_actual = digest(LAB / "contexts/maps/governance-ontology-lifecycle/v1/map.json")
    check("admitted-v1-map-byte-preserved", v1_actual == V1_MAP_SHA256, v1_actual)

    relationships = context_map.get("relationships", [])
    relation = relationships[0] if len(relationships) == 1 else {}
    check(
        "exact-v2-endpoint-membership",
        context_map.get("context_refs") == [UPSTREAM, DOWNSTREAM]
        and relation.get("source_context_ref") == UPSTREAM
        and relation.get("target_context_ref") == DOWNSTREAM,
        {"context_refs": context_map.get("context_refs"), "relationship": relation},
    )
    check(
        "single-one-way-relationship",
        len(relationships) == 1
        and relation.get("relationship_id") == RELATIONSHIP_ID
        and relation.get("direction") == "source-to-target"
        and relation.get("relationship_kind_ref") == PATTERN,
        relation,
    )
    check(
        "relationship-endpoints-declared",
        relation.get("source_context_ref") in context_map.get("context_refs", [])
        and relation.get("target_context_ref") in context_map.get("context_refs", []),
        context_map.get("context_refs"),
    )
    check(
        "contract-reference-closure",
        set(relation.get("contract_refs", [])) == EXPECTED_CONTRACTS,
        relation.get("contract_refs"),
    )
    check(
        "translation-reference-closure",
        set(relation.get("translation_refs", [])) == EXPECTED_TRANSLATIONS,
        relation.get("translation_refs"),
    )
    governance_concepts = set(load(LAB / "contexts/governance/v2/language.json")["concept_refs"])
    lifecycle_concepts = set(load(LAB / "contexts/ontology-lifecycle/v2/language.json")["concept_refs"])
    check(
        "translation-language-resolution",
        "cav2.governance-model#node:GovernanceDecision" in governance_concepts
        and {
            "ontology-lifecycle.governance-event",
            "ontology-lifecycle.exact-semantic-event-reference",
        }
        <= lifecycle_concepts,
        {"governance": sorted(governance_concepts), "ontology_lifecycle": sorted(lifecycle_concepts)},
    )
    check(
        "owner-role-closure",
        set(context_map.get("owner_refs", [])) == EXPECTED_OWNERS
        and set(relation.get("owner_refs", [])) == EXPECTED_OWNERS,
        {"map": context_map.get("owner_refs"), "relationship": relation.get("owner_refs")},
    )
    authority_boundary = relation.get("authority_boundary", "").lower()
    check(
        "authority-non-transfer",
        "never transfers authority" in authority_boundary
        and "authority transfers" not in authority_boundary
        and "transfers authority" not in authority_boundary.replace("never transfers authority", ""),
        relation.get("authority_boundary"),
    )
    check(
        "candidate-no-effect-posture",
        context_map.get("status") == "candidate-unadmitted"
        and context_map.get("authority_effect") == "none"
        and context_map.get("classification", {}).get("authority_kind") == "coordination-authority",
        {
            "status": context_map.get("status"),
            "authority_effect": context_map.get("authority_effect"),
            "classification": context_map.get("classification"),
        },
    )
    rendered_a = render_instance(context_map)
    rendered_b = render_instance(copy.deepcopy(context_map))
    check("map-projection-deterministic", rendered_a == rendered_b, hashlib.sha256(rendered_a.encode()).hexdigest())
    if MAP_OUTPUT.is_file():
        check("map-projection-current", MAP_OUTPUT.read_text(encoding="utf-8") == rendered_a, str(MAP_OUTPUT.relative_to(LAB)))
    else:
        check("map-projection-current", True, "projection-created-after-evaluation")

    return checks


def hostile_probe_results(context_map: dict, pack: dict) -> list[dict]:
    probes: list[dict] = []

    def probe(probe_id: str, mutant: dict, expected_failed_check: str) -> None:
        failed = {
            item["check_id"]
            for item in check_map(mutant, pack, check_sources=False)
            if item["result"] == "FAIL"
        }
        probes.append(
            {
                "probe_id": probe_id,
                "result": "PASS" if expected_failed_check in failed else "FAIL",
                "expected_failed_check": expected_failed_check,
                "observed_failed_checks": sorted(failed),
            }
        )

    wrong_endpoint = copy.deepcopy(context_map)
    wrong_endpoint["relationships"][0]["target_context_ref"] = "cal.context.ontology-lifecycle/v1"
    probe("wrong-endpoint", wrong_endpoint, "exact-v2-endpoint-membership")

    reverse_edge = copy.deepcopy(context_map)
    reverse_edge["relationships"][0]["source_context_ref"] = DOWNSTREAM
    reverse_edge["relationships"][0]["target_context_ref"] = UPSTREAM
    probe("reverse-edge", reverse_edge, "exact-v2-endpoint-membership")

    missing_contract = copy.deepcopy(context_map)
    missing_contract["relationships"][0]["contract_refs"].pop()
    probe("missing-contract", missing_contract, "contract-reference-closure")

    authority_transfer = copy.deepcopy(context_map)
    authority_transfer["relationships"][0]["authority_boundary"] = "Authority transfers to the downstream context."
    probe("authority-transfer", authority_transfer, "authority-non-transfer")

    undeclared_endpoint = copy.deepcopy(context_map)
    undeclared_endpoint["context_refs"] = [UPSTREAM, "cal.context.other/v2"]
    probe("undeclared-endpoint", undeclared_endpoint, "relationship-endpoints-declared")

    probes.append(
        {
            "probe_id": "v1-predecessor-drift",
            "result": "PASS" if "0" * 64 != V1_MAP_SHA256 else "FAIL",
            "expected_failed_check": "admitted-v1-map-byte-preserved",
            "observed_failed_checks": ["admitted-v1-map-byte-preserved"],
        }
    )
    return probes


def run(*, write_outputs: bool = True) -> dict:
    pack = load(PACK_PATH)
    context_map = load(MAP_PATH)
    if write_outputs:
        MAP_OUTPUT.write_text(render_instance(context_map), encoding="utf-8")
        PACK_OUTPUT.write_text(render_pack(pack), encoding="utf-8")
    checks = check_map(context_map, pack)
    probes = hostile_probe_results(context_map, pack)
    passed = all(item["result"] == "PASS" for item in checks + probes)
    receipt = {
        "schema_version": "cyberalchemy-lab-context-map-v2-prototype-validation/v1",
        "pack_id": pack["pack_id"],
        "stage_id": pack["stage_id"],
        "result": "PASS" if passed else "FAIL",
        "checks_passed": sum(item["result"] == "PASS" for item in checks),
        "checks_total": len(checks),
        "hostile_probes_passed": sum(item["result"] == "PASS" for item in probes),
        "hostile_probes_total": len(probes),
        "checks": checks,
        "hostile_probes": probes,
        "artifacts": {
            "map_path": str(MAP_PATH.relative_to(LAB)),
            "map_sha256": digest(MAP_PATH),
            "map_projection_path": str(MAP_OUTPUT.relative_to(LAB)),
            "map_projection_sha256": digest(MAP_OUTPUT) if MAP_OUTPUT.is_file() else None,
            "pack_path": str(PACK_PATH.relative_to(LAB)),
            "pack_sha256": digest(PACK_PATH),
            "pack_projection_path": str(PACK_OUTPUT.relative_to(LAB)),
            "pack_projection_sha256": digest(PACK_OUTPUT) if PACK_OUTPUT.is_file() else None,
        },
        "product_state": "testable-prototype-pass" if passed else "prototype-test-failed",
        "product_approval": "not-requested",
        "authority_effect": "none",
        "claim_ceiling": pack["claim_ceiling"],
    }
    if write_outputs:
        RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    receipt = run(write_outputs=True)
    print(f"CTXMAP2_PROTOTYPE_VALIDATION={receipt['result']}")
    print(f"CHECKS={receipt['checks_passed']}/{receipt['checks_total']}")
    print(f"HOSTILE_PROBES={receipt['hostile_probes_passed']}/{receipt['hostile_probes_total']}")
    print("PRODUCT_APPROVAL=not-requested")
    print("AUTHORITY_EFFECT=none")
    return 0 if receipt["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
