<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Residue Fixture

- Identity: `EXAMPLE-PROJECTION-LOSS-001`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Artifact Type Ref**: `cal.artifact-type.residue/v1`
- **Claim Ceiling**: `Exact field-preservation remainder only; no semantic equivalence, actual operation execution, treatment completion or promotion.`
- **Closure Condition**: `Supply a revised representation preserving all required fields and an owner-reviewed closure record.`
### Observed Remainder

```json
[
  {
    "field": "meaning",
    "issue": "missing"
  },
  {
    "field": "owner",
    "issue": "missing"
  }
]
```

- **Owner Route**: `route:representation-owner`
### Preservation Condition

```json
{
  "description": "Preserve id, owner and meaning fields without changing their JSON values.",
  "required_fields": [
    "id",
    "owner",
    "meaning"
  ]
}
```

- **Profile**: `candidate:json-field-preservation/v1`
- **Residue Type**: `representation-loss`
### Result

```json
{
  "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0022-residue-carrier/examples/result.json",
  "sha256": "a1402773c7ca833a676496524c2365e2869eb55ebb299438dc0a059a50b1a3d0"
}
```

- **Schema Version**: `cal-residue-record/v1`
- **Scope Ref**: `scope:example-json-projection`
### Source

```json
{
  "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0022-residue-carrier/examples/source.json",
  "sha256": "9670a878b211e1dc6dd31b917b5efefd5b312cfc06a3d3155f13cf930793707f"
}
```

### Source Direction

```json
{
  "canonical": "residue-record.json",
  "human_projection": "RESIDUE.md",
  "projection_policy": "generated-only"
}
```

- **Source Operation**: `example:project-record-to-id`
- **Treatment**: `repair`
- **Treatment Route**: `route:projection-repair-review`

## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
