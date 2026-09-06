<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Artifact Type Registry Fixture

- Identity: `cal.registry.artifact-types.fixture`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Claim Ceiling**: `Fixture only; it does not create a live registry or alter lifecycle state.`
### Entries

```json
[
  {
    "admission_decision_ref": "CAL-DECISION-0030-CML07-S2-IDENTITY-ARTIFACT-TYPES-V1",
    "artifact_path": "authority/artifact-types/product-identity/v1/artifact.json",
    "artifact_sha256": "0823d26847ee93ae9326a059da7867225719ee7d8422ba19e06a31a572cdd4f9",
    "artifact_type_ref": "cal.artifact-type.product-identity/v1",
    "instance_discriminator": {
      "path": "/schema_version",
      "value": "cyberalchemy-lab-product-identity/v1"
    },
    "lifecycle_state": "admitted-current",
    "schema_path": "authority/artifact-types/product-identity/v1/schema.json",
    "schema_selector": null,
    "schema_sha256": "5298613ded703549f1c7ed082d0c46e8baea88f22bacf6fdeea307230c71decd",
    "semantic_definition_refs": [
      "cal.definition.product@1.0.0-candidate.1"
    ],
    "semantic_kind": "product-identity"
  }
]
```

- **Owner Ref**: `role:artifact-type-owner`
- **Schema Version**: `cyberalchemy-lab-artifact-type-registry/v1`
### Source Direction

```json
{
  "canonical": "registry.json",
  "generator_ref": "cal.generator.artifact-surface/v1",
  "human_projection": "REGISTRY.md",
  "projection_policy": "generated-only"
}
```

- **Version**: `1.0.0-candidate.1`

## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
