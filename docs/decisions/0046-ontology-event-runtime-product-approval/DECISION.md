<!-- Generated from decision.json. Do not edit. -->

# Ontology event-runtime Product approval

- Decision: `CAL-ONTOLOGY-EVENT-RUNTIME-PRODUCT-APPROVAL-0046`
- Gate: `G-CAL-ONTOLOGY-EVENT-RUNTIME-PRODUCT-APPROVAL`
- Status: `selected`
- Decided at: `2026-09-06T04:05:28Z`
- Authority effect: `product-approval-only`

## Exact approved subject

- Product: `CA2-PRODUCT-ONTOLOGY/v1`
- Candidate: `CAL-ONTOLOGY-AS-PRODUCT-CANDIDATE-0006-EVENT-RUNTIME-REALIZATION`
- Candidate digest: `5ebe011a083babcc383ca9ec0ea341be8448e18db65911a1a54d55dcf1e5860c`
- Binding digest: `28253f456733f75650cea4f52440c302de575c7c0e4af58a5cedab23afb65e9d`
- Product-test receipt digest: `a9aba1894ae529e39dd532ff6bd23016f9c9c38381023fa985821061522d8a95`

## Decision source

`do it`

## Product approval

- State: `approved`
- Scope: The exact frozen and tested CAL-ONTOLOGY-AS-PRODUCT-CANDIDATE-0006-EVENT-RUNTIME-REALIZATION bytes only.
- Rust tests: `15` cases in each of `2` runs
- Validator tests: `5`
- CLI materializations: `2`
- Initial graph: `14` nodes and `15` relations
- Initial histories: `29` semantic and `29` governance events
- Latest snapshots: `29`

## Next frontier

- Stage: `post-product-approval-binding-admission-candidate`
- Eligible: `true`
- Permitted effect: prepare and validate one exact non-effectful implementation-binding admission candidate
- Excluded effect: No binding admission or runtime adoption occurs until its owner selects a separately digest-bound option.

## Non-effects

- This decision does not mutate the frozen Product candidate, implementation binding, Rust source, tests, or Product-test receipt.
- This decision does not admit the implementation binding.
- This decision does not adopt or activate the Rust runtime.
- This decision does not admit any child ontology or change the previously admitted cohesive root.
- This decision does not resolve the DomainSpec successor-profile collision or unresolved review-owner routes.
- This decision does not authorize or perform migration, cutover, source retirement, credentials, or destructive action.
- This decision does not authorize publication, release, deployment, or external effects.
- This decision authorizes only preparation and validation of a separate non-effectful implementation-binding admission candidate.

## Claim ceiling

The exact frozen and tested event-runtime realization candidate is approved as an Ontology Product increment. The implementation binding is not admitted, the Rust runtime is not adopted or active, no child ontology is admitted, and no migration, cutover, publication, release, deployment, source retirement, credential, destructive action, or external effect is authorized.
