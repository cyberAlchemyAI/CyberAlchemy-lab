<!-- Generated from candidate.json. Do not edit. -->

# Ontology Product candidate 0004 — first stable candidate

- Candidate: `CAL-ONTOLOGY-AS-PRODUCT-CANDIDATE-0004`
- Version: `1.0.0-product-candidate.1`
- Status: `ready-for-product-approval`
- Authority effect: `none`
- Predecessor: `product/products/ontology/v1/candidates/0003-context-runtime-evolution/candidate.json`

## Exact Product-test evidence

- Receipt: `product/products/ontology/v1/product-tests/epoch-001/receipts/validation.json`
- Receipt digest: `f1d7cbaa3e14c74e4ac77e0cb0180740dc3d48b863576a3af75033ea177bea73`
- Selected source digest: `d442547f4d0238f3eab40ef1efbe2a9de7683e6b0c95487f29c798ee136b0b16`
- Package digest: `b3ccf8f02a6494ddf6f66a5c9a3b82d6b9cba1523dbc21612a8dbc71cfa170cc`
- Structural checks: `9/9`
- Rust behavior tests: `9/9`
- Graph: `23` nodes, `24` relations, `5` typed residues

## Acceptance criteria

- The exact imported registries and successor source bindings trace into one source-contract instance.
- The existing Rust Product runtime deterministically builds and validates one package over all 23 nodes, 24 relations, and 5 typed residues.
- Bounded retrieval covers every node and unknown identity fails closed.
- Evolution changes the Product observation while retaining authority_effect none.
- Full replay and checkpoint recovery are byte-equivalent.
- The existing lifecycle adapter and independent reference runtime agree over the real source.
- Context observation preserves the Governance v2, Ontology Lifecycle v2, and Context Map v2 references.
- All human views are generated projections of canonical machine records.
- The candidate remains private, non-authoritative, unapproved, and bounded to one Product approval decision.

## Single Product approval boundary

- Eligible: `true`
- Granted: `false`
- Scope: `Product approval only`
- Binding: A decision must bind the exact candidate.json and receipts/validation.json SHA-256 digests.

Approval does not grant:

- definition admission
- artifact-type admission
- context admission
- runtime adoption
- source admission
- activation
- cutover
- publication
- release
- deployment
- source retirement

## Visible operational residue

- Commit and publication remain owner-controlled and deferred.
- Admission, adoption, activation, cutover, release, deployment, and source retirement require separate post-approval routes.
- Imported typed residue remains visible and is not silently resolved by passing runtime tests.

## Claim ceiling

This exact private Product candidate has passing source-to-package, retrieval, evolution, recovery, context, and runtime-replacement evidence. It is eligible for one Product approval decision but is not approved, admitted, adopted, activated, cut over, published, released, deployed, or authorized to retire any source.
