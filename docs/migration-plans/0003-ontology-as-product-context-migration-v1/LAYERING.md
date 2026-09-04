<!-- Generated from plan.json. Do not edit. -->

# Implementation layering

## `L0-SEMANTIC-GRAPH-CLOSURE`

**After this layer, we know:** Whether Product, Product Ontology, ontology-package output, Craft, contexts, capabilities, and runtimes remain independently identifiable.

- State: `implemented-in-this-planning-epoch`
- Smallest unit: `SWU-CML11-201-SEMANTIC-GRAPH-CLOSURE`
- Concrete output: semantic-model.json plus generated SEMANTIC-MODEL.md
- Exit evidence:

  - Canonical Product and Ontology bindings resolve
  - The exact includes_capability and produces relations resolve
  - Both convenience labels are generated-only
  - All seven non-collapse invariants pass

## `L1-PRODUCT-IDENTITY-AND-PRODUCT-ONTOLOGY`

**After this layer, we know:** Whether the Product identity and its business-domain semantic scaffold can be represented in Lab without treating the scaffold as the delivered product.

- State: `blocked-by-source-drift`
- Smallest unit: `SWU-CML11-202-PRODUCT-ONTOLOGY-MIGRATION`
- Concrete output: Product identity carrier and source-preserving Product Ontology scaffold
- Exit evidence:

  - Three source drifts reconciled
  - Product identity schema PASS
  - Product Ontology package PASS
  - represents relation and non-collapse checks PASS

## `L2-ONTOLOGY-PACKAGE-PRODUCT-CONTRACT`

**After this layer, we know:** Whether one exact ontology package can carry the minimum value-bearing output independently of any runtime.

- State: `blocked-by-L1`
- Smallest unit: `SWU-CML11-203-ONTOLOGY-PACKAGE-CONTRACT`
- Concrete output: Ontology Package artifact-type candidate, schema, generator, validator, hostile fixtures, and one valid fixture
- Exit evidence:

  - Artifact Type four-facet validation PASS
  - Canonical machine and generated human views agree
  - Runtime independence and source-authority boundaries pass

## `L3-CONTEXT-AND-RUNTIME-PROTOTYPES`

**After this layer, we know:** Whether Governance and Ontology Lifecycle meanings plus replaceable runtime bindings can operate on the package contract without taking ownership of it.

- State: `blocked-by-L2`
- Smallest unit: `SWU-CML11-204-CONTEXT-RUNTIME-PROTOTYPE`
- Concrete output: Coordination Context, context compatibility evidence, capability bindings, and runtime prototype bindings
- Exit evidence:

  - Coordination Context PASS
  - Context Map ownership preserved
  - Runtime bindings target capabilities and package contract
  - No runtime or context becomes Product or meaning owner

## `L4-FIRST-TESTABLE-ONTOLOGY-AS-PRODUCT-CANDIDATE`

**After this layer, we know:** Whether one owner-selected source set can become a source-bound ontology package that is validated, inspected, queried, evolved, and recovered through the declared Product contract.

- State: `blocked-by-L1-L3`
- Smallest unit: `SWU-CML11-205-END-TO-END-PRODUCT-CANDIDATE`
- Concrete output: One immutable Product candidate manifest plus collect-all product-test evidence
- Exit evidence:

  - Source-to-package trace PASS
  - Deterministic validation PASS
  - Bounded retrieval PASS
  - Evolution and residue test PASS
  - Runtime replacement boundary PASS
  - Immutable candidate digest ready for one Product approval decision
