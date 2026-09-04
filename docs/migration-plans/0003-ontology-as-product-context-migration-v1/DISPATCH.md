<!-- Generated from dispatch.json. Do not edit. -->

# Successor authoring dispatch

- Dispatch: `cal-dispatch-migration-0003-ontology-as-product-v1`
- Mode: `sequence`
- Subagents: `none`

## Steps

1. `audit-definitions` — Resolve Product and Ontology definition authority via `definitions-governance`
2. `distill-semantic-model` — Distill Product, Product Ontology, and output identities via `distill`
3. `author-successor` — Author successor migration plan via `invoke`
4. `validate-successor` — Validate semantic model, plan, dispatch, and projections via `dispatch-spec`

## Gates

- `semantic-authority` — Product and Ontology bind canonical meanings while dependent labels remain generated projections. On failure: `block`.
- `non-collapse` — Product, Product Ontology, ontology-package output, Craft, contexts, capabilities, and runtimes remain distinct. On failure: `block`.
- `one-product-approval` — Only the immutable L4 end-to-end candidate may request Product approval; all authority effects remain later and separate. On failure: `block`.

## Guardrails

- Generated labels cannot create canonical axes.
- A Product Ontology cannot become the Product or its delivered output by placement or naming.
- Plan PASS cannot clear source drift, admit artifacts, approve the Product, or authorize operational effects.
