<!-- Generated from plan.json. Do not edit. -->

# Ontology Product L3 context and runtime bindings

- Plan: `CAL-MIGRATION-0005-ONTOLOGY-PRODUCT-CONTEXT-RUNTIME-BINDINGS-V1`
- Unit: `SWU-CML11-204-CONTEXT-RUNTIME-PROTOTYPE`
- Status: `implementation-directed-candidate`
- Authority effect: `none`

## Objective

Prove that the Ontology Product package contract can coordinate exact Governance and Ontology Lifecycle meanings and can evolve, replay, recover, and survive runtime replacement without transferring meaning or Product ownership to a runtime.

## Product construction

- One Product-anchored Coordination Context over exact Governance and Ontology Lifecycle context endpoints
- One canonical replaceable runtime binding descriptor with a generated human projection
- One Product-facing evolution port with an adapter around the existing Rust lifecycle runtime
- Independent reference-adapter parity plus evolution, replay, checkpoint recovery, context-observation, and hostile-chain tests
- One successor construction candidate bound to all L3 evidence

## Done criteria

- Coordination Context validates against its closed schema and preserves Context Map ownership
- The binding selects exact context, map, Product contract, and existing runtime source bytes
- The existing lifecycle runtime is unchanged and appears only as one replaceable adapter
- Evolution changes a Product observation through canonical events without changing authority effect
- Independent replay produces byte-equivalent normalized Product observations
- Checkpoint plus tail recovery equals full replay
- A second conforming reference adapter produces the same normalized Product observation
- Malformed event chains fail closed and all machine records reproduce generated human projections

## Operational support

- **non-blocking for Product construction** — Artifact-type and context owners may later decide admission of the Coordination Context and binding carriers — owner `separate artifact-type and context owners` — affects `post-Product-approval lifecycle only`
- **deferred** — Runtime owner may later decide adoption, activation, or replacement of an implementation — owner `runtime owner` — affects `none before final Product approval`
- **deferred** — Publication, release, deployment, cutover, and source retirement — owner `separate operational owners` — affects `none before final Product approval`

## Validation

```bash
PYTHONDONTWRITEBYTECODE=1 python3 coordination/contexts/ontology-product/v1/validate.py
cargo test --manifest-path implementation/bindings/ontology-product-lifecycle/v1/Cargo.toml
PYTHONDONTWRITEBYTECODE=1 python3 implementation/bindings/ontology-product-lifecycle/v1/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 product/products/ontology/v1/candidates/0003-context-runtime-evolution/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 docs/migration-plans/0005-ontology-product-context-runtime-bindings-v1/validate.py
```

## Approval boundary

Mode: `single-final-product-boundary`. This increment does not request approval.

## Claim ceiling

This L3 plan and evidence may prove only a private replaceable context/runtime construction prototype. They do not admit contexts or runtimes, approve the Product, complete migration, or authorize operational effects.
