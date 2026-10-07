<!-- GENERATED FILE: canonical data is record.json. -->

# Incident fixture

- Identity: `incident:example-001`
- Kind: `incident`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "accountable_principal_ref": "principal:lab-owner",
  "closure_state": "open",
  "communication_refs": [
    "feedback:owner-correction"
  ],
  "containment_refs": [
    "agent-action:pause-admission"
  ],
  "decision_refs": [
    "decision:pending-model-admission"
  ],
  "impact_summary": "Complete-model review required correction.",
  "occurrence_refs": [
    "failure-occurrence:lab-model-omission-001"
  ],
  "recovery_refs": [
    "agent-action:revise-model"
  ],
  "residue_refs": [
    "residue:owner-review-required"
  ],
  "timeline_refs": [
    "event:owner-correction",
    "event:model-revision"
  ]
}
```

## Declared relation roles

- `source` on `relation.affects` with `agent-capability` `agent-capability:example-001`

## Claim ceiling

Realistic Incident example for candidate review only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
