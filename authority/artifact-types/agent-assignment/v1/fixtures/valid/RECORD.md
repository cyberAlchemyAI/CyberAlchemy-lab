<!-- GENERATED FILE: canonical data is record.json. -->

# Agent Assignment fixture

- Identity: `agent-assignment:example-001`
- Kind: `agent-assignment`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "eligible_agent_ref": "agent-instance:lab-model-review-001",
  "expected_output_refs": [
    "artifact-type-candidates:definition-complete"
  ],
  "intent_ref": "intent:complete-lab-model",
  "owner_ref": "principal:lab-owner",
  "period": "session:lab-model-review-001",
  "project_ref": "project:lab-semantic-governance",
  "stop_conditions": [
    "candidate-validation-pass",
    "authority-boundary-reached"
  ],
  "work_ref": "work:materialize-carriers"
}
```

## Declared relation roles

- `source` on `relation.addresses-intent` with `intent` `intent:example-001`

## Claim ceiling

Realistic Agent Assignment example for candidate review only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
