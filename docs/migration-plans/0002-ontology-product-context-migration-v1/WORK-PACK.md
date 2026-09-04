<!-- Generated from plan.json. Do not edit this projection. -->

# Product/context migration work pack

- Current frontier: `SWU-CML11-101-SOURCE-CLOSURE`
- Execution designation: `non-executing-planning-candidate`
- Internal gate behavior: continue after PASS; fail closed on a causal failure; do not request intermediate approvals.

## Craft receiver contract

- Receiver: `CA2-PRODUCT-CRAFT/v1`
- State: `planned-not-written`
- Boundary: No Craft ledger mutation is authorized by this plan. The exact Craft intake artifact type and destination must be selected before writing work records.

## Product-construction sequence

1. `SWU-CML11-101-SOURCE-CLOSURE` — Reconcile the selected source epoch (`runnable-planning-work`)
2. `SWU-CML11-102-PRODUCT-IDENTITY` — Author the Ontology Product identity carrier (`blocked-by-L0`)
3. `SWU-CML11-103-COORDINATION-CONTEXT` — Bind Product and existing contexts without collapse (`blocked-by-L1`)
4. `SWU-CML11-104-ONTOLOGY-PACKAGE` — Copy the exact Ontology Product package (`blocked-by-L0-L2`)
5. `SWU-CML11-105-INTEGRATED-CANDIDATE` — Test the Product/Context migration candidate (`blocked-by-L1-L3`)

## Runnable now

- Author the immutable source-closure candidate for the three drifted selectors.
- Map the remaining five current source records and preserve their exact digests.
- Define the candidate Product identity fields and semantic references without writing the Product carrier yet.
- Prepare Craft intake records for the five SWUs after the Craft intake contract is selected.

## Causal blockers

- `CML11-B01` affects `L1-L4` — Ontology Product source validator is BLOCK because three source digests drifted. Owner: `definitions-governance and CyberAlchemy v2 product owner`.
- `CML11-B02` affects `L2 final conformance` — Governance v3, Ontology Lifecycle v3, and Context Map v2 are candidate-unadmitted. Owner: `respective context and context-map owners`.
- `CML11-B03` affects `Project/Goal achievement claims only` — External Goal-package validation is not evaluated. Owner: `Goal owner`.

## Operational support

- Select or author a Craft intake contract for these five SWUs — owner `Craft Project owner`; affects `no Product construction stage until an intake write is requested`; `non-blocking for L0 planning`.
- Prepare exact source and rollback manifests — owner `migration operator`; affects `L3`; `deferred until L0 PASS`.
- Prepare admission, publication, and cutover routes — owner `separate authority owners`; affects `no construction stage`; `deferred beyond product approval`.

## Closeout

- Re-hash every selected source and Lab dependency before implementation.
- Run collect-all non-effectful validation; mark dependent checks not_evaluable when causally blocked.
- Generate every human projection from its canonical machine record.
- Bind the final product approval to one immutable manifest digest.
- Route admission, activation, cutover, publication, release, deployment, and source retirement separately after product approval.

## Claim ceiling

This candidate plans a corrected Ontology Product and Bounded Context migration and identifies the first runnable source-closure unit. It does not reconcile the drifted sources, mutate Craft, create or admit a Product or Context, copy source files, prove runtime conformance, approve a product, authorize implementation, admit, activate, cut over, publish, release, deploy, or retire CyberAlchemy-v2 material.
