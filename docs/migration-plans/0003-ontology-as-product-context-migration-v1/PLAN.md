<!-- Generated from plan.json. Do not edit. -->

# Ontology-as-a-Product migration

## Outcome brief

The migration now treats the Ontology Product as a Product whose core value-bearing output is a governed ontology package. Its Product Ontology is a separate semantic scaffold that describes the Product. Craft receives the work; contexts and runtimes support the Product without becoming it.

- Plan: `CAL-MIGRATION-0003-ONTOLOGY-AS-PRODUCT-CONTEXT-V1`
- Product: `CA2-PRODUCT-ONTOLOGY`
- Product Ontology: `cav2.ontology-product`
- Core output: `CA2-OUTPUT-ONTOLOGY-PACKAGE`
- Current frontier: `SWU-CML11-202-PRODUCT-ONTOLOGY-MIGRATION`

## Boundary and next decision

The semantic correction is implemented and validated in this planning epoch. The next construction action is source closure for the three drifted Product Ontology dependencies, followed by the Product identity/scaffold migration. No approval is requested until the complete L4 Product candidate is tested.

## Architecture

- Product meaning: A durable Product identity for building and using project-owned governed ontologies.
- Product Ontology role: business-domain semantic scaffold describing Product meaning
- Core output role: core value-bearing Product output
- Runtime boundary: Runtimes implement or operate Product capabilities against ontology-package artifacts. They remain replaceable and cannot become the Product, Product Ontology, package meaning owner, or admission authority.

## Layers

### `L0-SEMANTIC-GRAPH-CLOSURE` — Close the Ontology-as-a-Product semantic graph

- State: `implemented-in-this-planning-epoch`
- SWU: `SWU-CML11-201-SEMANTIC-GRAPH-CLOSURE`
- Decision: Whether Product, Product Ontology, ontology-package output, Craft, contexts, capabilities, and runtimes remain independently identifiable.
- Output: semantic-model.json plus generated SEMANTIC-MODEL.md

### `L1-PRODUCT-IDENTITY-AND-PRODUCT-ONTOLOGY` — Migrate Product identity and descriptive Product Ontology

- State: `blocked-by-source-drift`
- SWU: `SWU-CML11-202-PRODUCT-ONTOLOGY-MIGRATION`
- Decision: Whether the Product identity and its business-domain semantic scaffold can be represented in Lab without treating the scaffold as the delivered product.
- Output: Product identity carrier and source-preserving Product Ontology scaffold

### `L2-ONTOLOGY-PACKAGE-PRODUCT-CONTRACT` — Define and prototype the governed ontology-package output

- State: `blocked-by-L1`
- SWU: `SWU-CML11-203-ONTOLOGY-PACKAGE-CONTRACT`
- Decision: Whether one exact ontology package can carry the minimum value-bearing output independently of any runtime.
- Output: Ontology Package artifact-type candidate, schema, generator, validator, hostile fixtures, and one valid fixture

### `L3-CONTEXT-AND-RUNTIME-PROTOTYPES` — Coordinate contexts and bind replaceable runtime prototypes

- State: `blocked-by-L2`
- SWU: `SWU-CML11-204-CONTEXT-RUNTIME-PROTOTYPE`
- Decision: Whether Governance and Ontology Lifecycle meanings plus replaceable runtime bindings can operate on the package contract without taking ownership of it.
- Output: Coordination Context, context compatibility evidence, capability bindings, and runtime prototype bindings

### `L4-FIRST-TESTABLE-ONTOLOGY-AS-PRODUCT-CANDIDATE` — Build and test one thin end-to-end Product candidate

- State: `blocked-by-L1-L3`
- SWU: `SWU-CML11-205-END-TO-END-PRODUCT-CANDIDATE`
- Decision: Whether one owner-selected source set can become a source-bound ontology package that is validated, inspected, queried, evolved, and recovered through the declared Product contract.
- Output: One immutable Product candidate manifest plus collect-all product-test evidence

## Approval

- Eligible after: `L4-FIRST-TESTABLE-ONTOLOGY-AS-PRODUCT-CANDIDATE`
- Decision: Approve or reject one immutable Ontology-as-a-Product candidate manifest.
- Effect: `Product approval only`

## Claim ceiling

This successor implements the corrected Ontology-as-a-Product planning architecture and machine-checkable semantic separation. It does not change canonical definitions, reconcile source drift, migrate Product or ontology bytes, mutate Craft, create a Product output contract, prove a runtime, approve the Product, or authorize admission, activation, cutover, publication, release, deployment, or source retirement.
