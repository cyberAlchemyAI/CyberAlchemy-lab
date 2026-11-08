#!/usr/bin/env python3
"""Validate the isolated ORODI Alert Profile candidate Definition Pack."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PACK_PATH = HERE / "ORODI-ALERT-PROFILE-DEFINITION-PACK.v1-candidate.json"

EXPECTED_CONCEPTS = {
    "orodi-alert-profile.alert-profile",
    "orodi-alert-profile.source-contract",
    "orodi-alert-profile.metric-projection-specification",
    "orodi-alert-profile.rule-specification",
    "orodi-alert-profile.evidence-state-model",
    "orodi-alert-profile.failure-meaning-separation",
    "orodi-alert-profile.label-contract",
    "orodi-alert-profile.rule-set",
    "orodi-alert-profile.platform-renderer",
    "orodi-alert-profile.rendered-artifact",
    "orodi-alert-profile.commissioning-evidence",
    "orodi-alert-profile.notification-delivery-binding",
}

EXPECTED_PROFILE_FIELDS = [
    "profile_id",
    "profile_version",
    "bounded_context",
    "source_contracts",
    "rule_set",
    "state_model",
    "label_contract",
    "renderer_contract",
    "commissioning_contract",
    "authority_effect",
]

EXPECTED_SOURCE_CONTRACT_FIELDS = [
    "source_id",
    "source_kind",
    "query_language",
    "availability_projection",
    "allowed_dimensions",
    "conservation_obligations",
]

EXPECTED_RULE_FIELDS = [
    "rule_id",
    "title",
    "projection",
    "predicate",
    "evaluation_interval",
    "persistence_duration",
    "no_data_policy",
    "error_policy",
    "fixed_labels",
    "annotations",
    "severity",
    "authority_effect",
]

EXPECTED_STATES = ["normal", "pending", "firing", "no_data", "error"]


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    errors: list[str] = []
    pack = json.loads(PACK_PATH.read_text(encoding="utf-8"))

    if pack.get("pack_id") != "DEFINE-PACK-ORODI-ALERT-PROFILE-001":
        errors.append("pack-id")
    if pack.get("status") != "candidate":
        errors.append("status")
    for field in ("authority_effect", "implementation_effect", "promotion_effect"):
        if pack.get(field) != "none":
            errors.append(f"effect:{field}")

    required = pack.get("required_concept_ids", [])
    concepts = pack.get("concepts", [])
    concept_ids = [item.get("concept_id") for item in concepts]
    if set(required) != EXPECTED_CONCEPTS or len(required) != len(EXPECTED_CONCEPTS):
        errors.append("required-concept-set")
    if set(concept_ids) != EXPECTED_CONCEPTS or len(concept_ids) != len(EXPECTED_CONCEPTS):
        errors.append("concept-coverage-or-duplicate")

    voices = {
        "normative_voice",
        "formal_voice",
        "plain_language_voice",
        "domain_context_voice",
        "boundary",
    }
    allowed_dispositions = {"propose", "specialize"}
    for concept in concepts:
        concept_id = concept.get("concept_id", "unknown")
        if concept.get("current_disposition") not in allowed_dispositions:
            errors.append(f"disposition:{concept_id}")
        definition = concept.get("definition", {})
        if set(definition) != voices or any(not isinstance(definition.get(v), str) or not definition[v].strip() for v in voices):
            errors.append(f"definition-voices:{concept_id}")
        if concept.get("current_disposition") == "specialize" and not concept.get("parent_definition_ref"):
            errors.append(f"specialization-parent:{concept_id}")

    relationships = pack.get("relationships", [])
    relation_ids = [item.get("relation_id") for item in relationships]
    if len(relation_ids) != len(set(relation_ids)):
        errors.append("relationship-id-duplicate")
    for relation in relationships:
        relation_id = relation.get("relation_id", "unknown")
        if relation.get("source_concept_id") not in EXPECTED_CONCEPTS:
            errors.append(f"relationship-source:{relation_id}")
        if relation.get("target_concept_id") not in EXPECTED_CONCEPTS:
            errors.append(f"relationship-target:{relation_id}")
        if not isinstance(relation.get("relation"), str) or not relation["relation"].strip():
            errors.append(f"relationship-type:{relation_id}")

    contract = pack.get("profile_contract", {})
    if contract.get("artifact_id") != "ORODI-ALERT-PROFILE":
        errors.append("profile-artifact-id")
    if contract.get("schema_version") != "cav2.orodi.alert-profile/v1-candidate":
        errors.append("profile-schema-version")
    if contract.get("required_profile_fields") != EXPECTED_PROFILE_FIELDS:
        errors.append("required-profile-fields")
    if contract.get("required_source_contract_fields") != EXPECTED_SOURCE_CONTRACT_FIELDS:
        errors.append("required-source-contract-fields")
    if contract.get("required_rule_fields") != EXPECTED_RULE_FIELDS:
        errors.append("required-rule-fields")
    if contract.get("authority_effect") != "none":
        errors.append("profile-authority-effect")

    state_model = contract.get("evidence_state_model", {})
    if state_model.get("states") != EXPECTED_STATES:
        errors.append("evidence-state-model")
    meanings = state_model.get("terminal_meanings", {})
    if set(meanings) != {"normal", "firing", "no_data", "error"}:
        errors.append("terminal-meanings")
    attention = state_model.get("attention_policy", {})
    if attention.get("no_data") != "operator-attention-fail-closed":
        errors.append("no-data-attention")
    if attention.get("error") != "operator-attention-fail-closed":
        errors.append("error-attention")
    separation = set(state_model.get("separation_invariants", []))
    required_separation = {
        "no_data is not normal",
        "error is not normal",
        "no_data is not error",
        "firing is not proof of causation",
        "shared attention policy does not collapse evidence meaning",
    }
    if separation != required_separation:
        errors.append("failure-meaning-separation")

    telemetry = contract.get("telemetry_policy", {})
    if telemetry.get("missing_data") != "preserve-as-no_data":
        errors.append("missing-data-preservation")
    if telemetry.get("evaluation_error") != "preserve-as-error":
        errors.append("evaluation-error-preservation")
    if telemetry.get("query_side_health_synthesis") != "forbidden":
        errors.append("query-side-health-synthesis")

    label_policy = contract.get("label_policy", {})
    if label_policy.get("cardinality") != "finite-declared-only":
        errors.append("label-cardinality")
    required_forbidden_categories = {
        "credentials",
        "secrets",
        "request-identifiers",
        "timestamps",
        "arbitrary-user-values",
        "request-bodies",
        "authorization-headers",
    }
    if set(label_policy.get("forbidden_categories", [])) != required_forbidden_categories:
        errors.append("label-forbidden-categories")

    renderer = contract.get("renderer_contract", {})
    if renderer.get("deterministic") is not True:
        errors.append("renderer-determinism")
    required_preservations = {
        "rule identity",
        "predicate meaning",
        "evidence states",
        "failure meaning separation",
        "non-actuation",
        "notification separation",
    }
    if not required_preservations.issubset(set(renderer.get("must_preserve", []))):
        errors.append("renderer-preservation")
    required_non_additions = {
        "healthy samples",
        "control endpoints",
        "operational actions",
        "notification destinations",
        "credentials",
        "authority",
    }
    if not required_non_additions.issubset(set(renderer.get("must_not_add", []))):
        errors.append("renderer-non-addition")

    commissioning = contract.get("commissioning_contract", {})
    scenarios = set(commissioning.get("required_scenarios", []))
    required_scenarios = {
        "observed predicate breach reaches firing",
        "observed recovery returns the rule from firing",
        "missing telemetry is preserved as no_data and requests attention",
        "evaluation failure is preserved as error and requests attention",
        "notification delivery attempts remain zero when no separate binding exists",
        "no control-plane action is reachable from evaluation or rendered artifacts",
    }
    if not required_scenarios.issubset(scenarios):
        errors.append("commissioning-scenarios")

    delivery = contract.get("notification_delivery", {})
    expected_delivery = {
        "included": False,
        "default_state": "absent",
        "separate_binding_required": True,
        "separate_human_authorization_required": True,
    }
    if delivery != expected_delivery:
        errors.append("notification-delivery-separation")

    contract_text = json.dumps(contract, sort_keys=True).lower()
    for forbidden in ("grafana", "pagerduty", "slack", "smtp", "webhook", "https://", "control/action"):
        if forbidden in contract_text:
            errors.append(f"platform-or-effect-token:{forbidden}")

    source_refs = pack.get("source_refs", [])
    if len(source_refs) != 12:
        errors.append("source-count")
    source_ids = [item.get("source_id") for item in source_refs]
    if len(source_ids) != len(set(source_ids)) or any(not item for item in source_ids):
        errors.append("source-id-duplicate-or-empty")
    seen_paths: set[str] = set()
    for source in source_refs:
        relative = source.get("path")
        expected = source.get("sha256")
        if not isinstance(relative, str) or relative in seen_paths:
            errors.append(f"source-path:{relative}")
            continue
        seen_paths.add(relative)
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"source-missing:{relative}")
        elif file_digest(path) != expected:
            errors.append(f"source-digest:{relative}")

    known_source_ids = set(source_ids)
    for evidence in pack.get("evidence", []):
        evidence_id = evidence.get("evidence_id", "unknown")
        source_id = evidence.get("source_ref", {}).get("source_id")
        if source_id not in known_source_ids:
            errors.append(f"evidence-source:{evidence_id}")

    requirement_value = {
        "goal": pack.get("goal"),
        "original_intent": pack.get("original_intent"),
        "context": pack.get("context", {}).get("statement"),
        "goal_limits": pack.get("goal_limits"),
    }
    requirement_digest = canonical_digest(requirement_value)
    profile_digest = canonical_digest(contract)
    sufficiency = pack.get("context_sufficiency", {})
    if sufficiency.get("requirement_digest") != requirement_digest:
        errors.append("requirement-digest")
    if sufficiency.get("candidate_digest") != profile_digest:
        errors.append("candidate-digest")

    check_outcomes = {item.get("check_id"): item.get("outcome") for item in pack.get("checks", [])}
    expected_checks = {
        "required-concept-coverage",
        "selected-source-currency",
        "platform-separation",
        "failure-meaning-separation",
        "notification-authority-separation",
        "authority-ceiling",
    }
    if set(check_outcomes) != expected_checks or set(check_outcomes.values()) != {"PASS"}:
        errors.append("declared-checks")

    result = {
        "validator": "ORODI-ALERT-PROFILE-CANDIDATE-VALIDATOR",
        "outcome": "PASS" if not errors else "FAIL",
        "pack_id": pack.get("pack_id"),
        "required_concepts": len(EXPECTED_CONCEPTS),
        "source_count": len(source_refs),
        "requirement_digest": requirement_digest,
        "profile_contract_digest": profile_digest,
        "errors": sorted(set(errors)),
        "claim_ceiling": "Candidate definition-pack structure and selected-source currency only; no adoption, admission, implementation, conformance, notification, publication, release, or deployment authority.",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
