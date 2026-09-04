<!-- GENERATED FILE: edit map.json and rerun generator.py. -->

# Context Map: cal.context-map.fixture-governance-ontology-lifecycle

> Generated from `map.json`; this view is not canonical.

- Identity: `cal.context-map.fixture-governance-ontology-lifecycle`
- Version: `2.0.0-candidate.1`
- Status: `candidate-unadmitted`
- Artifact type: `cal.artifact-type.context-map/v2`
- Semantic kind: `context-map`
- Authority effect: `none`

## Context Refs

- cal.context.fixture-governance/v3
- cal.context.fixture-ontology-lifecycle/v3

## Relationships

```json
[
  {
    "authority_boundary": "No authority crosses this fixture relationship.",
    "contract_refs": [
      "cal.definition.context-map@2.0.0-candidate.1"
    ],
    "direction": "source-to-target",
    "information_boundary": "Only the declared fixture envelope crosses.",
    "owner_refs": [
      "role:fixture-map-owner",
      "role:fixture-source-owner",
      "role:fixture-target-owner"
    ],
    "relationship_id": "cal.context-relationship.fixture-governance-to-ontology-lifecycle",
    "relationship_kind_ref": "fixture:upstream-downstream/v1",
    "source_context_ref": "cal.context.fixture-governance/v3",
    "target_context_ref": "cal.context.fixture-ontology-lifecycle/v3",
    "translation_refs": [
      "fixture:decision-envelope-to-event/v1"
    ]
  }
]
```

## Owner Refs

- role:fixture-map-owner
- role:fixture-source-owner
- role:fixture-target-owner

## Drift Route

role:fixture-map-owner

## Evidence

- CAL-DEFINITION-CANDIDATE-SET-CTX06-REFERENCE-NORMALIZATION-0002
- CAL-DECISION-0026-CTX06-REFERENCE-NORMALIZATION-DEFINITION-PROMOTION

## Residue

- fixture-only-no-relationship-selection
- artifact-type-v2-admission-required

## Claim ceiling

This fixture proves only Context Map/v2 representation, relation-ownership, and projection mechanics. It is not a real or admitted map.
