<!-- GENERATED FILE: canonical data is record.json. -->

# Classification Scheme fixture

- Identity: `classification-scheme:example-001`
- Kind: `classification-scheme`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "axis_refs": [
    "axis:actor-kind",
    "axis:evidence-posture"
  ],
  "cardinality_rules": [
    "one-actor-kind-per-agent-instance"
  ],
  "compatibility_rules": [
    "machine-agent-requires-ephemeral-instance"
  ],
  "mapping_refs": [],
  "scheme_name": "Agent and operational record classification",
  "value_refs": [
    "classification-value:machine-agent",
    "classification-value:supported"
  ]
}
```

## Declared relation roles

- `target` on `relation.challenges` with `challenge-event` `challenge-event:example-001`

## Claim ceiling

Realistic Classification Scheme example for candidate review only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
