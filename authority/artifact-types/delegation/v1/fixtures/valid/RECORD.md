<!-- GENERATED FILE: canonical data is record.json. -->

# Delegation fixture

- Identity: `delegation:example-001`
- Kind: `delegation`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "allowed_action_kinds": [
    "read-repository",
    "author-candidate",
    "run-validator"
  ],
  "approval_gate_refs": [
    "gate:owner-admission"
  ],
  "delegator_principal_ref": "principal:lab-owner",
  "effective_period": "session:lab-model-review-001",
  "eligible_agent_ref": "agent-instance:lab-model-review-001",
  "policy_refs": [
    "policy:no-implicit-admission"
  ],
  "redelegation_allowed": false,
  "revocation_state": "not-revoked",
  "scope_refs": [
    "project:lab-semantic-governance"
  ]
}
```

## Declared relation roles

- `target` on `relation.challenges` with `challenge-event` `challenge-event:example-001`

## Claim ceiling

Realistic Delegation example for candidate review only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
