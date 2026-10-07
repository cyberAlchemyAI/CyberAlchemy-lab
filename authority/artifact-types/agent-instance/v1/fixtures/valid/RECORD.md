<!-- GENERATED FILE: canonical data is record.json. -->

# Agent Instance fixture

- Identity: `agent-instance:example-001`
- Kind: `agent-instance`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "accountable_principal_ref": "principal:lab-owner",
  "agent_classification_assignment_ref": "classification:agent-instance/machine-agent",
  "capability_refs": [
    "agent-capability:candidate-authoring@1"
  ],
  "implementation_ref": "implementation:codex-agent",
  "profile_ref": "agent-profile:repository-model-review@1",
  "session_ref": "agent-session:lab-model-review-001",
  "started_at": "2026-10-06T00:00:00-03:00",
  "terminated_at": "when-session-terminates"
}
```

## Declared relation roles

- `source` on `relation.profiled-by` with `agent-profile` `agent-profile:example-001`

## Claim ceiling

Realistic Agent Instance example for candidate review only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
