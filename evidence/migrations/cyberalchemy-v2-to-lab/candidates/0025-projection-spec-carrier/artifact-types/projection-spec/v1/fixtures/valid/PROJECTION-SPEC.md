<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Projection Specification Fixture

- Identity: `EXAMPLE-RECEIPT-SUMMARY-001`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Artifact Type Ref**: `cal.artifact-type.projection-spec/v1`
- **Challenge Route**: `route:projection-drift-review`
- **Claim Ceiling**: `Deterministic selected-field view only; no source authority promotion, semantic completeness or reverse editing.`
### Fields

```json
[
  {
    "source_field": "receipt_id",
    "view_field": "receipt_id"
  },
  {
    "source_field": "reported_result",
    "view_field": "reported_result"
  },
  {
    "source_field": "exit_code",
    "view_field": "exit_code"
  }
]
```

### Omissions

```json
[
  {
    "reason": "Excluded from the compact view; consult the exact bound Receipt source for this field.",
    "source_field": "artifact_type_ref"
  },
  {
    "reason": "Excluded from the compact view; consult the exact bound Receipt source for this field.",
    "source_field": "authority_effect"
  },
  {
    "reason": "Excluded from the compact view; consult the exact bound Receipt source for this field.",
    "source_field": "challenge_route"
  },
  {
    "reason": "Excluded from the compact view; consult the exact bound Receipt source for this field.",
    "source_field": "claim_ceiling"
  },
  {
    "reason": "Excluded from the compact view; consult the exact bound Receipt source for this field.",
    "source_field": "execution_snapshot"
  },
  {
    "reason": "Excluded from the compact view; consult the exact bound Receipt source for this field.",
    "source_field": "implementation"
  },
  {
    "reason": "Excluded from the compact view; consult the exact bound Receipt source for this field.",
    "source_field": "input"
  },
  {
    "reason": "Excluded from the compact view; consult the exact bound Receipt source for this field.",
    "source_field": "limitations"
  },
  {
    "reason": "Excluded from the compact view; consult the exact bound Receipt source for this field.",
    "source_field": "operation_ref"
  },
  {
    "reason": "Excluded from the compact view; consult the exact bound Receipt source for this field.",
    "source_field": "owner_route"
  },
  {
    "reason": "Excluded from the compact view; consult the exact bound Receipt source for this field.",
    "source_field": "profile"
  },
  {
    "reason": "Excluded from the compact view; consult the exact bound Receipt source for this field.",
    "source_field": "python_version"
  },
  {
    "reason": "Excluded from the compact view; consult the exact bound Receipt source for this field.",
    "source_field": "schema_version"
  },
  {
    "reason": "Excluded from the compact view; consult the exact bound Receipt source for this field.",
    "source_field": "scope_ref"
  },
  {
    "reason": "Excluded from the compact view; consult the exact bound Receipt source for this field.",
    "source_field": "source_direction"
  },
  {
    "reason": "Excluded from the compact view; consult the exact bound Receipt source for this field.",
    "source_field": "status"
  },
  {
    "reason": "Excluded from the compact view; consult the exact bound Receipt source for this field.",
    "source_field": "stderr"
  },
  {
    "reason": "Excluded from the compact view; consult the exact bound Receipt source for this field.",
    "source_field": "stdout"
  }
]
```

- **Owner Route**: `route:projection-owner`
- **Profile**: `candidate:json-field-view/v1`
- **Schema Version**: `cal-projection-spec-record/v1`
- **Scope Ref**: `scope:receipt-summary`
### Source

```json
{
  "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0024-receipt-carrier/artifact-types/receipt/v1/fixtures/valid/receipt-record.json",
  "sha256": "7955cb04c03c03a5d0c0e7d033328a7553611ae1db5d9ac23bc921086e97fa2a"
}
```

### Source Direction

```json
{
  "canonical": "projection-spec-record.json",
  "human_projection": "PROJECTION-SPEC.md",
  "projection_policy": "generated-only"
}
```

- **Update Policy**: `regenerate-from-bound-source`
- **View Authority**: `none`

## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
