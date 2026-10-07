<!-- GENERATED FILE: canonical data is record.json. -->

# User Decision Preference fixture

- Identity: `user-decision-preference:example-001`
- Kind: `user-decision-preference`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "invalidation_conditions": [
    "profile-no-longer-allows-final-review",
    "owner-withdrawal"
  ],
  "preferred_checkpoint_kind": "final-review",
  "profile_ref": "workflow-decision-profile:lab-governance-single-checkpoint",
  "scope_kind": "workflow-type",
  "scope_ref": "workflow-type:governed-repository-change",
  "status": "active",
  "user_ref": "principal:lab-owner"
}
```

## Declared relation roles

- `source` on `relation.governed-by` with `policy` `policy:example-001`

## Claim ceiling

Realistic User Decision Preference example for candidate review only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
