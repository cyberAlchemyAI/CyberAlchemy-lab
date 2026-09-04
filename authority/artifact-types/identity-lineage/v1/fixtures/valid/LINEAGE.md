<!-- GENERATED FILE: canonical data is the sibling JSON fixture. -->

# Identity Lineage Fixture

- Identity: `fixture:lineage:craft`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical field projection

- **Schema Version**: `cyberalchemy-lab-identity-lineage/v1`
- **Version**: `1.0.0-candidate.1`
- **Name**: `DomainSpec v2 to Craft Product lineage`
### Semantic Definition Refs

```json
[
  "cal.definition.identity-lineage@1.0.0-candidate.1",
  "cal.definition.identity-carrier@1.0.0-candidate.1",
  "cal.definition.product@1.0.0-candidate.1"
]
```

- **Lineage Kind**: `same-product-renamed`
- **Subject Kind**: `product`
- **Predecessor Ref**: `legacy:product:domainspec-v2`
- **Predecessor Name**: `DomainSpec v2`
- **Successor Ref**: `fixture:product:craft`
- **Successor Name**: `Craft`
### Preserved Identity Assertions

```json
[
  "Product purpose continuity requires explicit evidence",
  "Renaming alone does not create a new Product"
]
```

### Changed Attributes

```json
[
  "Product display name",
  "Repository location"
]
```

### Evidence Refs

```json
[
  "fixture:evidence:craft-lineage"
]
```

- **Lineage Owner Ref**: `role:craft-product-owner`
- **Challenge Route**: `role:craft-product-owner`
- **Claim Ceiling**: `Fixture only; lineage evidence does not admit either endpoint or infer context lineage.`

## Projection boundary

This document is generated from the canonical machine fixture and adds no identity, relation, lifecycle, conformance, or authority field.
