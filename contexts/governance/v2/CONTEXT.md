<!-- GENERATED FILE: edit context.json and rerun generator.py. -->

# Bounded Context: cal.context.governance

> Generated from `context.json`; this view is not canonical.

- Identity: `cal.context.governance`
- Version: `1.1.0-candidate.1`
- Status: `candidate-unadmitted`
- Artifact type: `cal.artifact-type.bounded-context/v1`
- Semantic kind: `bounded-context`
- Authority effect: `none`

## Domain Model Ref

cav2.governance-model@candidate

## Ubiquitous Language Ref

cal.language.governance/v2

## Scope

```json
{
  "exclusions": [
    "Ontology event history, replay, consistent cuts, lifecycle-state reconstruction, and context projections belong to the Ontology Lifecycle Bounded Context.",
    "A candidate governance model, assessment, policy, or evidence item does not create an owner decision, adoption, enforcement, publication, or deployment effect.",
    "The admitted Context Map transfers an exact decision envelope to Ontology Lifecycle; it does not transfer Governance semantic ownership or authority."
  ],
  "statement": "Own the meaning and authority boundaries of governance axioms, invariants, rules, policies, evidence, observations, assessments, decisions, disciplines, constitutions, authority scopes, modes, friction contracts, and product bindings."
}
```

## Semantic Owner Ref

role:governance-context-owner

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

role:governance-context-owner

## Evidence

- CAL-CONTEXT-PACK-CTX05-0001
- CAL-DECISION-0023-GOVERNANCE-AND-ONTOLOGY-LIFECYCLE-CONTEXT-PROMOTION
- CAL-DECISION-0024-GOVERNANCE-ONTOLOGY-LIFECYCLE-CONTEXT-MAP-PROMOTION
- cal.context.governance/v1
- source:cav2.governance-model@candidate

## Residue

- residue:governance-v2-context-and-language-owner-admission-required
- residue:governance-source-model-remains-separately-governed
- residue:context-map-endpoint-remains-admitted-v1-predecessor-until-successor-map-epoch

## Claim ceiling

This successor candidate preserves Governance meaning while adding one explicit reference to the admitted Governance-to-Ontology-Lifecycle Context Map. It does not admit this v2 context or language, rewrite the admitted v1 epoch or map, admit the source governance ontology, authorize migration or implementation, publish, deploy, or establish a stable release.
