<!-- GENERATED FILE: canonical data is record.json. -->

# Agent Session fixture

- Identity: `agent-session:example-001`
- Kind: `agent-session`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "agent_instance_ref": "agent-instance:lab-model-review-001",
  "assignment_ref": "agent-assignment:complete-lab-model",
  "authority_envelope_ref": "delegation:candidate-materialization",
  "budget_refs": [
    "budget:bounded-task"
  ],
  "context_view_ref": "context-view:lab-model-cut-120",
  "event_cursor": "cursor:120",
  "input_refs": [
    "intent:complete-lab-model"
  ],
  "ontology_view_ref": "ontology-view:lab-model-cut-120",
  "policy_refs": [
    "policy:owner-review-required"
  ],
  "session_memory": {
    "expires_with_session": true,
    "selected_input_refs": [
      "context-view:lab-model-cut-120"
    ],
    "unresolved_questions": [
      "owner-admission-decision"
    ],
    "working_record_refs": [
      "working:audit-counts"
    ]
  },
  "termination_state": "active"
}
```

## Declared relation roles

- `source` on `relation.consumes-view` with `context-view` `context-view:example-001`

## Claim ceiling

Realistic Agent Session example for candidate review only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
