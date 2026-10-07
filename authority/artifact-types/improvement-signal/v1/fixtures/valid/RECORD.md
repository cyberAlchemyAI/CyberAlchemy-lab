<!-- GENERATED FILE: canonical data is record.json. -->

# Improvement Signal fixture

- Identity: `improvement-signal:example-001`
- Kind: `improvement-signal`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "deduplication_key": "qualifier-validation/missing-axis",
  "evidence_posture": "candidate",
  "improvement_target_ref": "none",
  "observed_window": "2026-10-05/2026-10-06",
  "routing_owner_ref": "role:workflow-owner",
  "signal_statement": "Repeated qualifier validation failures may indicate a missing shared validator rule.",
  "source_refs": [
    "receipt:qualifier-validation-failure-1",
    "receipt:qualifier-validation-failure-2"
  ]
}
```

## Declared relation roles

- `target` on `relation.challenges` with `challenge-event` `challenge-event:example-001`

## Claim ceiling

Realistic Improvement Signal example for candidate review only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
