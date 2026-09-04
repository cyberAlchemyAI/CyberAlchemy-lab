<!-- Generated from semantic-model.json. Do not edit. -->

# Ontology-as-a-Product semantic model

```text
Product: CA2-PRODUCT-ONTOLOGY
  includes capability: CA2-CAP-ONTOLOGY-TYPED-MEANING
    produces output: CA2-OUTPUT-ONTOLOGY-PACKAGE

Product Ontology: cav2.ontology-product
  represents: CA2-PRODUCT-ONTOLOGY

Craft: receives migration work only
```

## Subjects

### `CA2-PRODUCT-ONTOLOGY`

- Role: `product-identity`
- Kind: `cal.definition.product@1.0.0-candidate.1`
- Meaning: The durable Product identity whose value promise concerns building and using project-owned governed ontologies.

### `cav2.ontology-product`

- Role: `product-ontology-scaffold`
- Kind: `CAV2-D19`
- Meaning: A business-domain ontology that models the Product's meaning, participants, problems, capabilities, outputs, outcomes, sources, and residue.

### `CA2-OUTPUT-ONTOLOGY-PACKAGE`

- Role: `core-value-bearing-output`
- Kind: `product-output`
- Meaning: The minimum durable Product output: an independently validatable, source-bound package of nodes, relations, residue, schema, and evidence.

### `CA2-PRODUCT-CRAFT`

- Role: `work-receiver`
- Kind: `cal.definition.product@1.0.0-candidate.1`
- Meaning: Craft receives and coordinates migration work; it is not the migrated Product, Product Ontology, ontology-package output, Bounded Context, or meaning owner.

## Generated labels

### Ontology-as-a-Product

- Derivation: Product(CA2-PRODUCT-ONTOLOGY) includes_capability TypedMeaning; TypedMeaning produces OntologyPackage(CA2-OUTPUT-ONTOLOGY-PACKAGE).
- Purpose: Readable architecture label for the existing Product-capability-output graph.
- Canonical axis: `false`
- Forbidden: Must not become a second Product ID, Product subtype, artifact kind, lifecycle axis, or authority source.

### Product Ontology

- Derivation: Ontology(cav2.ontology-product) represents Product(CA2-PRODUCT-ONTOLOGY).
- Purpose: Readable role label for the ontology that describes the Product.
- Canonical axis: `false`
- Forbidden: Must not be treated as the Product identity, the delivered ontology package, runtime evidence, or source authority.

## Non-collapse invariants

- `CA2-PRODUCT-ONTOLOGY != cav2.ontology-product`
- `CA2-PRODUCT-ONTOLOGY != CA2-OUTPUT-ONTOLOGY-PACKAGE`
- `cav2.ontology-product != CA2-OUTPUT-ONTOLOGY-PACKAGE`
- `CA2-PRODUCT-CRAFT != CA2-PRODUCT-ONTOLOGY`
- `A generated label cannot introduce a canonical classification axis.`
- `A Product Ontology may describe a Product without becoming that Product or its delivered output.`
- `A runtime may operate ontology packages without owning their meaning or becoming the Product.`

## Practical distinction

- Product: The durable Product identity whose value promise concerns building and using project-owned governed ontologies.
- Product Ontology: A business-domain ontology that models the Product's meaning, participants, problems, capabilities, outputs, outcomes, sources, and residue.
- Product output: The minimum durable Product output: an independently validatable, source-bound package of nodes, relations, residue, schema, and evidence.

## Claim ceiling

This candidate separates Product identity, Product Ontology scaffold, ontology-package output, Craft work reception, contexts, capabilities, and runtimes. It does not create or admit a Definition, Product, ontology package, context relation, implementation, approval, or authority effect.
