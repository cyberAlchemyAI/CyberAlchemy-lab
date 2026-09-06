<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Canonical Package Manifest Fixture

- Identity: `cal.package.fixture.ontology-product`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Aggregate Ref**: `CA2-PRODUCT-ONTOLOGY/v1`
- **Claim Ceiling**: `Fixture package declaration only; it does not migrate or admit the Ontology Product.`
- **Lifecycle Owner Ref**: `role:ontology-product-owner`
### Nested Packages

```json
[]
```

- **Package Root**: `product/products/ontology/v1`
- **Schema Version**: `cyberalchemy-lab-canonical-package-manifest/v1`
### Source Direction

```json
{
  "canonical": "package.json",
  "generator_ref": "cal.generator.artifact-surface/v1",
  "human_projection": "PACKAGE.md",
  "projection_policy": "generated-only"
}
```

### Surface Entries

```json
[
  {
    "artifact_type_ref": "cal.artifact-type.canonical-package-manifest/v1",
    "path": "package.json",
    "resolution_count": 1,
    "role": "canonical-instance"
  },
  {
    "artifact_type_ref": "cal.artifact-type.product-identity/v1",
    "path": "product.json",
    "resolution_count": 1,
    "role": "canonical-instance"
  },
  {
    "artifact_type_ref": null,
    "path": "PRODUCT.md",
    "role": "generated-projection"
  },
  {
    "artifact_type_ref": null,
    "path": "contracts/ontology-package.schema.json",
    "role": "declared-component"
  },
  {
    "artifact_type_ref": null,
    "path": "fixtures",
    "role": "fixture"
  },
  {
    "artifact_type_ref": null,
    "path": "runtime/target",
    "role": "transient-state"
  }
]
```

- **Unit Of Change**: `Ontology Product v1 candidate package`
- **Version**: `1.0.0-candidate.1`

## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
