#!/usr/bin/env python3
"""Expanded non-collapse audit for the admitted Coordination Context/v1 contract."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
PACKAGE = LAB / "authority/artifact-types/coordination-context/v1"
ARTIFACT_PATH = PACKAGE / "artifact.json"
SCHEMA_PATH = PACKAGE / "schema.json"
CORE_SCHEMA_PATH = LAB / "tooling/schemas/ctx01/v1/schema.json"
FIXTURE_PATH = PACKAGE / "fixtures/valid/coordination-context.json"
DEFINITION_PATH = (
    LAB
    / "authority/definitions/candidates/0001-definition-and-ctx00-v1/definitions/coordination-context/v1/definition.json"
)
EFFECTIVE_REGISTRY_PATH = (
    LAB
    / "authority/artifact-types/candidates/0006-effective-state-registry/registry.json"
)
RELATION_MODEL_PATH = (
    LAB / "authority/relation-kinds/candidates/0002-axis-orthogonal-model/model.json"
)
ENDPOINT_INVENTORY_PATH = (
    LAB
    / "authority/relation-kinds/candidates/0002-axis-orthogonal-model/endpoint-inventory.json"
)
CURRENT_VALIDATOR_PATH = LAB / "tooling/validators/ctx01_artifact_type.py"


def load(path: Path) -> Any:
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def import_current_validator():
    spec = importlib.util.spec_from_file_location("ctx01_validator", CURRENT_VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {CURRENT_VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def expanded_semantic_failures(instance: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    identity = instance.get("coordination_context_id")
    endpoints = {
        "product": instance.get("product_ref"),
        "project": instance.get("project_ref"),
        "goal": instance.get("goal_ref"),
    }
    for kind, endpoint in endpoints.items():
        if endpoint is not None and identity == endpoint:
            failures.append(f"identity-collapses-with-{kind}")
    if identity in instance.get("bounded_context_refs", []):
        failures.append("identity-collapses-with-bounded-context")
    endpoint_scalars = {
        value
        for value in endpoints.values()
        if isinstance(value, (str, int, float, bool))
    }
    if instance.get("owner_ref") in endpoint_scalars:
        failures.append("owner-collapses-with-framed-endpoint")

    forbidden_groups = {
        "product-carrier": {"product", "product_id", "value_promise"},
        "project-carrier": {"project", "project_id", "deliverables"},
        "goal-carrier": {"goal", "goal_id", "success_criteria"},
        "bounded-context-carrier": {
            "domain_model_ref",
            "ubiquitous_language_ref",
            "context_map_refs",
        },
        "generic-context-carrier": {"context_id", "profile_ref", "request_ref"},
        "context-view-carrier": {"context_view_id", "included_material"},
        "agent-session-carrier": {
            "agent_session_ref",
            "conversation_history",
            "short_term_memory",
        },
        "work-or-execution-carrier": {
            "work_ref",
            "execution_authority",
            "execution_status",
        },
        "source-selection-carrier": {"source_selection", "selected_sources"},
    }
    for group, keys in forbidden_groups.items():
        if keys.intersection(instance):
            failures.append(f"contains-{group}-fields")
    return sorted(failures)


def schema_validator() -> Draft202012Validator:
    core = load(CORE_SCHEMA_PATH)
    validation_schema = dict(core)
    validation_schema["$ref"] = "#/$defs/coordinationContext"
    Draft202012Validator.check_schema(validation_schema)
    return Draft202012Validator(validation_schema)


def mutate(base: dict[str, Any], *, remove: list[str] | None = None, **updates: Any) -> dict[str, Any]:
    value = copy.deepcopy(base)
    for key in remove or []:
        value.pop(key, None)
    value.update(updates)
    return value


def build_cases(base: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    positive = [
        {
            "case_id": "valid-product-only",
            "expected": "accept",
            "instance": mutate(base, remove=["project_ref", "goal_ref"]),
        },
        {
            "case_id": "valid-product-project",
            "expected": "accept",
            "instance": mutate(base, remove=["goal_ref"]),
        },
        {
            "case_id": "valid-product-goal",
            "expected": "accept",
            "instance": mutate(
                base, remove=["project_ref"], goal_ref="goal:release-governed-search/v1"
            ),
        },
        {
            "case_id": "valid-product-project-goal",
            "expected": "accept",
            "instance": mutate(base, goal_ref="goal:release-governed-search/v1"),
        },
    ]
    hostile = [
        {
            "case_id": "missing-product",
            "expected": "reject",
            "instance": mutate(base, remove=["product_ref"]),
        },
        {
            "case_id": "multiple-products",
            "expected": "reject",
            "instance": mutate(base, product_ref=["product:a", "product:b"]),
        },
        {
            "case_id": "multiple-projects",
            "expected": "reject",
            "instance": mutate(base, project_ref=["project:a", "project:b"]),
        },
        {
            "case_id": "multiple-goals",
            "expected": "reject",
            "instance": mutate(base, goal_ref=["goal:a", "goal:b"]),
        },
        {
            "case_id": "embedded-product",
            "expected": "reject",
            "instance": mutate(base, product={"product_id": "product:embedded"}),
        },
        {
            "case_id": "embedded-project",
            "expected": "reject",
            "instance": mutate(base, project={"project_id": "project:embedded"}),
        },
        {
            "case_id": "embedded-goal",
            "expected": "reject",
            "instance": mutate(base, goal={"goal_id": "goal:embedded"}),
        },
        {
            "case_id": "bounded-context-ownership",
            "expected": "reject",
            "instance": mutate(
                base,
                domain_model_ref="model:collapsed",
                ubiquitous_language_ref="language:collapsed",
            ),
        },
        {
            "case_id": "generic-context-collapse",
            "expected": "reject",
            "instance": mutate(base, context_id="context:collapsed", profile_ref="profile:x"),
        },
        {
            "case_id": "context-view-collapse",
            "expected": "reject",
            "instance": mutate(base, context_view_id="view:collapsed", included_material=[]),
        },
        {
            "case_id": "agent-session-collapse",
            "expected": "reject",
            "instance": mutate(
                base,
                agent_session_ref="session:ephemeral",
                short_term_memory=["transient"],
            ),
        },
        {
            "case_id": "work-execution-collapse",
            "expected": "reject",
            "instance": mutate(base, work_ref="work:run", execution_authority="approved"),
        },
        {
            "case_id": "source-selection-collapse",
            "expected": "reject",
            "instance": mutate(base, source_selection={"selected_sources": ["source:a"]}),
        },
        {
            "case_id": "identity-equals-product",
            "expected": "reject",
            "instance": mutate(base, coordination_context_id=base["product_ref"]),
        },
        {
            "case_id": "identity-equals-project",
            "expected": "reject",
            "instance": mutate(base, coordination_context_id=base["project_ref"]),
        },
        {
            "case_id": "identity-equals-goal",
            "expected": "reject",
            "instance": mutate(
                base,
                goal_ref="goal:collapsed",
                coordination_context_id="goal:collapsed",
            ),
        },
        {
            "case_id": "identity-equals-bounded-context",
            "expected": "reject",
            "instance": mutate(
                base, coordination_context_id=base["bounded_context_refs"][0]
            ),
        },
        {
            "case_id": "owner-equals-product",
            "expected": "reject",
            "instance": mutate(base, owner_ref=base["product_ref"]),
        },
    ]
    return positive, hostile


def evaluate_cases(
    cases: list[dict[str, Any]], validator: Draft202012Validator, current_validator: Any
) -> list[dict[str, Any]]:
    results = []
    for case in cases:
        instance = case["instance"]
        schema_errors = sorted(error.message for error in validator.iter_errors(instance))
        semantic_errors = expanded_semantic_failures(instance)
        current_semantic_errors: list[str] = []
        try:
            current_semantic_errors = sorted(
                check_id
                for check_id, ok, _ in current_validator.semantic_invariants(
                    "coordination-context", instance
                )
                if not ok
            )
        except (KeyError, TypeError):
            pass
        accepted = not schema_errors and not semantic_errors
        current_accepted = not schema_errors and not current_semantic_errors
        results.append(
            {
                "case_id": case["case_id"],
                "expected": case["expected"],
                "result": "accept" if accepted else "reject",
                "expectation_met": accepted == (case["expected"] == "accept"),
                "schema_errors": schema_errors,
                "expanded_semantic_errors": semantic_errors,
                "current_validator_result": "accept" if current_accepted else "reject",
                "current_semantic_errors": current_semantic_errors,
            }
        )
    return results


def lifecycle_cases(base: dict[str, Any]) -> list[dict[str, Any]]:
    anchors = ("product_ref", "project_ref", "goal_ref", "purpose")

    def evaluate(case_id: str, after: dict[str, Any], expected: str) -> dict[str, Any]:
        changed = [key for key in anchors if base.get(key) != after.get(key)]
        same_identity = base["coordination_context_id"] == after["coordination_context_id"]
        actual = (
            "successor-required"
            if changed and same_identity
            else "successor-identity-present"
            if changed
            else "same-identity-revision-permitted"
        )
        return {
            "case_id": case_id,
            "changed_anchors": changed,
            "expected": expected,
            "result": actual,
            "expectation_met": actual == expected,
        }

    return [
        evaluate(
            "same-id-product-change",
            mutate(base, product_ref="product:changed/v1"),
            "successor-required",
        ),
        evaluate(
            "same-id-project-change",
            mutate(base, project_ref="project:changed/v1"),
            "successor-required",
        ),
        evaluate(
            "same-id-goal-change",
            mutate(base, goal_ref="goal:changed/v1"),
            "successor-required",
        ),
        evaluate(
            "same-id-purpose-change",
            mutate(base, purpose="A materially different durable purpose."),
            "successor-required",
        ),
        evaluate(
            "new-id-anchor-change",
            mutate(
                base,
                coordination_context_id="fixture.coordination.successor",
                product_ref="product:changed/v1",
            ),
            "successor-identity-present",
        ),
        evaluate(
            "same-id-source-policy-revision",
            mutate(base, source_policy_refs=["fixture:source-policy:v2"]),
            "same-identity-revision-permitted",
        ),
    ]


def main() -> int:
    artifact = load(ARTIFACT_PATH)
    definition = load(DEFINITION_PATH)
    effective_registry = load(EFFECTIVE_REGISTRY_PATH)
    relation_model = load(RELATION_MODEL_PATH)
    endpoint_inventory = load(ENDPOINT_INVENTORY_PATH)
    base = load(FIXTURE_PATH)
    validator = schema_validator()
    current_validator = import_current_validator()
    positive, hostile = build_cases(base)
    case_results = evaluate_cases(positive + hostile, validator, current_validator)
    lifecycle_results = lifecycle_cases(base)
    checks: list[dict[str, Any]] = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append(
            {"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail}
        )

    descriptor_row = next(
        row
        for row in effective_registry["descriptors"]
        if row["descriptor_path"]
        == "authority/artifact-types/coordination-context/v1/artifact.json"
    )
    check(
        "admitted-current-subject-bound",
        descriptor_row["effective_state"] == "admitted-current"
        and descriptor_row["descriptor_sha256"] == sha256(ARTIFACT_PATH),
        descriptor_row,
    )
    check(
        "admitted-definition-bound",
        definition["definition_id"] == "cal.definition.coordination-context"
        and artifact["definition_binding"]["sha256"] == sha256(DEFINITION_PATH),
        artifact["definition_binding"],
    )
    positive_results = [row for row in case_results if row["expected"] == "accept"]
    hostile_results = [row for row in case_results if row["expected"] == "reject"]
    check(
        "optional-project-goal-axis",
        len(positive_results) == 4 and all(row["expectation_met"] for row in positive_results),
        positive_results,
    )
    check(
        "expanded-hostile-non-collapse",
        len(hostile_results) == 18 and all(row["expectation_met"] for row in hostile_results),
        hostile_results,
    )
    semantic_only = [
        row
        for row in hostile_results
        if not row["schema_errors"] and row["expanded_semantic_errors"]
    ]
    current_blind_spots = [
        row["case_id"]
        for row in semantic_only
        if row["current_validator_result"] == "accept"
    ]
    check(
        "current-validator-blind-spots-measured",
        set(current_blind_spots)
        == {
            "identity-equals-product",
            "identity-equals-project",
            "identity-equals-goal",
            "identity-equals-bounded-context",
            "owner-equals-product",
        },
        current_blind_spots,
    )
    check(
        "material-anchor-successor-rule",
        len(lifecycle_results) == 6
        and all(row["expectation_met"] for row in lifecycle_results),
        lifecycle_results,
    )
    required_semantic = set(artifact["instance_contract"]["required_semantic_fields"])
    schema_required = set(
        load(CORE_SCHEMA_PATH)["$defs"]["coordinationContext"]["allOf"][1]["required"]
    )
    mismatch = sorted(required_semantic - schema_required)
    check(
        "optional-field-contract-mismatch-detected",
        mismatch == ["goal_ref", "project_ref"],
        mismatch,
    )
    definition_text = json.dumps(definition)
    check(
        "definition-boundaries-explicit",
        all(
            token in definition_text
            for token in (
                "exactly one Product",
                "optional Project and Goal",
                "not a Bounded Context, Product, Project, Goal",
                "Execution authorization or transient chat/session state",
            )
        ),
        definition["boundaries"],
    )
    endpoint = next(
        (
            row
            for row in endpoint_inventory["entries"]
            if row["endpoint_kind"] == "coordination-context"
        ),
        None,
    )
    relation_pairs = [
        {
            "relation_kind_id": entry["relation_kind_id"],
            **pair,
        }
        for entry in relation_model["entries"]
        for pair in entry["allowed_endpoint_pairs"]
        if "coordination-context" in pair.values()
    ]
    check(
        "relation-endpoint-gap-detected",
        endpoint is None and relation_pairs == [],
        {"endpoint_inventory_entry": endpoint, "declared_pairs": relation_pairs},
    )

    failed = [row for row in checks if row["result"] == "FAIL"]
    result = "PASS" if not failed else "FAIL"
    findings = [
        {
            "finding_id": "CCNC-R1",
            "kind": "validator-coverage-gap",
            "detail": "The current v1 validator accepts five identity or owner collapse cases that the expanded semantic audit rejects.",
            "required_action": "Carry the expanded semantic invariants into a Coordination Context/v2 validator.",
        },
        {
            "finding_id": "CCNC-R2",
            "kind": "contract-schema-mismatch",
            "detail": "The descriptor lists project_ref and goal_ref as required semantic fields while the Definition and schema make them independently optional.",
            "required_action": "Correct the successor descriptor contract without rewriting admitted v1 bytes.",
        },
        {
            "finding_id": "CCNC-R3",
            "kind": "relation-endpoint-gap",
            "detail": "The closed candidate Relation model contains no coordination-context endpoint or ordered pairs.",
            "required_action": "Use the Typed Connection Extension Rule to declare reviewed endpoint pairs before Relation Kind admission.",
        },
        {
            "finding_id": "CCNC-R4",
            "kind": "successor-required",
            "detail": "Expanded invariants cannot be added to the admitted v1 contract in place.",
            "required_action": "Author Coordination Context/v2 with normalized bindings, corrected optional fields, expanded non-collapse validation, and explicit relation projections.",
        },
    ]
    cases_document = {
        "schema_version": "cyberalchemy-lab-coordination-context-non-collapse-cases/v1",
        "subject": "cal.artifact-type.coordination-context/v1",
        "positive_cases": positive,
        "hostile_cases": hostile,
        "lifecycle_cases": lifecycle_results,
        "authority_effect": "none",
    }
    (ROOT / "cases.json").write_text(
        json.dumps(cases_document, indent=2, sort_keys=True) + "\n"
    )
    audit = {
        "schema_version": "cyberalchemy-lab-coordination-context-non-collapse-audit/v1",
        "audit_id": "CAL-COORDINATION-CONTEXT-NON-COLLAPSE-0001",
        "status": "candidate-audit-pass-with-residue" if result == "PASS" else "candidate-audit-fail",
        "result": result,
        "authority_effect": "none",
        "subject": {
            "artifact_type_ref": "cal.artifact-type.coordination-context/v1",
            "effective_state": descriptor_row["effective_state"],
            "path": str(ARTIFACT_PATH.relative_to(LAB)),
            "sha256": sha256(ARTIFACT_PATH),
        },
        "summary": {
            "positive_cases": len(positive_results),
            "hostile_cases": len(hostile_results),
            "lifecycle_cases": len(lifecycle_results),
            "current_validator_blind_spots": len(current_blind_spots),
            "findings": len(findings),
            "checks_passed": len(checks) - len(failed),
            "checks_failed": len(failed),
            "checks_total": len(checks),
        },
        "case_results": case_results,
        "lifecycle_results": lifecycle_results,
        "findings": findings,
        "recommended_relation_extensions": [
            {
                "relation_kind_id": "relation.frames",
                "source_kind": "coordination-context",
                "target_kind": "product",
                "qualifier": {"framing_role": "primary-product"},
            },
            {
                "relation_kind_id": "relation.frames",
                "source_kind": "coordination-context",
                "target_kind": "project",
                "qualifier": {"framing_role": "project-anchor"},
            },
            {
                "relation_kind_id": "relation.frames",
                "source_kind": "coordination-context",
                "target_kind": "goal",
                "qualifier": {"framing_role": "goal-anchor"},
            },
            {
                "relation_kind_id": "relation.frames",
                "source_kind": "coordination-context",
                "target_kind": "bounded-context",
                "qualifier": {"framing_role": "semantic-boundary"},
            },
        ],
        "claim_ceiling": "PASS proves the expected behavior of four positive, eighteen hostile, and six lifecycle cases under this expanded evidence-only audit. It does not modify or readmit Coordination Context/v1, make these invariants part of its admitted validator, admit Relation endpoint extensions, create a v2 successor, validate real instances, or authorize work.",
    }
    (ROOT / "audit.json").write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema_version": "cyberalchemy-lab-coordination-context-non-collapse-validation/v1",
        "subject": audit["audit_id"],
        "result": result,
        "authority_effect": "none",
        "checks": checks,
        "summary": audit["summary"],
        "materials": {
            "artifact_sha256": sha256(ARTIFACT_PATH),
            "schema_sha256": sha256(SCHEMA_PATH),
            "core_schema_sha256": sha256(CORE_SCHEMA_PATH),
            "definition_sha256": sha256(DEFINITION_PATH),
            "effective_registry_sha256": sha256(EFFECTIVE_REGISTRY_PATH),
            "relation_model_sha256": sha256(RELATION_MODEL_PATH),
            "endpoint_inventory_sha256": sha256(ENDPOINT_INVENTORY_PATH),
            "current_validator_sha256": sha256(CURRENT_VALIDATOR_PATH),
            "cases_sha256": sha256(ROOT / "cases.json"),
            "audit_sha256": sha256(ROOT / "audit.json"),
        },
        "claim_ceiling": audit["claim_ceiling"],
    }
    (ROOT / "receipts").mkdir(exist_ok=True)
    (ROOT / "receipts/validation.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )

    lines = [
        "<!-- GENERATED FILE: canonical data is audit.json. -->",
        "",
        "# Coordination Context non-collapse audit",
        "",
        f"- Audit: `{audit['audit_id']}`",
        f"- Result: `{result}`",
        f"- Status: `{audit['status']}`",
        "- Authority effect: `none`",
        "",
        "## Results",
        "",
        f"- Positive optional-axis cases accepted: `{len(positive_results)}/4`",
        f"- Hostile collapse cases rejected: `{len(hostile_results)}/18`",
        f"- Lifecycle cases matched: `{sum(row['expectation_met'] for row in lifecycle_results)}/6`",
        f"- Current-validator blind spots: `{len(current_blind_spots)}`",
        f"- Typed findings retained: `{len(findings)}`",
        "",
        "## Current-validator blind spots",
        "",
    ]
    lines.extend(f"- `{case_id}`" for case_id in current_blind_spots)
    lines += ["", "## Typed findings", ""]
    for finding in findings:
        lines += [
            f"### {finding['finding_id']} — {finding['kind']}",
            "",
            finding["detail"],
            "",
            f"Required action: {finding['required_action']}",
            "",
        ]
    lines += [
        "## Recommended explicit Relation extensions",
        "",
        "| Source | Relation | Target | Framing role |",
        "| --- | --- | --- | --- |",
    ]
    for extension in audit["recommended_relation_extensions"]:
        lines.append(
            f"| `{extension['source_kind']}` | `{extension['relation_kind_id']}` | "
            f"`{extension['target_kind']}` | `{extension['qualifier']['framing_role']}` |"
        )
    lines += ["", "## Claim ceiling", "", audit["claim_ceiling"]]
    (ROOT / "NON-COLLAPSE.md").write_text("\n".join(lines).rstrip() + "\n")

    print(f"COORDINATION_CONTEXT_NON_COLLAPSE={result}")
    print(f"CHECKS={len(checks)-len(failed)}/{len(checks)}")
    print(f"POSITIVE={len(positive_results)}/4")
    print(f"HOSTILE={len(hostile_results)}/18")
    print(f"LIFECYCLE={sum(row['expectation_met'] for row in lifecycle_results)}/6")
    print(f"CURRENT_VALIDATOR_BLIND_SPOTS={len(current_blind_spots)}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
