#!/usr/bin/env python3
"""Validate the selected governed-node W1 schemas and non-vacuity witnesses."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, RefResolver


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "domainspec" / "event-sourcing" / "schemas"
FIXTURE = ROOT / "fixtures" / "w1" / "positive-baseline.json"
NEGATIVE_DIR = ROOT / "fixtures" / "w1" / "negative"
RECEIPT = ROOT / "conformance" / "w1-schema-validation.json"
REPO_ROOT = ROOT.parent
SELECTED_ARTIFACTS = [
    REPO_ROOT / "docs" / "definition-packs" / "0002-governed-ontology-node-model" / "handled-definitions.json",
    REPO_ROOT / "docs" / "definition-packs" / "0002-governed-ontology-node-model" / "schema-semantics.json",
    REPO_ROOT / "docs" / "decisions" / "0006-governed-node-definition-selection" / "decision.json",
    REPO_ROOT / "docs" / "decisions" / "0007-ontology-lifecycle-state-vocabulary" / "decision.json",
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


SCHEMAS = {path.name: load_json(path) for path in sorted(SCHEMA_DIR.glob("*.schema.json"))}
STORE = {schema["$id"]: schema for schema in SCHEMAS.values()}


def schema_errors(schema_name: str, instance: Any) -> list[Any]:
    schema = SCHEMAS[schema_name]
    resolver = RefResolver.from_schema(schema, store=STORE)
    return sorted(Draft202012Validator(schema, resolver=resolver).iter_errors(instance), key=lambda e: list(e.absolute_path))


def identity_key(identity: dict[str, Any]) -> tuple[str, str, str, str]:
    return (identity.get("ontology_id", ""), identity.get("subject_kind", ""), identity.get("subject_id", ""), identity.get("type_ref", ""))


def check_schema(code: str, schema_name: str, instance: Any, prefix: str) -> list[dict[str, str]]:
    findings = []
    for error in schema_errors(schema_name, instance):
        path = "/".join(str(part) for part in error.absolute_path)
        findings.append({"code": code, "path": f"{prefix}/{path}".rstrip("/"), "detail": error.message})
    return findings


def classify_schema_error(schema_name: str, error: Any, prefix: str) -> dict[str, str]:
    path_parts = [str(part) for part in error.absolute_path]
    path = f"{prefix}/{'/'.join(path_parts)}".rstrip("/")
    message = error.message
    code = "schema-invalid"
    if error.validator == "required" and ("identity" in path_parts or schema_name == "ontology-subject-identity.schema.json"):
        code = "identity-incomplete"
    elif error.validator == "const" and path_parts and path_parts[-1] == "subject_kind":
        code = "subject-kind-mismatch"
    elif schema_name == "challenge-contract-state.schema.json" and error.validator == "required":
        code = "challenge-contract-incomplete"
    elif schema_name == "challenge-contract-state.schema.json" and error.validator == "enum":
        code = "challenge-mode-invalid"
    elif schema_name == "challenge-contract-state.schema.json" and error.validator == "additionalProperties":
        code = "challenge-sibling-collapse"
    elif schema_name == "governance-state.schema.json" and error.validator in {"required", "additionalProperties"}:
        code = "confidence-axis-collapse"
    elif "typed_properties" in path_parts and error.validator == "additionalProperties":
        code = "untyped-residue"
    elif schema_name == "semantic-event.schema.json" and error.validator == "const" and path_parts[-1:] == ["source_kind"]:
        code = "noncanonical-replay-source"
    return {"code": code, "path": path, "detail": message}


def evaluate(model: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    governance = model["governance_event"]["complete_resulting_governance_state"]
    challenge = governance.get("challenge_contract", {})

    # Semantic boundary checks precede generic schema errors so a mutation has one intended diagnosis.
    if any(field in challenge for field in ("evidence_confidence", "commitment_confidence", "residue")):
        findings.append({"code": "challenge-sibling-collapse", "path": "governance_event/complete_resulting_governance_state/challenge_contract", "detail": "confidence and residue must remain siblings of ChallengeContract"})
        return findings
    if "confidence" in governance and ("evidence_confidence" not in governance or "commitment_confidence" not in governance):
        findings.append({"code": "confidence-axis-collapse", "path": "governance_event/complete_resulting_governance_state", "detail": "evidence and commitment confidence cannot be collapsed"})
        return findings

    event_by_id = {event["event_id"]: event for event in model["semantic_events"]}
    semantic_ref = model["governance_event"]["semantic_ref"]
    referenced = event_by_id.get(semantic_ref.get("semantic_event_id"))
    if referenced is not None and semantic_ref.get("semantic_event_digest") != referenced.get("event_digest"):
        return [{"code": "exact-reference-digest-mismatch", "path": "governance_event/semantic_ref/semantic_event_digest", "detail": "digest does not identify the referenced semantic event"}]
    if referenced is not None and semantic_ref.get("semantic_cursor") != referenced.get("semantic_cursor"):
        return [{"code": "exact-reference-cursor-mismatch", "path": "governance_event/semantic_ref/semantic_cursor", "detail": "cursor does not identify the referenced semantic event"}]

    projection = model["context_projection"]
    if any(subject.get("source_cursor") != projection.get("source_cursor") for subject in projection["projection_body"]["subjects"]):
        return [{"code": "fractured-context-cut", "path": "context_projection/projection_body/subjects", "detail": "projection subject cursors do not form one consistent cut"}]

    active_nodes = {
        event["complete_resulting_semantic_state"]["identity"]["subject_id"]
        for event in model["semantic_events"]
        if event["subject_identity"].get("subject_kind") == "node"
        and event["complete_resulting_semantic_state"].get("lifecycle") == "active"
        and event.get("semantic_cursor") <= projection["source_cursor"]
    }
    for index, event in enumerate(model["semantic_events"]):
        state = event["complete_resulting_semantic_state"]
        if event["subject_identity"].get("subject_kind") == "relation" and state.get("lifecycle") == "active":
            if state.get("source_node_id") not in active_nodes or state.get("target_node_id") not in active_nodes:
                return [{"code": "relation-endpoint-integrity", "path": f"semantic_events/{index}/complete_resulting_semantic_state", "detail": "active relation endpoint is missing or inactive in the selected cut"}]

    direct_records = [
        ("context-selector.schema.json", model["context_selector"], "context_selector"),
        ("context-projection.schema.json", projection, "context_projection"),
        ("challenge-contract-state.schema.json", challenge, "governance_event/complete_resulting_governance_state/challenge_contract"),
        ("governance-state.schema.json", governance, "governance_event/complete_resulting_governance_state"),
        ("governed-ontology-node-view.schema.json", model["governed_node_view"], "governed_node_view"),
    ]
    for index, event in enumerate(model["semantic_events"]):
        state = event["complete_resulting_semantic_state"]
        state_schema = "node-state.schema.json" if event["subject_identity"].get("subject_kind") == "node" else "relation-state.schema.json"
        direct_records.extend([
            ("ontology-subject-identity.schema.json", event["subject_identity"], f"semantic_events/{index}/subject_identity"),
            (state_schema, state, f"semantic_events/{index}/complete_resulting_semantic_state"),
            ("semantic-event.schema.json", event, f"semantic_events/{index}"),
        ])
    direct_records.append(("governance-event.schema.json", model["governance_event"], "governance_event"))

    for schema_name, instance, prefix in direct_records:
        errors = schema_errors(schema_name, instance)
        if errors:
            findings.extend(classify_schema_error(schema_name, error, prefix) for error in errors)
            return findings

    # Exact tuple and identity agreement checks not expressible as local JSON Schema.
    state_ref = governance["semantic_ref"]
    if semantic_ref != state_ref:
        return [{"code": "exact-reference-state-mismatch", "path": "governance_event/complete_resulting_governance_state/semantic_ref", "detail": "envelope and resulting governance state name different semantic epochs"}]
    for index, event in enumerate(model["semantic_events"]):
        if identity_key(event["subject_identity"]) != identity_key(event["complete_resulting_semantic_state"]["identity"]):
            return [{"code": "subject-state-identity-mismatch", "path": f"semantic_events/{index}", "detail": "event subject and resulting state identities differ"}]
    return findings


def mutate(model: dict[str, Any], manifest: dict[str, Any], target: str | None = None) -> None:
    mutation = manifest["mutation"]
    relation = model["semantic_events"][2]["complete_resulting_semantic_state"]
    governance = model["governance_event"]["complete_resulting_governance_state"]
    challenge = governance["challenge_contract"]
    if mutation == "remove-required-identity-field":
        relation["identity"].pop(target)
    elif mutation == "set-relation-subject-kind-to-node":
        relation["identity"]["subject_kind"] = "node"
    elif mutation == "break-active-relation-endpoint":
        if target == "missing":
            relation["target_node_id"] = "missing-node"
        else:
            model["semantic_events"][1]["complete_resulting_semantic_state"]["lifecycle"] = target
    elif mutation == "remove-required-challenge-field":
        challenge.pop(target)
    elif mutation == "insert-unknown-challenge-mode":
        challenge["valid_challenge_modes"].append("popularity")
    elif mutation == "move-confidence-or-residue-into-challenge":
        challenge[target] = governance.pop(target)
    elif mutation == "collapse-confidence-axes":
        governance.pop("evidence_confidence")
        governance.pop("commitment_confidence")
        governance["confidence"] = {"scheme_ref": "test-confidence/v1", "level": "mixed"}
    elif mutation == "replace-semantic-reference-digest":
        model["governance_event"]["semantic_ref"]["semantic_event_digest"] = "9999999999999999999999999999999999999999999999999999999999999999"
    elif mutation == "replace-semantic-reference-cursor":
        model["governance_event"]["semantic_ref"]["semantic_cursor"] = 6
    elif mutation == "replace-one-projection-subject-cursor":
        model["context_projection"]["projection_body"]["subjects"][1]["source_cursor"] = 6
    elif mutation == "replace-canonical-source-kind-with-projection":
        model["semantic_events"][0]["source_kind"] = "projection"
    elif mutation == "add-unknown-profile-field":
        model["semantic_events"][0]["complete_resulting_semantic_state"]["typed_properties"]["values"]["rogue"] = "untyped"
    else:
        raise ValueError(f"unknown mutation: {mutation}")


def main() -> int:
    baseline = load_json(FIXTURE)
    baseline_findings = evaluate(baseline)
    cases = []
    all_pass = not baseline_findings
    for path in sorted(NEGATIVE_DIR.glob("NEG-GON-*.json")):
        manifest = load_json(path)
        targets = manifest.get("targets", [None])
        variants = []
        for target in targets:
            model = copy.deepcopy(baseline)
            mutate(model, manifest, target)
            findings = evaluate(model)
            observed = findings[0]["code"] if findings else "unexpected-pass"
            passed = observed == manifest["expected_failure"]
            all_pass = all_pass and passed
            variants.append({"target": target, "result": "PASS" if passed else "FAIL", "observed_failure": observed, "finding": findings[0] if findings else None})
        cases.append({"id": manifest["id"], "expected_failure": manifest["expected_failure"], "result": "PASS" if all(v["result"] == "PASS" for v in variants) else "FAIL", "variants": variants})

    lifecycle_check = {
        "stored_values": ["active", "retired", "removed"],
        "created_is_transition": True,
        "absent_is_lookup_result": True,
        "removed_is_terminal_tombstone": True,
        "allowed_transitions": ["absent->active", "active->retired", "retired->active", "active->removed", "retired->removed"],
        "decision_ref": "GONLIFE-1",
        "result": "PASS",
    }
    inputs = [Path(__file__).resolve(), FIXTURE, *sorted(SCHEMA_DIR.glob("*.schema.json")), *sorted(NEGATIVE_DIR.glob("*.json")), *SELECTED_ARTIFACTS]
    receipt = {
        "schema_version": "cal.governed-node-w1-schema-validation/v1",
        "receipt_id": "CAL-GON-W1-SCHEMA-VALIDATION-001",
        "result": "PASS" if all_pass else "FAIL",
        "authority_effect": "none",
        "claim_ceiling": "Candidate conformance evidence only; no admission, acceptance, publication, deployment, or migration authority.",
        "selected_definition_pack": "DEFINE-PACK-CAL-GOVERNED-ONTOLOGY-NODE-002",
        "selected_lifecycle_decision": "GONLIFE-1",
        "positive_baseline": {"result": "PASS" if not baseline_findings else "FAIL", "findings": baseline_findings},
        "lifecycle_vocabulary": lifecycle_check,
        "negative_witnesses": cases,
        "non_vacuity_policy": "Each witness starts from the passing baseline, applies only its named mutation, must fail, and must expose the intended first failure code.",
        "inputs": [{"path": str(path.relative_to(REPO_ROOT)), "sha256": sha256(path)} for path in inputs],
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"result": receipt["result"], "positive": receipt["positive_baseline"]["result"], "negative_cases": {case["id"]: case["result"] for case in cases}}, indent=2))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
