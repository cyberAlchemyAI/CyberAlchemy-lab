<!-- GENERATED FILE: canonical data is record.json. -->

# Communication Preference fixture

- Identity: `communication-preference:example-001`
- Kind: `communication-preference`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "audience_ref": "agent-profile:repository-model-review",
  "conditions": [
    "artifact-admission-review"
  ],
  "effective_period": "current-task",
  "override_rules": [
    "current-explicit-instruction-wins"
  ],
  "preference_statement": "Show the revised content with a realistic example before each decision.",
  "source_ref": "principal-reference:lab-owner",
  "strength": "explicit",
  "target_kind": "admission-review-response"
}
```

## Declared relation roles

- `target` on `relation.challenges` with `challenge-event` `challenge-event:example-001`

## Claim ceiling

Realistic Communication Preference example for candidate review only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
