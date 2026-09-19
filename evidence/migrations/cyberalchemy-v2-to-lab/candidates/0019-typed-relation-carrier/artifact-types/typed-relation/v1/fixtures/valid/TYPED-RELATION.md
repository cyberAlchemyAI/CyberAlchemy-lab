<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Typed Relation Fixture

- Identity: `EXAMPLE-GATE-DEFINITION-BINDING-001`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Artifact Type Ref**: `cal.artifact-type.typed-relation/v1`
- **Challenge Route**: `route:artifact-definition-binding-review`
- **Claim Ceiling**: `Exact directed binding checks only; owner-local meaning, relation-kind adoption and endpoint promotion remain unproven.`
### Declared Effect

```json
{
  "category": "validation",
  "description": "Require the Gate artifact to retain its exact declared Definition binding before relying on the link."
}
```

- **Direction**: `source-to-target`
### Evidence

```json
[
  {
    "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0018-gate-carrier/receipts/validation.json",
    "sha256": "e20c41424adad6c49905e7dc332a0b700c0dd7202dd0eb61cdfb2858db82c691"
  }
]
```

- **Owner Route**: `route:artifact-type-owner`
- **Profile**: `candidate:artifact-definition-binding/v1`
- **Relation Kind Ref**: `candidate:binds-definition/v1`
- **Schema Version**: `cal-typed-relation-record/v1`
- **Scope Ref**: `scope:lab-candidate-definition-bindings`
### Source

```json
{
  "binding": {
    "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0018-gate-carrier/artifact-types/gate/v1/artifact.json",
    "sha256": "9fd554c67bd94f06f698c5d951c853df130bbeaeeae63d86a779d17f08a86359"
  },
  "object_ref": "cal.artifact-type.gate/v1"
}
```

### Source Direction

```json
{
  "canonical": "typed-relation-record.json",
  "human_projection": "TYPED-RELATION.md",
  "projection_policy": "generated-only"
}
```

### Target

```json
{
  "binding": {
    "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/gate/v1/definition.json",
    "sha256": "29e494b465b013fda1e0ed9eeb6dc8fc17126eb132e15bf153b58db6075e2b97"
  },
  "object_ref": "cal.definition.gate@1.0.0-candidate.1"
}
```


## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
