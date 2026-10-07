<!-- GENERATED FILE: canonical data is record.json. -->

# Decision Checkpoint fixture

- Identity: `decision-checkpoint:example-001`
- Kind: `decision-checkpoint`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "checkpoint_kind": "final-review",
  "closed_at": null,
  "decision_bundle_ref": "decision-bundle:governance-transaction-surface-001",
  "opened_at": "2026-10-06T00:00:00-03:00",
  "presentation_state": "pending",
  "resolved_preference_ref": "user-decision-preference:lab-owner-final-review",
  "workflow_instance_ref": "workflow:governance-transaction-surface-001",
  "workflow_profile_ref": "workflow-decision-profile:lab-governance-single-checkpoint"
}
```

## Declared relation roles

- `source` on `relation.governed-by` with `policy` `policy:example-001`

## Claim ceiling

Realistic Decision Checkpoint example for candidate review only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
