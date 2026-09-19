<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Withdrawal Record Fixture

- Identity: `WITHDRAWAL-PRESERVATION-D70-D81-001`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Artifact Type Ref**: `cal.artifact-type.withdrawal-record/v1`
- **Challenge Route**: `route:withdrawal-lineage-review`
- **Claim Ceiling**: `Exact recorded reservations and allocation collision checks only; no new withdrawal, successor authority or global allocation permission.`
### Normalization

```json
{
  "path": "docs/normalizations/0001-definition-migration-model/normalization.json",
  "sha256": "c1021431d8d33ee1e7c8bc6caf3ca0e89cba20e840a9360a2cefbff240cb5016"
}
```

- **Owner Route**: `route:migration-owner`
- **Profile**: `candidate:normalized-withdrawal-reservation/v1`
- **Reason**: `Preserve every identifier already listed as withdrawn in the accepted normalization; never recycle its legacy name.`
### Reservations

```json
[
  {
    "permanently_reserved": true,
    "retired_id": "CAV2-D70",
    "successor_id": "KEP-D1"
  },
  {
    "permanently_reserved": true,
    "retired_id": "CAV2-D71",
    "successor_id": "KEP-D2"
  },
  {
    "permanently_reserved": true,
    "retired_id": "CAV2-D72",
    "successor_id": "KEP-D3"
  },
  {
    "permanently_reserved": true,
    "retired_id": "CAV2-D73",
    "successor_id": "KEP-D4"
  },
  {
    "permanently_reserved": true,
    "retired_id": "CAV2-D74",
    "successor_id": "KEP-D5"
  },
  {
    "permanently_reserved": true,
    "retired_id": "CAV2-D75",
    "successor_id": "KEP-D6"
  },
  {
    "permanently_reserved": true,
    "retired_id": "CAV2-D76",
    "successor_id": "KEP-D7"
  },
  {
    "permanently_reserved": true,
    "retired_id": "CAV2-D77",
    "successor_id": "KEP-D8"
  },
  {
    "permanently_reserved": true,
    "retired_id": "CAV2-D78",
    "successor_id": "KEP-D9"
  },
  {
    "permanently_reserved": true,
    "retired_id": "CAV2-D79",
    "successor_id": "KEP-D10"
  },
  {
    "permanently_reserved": true,
    "retired_id": "CAV2-D80",
    "successor_id": "KEP-D11"
  },
  {
    "permanently_reserved": true,
    "retired_id": "CAV2-D81",
    "successor_id": "KEP-D12"
  }
]
```

- **Schema Version**: `cal-withdrawal-record/v1`
- **Scope Ref**: `scope:normalized-legacy-identifier-reservation`
### Source Direction

```json
{
  "canonical": "withdrawal-record.json",
  "human_projection": "WITHDRAWAL-RECORD.md",
  "projection_policy": "generated-only"
}
```


## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
