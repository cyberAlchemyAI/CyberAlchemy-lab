<!-- GENERATED FILE: edit context.json and rerun generator.py. -->

# Bounded Context: cal.context.governance

> Generated from `context.json`; this view is not canonical.

- Identity: `cal.context.governance`
- Version: `2.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Artifact type: `cal.artifact-type.bounded-context/v2`
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
    "Exact endpoint membership and directional cross-context relationships belong exclusively to canonical Context Map records; this Bounded Context owns no canonical map backreference."
  ],
  "statement": "Own the meaning and authority boundaries of governance axioms, invariants, rules, policies, evidence, observations, assessments, decisions, disciplines, constitutions, authority scopes, modes, friction contracts, and product bindings."
}
```

## Semantic Owner Ref

role:governance-context-owner

## Contract Refs

- cal.definition.bounded-context@2.0.0-candidate.1
- cal.definition.ubiquitous-language@1.0.0-candidate.1
- cal.definition.context-map@2.0.0-candidate.1
- cal.artifact-type.bounded-context/v2
- cal.artifact-type.ubiquitous-language/v1
- cal.artifact-type.context-map/v2

## Challenge Route

role:governance-context-owner

## Evidence

- CAL-DECISION-0025-GOVERNANCE-ONTOLOGY-LIFECYCLE-SUCCESSOR-PROMOTION
- CAL-DECISION-0026-CTX06-REFERENCE-NORMALIZATION-DEFINITION-PROMOTION
- CAL-DECISION-0027-CTX07-NORMALIZED-CONTEXT-ARTIFACT-TYPE-PROMOTION
- cal.context.governance/v2
- cal.language.governance/v2
- source:cav2.governance-model@candidate

## Residue

- residue:governance-v3-context-owner-admission-required
- residue:governance-v2-language-retained-as-exact-owned-language
- residue:normalized-successor-context-map-for-v3-endpoints-not-authored
- residue:v2-to-v3-migration-amendment-not-authored
- residue:governance-source-model-remains-separately-governed

## Claim ceiling

This candidate preserves Governance meaning while normalizing the Bounded Context representation so Context Maps solely own endpoint membership and relationships. It does not admit this v3 epoch, revise its admitted v2 language, create or admit a successor Context Map, infer migration or supersession, admit the source governance ontology, authorize implementation, publish, deploy, or establish stable-release state.
