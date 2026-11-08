# TASK T2 — Product Ontology Adapter

Layer: L2. Status: testable candidate complete.
Authority effect: none.

## Objective

Implement one real Product Ontology authoring adapter without moving product
meaning into Define core.

## Inputs And Outputs

Inputs are an exact Definition Pack receipt, selected Product Ontology sources,
owner-approved question/readiness contracts, and the L1 Client API. Outputs are
ontology-specific `.alch` source and compiled evidence, one adapter, a candidate
Product Ontology, validation evidence, and a handoff receipt.

## Smallest Working Unit

One realistic Definition Pack leads through one Product question sequence to a
user-confirmed, deterministically serialized Product Ontology candidate.

## Ordered Rules

Verify the prerequisite receipt; ask only Product-owned questions; preserve
exact user language and evidence; evaluate independent quality dimensions;
materialize only after readiness; validate without admission; confirm exact
bytes; export a no-effect receipt.

## Edge Cases And Failure Modes

Wrong Definition Pack, unresolved meaning, collapsed product terms, coupled
axes without a named relation, adapter drift, candidate byte change after
confirmation, and validator PASS misrepresented as admission.

## Verification And Completion

Positive and hostile fixtures pass; identical sources, answers, and
configuration reproduce bytes and receipt; zero-adapter and Definition Pack
regressions remain green; Product-specific code exists only in its adapter
package and sources.

Observed candidate evidence on 2026-09-08:

- selected source: `language/capabilities/alchlang/define/alch-product-business-ontology-v1/product-ontology.json`;
- exact prerequisite: the sibling candidate `definition-pack.json`, bound by
  candidate, source, graph, module-set, manifest, and handoff digests;
- Product-owned questions cover capability, primary user, user job, outcome,
  and constraint through the L1 Client API;
- Product-specific Alch entries compile question selection and readiness without
  placing Product meaning in Define core;
- the real source fixture reached exact-byte confirmation and deterministic export;
- missing and substituted Definition Pack evidence blocked Product only;
- semantic grounding, non-collapse, and orthogonality failed independently;
- focused Product tests passed twice at 3/3 and the complete Node surface passed
  63/63; and
- fresh Product Alch compilation was byte-identical across 61 generated files.

The selected source package independently passed its validator and all 6/6
negative semantic mutation cases. These are candidate construction facts only.

Open questions and blockers are owned by [the work pack](../WORK-PACK.md#blockers).
