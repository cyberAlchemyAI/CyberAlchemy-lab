<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Canonical Package Manifest Fixture

- Identity: `cal.package.fixture.ontology-product`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Schema Version**: `cyberalchemy-lab-canonical-package-manifest/v1`
- **Version**: `1.0.0-candidate.1`
- **Aggregate Ref**: `CA2-PRODUCT-ONTOLOGY/v1`
- **Package Root**: `product/products/ontology/v1`
- **Lifecycle Owner Ref**: `role:ontology-product-owner`
- **Unit Of Change**: `Ontology Product v1 candidate package`
### Surface Entries

```json
[
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

### Nested Packages

```json
[]
```

### Source Direction

```json
{
  "canonical": "package.json",
  "generator_ref": "cal.generator.artifact-surface/v1",
  "human_projection": "PACKAGE.md",
  "projection_policy": "generated-only"
}
```

- **Claim Ceiling**: `Fixture package declaration only; it does not migrate or admit the Ontology Product.`

## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
