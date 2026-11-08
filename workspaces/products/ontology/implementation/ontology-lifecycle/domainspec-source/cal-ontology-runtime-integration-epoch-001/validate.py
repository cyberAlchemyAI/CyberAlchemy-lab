#!/usr/bin/env python3
"""Fail-closed D65-S4 candidate validator; it never grants admission."""

from __future__ import annotations

import glob
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


PACKAGE_ROOT = Path(__file__).resolve().parent
DOMAINSPEC_ROOT = Path("/home/vrondelli/projects/domainspec-core")
LAB_ROOT = Path("/home/vrondelli/projects/CyberAlchemy-lab")


def load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, code: str, detail: str, failures: list[dict[str, str]]) -> None:
    if not condition:
        failures.append({"code": code, "detail": detail})


def node_binary() -> str | None:
    candidates = sorted(
        glob.glob("/home/vrondelli/.nvm/versions/node/*/bin/node"),
        key=lambda item: [int(part) for part in Path(item).parts[-3].lstrip("v").split(".")],
    )
    return candidates[-1] if candidates else None


def main() -> int:
    failures: list[dict[str, str]] = []
    checks: list[dict[str, object]] = []

    profile = load(PACKAGE_ROOT / "profile.json")
    require(profile.get("schema_version") == "cal-d65-domainspec-source-package/v1", "PROFILE_SCHEMA", "profile schema_version differs", failures)
    require(profile.get("status") == "candidate-not-admitted", "CLAIM_CEILING", "source must remain candidate-not-admitted", failures)
    for field in ("generated_graph_present", "system_ontology_present", "implementation_binding_present"):
        require(profile.get(field) is False, "SUCCESSOR_ARTIFACT_FORBIDDEN", f"{field} must be false", failures)

    generated = PACKAGE_ROOT / "domainspec/generated"
    require(not generated.exists(), "GENERATED_OUTPUT_PRESENT", str(generated), failures)

    sources = load(PACKAGE_ROOT / "sources.json")
    for record in sources.get("records", []):
        path = Path(record["path"])
        require(path.is_file(), "SELECTED_SOURCE_MISSING", str(path), failures)
        if path.is_file():
            require(digest(path) == record["sha256"], "SELECTED_SOURCE_DIGEST_DRIFT", record["source_id"], failures)
    checks.append({"check": "selected-source-currentness", "records": len(sources.get("records", [])), "result": "PASS" if not failures else "FAIL"})

    decision = load(LAB_ROOT / "docs/decisions/0018-d65-business-ontology-admission/decision.json")
    require(decision.get("decision_id") == "CAL-D65BIZ-0018", "PREDECESSOR_DECISION", "business admission decision identity differs", failures)
    require(decision.get("status") == "selected", "PREDECESSOR_NOT_SELECTED", "business admission decision is not selected", failures)
    require(decision.get("selection", {}).get("option_id") == "D65BIZ-1", "PREDECESSOR_NOT_ADMITTED", "business predecessor is not admitted by D65BIZ-1", failures)
    require(decision.get("authority_effect") == "admit-exact-d65-s3-business-ontology-only", "PREDECESSOR_AUTHORITY", "business admission authority effect differs", failures)

    mapping = load(PACKAGE_ROOT / "mappings/business-to-domainspec.json")
    business_root = LAB_ROOT / "ontology-lifecycle/business-ontology/cal-ontology-runtime-integration-epoch-001"
    business_nodes = load(business_root / "nodes.json")["nodes"]
    business_relations = load(business_root / "relations.json")["relations"]
    business_contracts = load(business_root / "contracts.json")["contracts"]
    business_failures = load(business_root / "failures.json")["failures"]

    require(len(mapping.get("node_mappings", [])) == 26, "NODE_MAPPING_COUNT", "expected 26 admitted business-node mappings", failures)
    require(len(mapping.get("relation_mappings", [])) == 35, "RELATION_MAPPING_COUNT", "expected 35 business-relation mappings", failures)
    require(len(mapping.get("contract_mappings", [])) == 8, "CONTRACT_MAPPING_COUNT", "expected 8 business-contract mappings", failures)
    require(len(mapping.get("failure_mappings", [])) == 13, "FAILURE_MAPPING_COUNT", "expected 13 business-failure mappings", failures)
    require({item["business_node_id"] for item in mapping["node_mappings"]} == {item["id"] for item in business_nodes}, "NODE_MAPPING_CLOSURE", "business node identities do not close exactly", failures)
    require({item["business_relation_id"] for item in mapping["relation_mappings"]} == {item["id"] for item in business_relations}, "RELATION_MAPPING_CLOSURE", "business relation identities do not close exactly", failures)
    require({item["business_contract_id"] for item in mapping["contract_mappings"]} == {item["contract_id"] for item in business_contracts}, "CONTRACT_MAPPING_CLOSURE", "business contract identities do not close exactly", failures)
    require({item["business_failure_id"] for item in mapping["failure_mappings"]} == {item["failure_id"] for item in business_failures}, "FAILURE_MAPPING_CLOSURE", "business failure identities do not close exactly", failures)

    feature = load(PACKAGE_ROOT / "domainspec/feature.json")
    node_paths = sorted((PACKAGE_ROOT / "domainspec/nodes").glob("*.json"))
    listed_paths = sorted(PACKAGE_ROOT / "domainspec" / item for item in feature.get("node_sources", []))
    require(node_paths == listed_paths, "NODE_SOURCE_ENUMERATION", "feature node_sources must exactly enumerate node files", failures)
    node_docs = [load(path) for path in node_paths]
    node_ids = {item["node_id"] for item in node_docs}
    require(len(node_docs) == 41 and len(node_ids) == 41, "DOMAINSPEC_NODE_COUNT", "expected 41 unique authored nodes", failures)
    require({item["domainspec_node_id"] for item in mapping["node_mappings"]}.issubset(node_ids), "MAPPED_NODE_MISSING", "one or more mapped DomainSpec nodes are absent", failures)
    mechanics = {
        "ontology-runtime-integration.CalculateLatestNodeSnapshot",
        "ontology-runtime-integration.CalculateLatestRelationSnapshot",
        "ontology-runtime-integration.CalculateEventProjection",
        "ontology-runtime-integration.EntitySemanticStateWasRecorded",
        "ontology-runtime-integration.RelationSemanticStateWasRecorded",
        "ontology-runtime-integration.EntityGovernanceStateWasRecorded",
        "ontology-runtime-integration.RelationGovernanceStateWasRecorded",
        "ontology-runtime-integration.IntegrationEpochWasRecorded",
    }
    require(mechanics.issubset(node_ids), "EVENT_CALCULATION_MECHANICS", "required snapshot/event mechanics are missing", failures)

    development_profile = load(PACKAGE_ROOT / "domainspec/development-profile.json")
    for binding in development_profile.get("formation_schema_bindings", {}).values():
        path = DOMAINSPEC_ROOT / "projects/domainspec-v2" / binding["path"]
        require(path.is_file() and digest(path) == binding["sha256"], "FORMATION_SCHEMA_DRIFT", binding["path"], failures)

    event_source = load(PACKAGE_ROOT / "contracts/event-sourcing-source.json")
    require(event_source.get("schemaVersion") == "domainspec.event-sourcing-source/v1", "EVENT_SOURCE_SCHEMA", "event source schema differs", failures)
    require(len(event_source.get("streams", [])) == 5, "EVENT_STREAM_COUNT", "expected five semantic/governance/process streams", failures)
    require(len(event_source.get("events", [])) == 5, "EVENT_DEFINITION_COUNT", "expected five complete-resulting-state event definitions", failures)
    require(len(event_source.get("projections", [])) == 3, "PROJECTION_COUNT", "expected node, relation, and governed ontology projections", failures)
    require(len(event_source.get("joins", [])) == 2, "JOIN_COUNT", "expected entity and relation governance joins", failures)
    require(all(join.get("failClosed") is True for join in event_source.get("joins", [])), "JOIN_NOT_FAIL_CLOSED", "all governance joins must fail closed", failures)

    compile_result: dict[str, object] | None = None
    node = node_binary()
    require(node is not None, "NODE_RUNTIME_MISSING", "no WSL-native NVM Node runtime found", failures)
    if node is not None and not failures:
        tsx = DOMAINSPEC_ROOT / "implementation/domainspec/backend/node_modules/tsx/dist/cli.mjs"
        command = [node, str(tsx), str(PACKAGE_ROOT / "compile-check.ts")]
        completed = subprocess.run(command, cwd=DOMAINSPEC_ROOT, text=True, capture_output=True, env={**os.environ, "TMPDIR": "/tmp"})
        if completed.returncode != 0:
            failures.append({"code": "DETERMINISTIC_COMPILE_FAILED", "detail": completed.stderr.strip() or completed.stdout.strip()})
        else:
            compile_result = json.loads(completed.stdout)
            require(compile_result.get("result") == "PASS", "COMPILE_RECEIPT", "compile-check did not report PASS", failures)

    checks.append({"check": "business-mapping-closure", "nodes": 26, "relations": 35, "contracts": 8, "failures": 13, "result": "PASS" if not failures else "FAIL"})
    checks.append({"check": "successor-artifact-absence", "generated_graph": False, "system_ontology": False, "implementation_binding": False, "result": "PASS" if not failures else "FAIL"})
    checks.append({"check": "deterministic-double-compile", "result": "PASS" if compile_result and not failures else "FAIL"})

    receipt = {
        "schema_version": "cal-d65-s4-validation-receipt/v1",
        "package_id": profile.get("package_id"),
        "stage": "D65-S4",
        "result": "PASS" if not failures else "FAIL",
        "checks": checks,
        "compile_result": compile_result,
        "failures": failures,
        "owner_gate": "G-D65-DOMAINSPEC-SOURCE",
        "admission_granted": False,
        "successor_execution_authorized": False,
        "claim_ceiling": "PASS means the authored D65-S4 candidate is internally valid and deterministic. It does not admit source or authorize D65-S5.",
    }
    print(json.dumps(receipt, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
