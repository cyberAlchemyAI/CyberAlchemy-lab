<!-- Generated from product-ontology/ontology.json. Do not edit. -->

# Product Ontology

- Ontology: `cal.product-ontology.ontology-as-product`
- Represents: `CA2-PRODUCT-ONTOLOGY`
- Role: `product-ontology-scaffold`
- Status: `test-candidate`
- Authority effect: `none`

## Product graph

| Node | Role | Type |
| --- | --- | --- |
| `CA2-PRODUCT-ONTOLOGY` | `product-identity` | `cal.definition.product@1.0.0-candidate.1` |
| `CA2-CAP-ONTOLOGY-TYPED-MEANING` | `product-capability` | `CAV2-D67` |
| `CA2-OUTPUT-ONTOLOGY-PACKAGE` | `core-value-bearing-output` | `product-output` |

| Relation | Type | Source | Target |
| --- | --- | --- | --- |
| `CA2-REL-ONTOLOGY-PRODUCT-INCLUDES-TYPED-MEANING` | `includes_capability` | `CA2-PRODUCT-ONTOLOGY` | `CA2-CAP-ONTOLOGY-TYPED-MEANING` |
| `CA2-REL-TYPED-MEANING-PRODUCES-PACKAGE` | `produces` | `CA2-CAP-ONTOLOGY-TYPED-MEANING` | `CA2-OUTPUT-ONTOLOGY-PACKAGE` |

## Non-collapse

- `CA2-PRODUCT-ONTOLOGY != cal.product-ontology.ontology-as-product`
- `CA2-PRODUCT-ONTOLOGY != CA2-OUTPUT-ONTOLOGY-PACKAGE`
- `cal.product-ontology.ontology-as-product != CA2-OUTPUT-ONTOLOGY-PACKAGE`

## Claim ceiling

This Product Ontology describes the Product test candidate. It is not the Product identity, the governed ontology-package output, source authority, runtime evidence, Product approval, or an admitted ontology.
