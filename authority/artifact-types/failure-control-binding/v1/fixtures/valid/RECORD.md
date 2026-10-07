<!-- GENERATED FILE: canonical data is record.json. -->

# Failure Control Binding fixture

- Identity: `failure-control-binding:example-001`
- Kind: `failure-control-binding`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "control_subject_ref": "validator:definition-carrier-coverage",
  "effectiveness_evidence_refs": [],
  "execution_evidence_refs": [
    "receipt:coverage-audit-pass"
  ],
  "failure_mode_ref": "failure-mode:complete-model-layer-omission@1",
  "installation_posture": "candidate",
  "owner_ref": "role:artifact-type-owner",
  "primary_control_role": "detect"
}
```

## Declared relation roles

- `source` on `relation.controls` with `failure-mode` `failure-mode:example-001`

## Claim ceiling

Realistic Failure Control Binding example for candidate review only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
