<!-- GENERATED FILE: canonical data is record.json. -->

# Feedback Record fixture

- Identity: `feedback-record:example-001`
- Kind: `feedback-record`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "context_ref": "task:complete-lab-model",
  "feedback_kind": "correction",
  "interpretation_posture": "explicit-requirement",
  "recorded_at": "2026-10-05T00:00:00-03:00",
  "source_ref": "principal-reference:lab-owner",
  "statement": "Include Agent, memory ownership, classifications, and failure modes.",
  "target_ref": "review:lab-model"
}
```

## Declared relation roles

- `target` on `relation.challenges` with `challenge-event` `challenge-event:example-001`

## Claim ceiling

Realistic Feedback Record example for candidate review only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
