<!-- GENERATED FILE: canonical data is the sibling JSON fixture. -->

# Product Identity Fixture

- Identity: `fixture:product:craft`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical field projection

- **Schema Version**: `cyberalchemy-lab-product-identity/v1`
- **Version**: `1.0.0-candidate.1`
- **Name**: `Craft`
### Semantic Definition Refs

```json
[
  "cal.definition.product@1.0.0-candidate.1",
  "cal.definition.identity-carrier@1.0.0-candidate.1"
]
```

- **Purpose**: `Provide governed development workflows as a Product distinct from its coordinating Project and applied Method.`
### Scope

```json
{
  "excludes": [
    "Project coordination",
    "Method definition",
    "Bounded Context inference"
  ],
  "includes": [
    "Product meaning and outcomes"
  ]
}
```

- **Semantic Owner Ref**: `role:craft-product-owner`
- **Lineage Ref**: `fixture:lineage:craft`
### Evidence Refs

```json
[
  "fixture:evidence:craft-product"
]
```

- **Challenge Route**: `role:craft-product-owner`
- **Claim Ceiling**: `Fixture only; it does not admit a Product or establish implementation conformance.`

## Projection boundary

This document is generated from the canonical machine fixture and adds no identity, relation, lifecycle, conformance, or authority field.
