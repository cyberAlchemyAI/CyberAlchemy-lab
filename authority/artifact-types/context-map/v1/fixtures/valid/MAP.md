<!-- GENERATED FILE: edit map.json and rerun generator.py. -->

# Context Map: fixture.context-map.example

> Generated from `map.json`; this view is not canonical.

- Identity: `fixture.context-map.example`
- Version: `1.0.0-fixture`
- Status: `candidate-unadmitted`
- Artifact type: `cal.artifact-type.context-map/v1`
- Semantic kind: `context-map`
- Authority effect: `none`

## Context Refs

- fixture.context.source/v1
- fixture.context.target/v1

## Relationships

```json
[
  {
    "authority_boundary": "No authority transfers.",
    "contract_refs": [],
    "direction": "source-to-target",
    "information_boundary": "Only fixture payloads cross.",
    "owner_refs": [
      "fixture:role:map-owner"
    ],
    "relationship_id": "fixture.relationship.source-target",
    "relationship_kind_ref": "candidate:relationship.unselected/v1",
    "source_context_ref": "fixture.context.source/v1",
    "target_context_ref": "fixture.context.target/v1",
    "translation_refs": []
  }
]
```

## Owner Refs

- fixture:role:map-owner

## Drift Route

fixture:route:map-drift

## Evidence

- fixture:evidence:map

## Residue

- fixture:residue:relationship-pattern-unselected

## Claim ceiling

Fixture only; it does not select or admit a real inter-context relationship.
