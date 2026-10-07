#!/usr/bin/env python3
"""Coherent owner-review refinements for the remaining migration Artifact Types."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


def s() -> dict[str, Any]:
    return {"type": "string", "pattern": "\\S"}


def nullable_string() -> dict[str, Any]:
    return {"anyOf": [s(), {"type": "null"}]}


def strings(*, minimum: int = 0) -> dict[str, Any]:
    value: dict[str, Any] = {
        "type": "array",
        "items": s(),
        "maxItems": 100,
        "uniqueItems": True,
    }
    if minimum:
        value["minItems"] = minimum
    return value


def enum(*values: str) -> dict[str, Any]:
    return {"type": "string", "enum": list(values)}


def timestamp(*, nullable: bool = False) -> dict[str, Any]:
    value = {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$"}
    return {"anyOf": [value, {"type": "null"}]} if nullable else value


def period() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {"start": timestamp(), "end": timestamp(nullable=True)},
        "required": ["start", "end"],
    }


def objects(properties: dict[str, Any], required: list[str], *, minimum: int = 0) -> dict[str, Any]:
    value: dict[str, Any] = {
        "type": "array",
        "items": {
            "type": "object",
            "additionalProperties": False,
            "properties": properties,
            "required": required,
        },
        "maxItems": 100,
    }
    if minimum:
        value["minItems"] = minimum
    return value


def product_evaluation_context() -> dict[str, Any]:
    return {
        "anyOf": [
            {"type": "null"},
            {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "product_ref": s(),
                    "product_thesis_ref": nullable_string(),
                    "thesis_hypothesis_refs": strings(),
                    "thesis_outcome_refs": strings(),
                    "product_capability_refs": strings(),
                    "realization_binding_refs": strings(),
                    "evaluation_purpose": s(),
                },
                "required": [
                    "product_ref", "product_thesis_ref", "thesis_hypothesis_refs",
                    "thesis_outcome_refs", "product_capability_refs",
                    "realization_binding_refs", "evaluation_purpose",
                ],
            },
        ]
    }


COMMON = {
    "authority_effect": {"const": "none"},
    "kind": s(),
    "node_id": s(),
    "owner_ref": s(),
    "scope_ref": s(),
    "status": {"const": "candidate-unadmitted"},
}
COMMON_REQUIRED = ["authority_effect", "kind", "node_id", "owner_ref", "scope_ref", "status"]


MODELS: dict[str, dict[str, Any]] = {
    "type.experiment-design": {
        "purpose": "Defines one pre-run empirical test with explicit Project and Goal linkage, optional Research Inquiry and Product evaluation context, hypothesis, protocol, variables, measures, prerequisites, stop rules, timestamps, ownership, and challenge route.",
        "fields": {
            "project_ref": s(), "goal_refs": strings(minimum=1), "research_refs": strings(), "product_evaluation_context": product_evaluation_context(), "question_or_hypothesis": s(),
            "subject_ref": s(), "protocol_ref": s(), "conditions": strings(minimum=1),
            "variables_or_interventions": objects({"name": s(), "kind": enum("controlled", "independent", "intervention"), "planned_value": s()}, ["name", "kind", "planned_value"], minimum=1),
            "measure_refs": strings(minimum=1), "environment": s(), "prerequisites": strings(),
            "stop_rules": strings(minimum=1), "run_refs": strings(), "evidence_refs": strings(),
            "finding_refs": strings(), "limitations": strings(minimum=1), "design_state": enum("draft", "ready", "running", "closed", "superseded"),
            "created_at": timestamp(), "last_updated_at": timestamp(), "owner_route": s(), "challenge_route": s(), "claim_ceiling": s(),
        },
        "example": {
            "node_id": "experiment-design:definition-normalization-residue", "project_ref": "project:lab-semantic-governance", "goal_refs": ["goal:reduce-unresolved-definition-residue"],
            "research_refs": ["research-inquiry:definition-normalization-residue"],
            "product_evaluation_context": {
                "product_ref": "CA2-PRODUCT-CRAFT",
                "product_thesis_ref": "product-thesis:craft",
                "thesis_hypothesis_refs": [],
                "thesis_outcome_refs": ["product-thesis:craft#outcome-authoritative-state"],
                "product_capability_refs": ["capability:craft:governed-definition-admission"],
                "realization_binding_refs": ["binding:craft:governed-definition-admission:workflow-v1"],
                "evaluation_purpose": "Measure one normalization-residue signal relevant to the governed Definition admission realization without treating it as proof of the Product outcome or thesis.",
            },
            "question_or_hypothesis": "Applying the reviewed semantic-key map lowers finite probabilistic residue entropy in the fixed unresolved source-term set.", "subject_ref": "pipeline:definition-normalization",
            "protocol_ref": "protocol:definition-normalization-residue-comparison/v1", "conditions": ["Same source-term set", "Same residue classification vocabulary"],
            "variables_or_interventions": [{"name": "semantic-key map", "kind": "intervention", "planned_value": "baseline versus reviewed map"}],
            "measure_refs": ["measurement-method:definition-normalization-residue-entropy"], "environment": "CyberAlchemy Lab local checkout at one fixed revision",
            "prerequisites": ["Source-term set is digest-bound", "Residue classes are frozen before the run"],
            "stop_rules": ["Stop after baseline and intervention classifications complete", "Stop if source or class vocabulary changes"], "run_refs": [], "evidence_refs": [], "finding_refs": [],
            "limitations": ["The design measures one finite normalization residue model and does not establish general semantic quality or product value"], "design_state": "ready",
            "created_at": "2026-10-05T13:40:00Z", "last_updated_at": "2026-10-05T13:40:00Z",
            "owner_route": "role:research-owner", "challenge_route": "route:research-challenge",
            "claim_ceiling": "This design specifies a test. It does not show that the test ran or that the hypothesis is supported.",
        },
        "dependencies": ["cal.artifact-type.project-identity/v1", "cal.artifact-type.research-inquiry/v1 (optional research framing)", "cal.artifact-type.product-identity/v2 (optional product evaluation)", "cal.artifact-type.product-thesis/v1 (optional product evaluation)", "cal.artifact-type.product-capability/v1 (optional product evaluation)", "cal.artifact-type.capability-realization-binding/v1 (optional product evaluation)", "cal.artifact-type.measurement-method/v1"],
        "rules": [
            ("EXPERIMENT-DESIGN-PRE-RUN", "A design describes a bounded test and cannot represent execution, observations, measurements, or findings."),
            ("EXPERIMENT-DESIGN-TRACE", "Project, Goals, explicit Research and Product evaluation links when present, protocol, variables, measures, stop rules, timestamps, owner, challenge route, limitations, and claim ceiling remain explicit."),
            ("EXPERIMENT-PRODUCT-EVIDENCE-BOUNDARY", "Testing a Product Thesis outcome, Product Capability, or realization produces bounded evidence and cannot establish Product value, adoption, realization, conformance, or effectiveness by itself."),
        ],
    },
    "type.experiment-run": {
        "purpose": "Records one attributable execution of an exact Experiment Design while preserving its Project, Goal, optional Research Inquiry trace, and optional Product evaluation context together with actual inputs, environment, interventions, deviations, observations, measurements, timing, and stop state.",
        "fields": {
            "design_ref": s(), "design_version_ref": s(), "project_ref": s(), "goal_refs": strings(minimum=1), "research_refs": strings(),
            "product_evaluation_context": product_evaluation_context(),
            "environment": s(), "input_refs": strings(minimum=1),
            "interventions": strings(minimum=1), "deviations": strings(), "observation_refs": strings(minimum=1),
            "measurement_result_refs": strings(minimum=1), "evidence_set_ref": nullable_string(),
            "run_state": enum("running", "completed", "stopped", "failed"), "stop_reason": nullable_string(),
            "period": period(), "owner_route": s(), "challenge_route": s(), "claim_ceiling": s(),
        },
        "example": {
            "node_id": "experiment-run:definition-normalization-residue:2026-10-05", "design_ref": "experiment-design:definition-normalization-residue",
            "design_version_ref": "experiment-design:definition-normalization-residue@1.0.0-candidate.1", "environment": "CyberAlchemy Lab local checkout at revision review-2026-10-05",
            "project_ref": "project:lab-semantic-governance", "goal_refs": ["goal:reduce-unresolved-definition-residue"],
            "research_refs": ["research-inquiry:definition-normalization-residue"],
            "product_evaluation_context": {
                "product_ref": "CA2-PRODUCT-CRAFT",
                "product_thesis_ref": "product-thesis:craft",
                "thesis_hypothesis_refs": [],
                "thesis_outcome_refs": ["product-thesis:craft#outcome-authoritative-state"],
                "product_capability_refs": ["capability:craft:governed-definition-admission"],
                "realization_binding_refs": ["binding:craft:governed-definition-admission:workflow-v1"],
                "evaluation_purpose": "Preserve the exact Product evaluation scope from the design without converting this run into Product evidence acceptance or an owner decision.",
            },
            "input_refs": ["fixture:unresolved-source-terms/v1", "vocabulary:normalization-residue-classes/v1"], "interventions": ["Apply reviewed semantic-key map before residue classification"], "deviations": [],
            "observation_refs": ["observation:definition-normalization-residue-classes"], "measurement_result_refs": ["measurement-result:definition-normalization-residue-entropy:2026-10-05"],
            "evidence_set_ref": "evidence-set:definition-normalization-residue-run-2026-10-05", "run_state": "completed", "stop_reason": None,
            "period": {"start": "2026-10-05T14:00:00Z", "end": "2026-10-05T14:20:00Z"},
            "owner_route": "role:research-owner", "challenge_route": "route:research-challenge",
            "claim_ceiling": "This run records one execution. Completion does not establish a Finding or product value.",
        },
        "dependencies": ["cal.artifact-type.experiment-design/v1", "cal.artifact-type.observation/v1", "cal.artifact-type.measurement-result/v1"],
        "all_of": [
            {"if": {"properties": {"run_state": {"const": "completed"}}, "required": ["run_state"]}, "then": {"properties": {"evidence_set_ref": s(), "period": {"properties": {"end": timestamp()}, "required": ["end"]}}}},
            {"if": {"properties": {"run_state": {"enum": ["stopped", "failed"]}}, "required": ["run_state"]}, "then": {"properties": {"stop_reason": s(), "period": {"properties": {"end": timestamp()}, "required": ["end"]}}}},
        ],
        "rules": [
            ("EXPERIMENT-RUN-DESIGN-BINDING", "Every run binds an exact design version, preserves its Project, Goal, optional Research trace, and optional Product evaluation anchors, and records actual conditions separately from planned conditions."),
            ("EXPERIMENT-RUN-NO-CONCLUSION", "Completion, observations, measurements, and an evidence set do not become a Finding or decision."),
        ],
    },
    "type.observation": {
        "purpose": "Records one attributable perception or instrument readout during a Research Run or Experiment Run, including method, conditions, provenance, uncertainty, and limitations.",
        "fields": {
            "run_ref": s(), "subject_ref": s(), "statement": s(), "method_ref": s(), "conditions": strings(minimum=1),
            "observed_at": timestamp(), "observer_ref": s(), "provenance_refs": strings(minimum=1), "uncertainty": s(),
            "evidence_ref": s(), "limitations": strings(minimum=1), "owner_route": s(), "challenge_route": s(), "claim_ceiling": s(),
        },
        "example": {
            "node_id": "observation:definition-normalization-residue-classes", "run_ref": "experiment-run:definition-normalization-residue:2026-10-05",
            "subject_ref": "residue-set:unresolved-source-terms:2026-10-05", "statement": "Twelve unresolved source terms remained after normalization and were classified into four declared residue classes.",
            "method_ref": "protocol:definition-normalization-residue-comparison/v1#classify", "conditions": ["Reviewed semantic-key map applied", "Source and class vocabularies fixed"],
            "observed_at": "2026-10-05T14:18:00Z", "observer_ref": "person-reference:repository-reviewer",
            "provenance_refs": ["receipt:definition-normalization-classification"], "uncertainty": "Manual classification may assign ambiguous terms differently under another reviewed vocabulary.",
            "evidence_ref": "evidence:unresolved-term-class-counts", "limitations": ["One source set, one normalization revision, and one residue vocabulary"],
            "owner_route": "role:research-owner", "challenge_route": "route:research-challenge",
            "claim_ceiling": "This observation records what was seen in one run and is not an explanatory Finding.",
        },
        "dependencies": ["cal.artifact-type.research-run/v1 or cal.artifact-type.experiment-run/v1"],
        "rules": [("OBSERVATION-NO-EXPLANATION", "An Observation records a bounded readout and does not assert causal or explanatory conclusions."), ("OBSERVATION-PROVENANCE", "Run, method, conditions, observer, evidence, uncertainty, limitations, owner, and challenge route remain explicit.")],
    },
    "type.measurement-method": {
        "purpose": "Defines one residue-entropy observable after a declared source operation, including entropy register, typed residue, mathematical reading, scope, procedure, uncertainty, claim status, authority treatment, and interpretation.",
        "fields": {
            "name": s(), "property": {"const": "residue entropy"}, "entropy_register": enum("finite-probabilistic", "finite-microcanonical", "weighted", "retrieval", "categorical"),
            "source_operation_ref": s(), "residue_type_ref": s(), "observable_kind": enum("shannon-entropy", "fiber-cardinality", "declared-numeric-bridge"),
            "mathematical_reading": s(), "scope_kind": enum("finite", "weighted", "retrieval", "probabilistic", "categorical"), "procedure": s(),
            "conditions": strings(minimum=1), "unit": s(), "uncertainty_rule": s(), "claim_status": enum("theorem", "conjecture", "analogy", "review"),
            "authority_treatment": enum("non-governing", "advisory", "governed-by-separate-decision"), "interpretation": s(),
            "owner_route": s(), "challenge_route": s(), "claim_ceiling": s(),
        },
        "example": {
            "node_id": "measurement-method:definition-normalization-residue-entropy", "name": "Definition normalization residue entropy", "property": "residue entropy",
            "entropy_register": "finite-probabilistic", "source_operation_ref": "operation:normalize-source-terms-to-definition-identities",
            "residue_type_ref": "residue:unresolved-source-term", "observable_kind": "shannon-entropy",
            "mathematical_reading": "H(R) = sum over unresolved term classes of -rho(x) log rho(x).", "scope_kind": "probabilistic",
            "procedure": "Classify every unresolved source term after normalization, compute its empirical probability mass, then calculate Shannon entropy over the finite class set.",
            "conditions": ["The source set and normalization revision are fixed", "Every unresolved term belongs to exactly one declared residue class"],
            "unit": "nats", "uncertainty_rule": "Report bootstrap interval over source-term resamples and preserve the class counts.",
            "claim_status": "review", "authority_treatment": "non-governing",
            "interpretation": "Higher entropy means unresolved terms remain distributed across more distinguishable classes in this normalization run; it is not generic disorder or automatic promotion.",
            "owner_route": "role:measurement-owner", "challenge_route": "route:measurement-challenge",
            "claim_ceiling": "The method defines one finite residue-entropy observable. It does not supply a result, prove novelty, or determine authority.",
        },
        "dependencies": [],
        "rules": [("MEASUREMENT-METHOD-DECLARATION", "Residue type and source operation are declared before interpreting distinguishability, uncertainty, or information loss."), ("MEASUREMENT-METHOD-NO-AUTHORITY", "A measurement method may inform governance but cannot determine authority by itself.")],
    },
    "type.measurement-result": {
        "purpose": "Records one attributable residue-entropy result produced by an exact Measurement Method, preserving entropy register, source operation, typed residue, mathematical reading, scope, uncertainty, claim status, authority treatment, evidence, and receipt.",
        "fields": {
            "method_ref": s(), "subject_ref": s(), "residue_ref": s(), "source_operation_ref": s(),
            "entropy_register": enum("finite-probabilistic", "finite-microcanonical", "weighted", "retrieval", "categorical"),
            "observable_kind": enum("shannon-entropy", "fiber-cardinality", "declared-numeric-bridge"), "mathematical_reading": s(),
            "scope_kind": enum("finite", "weighted", "retrieval", "probabilistic", "categorical"), "value": {"type": "number"},
            "unit": s(), "uncertainty": {"type": "object", "additionalProperties": False, "properties": {"value": {"type": "number", "minimum": 0}, "interpretation": s()}, "required": ["value", "interpretation"]},
            "claim_status": enum("theorem", "conjecture", "analogy", "review"), "authority_treatment": enum("non-governing", "advisory", "governed-by-separate-decision"),
            "observed_at": timestamp(), "evidence_ref": s(), "receipt_ref": s(), "owner_route": s(), "challenge_route": s(), "claim_ceiling": s(),
        },
        "example": {
            "node_id": "measurement-result:definition-normalization-residue-entropy:2026-10-05", "method_ref": "measurement-method:definition-normalization-residue-entropy",
            "subject_ref": "experiment-run:definition-normalization-residue:2026-10-05", "residue_ref": "residue-set:unresolved-source-terms:2026-10-05",
            "source_operation_ref": "operation:normalize-source-terms-to-definition-identities", "entropy_register": "finite-probabilistic",
            "observable_kind": "shannon-entropy", "mathematical_reading": "H(R) over 12 unresolved terms grouped into 4 declared classes.", "scope_kind": "probabilistic",
            "value": 1.21, "unit": "nats", "uncertainty": {"value": 0.12, "interpretation": "Bootstrap standard error over source-term resamples."},
            "claim_status": "review", "authority_treatment": "non-governing",
            "observed_at": "2026-10-05T14:18:00Z", "evidence_ref": "evidence:unresolved-term-class-counts", "receipt_ref": "receipt:residue-entropy-calculation",
            "owner_route": "role:measurement-owner", "challenge_route": "route:measurement-challenge",
            "claim_ceiling": "This result quantifies distinguishability within one declared finite residue model. It does not prove novelty, generic disorder, promotion, or authority.",
        },
        "dependencies": ["cal.artifact-type.measurement-method/v1"],
        "rules": [("MEASUREMENT-RESULT-METHOD-BINDING", "Every result identifies its exact method, subject, residue, source operation, unit, uncertainty, evidence, and receipt."), ("MEASUREMENT-RESULT-NO-GOVERNANCE", "A measured value does not itself decide authority, admission, adoption, or value.")],
    },
    "type.ontology": {
        "purpose": "Defines one governed meaning layer as typed nodes, typed relations, branch and role context, provenance, confidence, promotion state, and use obligations.",
        "fields": {
            "name": s(), "ontology_version": s(), "purpose": s(), "boundaries": strings(minimum=1), "node_refs": strings(minimum=1),
            "relation_refs": strings(minimum=1), "branch_refs": strings(), "role_assignment_refs": strings(), "provenance_refs": strings(minimum=1),
            "confidence_policy_ref": s(), "promotion_state": enum("draft", "review", "admitted", "superseded", "retired"),
            "governance_rules": strings(minimum=1), "owner_route": s(), "challenge_route": s(), "successor_refs": strings(), "claim_ceiling": s(),
        },
        "example": {
            "node_id": "ontology:artifact-governance", "name": "Artifact governance ontology", "ontology_version": "1.0.0-candidate.1",
            "purpose": "Represent Artifact Types, Definitions, instances, decisions, owners, and their governed relations.",
            "boundaries": ["Covers repository semantic governance", "Does not describe runtime infrastructure"],
            "node_refs": ["cal.definition.artifact-type", "cal.definition.definition", "cal.definition.validation"],
            "relation_refs": ["relation.carries-definition", "relation.admits"],
            "branch_refs": ["branch:authority"], "role_assignment_refs": ["role-assignment:definition-owner"],
            "provenance_refs": ["authority/definitions/registry.json", "authority/artifact-types/registry.json"],
            "confidence_policy_ref": "policy:ontology-confidence/v1", "promotion_state": "draft",
            "governance_rules": ["Every relation has a registered kind", "Contradictions remain visible until resolved", "Promotion requires an owner decision"],
            "owner_route": "role:ontology-owner", "challenge_route": "route:ontology-challenge", "successor_refs": [],
            "claim_ceiling": "This ontology governs represented meanings and relations. It does not prove that referenced real-world objects exist or are correct.",
        },
        "dependencies": [],
        "rules": [("ONTOLOGY-MINIMUM-STRUCTURE", "A pointer list without typed relations, provenance, confidence, lifecycle, and governance is an index rather than an Ontology."), ("ONTOLOGY-USE-OBLIGATION", "Promotion, contradiction handling, drift checks, and consumer obligations remain explicit.")],
    },
    "type.context": {
        "purpose": "Defines one durable owner-qualified boundary of relevance and interpretation for a purpose, exact Product, optional Project or Goal, consumers, subject scope, and source policies.",
        "fields": {
            "context_kind": enum("product", "project", "goal"), "product_ref": s(), "project_ref": nullable_string(), "goal_ref": nullable_string(),
            "purpose": s(), "bounded_context_refs": strings(), "consumer_refs": strings(minimum=1), "intended_uses": strings(minimum=1),
            "subject_scope": strings(minimum=1), "source_policy_refs": strings(minimum=1), "profile_ref": s(), "owner_route": s(),
            "lifecycle_state": enum("draft", "active", "superseded", "retired"), "revision_history": strings(), "successor_refs": strings(), "challenge_route": s(), "claim_ceiling": s(),
        },
        "example": {
            "node_id": "context:lab-artifact-type-admission", "context_kind": "project", "product_ref": "product:craft", "project_ref": "project:lab-semantic-governance", "goal_ref": None,
            "purpose": "Resolve evidence needed to review and admit Artifact Type contracts.", "bounded_context_refs": ["bounded-context:semantic-governance"],
            "consumer_refs": ["consumer:artifact-type-review"], "intended_uses": ["Artifact Type review", "Admission decision preparation"],
            "subject_scope": ["Definitions", "Artifact Type packages", "validation receipts", "admission decisions"],
            "source_policy_refs": ["policy:admitted-authority-first", "policy:exact-digest-provenance"], "profile_ref": "context-profile:governed-review",
            "owner_route": "role:context-owner", "lifecycle_state": "active", "revision_history": [], "successor_refs": [], "challenge_route": "route:context-challenge",
            "claim_ceiling": "This Context defines relevance and interpretation boundaries. It is not a Bounded Context, source assertion, or Context View.",
        },
        "dependencies": ["cal.artifact-type.product-identity/v2", "cal.artifact-type.project-identity/v1", "cal.artifact-type.context-profile/v1"],
        "all_of": [
            {"if": {"properties": {"context_kind": {"const": "product"}}, "required": ["context_kind"]}, "then": {"properties": {"project_ref": {"type": "null"}, "goal_ref": {"type": "null"}}}},
            {"if": {"properties": {"context_kind": {"const": "project"}}, "required": ["context_kind"]}, "then": {"properties": {"project_ref": s(), "goal_ref": {"type": "null"}}}},
            {"if": {"properties": {"context_kind": {"const": "goal"}}, "required": ["context_kind"]}, "then": {"properties": {"goal_ref": s()}}},
            {"if": {"properties": {"lifecycle_state": {"const": "superseded"}}, "required": ["lifecycle_state"]}, "then": {"properties": {"successor_refs": {"minItems": 1}}}},
        ],
        "rules": [("CONTEXT-IDENTITY", "Product is required; Project and Goal cardinality follows context_kind, and material anchor or purpose changes create a successor."), ("CONTEXT-NON-COLLAPSE", "Context remains distinct from Bounded Context, Context Request, Context View, and source truth.")],
    },
    "type.context-profile": {
        "purpose": "Carries reusable construction and resolution policy derived from the admitted Context contract, including anchor rules, source eligibility, freshness, exclusions, output constraints, and succession, without representing a Context instance.",
        "fields": {
            "name": s(), "allowed_context_kinds": strings(minimum=1), "required_anchor_fields": strings(minimum=1),
            "allowed_source_kinds": strings(minimum=1), "consumer_requirements": strings(minimum=1), "freshness_policy": s(),
            "exclusion_policy": strings(minimum=1), "output_constraints": strings(minimum=1), "successor_rule": s(),
            "lifecycle_state": enum("draft", "active", "superseded", "retired"), "successor_refs": strings(), "owner_route": s(), "challenge_route": s(), "claim_ceiling": s(),
        },
        "example": {
            "node_id": "context-profile:governed-review", "name": "Governed repository review", "allowed_context_kinds": ["product", "project", "goal"],
            "required_anchor_fields": ["product_ref", "purpose", "consumer_refs", "subject_scope", "source_policy_refs"],
            "allowed_source_kinds": ["admitted authority", "digest-bound candidate", "validation receipt"],
            "consumer_requirements": ["Name the review consumer", "Declare intended use"], "freshness_policy": "Re-resolve when any bound source digest changes.",
            "exclusion_policy": ["Exclude secrets and live operator state", "Exclude unbound narrative claims"],
            "output_constraints": ["Preserve included and excluded material", "Expose limitations and expiry"],
            "successor_rule": "Create a successor when anchor rules, allowed sources, or output obligations change materially.",
            "lifecycle_state": "active", "successor_refs": [], "owner_route": "role:context-policy-owner", "challenge_route": "route:context-policy-challenge",
            "claim_ceiling": "This profile constrains Context construction and resolution. It is not a Context identity or resolved view.",
        },
        "dependencies": [],
        "rules": [("CONTEXT-PROFILE-POLICY", "A profile defines reusable construction and resolution policy and does not carry Context identity."), ("CONTEXT-PROFILE-SUCCESSION", "Material policy changes create an explicit successor rather than silently changing prior resolutions.")],
    },
    "type.context-request": {
        "purpose": "Records one bounded attributable request to resolve an exact Context version for named consumers and uses under explicit selectors, freshness, exclusions, budget, and output constraints.",
        "fields": {
            "context_ref": s(), "context_version_ref": s(), "consumer_refs": strings(minimum=1), "intended_uses": strings(minimum=1),
            "selectors": strings(minimum=1), "freshness_requirement": s(), "exclusions": strings(), "output_constraints": strings(minimum=1),
            "budget": {"type": "object", "additionalProperties": False, "properties": {"max_items": {"type": "integer", "minimum": 1}, "max_bytes": {"type": "integer", "minimum": 1}}, "required": ["max_items", "max_bytes"]},
            "requested_at": timestamp(), "owner_route": s(), "challenge_route": s(), "claim_ceiling": s(),
        },
        "example": {
            "node_id": "context-request:remaining-18-review", "context_ref": "context:lab-artifact-type-admission", "context_version_ref": "context:lab-artifact-type-admission@sha256:79e1",
            "consumer_refs": ["consumer:artifact-type-review"], "intended_uses": ["Review the remaining 18 Artifact Type candidates as one batch"],
            "selectors": ["Admitted Definition bound to each target", "Candidate artifact schema and fixture", "Existing admitted Artifact Type carriers"],
            "freshness_requirement": "All selected files must match their declared SHA-256 at resolution time.",
            "exclusions": ["Secrets", "Live service state", "Unrelated dirty work"], "output_constraints": ["One complete model", "One exact example per type", "One admission decision"],
            "budget": {"max_items": 250, "max_bytes": 2000000}, "requested_at": "2026-10-05T15:00:00Z",
            "owner_route": "role:context-request-owner", "challenge_route": "route:context-request-challenge",
            "claim_ceiling": "This request authorizes resolution only; it does not mutate Context, grant source authority, or admit Artifact Types.",
        },
        "dependencies": ["cal.artifact-type.context/v1"],
        "rules": [("CONTEXT-REQUEST-EXACTNESS", "Context version, consumers, intended uses, selectors, freshness, exclusions, budget, and output constraints are explicit."), ("CONTEXT-REQUEST-NO-AUTHORITY", "A request does not mutate Context, grant source authority, or create a resolved view by itself.")],
    },
    "type.context-view": {
        "purpose": "Records one immutable digest-bound projection resolving an exact Context Request against one Context version and source epoch, including included and excluded material, lineage, limitations, and expiry.",
        "fields": {
            "request_ref": s(), "context_ref": s(), "context_version_ref": s(), "source_epoch": s(), "generated_at": timestamp(), "expires_at": timestamp(),
            "included_material": objects({"source_ref": s(), "selector": s(), "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"}}, ["source_ref", "selector", "sha256"], minimum=1),
            "excluded_material": objects({"source_ref": s(), "reason": s()}, ["source_ref", "reason"]), "lineage_refs": strings(minimum=1),
            "limitations": strings(minimum=1), "selection_basis": s(), "owner_route": s(), "challenge_route": s(), "claim_ceiling": s(),
        },
        "example": {
            "node_id": "context-view:remaining-18-review:2026-10-05", "request_ref": "context-request:remaining-18-review", "context_ref": "context:lab-artifact-type-admission",
            "context_version_ref": "context:lab-artifact-type-admission@sha256:79e1", "source_epoch": "git-worktree:2026-10-05T15:05:00Z",
            "generated_at": "2026-10-05T15:05:00Z", "expires_at": "2026-10-06T15:05:00Z",
            "included_material": [{"source_ref": "authority/definitions/registry.json", "selector": "admitted entries bound by remaining 18 packages", "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}],
            "excluded_material": [{"source_ref": "runtime:live-services", "reason": "Outside the repository review Context"}],
            "lineage_refs": ["context-request:remaining-18-review", "receipt:remaining-18-model-validation"],
            "limitations": ["The view covers repository state at one source epoch"], "selection_basis": "Exact request selectors and admitted-authority-first source policy.",
            "owner_route": "role:context-view-owner", "challenge_route": "route:context-view-challenge",
            "claim_ceiling": "This immutable view records a bounded projection. It is not the Context itself and does not make included claims true.",
        },
        "dependencies": ["cal.artifact-type.context/v1", "cal.artifact-type.context-request/v1"],
        "rules": [("CONTEXT-VIEW-IMMUTABLE", "Request, Context version, source epoch, selected digests, exclusions, lineage, limitations, and expiry bind one immutable projection."), ("CONTEXT-VIEW-NON-COLLAPSE", "A current Context View does not imply that its Context or included sources remain current or authoritative.")],
    },
    "type.model-instance-binding": {
        "purpose": "Binds one exact governed parent model to one locally owned instance while separating inherited contract, extensions, owners, authority scopes, conformance, and lifecycle.",
        "fields": {
            "parent_model_ref": s(), "parent_model_version_ref": s(), "instance_ref": s(), "parent_owner_route": s(), "instance_owner_route": s(),
            "inherited_contract_refs": strings(minimum=1), "parent_authority_scope": s(), "instance_authority_scope": s(), "extension_scope": strings(),
            "local_override_refs": strings(), "conformance_refs": strings(), "binding_state": enum("proposed", "active", "suspended", "superseded", "retired"),
            "successor_refs": strings(), "owner_route": s(), "challenge_route": s(), "claim_ceiling": s(),
        },
        "example": {
            "node_id": "model-instance-binding:artifact-type-reviewer", "parent_model_ref": "product-capability:governed-definition-admission",
            "parent_model_version_ref": "product-capability:governed-definition-admission@1.0.0-candidate.1", "instance_ref": "capability-instance:lab-artifact-type-reviewer",
            "parent_owner_route": "role:product-capability-owner", "instance_owner_route": "role:lab-tool-owner",
            "inherited_contract_refs": ["contract:definition-admission-boundaries/v1"], "parent_authority_scope": "scope:product-capability-semantics",
            "instance_authority_scope": "scope:lab-review-tool-operation", "extension_scope": ["Render batch review documents"],
            "local_override_refs": [], "conformance_refs": ["conformance:lab-artifact-type-reviewer:v1"], "binding_state": "active", "successor_refs": [],
            "owner_route": "role:model-binding-owner", "challenge_route": "route:model-binding-challenge",
            "claim_ceiling": "The binding connects parent and instance contracts. It does not transfer parent ownership or prove runtime effectiveness.",
        },
        "dependencies": [],
        "rules": [("MODEL-BINDING-AUTHORITY-SEPARATION", "Parent and instance keep distinct identities, owners, authority scopes, and lifecycle state."), ("MODEL-BINDING-CONFORMANCE", "Inheritance and conformance do not imply adoption, operation, effectiveness, or value.")],
    },
    "type.person-reference": {
        "purpose": "Provides one minimal purpose-bounded reference to a Person while limiting exposed personal data and separating the reference from identity claims, accounts, roles, memberships, and authority.",
        "fields": {
            "local_label": s(), "reference_type": enum("opaque-local", "workspace-handle", "external-pseudonym"), "reference_value": s(),
            "purpose": s(), "identity_scope": s(), "minimization_basis": s(), "permitted_uses": strings(minimum=1), "prohibited_uses": strings(minimum=1),
            "lifecycle_state": enum("active", "superseded", "retired"), "successor_refs": strings(), "owner_route": s(), "challenge_route": s(), "claim_ceiling": s(),
        },
        "example": {
            "node_id": "person-reference:repository-reviewer", "local_label": "Repository reviewer", "reference_type": "opaque-local", "reference_value": "person-local-001",
            "purpose": "Attribute repository review observations without storing private identity attributes.", "identity_scope": "CyberAlchemy Lab semantic-governance records",
            "minimization_basis": "Only a stable opaque reference and functional label are needed for attribution.",
            "permitted_uses": ["Attribute review observations", "Bind explicit assignments"], "prohibited_uses": ["Infer legal identity", "Infer employment or permissions"],
            "lifecycle_state": "active", "successor_refs": [], "owner_route": "role:people-data-owner", "challenge_route": "route:person-reference-challenge",
            "claim_ceiling": "This is a minimal Person reference, not proof of identity, account ownership, role, membership, or authority.",
        },
        "dependencies": [],
        "rules": [("PERSON-REFERENCE-MINIMIZATION", "The reference carries only data needed for its declared purpose and identity scope."), ("PERSON-REFERENCE-NON-COLLAPSE", "Account, Person, Role, Membership, ownership, observed record, and authority remain separate facts.")],
    },
    "type.identity-claim": {
        "purpose": "Records one attributable challengeable assertion that a Person Reference denotes a particular identifier under declared evidence and assurance policy.",
        "fields": {
            "person_reference_ref": s(), "asserted_identifier": s(), "claim_scope": s(), "evidence_refs": strings(minimum=1), "assurance_policy_ref": s(),
            "assurance_level": enum("self-asserted", "corroborated", "verified"), "claim_state": enum("proposed", "current", "contested", "expired", "withdrawn"),
            "asserted_at": timestamp(), "expires_at": timestamp(nullable=True), "limitations": strings(minimum=1), "owner_route": s(), "challenge_route": s(), "claim_ceiling": s(),
        },
        "example": {
            "node_id": "identity-claim:repository-reviewer:workspace-handle", "person_reference_ref": "person-reference:repository-reviewer",
            "asserted_identifier": "workspace-handle:reviewer-001", "claim_scope": "CyberAlchemy Lab review attribution",
            "evidence_refs": ["evidence:workspace-handle-owner-attestation"], "assurance_policy_ref": "policy:workspace-identity-assurance/v1", "assurance_level": "self-asserted",
            "claim_state": "current", "asserted_at": "2026-10-05T15:10:00Z", "expires_at": None,
            "limitations": ["No legal identity verification", "No authority or permission inference"], "owner_route": "role:identity-claim-owner", "challenge_route": "route:identity-claim-challenge",
            "claim_ceiling": "The evidence supports only the declared workspace identifier relation and no private attributes, roles, membership, or authority.",
        },
        "dependencies": ["cal.artifact-type.person-reference/v1"],
        "rules": [("IDENTITY-CLAIM-EVIDENCE", "Person Reference, asserted identifier, scope, evidence, assurance policy, state, time, limits, and challenge route remain explicit."), ("IDENTITY-CLAIM-NO-AUTHORITY", "An identity claim does not establish private attributes, roles, team membership, ownership, permission, or authority.")],
    },
    "type.team": {
        "purpose": "Defines one durable owner-qualified collective identity for Persons coordinating toward a declared purpose and scope, separately from membership, roles, responsibilities, and authority.",
        "fields": {
            "name": s(), "purpose": s(), "identity_boundary": s(), "owner_route": s(), "lifecycle_state": enum("proposed", "active", "suspended", "retired", "superseded"),
            "membership_refs": strings(), "responsibility_refs": strings(), "role_assignment_refs": strings(), "authority_claim_refs": strings(),
            "revision_history": strings(), "successor_refs": strings(), "challenge_route": s(), "claim_ceiling": s(),
        },
        "example": {
            "node_id": "team:semantic-governance", "name": "Semantic Governance Team", "purpose": "Coordinate Definition and Artifact Type review for CyberAlchemy Lab.",
            "identity_boundary": "The team is identified by this purpose, repository scope, and owner route; membership changes do not replace it.",
            "owner_route": "role:team-owner", "lifecycle_state": "active", "membership_refs": ["team-membership:reviewer:semantic-governance"],
            "responsibility_refs": ["responsibility:maintain-definition-authority"], "role_assignment_refs": ["role-assignment:reviewer:artifact-type-reviewer"],
            "authority_claim_refs": [], "revision_history": [], "successor_refs": [], "challenge_route": "route:team-challenge",
            "claim_ceiling": "The Team record defines collective identity. Membership, roles, responsibilities, and authority require separate records.",
        },
        "dependencies": ["cal.artifact-type.team-membership/v1", "cal.artifact-type.role-assignment/v1"],
        "all_of": [{"if": {"properties": {"lifecycle_state": {"const": "active"}}, "required": ["lifecycle_state"]}, "then": {"properties": {"membership_refs": {"minItems": 1}}}}],
        "rules": [("TEAM-DURABLE-IDENTITY", "Membership changes do not replace a Team while purpose, scope, and owner boundary remain stable."), ("TEAM-SEPARATION", "Membership, role assignment, responsibility ownership, and authority remain independently governed relations.")],
    },
    "type.team-membership": {
        "purpose": "Records one owner-qualified time-bounded Person-to-Team membership relation with its own lifecycle, basis, succession, and challenge route.",
        "fields": {
            "person_reference_ref": s(), "team_ref": s(), "membership_state": enum("proposed", "active", "inactive", "revoked"), "period": period(),
            "basis_ref": s(), "owner_route": s(), "challenge_route": s(), "successor_refs": strings(), "claim_ceiling": s(),
        },
        "example": {
            "node_id": "team-membership:reviewer:semantic-governance", "person_reference_ref": "person-reference:repository-reviewer", "team_ref": "team:semantic-governance",
            "membership_state": "active", "period": {"start": "2026-10-05T00:00:00Z", "end": None}, "basis_ref": "decision:semantic-governance-team-membership",
            "owner_route": "role:team-membership-owner", "challenge_route": "route:team-membership-challenge", "successor_refs": [],
            "claim_ceiling": "This record establishes only the scoped membership relation and does not assign a Role, responsibility, permission, or authority.",
        },
        "dependencies": ["cal.artifact-type.person-reference/v1", "cal.artifact-type.team/v1"],
        "all_of": [{"if": {"properties": {"membership_state": {"const": "active"}}, "required": ["membership_state"]}, "then": {"properties": {"period": {"properties": {"end": {"type": "null"}}, "required": ["end"]}}}}],
        "rules": [("TEAM-MEMBERSHIP-INDEPENDENT", "Membership has its own state, period, basis, owner, challenge route, and succession."), ("TEAM-MEMBERSHIP-NO-GRANT", "Membership does not assign a Role, responsibility, permission, ownership, or authority.")],
    },
    "type.role": {
        "purpose": "Defines one reusable scope-bounded position with expected functions, responsibilities, eligible authority relations, explicit exclusions, ownership, lifecycle, and challenge route.",
        "fields": {
            "name": s(), "purpose": s(), "functions": strings(minimum=1), "responsibility_refs": strings(), "eligible_authority_relation_kinds": strings(),
            "authority_boundary": s(), "exclusions": strings(minimum=1), "lifecycle_state": enum("draft", "active", "retired", "superseded"),
            "successor_refs": strings(), "owner_route": s(), "challenge_route": s(), "claim_ceiling": s(),
        },
        "example": {
            "node_id": "role:artifact-type-reviewer", "name": "Artifact Type Reviewer", "purpose": "Review candidate Artifact Type contracts against admitted Definitions and evidence boundaries.",
            "functions": ["Compare schema to admitted Definition", "Review example and validation receipt", "Record unresolved residue"],
            "responsibility_refs": ["responsibility:artifact-type-review-quality"], "eligible_authority_relation_kinds": ["relation.claims-authority-over"],
            "authority_boundary": "The role may recommend an admission decision but does not admit, activate, publish, or deploy by itself.",
            "exclusions": ["No implicit repository-owner authority", "No runtime permission grant"], "lifecycle_state": "active", "successor_refs": [],
            "owner_route": "role:role-model-owner", "challenge_route": "route:role-challenge",
            "claim_ceiling": "This Role describes expected work and eligible authority relations; it grants no authority without a separate assignment and authority claim.",
        },
        "dependencies": [],
        "rules": [("ROLE-REUSABLE", "Role identity is independent of any Person, Team, Team Membership, or current assignment."), ("ROLE-NO-GRANT", "Expected functions and eligible authority relations do not grant authority.")],
    },
    "type.role-assignment": {
        "purpose": "Records one owner-qualified time-bounded assignment of a Person Reference or Team to a Role in an exact scope and lifecycle epoch, with separate responsibility and authority claims.",
        "fields": {
            "assignee_kind": enum("person-reference", "team"), "assignee_ref": s(), "role_ref": s(), "assignment_basis_ref": s(),
            "assignment_state": enum("proposed", "active", "suspended", "ended", "revoked"), "period": period(),
            "responsibility_refs": strings(), "authority_claim_refs": strings(), "owner_route": s(), "challenge_route": s(), "successor_refs": strings(), "claim_ceiling": s(),
        },
        "example": {
            "node_id": "role-assignment:reviewer:artifact-type-reviewer", "assignee_kind": "person-reference", "assignee_ref": "person-reference:repository-reviewer",
            "role_ref": "role:artifact-type-reviewer", "assignment_basis_ref": "decision:assign-artifact-type-reviewer", "assignment_state": "active",
            "period": {"start": "2026-10-05T00:00:00Z", "end": None}, "responsibility_refs": ["responsibility:artifact-type-review-quality"],
            "authority_claim_refs": ["authority-claim:may-recommend-artifact-type-admission"], "owner_route": "role:role-assignment-owner",
            "challenge_route": "route:role-assignment-challenge", "successor_refs": [],
            "claim_ceiling": "This assignment binds an assignee to a Role in scope and time. It does not create Team Membership or authority beyond separately admitted claims.",
        },
        "dependencies": ["cal.artifact-type.person-reference/v1 or cal.artifact-type.team/v1", "cal.artifact-type.role/v1"],
        "all_of": [{"if": {"properties": {"assignment_state": {"const": "active"}}, "required": ["assignment_state"]}, "then": {"properties": {"period": {"properties": {"end": {"type": "null"}}, "required": ["end"]}}}}],
        "rules": [("ROLE-ASSIGNMENT-EXACT", "Assignee kind, assignee, Role, scope, basis, state, period, owner, challenge route, and succession are explicit."), ("ROLE-ASSIGNMENT-NO-IMPLICIT-GRANT", "Assignment does not imply Team Membership, permissions, or authority beyond separate admitted claims.")],
    },
}


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def apply_package(target_id: str, destination: Path) -> None:
    model = MODELS.get(target_id)
    if model is None:
        return
    slug = target_id.removeprefix("type.")
    properties = deepcopy(COMMON)
    properties["kind"] = {"const": slug}
    properties.update(deepcopy(model["fields"]))
    required = COMMON_REQUIRED + list(model["fields"])
    schema: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        "required": required,
    }
    if model.get("all_of"):
        schema["allOf"] = deepcopy(model["all_of"])
    dump(destination / "schema.json", schema)

    witness = {
        "authority_effect": "none",
        "kind": slug,
        "owner_ref": "role:artifact-type-owner",
        "scope_ref": "scope:cyberalchemy-lab-model-review",
        "status": "candidate-unadmitted",
        **deepcopy(model["example"]),
    }
    dump(destination / "fixtures/valid/record.json", witness)
    missing_field = next(iter(model["fields"]))
    invalid = deepcopy(witness)
    del invalid[missing_field]
    dump(destination / "fixtures/invalid/missing-model-field.json", invalid)


def apply_artifact(target_id: str, artifact: dict[str, Any]) -> None:
    model = MODELS.get(target_id)
    if model is None:
        return
    slug = target_id.removeprefix("type.")
    artifact["version"] = "1.0.0-candidate.2"
    artifact["schema_ref"] = f"cal.schema.{slug}-review-candidate/v2"
    artifact["distinct_validation_purpose"] = model["purpose"]
    artifact["four_facets"] = dict(artifact["four_facets"])
    artifact["four_facets"]["human_continuation"] = "Generated RECORD.md and the complete-model review explain the revised contract, realistic example, dependencies, and claim limits."
    artifact["instance_contract"] = dict(artifact["instance_contract"])
    artifact["instance_contract"]["required_semantic_fields"] = sorted(set(COMMON_REQUIRED[1:]) | set(model["fields"]))
    artifact["orthogonality_rules"] = [
        {"rule_id": rule_id, "statement": statement} for rule_id, statement in model["rules"]
    ]
    artifact["validation_contract"] = dict(artifact["validation_contract"])
    artifact["validation_contract"]["negative_witnesses"] = list(artifact["validation_contract"]["negative_witnesses"]) + ["fixtures/invalid/missing-model-field.json"]


def review_entry(target_id: str) -> dict[str, Any]:
    model = MODELS[target_id]
    return {
        "target_id": target_id,
        "purpose": model["purpose"],
        "dependencies": model["dependencies"],
        "rules": [{"rule_id": rule_id, "statement": statement} for rule_id, statement in model["rules"]],
    }
