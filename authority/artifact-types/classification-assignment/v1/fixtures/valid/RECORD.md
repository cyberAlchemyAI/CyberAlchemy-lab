<!-- GENERATED FILE: canonical data is record.json. -->

# Classification Assignment fixture

- Identity: `classification-assignment:example-001`
- Kind: `classification-assignment`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "action_ref": "agent-action:create-instance",
  "axis_ref": "axis:actor-kind",
  "basis": "owner-declared",
  "effective_period": "session:lab-model-review-001",
  "evidence_refs": [
    "evidence:session-lifecycle"
  ],
  "implementation_ref": "implementation:codex-agent",
  "method_ref": "method:classification-review",
  "scheme_version_ref": "classification-scheme:agent-operational@1",
  "status": "active",
  "subject_ref": "agent-instance:lab-model-review-001",
  "subject_version_ref": "agent-instance:lab-model-review-001@1",
  "value_ref": "classification-value:machine-agent"
}
```

## Declared relation roles

- `target` on `relation.challenges` with `challenge-event` `challenge-event:example-001`

## Claim ceiling

Realistic Classification Assignment example for candidate review only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
