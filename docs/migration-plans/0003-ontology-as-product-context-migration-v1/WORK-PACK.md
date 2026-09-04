<!-- Generated from plan.json. Do not edit. -->

# Ontology-as-a-Product work pack

- Construction frontier: `SWU-CML11-202-PRODUCT-ONTOLOGY-MIGRATION`
- Execution designation: `non-executing-planning-candidate`
- Internal behavior: continue on PASS, fail closed on a causal blocker, request approval only after L4.

## Product construction

1. `SWU-CML11-201-SEMANTIC-GRAPH-CLOSURE` — Close the Ontology-as-a-Product semantic graph (`implemented-in-this-planning-epoch`)
2. `SWU-CML11-202-PRODUCT-ONTOLOGY-MIGRATION` — Migrate Product identity and descriptive Product Ontology (`blocked-by-source-drift`)
3. `SWU-CML11-203-ONTOLOGY-PACKAGE-CONTRACT` — Define and prototype the governed ontology-package output (`blocked-by-L1`)
4. `SWU-CML11-204-CONTEXT-RUNTIME-PROTOTYPE` — Coordinate contexts and bind replaceable runtime prototypes (`blocked-by-L2`)
5. `SWU-CML11-205-END-TO-END-PRODUCT-CANDIDATE` — Build and test one thin end-to-end Product candidate (`blocked-by-L1-L3`)

## Runnable now

- Author a source-closure candidate for the three drifted selectors
- Prepare the Product identity carrier against the admitted Product and Identity Carrier Definitions
- Design the represents relation validation between Product Ontology and Product

## Causal blockers

- `CML11-B01` affects `L1-L4` — Product Ontology validator is BLOCK on three selected source digests. Owner: `definitions-governance and CyberAlchemy v2 product owner`.
- `CML11-B02` affects `L3 admitted-context conformance` — Governance v3, Ontology Lifecycle v3, and Context Map v2 remain candidate-unadmitted. Owner: `context and context-map owners`.

## Operational support

- Select the exact Craft intake artifact type and destination — owner `Craft Project owner`; affects `no Product stage until intake mutation is requested`; `non-blocking`.
- Prepare source and rollback manifests — owner `migration operator`; affects `L1`; `blocked by source closure`.
- Prepare admission, activation, cutover, publication, release, and deployment routes — owner `separate authority owners`; affects `none before Product approval`; `deferred residue`.

## Craft intake

- State: `planned-not-written`
- Receiver: `CA2-PRODUCT-CRAFT/v1`
- Boundary: Craft receives work records only after its intake contract is selected. Receipt does not transfer Product, context, source, or runtime authority.
