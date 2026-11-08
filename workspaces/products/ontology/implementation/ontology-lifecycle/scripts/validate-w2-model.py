#!/usr/bin/env python3
"""Validate W2 Product Capability and capability-local business ontology candidates."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
PRODUCT = ROOT / "product-capability.json"
ONTOLOGY = ROOT / "business-ontology.json"
DEFINITIONS = REPO / "docs" / "definition-packs" / "0002-governed-ontology-node-model" / "handled-definitions.json"
DEFINITION_DECISION = REPO / "docs" / "decisions" / "0006-governed-node-definition-selection" / "decision.json"
LIFECYCLE_DECISION = REPO / "docs" / "decisions" / "0007-ontology-lifecycle-state-vocabulary" / "decision.json"
W1_RECEIPT = ROOT / "conformance" / "w1-schema-validation.json"
RECEIPT = ROOT / "conformance" / "w2-model-validation.json"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    product, ontology, definitions, w1 = map(load, [PRODUCT, ONTOLOGY, DEFINITIONS, W1_RECEIPT])
    findings: list[dict[str, str]] = []
    definition_ids = {record["concept_id"] for record in definitions["records"]}
    behavior_ids = [item["behavior_id"] for item in product.get("promised_behaviors", [])]
    if len(behavior_ids) != len(set(behavior_ids)):
        findings.append({"code": "duplicate-behavior-id", "path": "product-capability.json/promised_behaviors"})
    for index, behavior in enumerate(product.get("promised_behaviors", [])):
        if not behavior.get("definition_refs"):
            findings.append({"code": "unmapped-behavior", "path": f"product-capability.json/promised_behaviors/{index}"})
        for ref in behavior.get("definition_refs", []):
            if ref not in definition_ids:
                findings.append({"code": "unknown-definition-ref", "path": f"product-capability.json/promised_behaviors/{index}/definition_refs", "detail": ref})

    concepts = ontology.get("concepts", [])
    concept_ids = [item["id"] for item in concepts]
    relation_ids = [item["id"] for item in ontology.get("relationships", [])]
    if len(concept_ids) != len(set(concept_ids)):
        findings.append({"code": "duplicate-concept-id", "path": "business-ontology.json/concepts"})
    if len(relation_ids) != len(set(relation_ids)):
        findings.append({"code": "duplicate-relation-id", "path": "business-ontology.json/relationships"})
    known = set(concept_ids)
    for index, relation in enumerate(ontology.get("relationships", [])):
        for endpoint in ("from", "to"):
            if relation.get(endpoint) not in known:
                findings.append({"code": "unresolved-relation-endpoint", "path": f"business-ontology.json/relationships/{index}/{endpoint}", "detail": str(relation.get(endpoint))})

    required_explicit_concepts = {
        "ontology-lifecycle.ontology-node", "ontology-lifecycle.ontology-relation", "ontology-lifecycle.challenge-contract",
        "ontology-lifecycle.typed-residue", "ontology-lifecycle.context-selector", "ontology-lifecycle.context-projection",
        "ontology-lifecycle.exact-semantic-event-reference", "ontology-lifecycle.ontology-governance-state",
    }
    for missing in sorted(required_explicit_concepts - known):
        findings.append({"code": "missing-governed-concept", "path": "business-ontology.json/concepts", "detail": missing})
    relation_types = {relation["type"] for relation in ontology.get("relationships", [])}
    for needed in {"joins-through", "keeps-separate", "routes", "produces", "derives-from"} - relation_types:
        findings.append({"code": "missing-explicit-relationship", "path": "business-ontology.json/relationships", "detail": needed})

    if product.get("capability_id") != ontology.get("product_capability_ref"):
        findings.append({"code": "capability-binding-mismatch", "path": "business-ontology.json/product_capability_ref"})
    for key in ("definition_pack_ref", "definition_selection_ref", "lifecycle_selection_ref"):
        if product.get(key) != ontology.get(key):
            findings.append({"code": "selected-source-binding-mismatch", "path": key})
    if w1.get("result") != "PASS":
        findings.append({"code": "w1-predecessor-not-pass", "path": "conformance/w1-schema-validation.json/result"})
    if product.get("status") != "candidate-unadmitted" or ontology.get("status") != "candidate-unadmitted":
        findings.append({"code": "claim-ceiling-violation", "path": "status"})
    if product.get("authority_effect") != "none" or ontology.get("authority_effect") != "none":
        findings.append({"code": "authority-effect-violation", "path": "authority_effect"})

    inputs = [Path(__file__).resolve(), PRODUCT, ONTOLOGY, DEFINITIONS, DEFINITION_DECISION, LIFECYCLE_DECISION, W1_RECEIPT]
    receipt = {
        "schema_version": "cal.w2-model-validation/v1",
        "receipt_id": "CAL-GON-W2-MODEL-VALIDATION-001",
        "result": "PASS" if not findings else "FAIL",
        "checks": {
            "w1_predecessor": "PASS" if w1.get("result") == "PASS" else "FAIL",
            "behavior_definition_mapping": "PASS" if not any(f["code"] in {"unmapped-behavior", "unknown-definition-ref", "duplicate-behavior-id"} for f in findings) else "FAIL",
            "concept_and_relation_identity": "PASS" if not any(f["code"].startswith("duplicate-") for f in findings) else "FAIL",
            "relationship_endpoint_closure": "PASS" if not any(f["code"] == "unresolved-relation-endpoint" for f in findings) else "FAIL",
            "explicit_challenge_context_residue_relations": "PASS" if not any(f["code"] in {"missing-governed-concept", "missing-explicit-relationship"} for f in findings) else "FAIL",
            "cross_artifact_binding": "PASS" if not any(f["code"] in {"capability-binding-mismatch", "selected-source-binding-mismatch"} for f in findings) else "FAIL",
            "claim_ceiling": "PASS" if not any(f["code"] in {"claim-ceiling-violation", "authority-effect-violation"} for f in findings) else "FAIL"
        },
        "findings": findings,
        "acceptance_state": "pending-owner-decision",
        "authority_effect": "none",
        "claim_ceiling": "Validated W2 candidate alignment only; no Product Capability or business ontology admission or acceptance.",
        "inputs": [{"path": str(path.relative_to(REPO)), "sha256": digest(path)} for path in inputs]
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"result": receipt["result"], "checks": receipt["checks"], "findings": findings}, indent=2))
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
