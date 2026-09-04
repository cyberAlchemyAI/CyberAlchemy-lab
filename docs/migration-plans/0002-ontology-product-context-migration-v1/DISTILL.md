<!-- Generated from plan.json. Do not edit this projection. -->

# Distill result

- Mode: `standard`
- Verdict: `pass-for-planning`
- Smallest coherent unit: `SWU-CML11-101-SOURCE-CLOSURE`

## Proposer/Balancer trace

### Round 1

- Proposer: Migrate Registry Context first because its validator currently passes.
- Balancer (`identity-collapse`): Registry Context is explicitly a Product Capability of CyberAlchemy, not an independent Product. Treating it as the Product/Context migration subject would create a false Product identity.
- Reconciliation: `reject`

### Round 2

- Proposer: Migrate the Ontology Product and bind its already-authored Governance and Ontology Lifecycle contexts.
- Balancer (`source-currency`): The target is coherent, but its current package validator is BLOCK on three source digests; copying now would preserve a stale source registry.
- Reconciliation: `accept-with-L0-source-closure-first`

## Recomposition proof

Resolving the three drifted selectors closes the exact source epoch required by the Product identity, product ontology package, and later integrated tests. It adds no Product, Context, runtime, or authority claim by itself.

## Deferred complexity

Capability migration, runtime replacement, context admission, and operational effects remain separate chains.
