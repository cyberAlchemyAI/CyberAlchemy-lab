<!-- GENERATED FILE: edit context.json and rerun generator.py. -->

# Bounded Context: cal.context.governance

> Generated from `context.json`; this view is not canonical.

- Identity: `cal.context.governance`
- Version: `1.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Artifact type: `cal.artifact-type.bounded-context/v1`
- Semantic kind: `bounded-context`
- Authority effect: `none`

## Domain Model Ref

cav2.governance-model@candidate

## Ubiquitous Language Ref

cal.language.governance/v1

## Scope

```json
{
  "exclusions": [
    "Ontology event history, replay, consistent cuts, lifecycle-state reconstruction, and context projections belong to the Ontology Lifecycle Bounded Context.",
    "A candidate governance model, assessment, policy, or evidence item does not create an owner decision, adoption, enforcement, publication, or deployment effect.",
    "Cross-context relationship patterns and translation contracts require a separately selected Context Map."
  ],
  "statement": "Own the meaning and authority boundaries of governance axioms, invariants, rules, policies, evidence, observations, assessments, decisions, disciplines, constitutions, authority scopes, modes, friction contracts, and product bindings."
}
```

## Semantic Owner Ref

role:governance-context-owner

## Contract Refs

- cal.definition.bounded-context@1.0.0-candidate.1
- cal.definition.ubiquitous-language@1.0.0-candidate.1
- cal.artifact-type.bounded-context/v1
- cal.artifact-type.ubiquitous-language/v1

## Context Map Refs

None declared.

## Challenge Route

role:governance-context-owner

## Evidence

- CAL-CONTEXT-PACK-CTX03-0001
- CAL-DECISION-0018-DEFINITION-AND-CTX00-PROMOTION
- CAL-DECISION-0021-CTX01-ARTIFACT-TYPE-PROMOTION
- CAL-DECISION-0022-CONTEXT-OPERATIONAL-OWNER-PROMOTION
- source:cav2.governance-model@candidate

## Residue

- residue:governance-context-owner-admission-required
- residue:governance-language-owner-admission-required
- residue:governance-source-model-remains-separately-governed
- residue:governance-ontology-lifecycle-context-map-unselected

## Claim ceiling

This artifact is a candidate semantic boundary only. It does not admit the Governance Bounded Context or its language, adopt the source governance ontology, select a Context Map relationship, authorize migration or implementation, publish, deploy, or establish a stable release.
