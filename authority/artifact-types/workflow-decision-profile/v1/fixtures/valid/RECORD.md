<!-- GENERATED FILE: canonical data is record.json. -->

# Workflow Decision Profile fixture

- Identity: `workflow-decision-profile:example-001`
- Kind: `workflow-decision-profile`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "allowed_checkpoint_kinds": [
    "final-review"
  ],
  "decision_mode": "single",
  "default_checkpoint_kind": "final-review",
  "exact_target_required": true,
  "invalidation_conditions": [
    "unmaterialized-target",
    "authority-owner-change",
    "new-external-effect"
  ],
  "none_mode_authority_basis_refs": [],
  "post_decision_continuation_limit": 1,
  "workflow_type_ref": "workflow-type:governed-repository-change"
}
```

## Declared relation roles

- `source` on `relation.governed-by` with `policy` `policy:example-001`

## Claim ceiling

Realistic Workflow Decision Profile example for candidate review only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
