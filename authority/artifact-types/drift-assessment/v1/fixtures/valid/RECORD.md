<!-- GENERATED FILE: canonical data is record.json. -->

# Drift Assessment fixture

- Identity: `drift-assessment:example-001`
- Kind: `drift-assessment`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "cause_posture": "unresolved",
  "comparison_time": "2026-10-06T00:00:00-03:00",
  "evidence_refs": [
    "source:runtime-lib",
    "source:README"
  ],
  "expected_version_ref": "runtime-source:f1b3f7",
  "mismatch_refs": [
    "mismatch:challenge-contract-implementation-claim"
  ],
  "observed_version_ref": "README:current",
  "remediation_authority_ref": "none",
  "severity_posture": "unassessed",
  "subject_ref": "README:challenge-contract-status"
}
```

## Declared relation roles

- `target` on `relation.challenges` with `challenge-event` `challenge-event:example-001`

## Claim ceiling

Realistic Drift Assessment example for candidate review only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
