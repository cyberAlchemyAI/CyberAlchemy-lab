<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Method Fixture

- Identity: `EXAMPLE-REVIEW-SCHEMA-CHANGE-001`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

### Actions

```json
[
  {
    "action_id": "inspect",
    "gate_refs": [
      "shape-check"
    ],
    "instruction": "Inspect the proposal with its exact bound validator; preserve the assessment.",
    "reads": [
      "proposal"
    ],
    "role_ref": "role:checker",
    "writes": [
      "assessment"
    ]
  },
  {
    "action_id": "review",
    "gate_refs": [
      "review-check"
    ],
    "instruction": "Review the assessment and identify missing consumers and migration obligations.",
    "reads": [
      "proposal",
      "assessment"
    ],
    "role_ref": "role:reviewer",
    "writes": [
      "review"
    ]
  }
]
```

- **Artifact Type Ref**: `cal.artifact-type.method/v1`
- **Boundary**: `Specification only; no execution, actor authority, consumer completeness or adoption is established.`
- **Claim Ceiling**: `Static procedure coherence only. Instructions and gate conditions are text; no execution or successful outcome is inferred.`
### Evidence

```json
[
  {
    "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0010-schema-change-carrier/receipts/demonstration.json",
    "sha256": "d0b1811c532a0336c634064cedf6add16274022f4138f700086cee924e5f34d3"
  }
]
```

### Gates

```json
[
  {
    "condition": "The validator accepts exact bindings and supplied regression expectations.",
    "gate_id": "shape-check",
    "on_failure": "stop-and-record-residue",
    "role_ref": "role:checker",
    "subject_refs": [
      "assessment"
    ]
  },
  {
    "condition": "Each unresolved obligation has a named owner and continuation route.",
    "gate_id": "review-check",
    "on_failure": "stop-and-record-residue",
    "role_ref": "role:reviewer",
    "subject_refs": [
      "review"
    ]
  }
]
```

### Inputs

```json
[
  {
    "description": "Exact schema change record and its bound inputs.",
    "slot_id": "proposal"
  }
]
```

### Outputs

```json
[
  {
    "description": "Compatibility assessment for supplied witnesses.",
    "slot_id": "assessment"
  },
  {
    "description": "Review findings and unresolved consumer obligations.",
    "slot_id": "review"
  }
]
```

- **Owner Ref**: `role:method-owner`
- **Purpose**: `Turn a proposed schema change into reviewable evidence and unresolved obligations.`
- **Recomposition Rule**: `Version the Method and review affected gates whenever fixed fields change. Retain earlier evidence and open residue.`
### Residue Rule

```json
{
  "instruction": "Record failure, affected inputs and missing evidence; stop before claiming completion.",
  "owner_ref": "role:reviewer",
  "route_ref": "route:schema-owner-review"
}
```

### Reuse

```json
{
  "fixed_fields": [
    "inputs",
    "actions",
    "roles",
    "gates",
    "outputs",
    "evidence",
    "residue_rule",
    "validation_rule",
    "recomposition_rule",
    "boundary"
  ],
  "specializable_fields": [
    "scope_ref"
  ],
  "specialization_rule": "Bind an exact Method version to the chosen scope in a separate Method Binding; preserve open residue."
}
```

### Roles

```json
[
  "role:checker",
  "role:reviewer"
]
```

- **Schema Version**: `cal-method-record/v1`
- **Scope Ref**: `scope:schema-change-review`
### Source Direction

```json
{
  "canonical": "method-record.json",
  "human_projection": "METHOD.md",
  "projection_policy": "generated-only"
}
```

### Validation Rule

```json
{
  "completion_condition": "Both checks have evidence of success and remaining obligations are recorded; completion does not authorize adoption.",
  "required_gate_refs": [
    "shape-check",
    "review-check"
  ]
}
```


## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
