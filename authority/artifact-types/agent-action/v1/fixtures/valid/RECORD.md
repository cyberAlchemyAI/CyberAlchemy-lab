<!-- GENERATED FILE: canonical data is record.json. -->

# Agent Action fixture

- Identity: `agent-action:example-001`
- Kind: `agent-action`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "action_kind": "materialize-candidate",
  "agent_instance_ref": "agent-instance:lab-model-review-001",
  "assignment_ref": "agent-assignment:complete-lab-model",
  "authority_evidence_refs": [
    "delegation:candidate-materialization"
  ],
  "implementation_refs": [
    "implementation:codex-agent"
  ],
  "input_refs": [
    "audit:definition-carrier-coverage"
  ],
  "output_refs": [
    "artifact-type:agent-session/v1"
  ],
  "posture": "completed",
  "receipt_refs": [
    "receipt:carrier-validation"
  ],
  "residue_refs": [
    "residue:owner-admission-required"
  ],
  "session_ref": "agent-session:lab-model-review-001",
  "tool_refs": [
    "tool:repository-patch"
  ]
}
```

## Declared relation roles

- `source` on `relation.produces` with `agent-reflection` `agent-reflection:example-001`

## Claim ceiling

Realistic Agent Action example for candidate review only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
