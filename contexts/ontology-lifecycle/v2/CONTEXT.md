<!-- GENERATED FILE: edit context.json and rerun generator.py. -->

# Bounded Context: cal.context.ontology-lifecycle

> Generated from `context.json`; this view is not canonical.

- Identity: `cal.context.ontology-lifecycle`
- Version: `1.1.0-candidate.1`
- Status: `candidate-unadmitted`
- Artifact type: `cal.artifact-type.bounded-context/v1`
- Semantic kind: `bounded-context`
- Authority effect: `none`

## Domain Model Ref

cal.ontology-lifecycle.business-domain.v2-candidate

## Ubiquitous Language Ref

cal.language.ontology-lifecycle/v2

## Scope

```json
{
  "exclusions": [
    "Governance axioms, rules, policies, assessments, decisions, constitutions, disciplines, and authority scopes belong to the Governance Bounded Context.",
    "A Governance Event records an exact Governance-owned decision envelope; it cannot create, replace, reinterpret, amend, revoke, invalidate, or enforce that decision.",
    "Rebuildable views and projections are derived surfaces and never become canonical ontology truth.",
    "The admitted Context Map authorizes only its declared downstream translation boundary; no reverse dependency is inferred."
  ],
  "statement": "Own the meaning of ontology subjects, exact semantic and governance event histories, lifecycle-state reconstruction, graph commit ordering, consistent cuts, endpoint integrity, governed views, context projections, replay failure, and typed residue."
}
```

## Semantic Owner Ref

role:ontology-lifecycle-context-owner

## Contract Refs

- cal.definition.bounded-context@1.0.0-candidate.1
- cal.definition.ubiquitous-language@1.0.0-candidate.1
- cal.definition.context-map@1.0.0-candidate.1
- cal.artifact-type.bounded-context/v1
- cal.artifact-type.ubiquitous-language/v1
- cal.artifact-type.context-map/v1

## Context Map Refs

- cal.context-map.governance-ontology-lifecycle/v1

## Challenge Route

role:ontology-lifecycle-context-owner

## Evidence

- CAL-CONTEXT-PACK-CTX05-0001
- CAL-DECISION-0023-GOVERNANCE-AND-ONTOLOGY-LIFECYCLE-CONTEXT-PROMOTION
- CAL-DECISION-0024-GOVERNANCE-ONTOLOGY-LIFECYCLE-CONTEXT-MAP-PROMOTION
- cal.context.ontology-lifecycle/v1
- source:cal.ontology-lifecycle.business-domain.v2-candidate

## Residue

- residue:ontology-lifecycle-v2-context-and-language-owner-admission-required
- residue:ontology-lifecycle-business-model-remains-candidate-unadmitted
- residue:context-map-endpoint-remains-admitted-v1-predecessor-until-successor-map-epoch
- residue:runtime-payload-schema-and-anticorruption-adapter-not-authored

## Claim ceiling

This successor candidate preserves Ontology Lifecycle meaning while adding one explicit reference to the admitted Governance-to-Ontology-Lifecycle Context Map. It does not admit this v2 context or language, rewrite the admitted v1 epoch or map, admit the candidate business ontology, authorize a runtime adapter, migration or enforcement, publish, deploy, or establish a stable release.
