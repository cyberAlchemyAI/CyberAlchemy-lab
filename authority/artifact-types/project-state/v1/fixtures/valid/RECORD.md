<!-- GENERATED FILE: canonical data is record.json. -->

# Project State fixture

- Identity: `project-state:example-001`
- Kind: `project-state`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "artifact_refs": [
    "authority/definitions/registry.json"
  ],
  "cursor": "cursor:120",
  "decision_refs": [
    "CAL-DECISION-0065-INTEGRATED-LAB-DEFINITION-MODEL-ADMISSION"
  ],
  "governance_history_ref": "governance-event-history:lab",
  "project_ref": "project:lab-semantic-governance",
  "semantic_history_ref": "semantic-event-history:lab",
  "state_digest": "sha256:project-state-example"
}
```

## Declared relation roles

- `target` on `relation.challenges` with `challenge-event` `challenge-event:example-001`

## Claim ceiling

Realistic Project State example for candidate review only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
