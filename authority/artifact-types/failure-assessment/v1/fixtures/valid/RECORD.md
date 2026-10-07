<!-- GENERATED FILE: canonical data is record.json. -->

# Failure Assessment fixture

- Identity: `failure-assessment:example-001`
- Kind: `failure-assessment`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "cause_hypothesis_refs": [
    "hypothesis:coverage-check-missing"
  ],
  "containment_posture": "contained",
  "impact_posture": "bounded",
  "mode_assignment_ref": "classification:lab-model-omission/mode@1",
  "mode_posture": "proposed",
  "occurrence_posture": "supported",
  "occurrence_ref": "failure-occurrence:lab-model-omission-001",
  "recovery_posture": "recovered-with-residue",
  "uncertainty_refs": [
    "uncertainty:generalization"
  ]
}
```

## Declared relation roles

- `target` on `relation.challenges` with `challenge-event` `challenge-event:example-001`

## Claim ceiling

Realistic Failure Assessment example for candidate review only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
