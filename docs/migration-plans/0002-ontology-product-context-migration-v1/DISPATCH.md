<!-- Generated from dispatch.json. Do not edit this projection. -->

# Migration planning dispatch

- Dispatch: `cal-dispatch-migration-0002-ontology-product-context-v1`
- Mode: `sequence`
- Subagents: `none`
- Authority: planning and validation only

## Steps

1. `inventory-identities` — Inventory genuine Product and Bounded Context identities via `inventory`
2. `distill-target` — Distill the migration subject and first unit via `distill`
3. `author-plan` — Author the layered Product/Context migration plan via `invoke`
4. `validate-plan` — Validate canonical records and generated projections via `dispatch-spec`

## Gates

- `identity-boundary` — Ontology Product is the migration subject; Craft remains only the work receiver; contexts and capabilities retain distinct identities. On failure: `block`.
- `source-closure` — The three current source drifts remain explicit blockers to Product copying and are routed to L0. On failure: `block`.
- `single-product-approval` — Only the immutable integrated L4 candidate may request product approval; all later authority effects remain separate. On failure: `block`.

## Promotion guardrails

- Planning and validation create no implementation, Product, Context, admission, publication, release, deployment, or source-retirement authority.
- Current source BLOCK cannot be described as PASS or bypassed by copying stale source records.
- Craft work intake cannot change the semantic owner of the migrated Product or its Bounded Contexts.
