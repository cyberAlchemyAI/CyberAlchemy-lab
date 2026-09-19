<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Schema Fixture

- Identity: `CAL-ARTIFACT-OWNER-GRAPH-001`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Artifact Type Ref**: `cal.artifact-type.schema/v1`
- **Claim Ceiling**: `Structural example only. An owned-by edge is not proof that the named person or role has authority.`
### Connection Rules

```json
[
  {
    "max_per_source": 1,
    "max_per_target": null,
    "min_per_source": 1,
    "min_per_target": 0,
    "relation_ref": "owned-by",
    "source_kind": "artifact",
    "target_kind": "owner"
  }
]
```

### Constraints

```json
[
  {
    "closed_fields": true,
    "fields": [
      {
        "name": "title",
        "required": true,
        "value_type": "string"
      }
    ],
    "kind_ref": "artifact"
  },
  {
    "closed_fields": true,
    "fields": [
      {
        "name": "name",
        "required": true,
        "value_type": "string"
      }
    ],
    "kind_ref": "owner"
  }
]
```

### Kinds

```json
[
  "artifact",
  "owner"
]
```

- **Owner Ref**: `role:schema-owner`
### Path Equations

```json
[]
```

- **Profile**: `candidate:finite-typed-graph/v1`
### Relations

```json
[
  "owned-by"
]
```

### Relative Level

```json
{
  "occupant_level_ref": "level:artifact-owner-records",
  "schema_level_ref": "level:artifact-owner-schema"
}
```

- **Schema Version**: `cyberalchemy-lab-schema-carrier/v1`
- **Scope Ref**: `scope:artifact-owner-structure`
### Source Direction

```json
{
  "canonical": "schema-record.json",
  "human_projection": "SCHEMA.md",
  "projection_policy": "generated-only"
}
```


## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
