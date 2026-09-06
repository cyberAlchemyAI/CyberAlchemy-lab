#!/usr/bin/env python3
"""Evaluate the W4 deterministic compile and exact profile-admission gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
PROFILE_SOURCE = ROOT / "domainspec" / "development-profile-source.json"
PROFILE = ROOT / "domainspec" / "development-profile.json"
PROJECT = ROOT / "domainspec" / "project.json"
RELATIONSHIPS = ROOT / "domainspec" / "relationship-registry.json"
BUILD = ROOT / "domainspec" / ".domainspec" / "generated" / "build-receipt.json"
GRAPH = ROOT / "domainspec" / ".domainspec" / "generated" / "graph.json"
EVENT_RECEIPT = ROOT / "domainspec" / "event-sourcing" / "generated" / "compile-receipt.json"
EVENT_CONTRACT = ROOT / "domainspec" / "event-sourcing" / "generated" / "contract.json"
SYSTEM_PROFILE = ROOT / "system-ontology" / "PROFILE.json"
W3 = ROOT / "conformance" / "w3-source-validation.json"
W2 = ROOT / "conformance" / "w2-model-validation.json"
BACKEND = ROOT / "conformance" / "domainspec-backend-validation.json"
RECEIPT = ROOT / "conformance" / "w4-gate.json"
DECISION_DIR = REPO / "docs" / "decisions" / "0008-domainspec-development-profile-admission"
ADMISSION_REQUEST = DECISION_DIR / "admissibility-request.json"
ADMISSION_RECEIPT = DECISION_DIR / "admissibility-receipt.json"
ADMISSION_DECISION = DECISION_DIR / "decision.json"
PRE_ADMISSION_GATE = DECISION_DIR / "pre-admission-w4-gate.json"
W2_DECISION_DIR = REPO / "docs" / "decisions" / "0009-w2-product-business-admission"
W2_ADMISSION_REQUEST = W2_DECISION_DIR / "admissibility-request.json"
W2_ADMISSION_RECEIPT = W2_DECISION_DIR / "admissibility-receipt.json"
W2_ADMISSION_DECISION = W2_DECISION_DIR / "decision.json"
PRE_W2_ADMISSION_GATE = W2_DECISION_DIR / "pre-admission-w4-gate.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_admission(profile_source: dict, profile: dict) -> tuple[bool, list[str]]:
    """Validate the bounded owner decision without mutating release status."""
    failures: list[str] = []
    try:
        decision = load(ADMISSION_DECISION)
        request = load(ADMISSION_REQUEST)
        admissibility = load(ADMISSION_RECEIPT)
        pre_gate = load(PRE_ADMISSION_GATE)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        return False, [f"admission evidence unavailable: {exc}"]

    expected_scalars = {
        "decision_id": "CAL-DPADM-0008",
        "question_id": "G-W4-PROFILE-ADMISSION",
        "status": "selected",
        "admission_status": "admitted",
        "authority_effect": "admit-exact-lab-development-profile-for-g-w4-only",
    }
    for field, expected in expected_scalars.items():
        if decision.get(field) != expected:
            failures.append(f"decision.{field} must equal {expected!r}")
    if decision.get("decision_source", {}).get("selection_token") != "DPADM-1":
        failures.append("decision source must bind exact user selection DPADM-1")
    if decision.get("selection", {}).get("option_id") != "DPADM-1":
        failures.append("selected option must be DPADM-1")

    admitted = decision.get("admitted_profile_epoch", {})
    if admitted.get("scope_id") != "cal.ontology-lifecycle.business-domain.v2-candidate":
        failures.append("admitted scope is not the bounded Lab ontology-lifecycle candidate")
    if admitted.get("profile_id") != profile_source.get("profile_id") or admitted.get("profile_version") != profile_source.get("profile_version"):
        failures.append("admitted profile identity does not match current profile source")

    exact_refs = {
        "profile_source_ref": PROFILE_SOURCE,
        "profile_registry_ref": PROFILE,
        "project_ref": PROJECT,
        "relationship_registry_ref": RELATIONSHIPS,
        "compiled_graph_ref": GRAPH,
        "event_contract_ref": EVENT_CONTRACT,
        "w3_receipt_ref": W3,
        "pre_admission_w4_gate_ref": PRE_ADMISSION_GATE,
    }
    for name, path in exact_refs.items():
        ref = admitted.get(name, {})
        if ref.get("sha256") != digest(path):
            failures.append(f"{name} digest does not match current exact bytes")

    decision_admissibility = decision.get("admissibility", {})
    if decision_admissibility.get("request_ref", {}).get("sha256") != digest(ADMISSION_REQUEST):
        failures.append("decision does not bind the current admissibility request bytes")
    if decision_admissibility.get("receipt_ref", {}).get("sha256") != digest(ADMISSION_RECEIPT):
        failures.append("decision does not bind the current admissibility receipt bytes")
    if decision_admissibility.get("request_digest") != admissibility.get("requestDigest"):
        failures.append("decision request digest does not match the prefilter receipt")
    if admissibility.get("routeOutcome") != "gate" or "DPADM-1" not in admissibility.get("admissibleOptionIds", []):
        failures.append("prefilter receipt does not admit DPADM-1 through a human gate")
    if request.get("decisionId") != "CAL-DPADM-0008":
        failures.append("admissibility request decision identity is wrong")

    if profile_source.get("release_admission") != "not-granted" or profile.get("release_admission") != "not-granted":
        failures.append("bounded Lab admission requires public release_admission fields to remain not-granted")
    if admitted.get("kinds_registry_binding") != profile.get("registry_bindings", {}).get("kinds"):
        failures.append("admitted kinds-registry binding does not match the profile registry")
    if admitted.get("source_set_sha256") != load(BUILD).get("source_set_digest"):
        failures.append("admitted source-set digest does not match the deterministic build receipt")
    if pre_gate.get("gate_id") != "G-W4" or pre_gate.get("result") != "not_evaluable":
        failures.append("pre-admission gate snapshot is not the blocked G-W4 candidate")
    if [item.get("code") for item in pre_gate.get("blockers", [])] != ["PROFILE_ADMISSION_NOT_GRANTED"]:
        failures.append("pre-admission gate did not have profile admission as its sole blocker")
    return not failures, failures


def validate_w2_admission() -> tuple[bool, list[str]]:
    """Validate the coupled Product Capability/business ontology owner decision."""
    if not W2_ADMISSION_DECISION.is_file():
        return False, ["exact W2 owner decision is absent"]
    failures: list[str] = []
    try:
        decision = load(W2_ADMISSION_DECISION)
        request = load(W2_ADMISSION_REQUEST)
        admissibility = load(W2_ADMISSION_RECEIPT)
        product = load(ROOT / "product-capability.json")
        ontology = load(ROOT / "business-ontology.json")
        pre_gate = load(PRE_W2_ADMISSION_GATE)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        return False, [f"W2 admission evidence unavailable: {exc}"]
    expected = {
        "decision_id": "CAL-W2ADM-0009",
        "question_id": "G-W2-PRODUCT-BUSINESS-ADMISSION",
        "status": "selected",
        "admission_status": "admitted",
        "authority_effect": "admit-exact-lab-w2-product-business-epoch-for-d65-only",
    }
    for field, value in expected.items():
        if decision.get(field) != value:
            failures.append(f"W2 decision.{field} must equal {value!r}")
    if decision.get("decision_source", {}).get("selection_token") != "W2ADM-1":
        failures.append("W2 decision must bind exact user selection W2ADM-1")
    if decision.get("selection", {}).get("option_id") != "W2ADM-1":
        failures.append("W2 selected option must be W2ADM-1")
    epoch = decision.get("admitted_w2_epoch", {})
    if epoch.get("scope_id") != "cal.ontology-lifecycle.business-domain.v2-candidate":
        failures.append("W2 admitted scope is not the bounded Lab ontology-lifecycle candidate")
    exact = {
        "product_capability_ref": ROOT / "product-capability.json",
        "business_ontology_ref": ROOT / "business-ontology.json",
        "w2_validation_ref": W2,
        "pre_admission_w4_gate_ref": PRE_W2_ADMISSION_GATE,
    }
    for name, path in exact.items():
        if epoch.get(name, {}).get("sha256") != digest(path):
            failures.append(f"{name} digest does not match current exact bytes")
    decision_admissibility = decision.get("admissibility", {})
    if decision_admissibility.get("request_ref", {}).get("sha256") != digest(W2_ADMISSION_REQUEST):
        failures.append("W2 decision does not bind current admissibility request")
    if decision_admissibility.get("receipt_ref", {}).get("sha256") != digest(W2_ADMISSION_RECEIPT):
        failures.append("W2 decision does not bind current admissibility receipt")
    if decision_admissibility.get("request_digest") != admissibility.get("requestDigest"):
        failures.append("W2 decision request digest does not match prefilter receipt")
    if admissibility.get("routeOutcome") != "gate" or "W2ADM-1" not in admissibility.get("admissibleOptionIds", []):
        failures.append("W2 prefilter does not admit W2ADM-1 through a human gate")
    if request.get("decisionId") != "CAL-W2ADM-0009":
        failures.append("W2 request decision identity is wrong")
    if product.get("status") != "candidate-unadmitted" or ontology.get("status") != "candidate-unadmitted":
        failures.append("bounded W2 admission requires candidate status fields to remain unchanged")
    if pre_gate.get("gate_id") != "G-W4" or pre_gate.get("result") != "not_evaluable":
        failures.append("pre-admission W4 snapshot is not the blocked G-W4 candidate")
    if [item.get("code") for item in pre_gate.get("blockers", [])] != ["W2_PREDECESSOR_ADMISSION_NOT_GRANTED"]:
        failures.append("pre-admission W4 snapshot did not have W2 admission as its sole blocker")
    return not failures, failures


def main() -> int:
    profile_source, profile, build, event, system, w3, backend = map(load, [PROFILE_SOURCE, PROFILE, BUILD, EVENT_RECEIPT, SYSTEM_PROFILE, W3, BACKEND])
    compiled_pass = all([
        w3.get("result") == "PASS", backend.get("result") == "PASS", build.get("status") == "pass",
        event.get("status") == "PASS", event.get("determinism", {}).get("repeated_run_byte_equality") is True,
        event.get("determinism", {}).get("permutation_byte_equality") is True,
        build.get("artifacts", {}).get("graph_digest") == digest(GRAPH),
        event.get("compiled_contract", {}).get("sha256") == digest(EVENT_CONTRACT),
        system.get("compiled_graph_digest") == digest(GRAPH),
    ])
    admission_granted, admission_failures = validate_admission(profile_source, profile)
    w2_admitted, w2_admission_failures = validate_w2_admission()
    result = "PASS" if compiled_pass and admission_granted and w2_admitted else "not_evaluable"
    blockers = []
    if not compiled_pass:
        blockers.append({"code":"COMPILE_EVIDENCE_INCOMPLETE","owner":"DomainSpec compiler owner"})
    if not admission_granted:
        blockers.append({
            "code":"PROFILE_ADMISSION_DECISION_INVALID",
            "owner":"DomainSpec profile admission owner",
            "observed":{"profile_source_release_admission":profile_source.get("release_admission"),"profile_registry_release_admission":profile.get("release_admission")},
            "failures": admission_failures,
            "resolution":"Repair or reselect the exact bounded admission evidence; do not change release status fields or refresh digests to simulate admission."
        })
    if not w2_admitted:
        blockers.append({
            "code":"W2_PREDECESSOR_ADMISSION_NOT_GRANTED",
            "owner":"Product Capability and business ontology owners",
            "failures":w2_admission_failures,
            "resolution":"Select one exact coupled W2 epoch through G-W2; do not edit candidate status fields or infer admission from structural validation."
        })
    inputs = [Path(__file__).resolve(), PROFILE_SOURCE, PROFILE, PROJECT, RELATIONSHIPS, BUILD, GRAPH, EVENT_RECEIPT, EVENT_CONTRACT, SYSTEM_PROFILE, W2, W3, BACKEND, ADMISSION_REQUEST, ADMISSION_RECEIPT, ADMISSION_DECISION, PRE_ADMISSION_GATE, W2_ADMISSION_REQUEST, W2_ADMISSION_RECEIPT]
    if W2_ADMISSION_DECISION.is_file():
        inputs.extend([W2_ADMISSION_DECISION, PRE_W2_ADMISSION_GATE])
    receipt = {
        "schema_version":"cal.w4-gate/v1", "gate_id":"G-W4", "result":result,
        "checks":{
            "w3_source":"PASS" if w3.get("result") == "PASS" else "FAIL",
            "domainspec_backend":"PASS" if backend.get("result") == "PASS" else "FAIL",
            "graph_compile_twice":"PASS" if compiled_pass else "FAIL",
            "event_contract_twice":"PASS" if compiled_pass else "FAIL",
            "profile_admission":"PASS" if admission_granted else "not_evaluable"
            ,"product_business_admission":"PASS" if w2_admitted else "not_evaluable"
        },
        "candidate_outputs":{"graph_sha256":digest(GRAPH),"event_contract_sha256":digest(EVENT_CONTRACT),"system_profile_sha256":digest(SYSTEM_PROFILE)},
        "blockers":blockers,
        "downstream":{"W5":"ready" if result == "PASS" else "not_evaluable","W6":"not_evaluable","W7":"not_evaluable","W8":"not_evaluable"},
        "authority_effect":"none",
        "claim_ceiling":"G-W4 PASS establishes the exact admitted W2 and DomainSpec predecessors for Lab-local W5 construction only. It does not release DomainSpec, accept or prove runtime conformance, or authorize publication, deployment, migration, cutover, or external effects." if result == "PASS" else "Deterministic W4 candidate outputs exist, but G-W4 cannot pass and no runtime implementation may claim CAV2-D65 succession until both the exact W2 product/business epoch and profile/source epoch admission evidence are valid.",
        "inputs":[{"path":str(path.relative_to(REPO)),"sha256":digest(path)} for path in inputs]
    }
    RECEIPT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"gate_id":"G-W4","result":result,"checks":receipt["checks"],"blockers":blockers},indent=2))
    return 0 if result == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
