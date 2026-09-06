<!-- GENERATED FILE: edit context.json and rerun generator.py. -->

# Bounded Context: cal.context.ontology-lifecycle

> Generated from `context.json`; this view is not canonical.

- Identity: `cal.context.ontology-lifecycle`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Artifact type: `cal.artifact-type.bounded-context/v1`
- Semantic kind: `bounded-context`
- Authority effect: `none`

## Domain Model Ref

cal.ontology-lifecycle.business-domain.v2-candidate

## Ubiquitous Language Ref

cal.language.ontology-lifecycle/v1

## Scope

```json
{
  "exclusions": [
    "Governance axioms, rules, policies, assessments, decisions, constitutions, disciplines, and authority scopes belong to the Governance Bounded Context.",
    "A governance event records governance state and its exact semantic-event reference; it does not create, replace, or infer the Governance owner decision that produced it.",
    "Rebuildable views and projections are derived surfaces and never become canonical ontology truth.",
    "Cross-context relationship patterns and translation contracts require a separately selected Context Map."
  ],
  "statement": "Own the meaning of ontology subjects, exact semantic and governance event histories, lifecycle-state reconstruction, graph commit ordering, consistent cuts, endpoint integrity, governed views, context projections, replay failure, and typed residue."
}
```

## Semantic Owner Ref

role:ontology-lifecycle-context-owner

## Contract Refs

- cal.definition.bounded-context@1.0.0-candidate.1
- cal.definition.ubiquitous-language@1.0.0-candidate.1
- cal.artifact-type.bounded-context/v1
- cal.artifact-type.ubiquitous-language/v1

## Context Map Refs

None declared.

## Challenge Route

role:ontology-lifecycle-context-owner

## Evidence

- CAL-CONTEXT-PACK-CTX03-0001
- CAL-DECISION-0018-DEFINITION-AND-CTX00-PROMOTION
- CAL-DECISION-0021-CTX01-ARTIFACT-TYPE-PROMOTION
- CAL-DECISION-0022-CONTEXT-OPERATIONAL-OWNER-PROMOTION
- source:cal.ontology-lifecycle.business-domain.v2-candidate

## Residue

- residue:ontology-lifecycle-context-owner-admission-required
- residue:ontology-lifecycle-language-owner-admission-required
- residue:ontology-lifecycle-business-model-remains-candidate-unadmitted
- residue:governance-ontology-lifecycle-context-map-unselected

## Claim ceiling

This artifact is a candidate semantic boundary only. It does not admit the Ontology Lifecycle Bounded Context or its language, admit the candidate business ontology, select a Context Map relationship, authorize migration or runtime enforcement, publish, deploy, or establish a stable release.
