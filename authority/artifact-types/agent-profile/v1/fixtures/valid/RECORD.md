<!-- GENERATED FILE: canonical data is record.json. -->

# Agent Profile fixture

- Identity: `agent-profile:example-001`
- Kind: `agent-profile`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "allowed_input_kinds": [
    "context-view",
    "ontology-view"
  ],
  "allowed_output_kinds": [
    "definition",
    "artifact-type",
    "typed-relation"
  ],
  "policy_refs": [
    "policy:owner-review-required"
  ],
  "profile_purpose": "Governed repository model review",
  "stop_conditions": [
    "assignment-complete",
    "authority-boundary-reached"
  ],
  "tool_class_refs": [
    "tool-class:repository-read",
    "tool-class:repository-write"
  ]
}
```

## Declared relation roles

- `source` on `relation.has-capability` with `agent-capability` `agent-capability:example-001`

## Claim ceiling

Realistic Agent Profile example for candidate review only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
