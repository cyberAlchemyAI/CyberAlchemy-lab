<!-- GENERATED FILE: canonical data is record.json. -->

# Intent Resolution fixture

- Identity: `intent-resolution:example-001`
- Kind: `intent-resolution`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "excluded_subject_refs": [
    "runtime:unapproved-cutover"
  ],
  "intent_ref": "intent:complete-lab-model",
  "owner_decision_ref": "decision:select-lab-model-work",
  "satisfaction_test_refs": [
    "test:all-definitions-realized",
    "test:all-relations-closed"
  ],
  "selected_subject_refs": [
    "project:lab-semantic-governance",
    "goal:complete-integrated-model"
  ]
}
```

## Declared relation roles

- `target` on `relation.challenges` with `challenge-event` `challenge-event:example-001`

## Claim ceiling

Realistic Intent Resolution example for candidate review only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
