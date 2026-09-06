<!-- GENERATED FILE: edit context.json and rerun generator.py. -->

# Bounded Context: cal.context.ontology-lifecycle

> Generated from `context.json`; this view is not canonical.

- Identity: `cal.context.ontology-lifecycle`
- Version: `2.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Artifact type: `cal.artifact-type.bounded-context/v2`
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
    "Exact endpoint membership and directional cross-context relationships belong exclusively to canonical Context Map records; this Bounded Context owns no canonical map backreference."
  ],
  "statement": "Own the meaning of ontology subjects, exact semantic and governance event histories, lifecycle-state reconstruction, graph commit ordering, consistent cuts, endpoint integrity, governed views, context projections, replay failure, and typed residue."
}
```

## Semantic Owner Ref

role:ontology-lifecycle-context-owner

## Contract Refs

- cal.definition.bounded-context@2.0.0-candidate.1
- cal.definition.ubiquitous-language@1.0.0-candidate.1
- cal.definition.context-map@2.0.0-candidate.1
- cal.artifact-type.bounded-context/v2
- cal.artifact-type.ubiquitous-language/v1
- cal.artifact-type.context-map/v2

## Challenge Route

role:ontology-lifecycle-context-owner

## Evidence

- CAL-DECISION-0025-GOVERNANCE-ONTOLOGY-LIFECYCLE-SUCCESSOR-PROMOTION
- CAL-DECISION-0026-CTX06-REFERENCE-NORMALIZATION-DEFINITION-PROMOTION
- CAL-DECISION-0027-CTX07-NORMALIZED-CONTEXT-ARTIFACT-TYPE-PROMOTION
- cal.context.ontology-lifecycle/v2
- cal.language.ontology-lifecycle/v2
- source:cal.ontology-lifecycle.business-domain.v2-candidate

## Residue

- residue:ontology-lifecycle-v3-context-owner-admission-required
- residue:ontology-lifecycle-v2-language-retained-as-exact-owned-language
- residue:normalized-successor-context-map-for-v3-endpoints-not-authored
- residue:v2-to-v3-migration-amendment-not-authored
- residue:ontology-lifecycle-business-model-remains-candidate-unadmitted
- residue:runtime-payload-schema-and-anticorruption-adapter-not-authored

## Claim ceiling

This candidate preserves Ontology Lifecycle meaning while normalizing the Bounded Context representation so Context Maps solely own endpoint membership and relationships. It does not admit this v3 epoch, revise its admitted v2 language, create or admit a successor Context Map, infer migration or supersession, admit the candidate business ontology, authorize a runtime adapter or enforcement, publish, deploy, or establish stable-release state.
