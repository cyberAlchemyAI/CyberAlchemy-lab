<!-- Generated from candidate.json. Do not edit. -->

# Ontology Product L3 context and runtime candidate

- Candidate: `CAL-ONTOLOGY-AS-PRODUCT-CANDIDATE-0003`
- Status: `ready-for-final-product-candidate`
- Authority effect: `none`
- Predecessor: `product/products/ontology/v1/candidates/0002-source-preserving-foundation/candidate.json`

## Construction increment

- Unit: `SWU-CML11-204-CONTEXT-RUNTIME-PROTOTYPE`
- Coordination Context: `coordination/contexts/ontology-product/v1/coordination-context.json`
- Runtime binding: `implementation/bindings/ontology-product-lifecycle/v1/binding.json`

## Acceptance criteria

- The Coordination Context is Product-anchored, schema-valid, and keeps context relationships owned by the Context Map.
- Exact Governance v2, Ontology Lifecycle v2, Context Map v2, Product contract, and existing runtime source bytes are bound by digest.
- The existing Rust lifecycle runtime is unchanged and exposed only through the ProductEvolutionRuntime port as one replaceable implementation.
- Evolution changes the normalized Product observation while authority_effect remains none.
- Full event replay and checkpoint plus tail recovery produce byte-equivalent Product observations.
- The existing runtime adapter and independent reference adapter produce equal Product observations.
- Malformed change chains fail closed in both adapters.
- All canonical machine records reproduce their generated human projections.

## Next Product frontier

- Assemble one immutable end-to-end Product candidate over source selection, package construction, retrieval, context coordination, evolution, recovery, and runtime replacement evidence
- Run the collect-all final Product test suite against the exact candidate digest
- Present one Product approval decision only after every acceptance-critical test passes

## Approval boundary

No approval is requested for L3. The single Product approval boundary remains after the immutable L4 end-to-end candidate and its collect-all Product tests pass.

## Claim ceiling

This successor is a tested private L3 construction candidate for context coordination and replaceable runtime behavior. It does not admit contexts or runtimes, approve the Product, complete migration, or authorize activation, cutover, publication, release, deployment, or source retirement.
