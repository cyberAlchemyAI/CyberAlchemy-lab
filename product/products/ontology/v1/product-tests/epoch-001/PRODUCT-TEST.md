<!-- Generated from test-profile.json. Do not edit. -->

# Ontology Product end-to-end test epoch 001

- Test epoch: `CAL-ONTOLOGY-PRODUCT-TEST-EPOCH-001`
- Status: `product-test-candidate`
- Authority effect: `none`
- Construction stage: `L4-FIRST-TESTABLE-ONTOLOGY-AS-PRODUCT-CANDIDATE`

## Selected real source

- Ontology: `cav2.ontology-product`
- Nodes: `23`
- Relations: `24`
- Typed residue: `5`
- Bound sources: `8`

## Acceptance criteria

- Exact imported registry and successor-binding digests match
- The selected source deterministically contains 23 nodes, 24 relations, and 5 typed residues
- Every node and relation source reference resolves to one of the 8 selected source records
- The existing Product runtime builds and validates one deterministic package
- Bounded list/get retrieval works and unknown identity fails closed
- Evolution, full replay, checkpoint recovery, context coordination, and runtime replacement pass over the real source
- Canonical machine records reproduce every human projection
- No test or artifact grants authority or Product approval

## Claim ceiling

A PASS proves the exact private Product candidate works end to end over the selected source bytes. It can support one Product approval decision but does not itself approve the Product or grant any lifecycle or operational authority.
