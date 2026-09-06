#!/usr/bin/env python3
"""Validate W3 authored DomainSpec and event-contract source closure."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
PRODUCT = ROOT / "product-capability.json"
W2 = ROOT / "conformance" / "w2-model-validation.json"
BINDINGS = ROOT / "domainspec" / "w2-behavior-bindings.json"
FEATURE = ROOT / "domainspec" / "specs" / "ontology-lifecycle" / "feature.json"
EVENT_SOURCE = ROOT / "domainspec" / "event-sourcing" / "source.json"
PROFILE_SOURCE = ROOT / "domainspec" / "development-profile-source.json"
PROFILE = ROOT / "domainspec" / "development-profile.json"
PROJECT = ROOT / "domainspec" / "project.json"
REGISTRY = ROOT / "domainspec" / "relationship-registry.json"
RECEIPT = ROOT / "conformance" / "w3-source-validation.json"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    product, w2, bindings, feature, event_source, profile_source, profile, project, registry = map(
        load, [PRODUCT, W2, BINDINGS, FEATURE, EVENT_SOURCE, PROFILE_SOURCE, PROFILE, PROJECT, REGISTRY]
    )
    findings: list[dict[str, str]] = []
    behavior_ids = {item["behavior_id"] for item in product["promised_behaviors"]}
    binding_ids = [item["behavior_id"] for item in bindings["bindings"]]
    if set(binding_ids) != behavior_ids or len(binding_ids) != len(set(binding_ids)):
        findings.append({"code":"behavior-binding-closure","path":"domainspec/w2-behavior-bindings.json/bindings"})

    node_files = [ROOT / "domainspec" / "specs" / "ontology-lifecycle" / item for item in feature["node_sources"]]
    nodes = [load(path) for path in node_files]
    node_ids = {node["node_id"] for node in nodes}
    event_symbols = {item["streamId"] for item in event_source["streams"]} | {item["eventType"] for item in event_source["events"]} | {item["projectionId"] for item in event_source["projections"]} | {item["joinId"] for item in event_source["joins"]}
    for index, binding in enumerate(bindings["bindings"]):
        for node_id in binding["domainspec_nodes"]:
            if node_id not in node_ids:
                findings.append({"code":"unresolved-domainspec-node", "path":f"bindings/{index}/domainspec_nodes", "detail":node_id})
        for symbol in binding["event_contract_symbols"]:
            if symbol not in event_symbols:
                findings.append({"code":"unresolved-event-contract-symbol", "path":f"bindings/{index}/event_contract_symbols", "detail":symbol})

    schema_dir = EVENT_SOURCE.parent / "schemas"
    for index, event in enumerate(event_source["events"]):
        if not (EVENT_SOURCE.parent / event["payloadSchemaRef"]).is_file():
            findings.append({"code":"missing-payload-schema", "path":f"event-sourcing/source.json/events/{index}/payloadSchemaRef"})
    identities = [item["id"] for item in registry["signatures"]]
    if registry["signature_count"] != len(registry["signatures"]):
        findings.append({"code":"registry-count-mismatch", "path":"domainspec/relationship-registry.json/signature_count"})
    supported = {(item["id"], item["source_kind"], item["target_kind"]) for item in profile["profiles"][0]["relationships"]}
    registered = {(item["id"], item["source_type"], item["target_type"]) for item in registry["signatures"]}
    if not supported <= registered:
        findings.append({"code":"profile-registry-signature-mismatch", "path":"domainspec/development-profile.json/profiles/0/relationships"})
    if digest(PROFILE_SOURCE) != profile["profile_binding"]["sha256"]:
        findings.append({"code":"profile-source-digest-mismatch", "path":"domainspec/development-profile.json/profile_binding/sha256"})
    if digest(REGISTRY) != profile["registry_bindings"]["relationships"]["sha256"]:
        findings.append({"code":"relationship-registry-digest-mismatch", "path":"domainspec/development-profile.json/registry_bindings/relationships/sha256"})
    if digest(PROFILE) != project["language"]["profile"]["digest"]:
        findings.append({"code":"project-profile-digest-mismatch", "path":"domainspec/project.json/language/profile/digest"})
    if profile_source.get("release_admission") != "not-granted" or profile.get("release_admission") != "not-granted":
        findings.append({"code":"profile-claim-ceiling-violation", "path":"release_admission"})
    if w2.get("result") != "PASS":
        findings.append({"code":"w2-predecessor-not-pass", "path":"conformance/w2-model-validation.json/result"})

    inputs = [Path(__file__).resolve(), PRODUCT, W2, BINDINGS, FEATURE, EVENT_SOURCE, PROFILE_SOURCE, PROFILE, PROJECT, REGISTRY, *node_files, *sorted(schema_dir.glob("*.schema.json"))]
    receipt = {
        "schema_version":"cal.w3-source-validation/v1", "receipt_id":"CAL-GON-W3-SOURCE-VALIDATION-001",
        "result":"PASS" if not findings else "FAIL", "findings":findings,
        "checks":{
            "w2_predecessor":"PASS" if w2.get("result") == "PASS" else "FAIL",
            "behavior_binding_closure":"PASS" if not any(f["code"].startswith("behavior-") or f["code"].startswith("unresolved-") for f in findings) else "FAIL",
            "payload_schema_resolution":"PASS" if not any(f["code"] == "missing-payload-schema" for f in findings) else "FAIL",
            "profile_registry_currentness":"PASS" if not any("digest-mismatch" in f["code"] or f["code"] in {"registry-count-mismatch","profile-registry-signature-mismatch"} for f in findings) else "FAIL",
            "development_claim_ceiling":"PASS" if not any(f["code"] == "profile-claim-ceiling-violation" for f in findings) else "FAIL"
        },
        "source_topology":{"domainspec_node_count":len(node_ids),"relationship_signature_count":len(identities),"event_stream_count":len(event_source["streams"]),"event_type_count":len(event_source["events"]),"projection_count":len(event_source["projections"]),"exact_join_count":len(event_source["joins"])},
        "external_validation_obligation":"Run DomainSpec typecheck and complete backend tests in the ABI-compatible installed Node runtime; this structural receipt does not manufacture that result.",
        "authority_effect":"none", "claim_ceiling":"Authored W3 source candidate validation only; no profile or ontology admission and no implementation conformance.",
        "inputs":[{"path":str(path.relative_to(REPO)),"sha256":digest(path)} for path in inputs]
    }
    RECEIPT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"result":receipt["result"],"checks":receipt["checks"],"topology":receipt["source_topology"],"findings":findings},indent=2))
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
