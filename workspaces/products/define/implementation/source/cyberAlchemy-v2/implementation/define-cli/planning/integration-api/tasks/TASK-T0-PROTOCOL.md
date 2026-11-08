# TASK T0 — Protocol And Synthetic Stage Proof

Layer: L0. Status: completed testable candidate on 2026-09-08. Authority effect:
none. Passing evidence grants no admission or activation.

## Objective

Prove that one ontology stage can participate end to end through generic Alch
decisions, a static registry, ARE Module Port mechanics, and a typed facade
without adding ontology-specific logic to Define core.

## Inputs And Outputs

Inputs are accepted descriptor/result shapes, an immutable Module Port, a
synthetic adapter, frozen stage state, explicit responses, and confirmation.
Outputs are compiled generic entries, a deterministic stage graph, candidate
artifact bytes, and a digest-bound no-effect handoff receipt.

## Smallest Working Units

1. `SWU-T0-01`: create closed schemas and hostile fixtures.
2. `SWU-T0-02`: declare four generic `.alch` entries and compile them into a
   separate generated root.
3. `SWU-T0-03`: implement the stage registry and typed facade with zero and one
   injected adapter.
4. `SWU-T0-04`: compose one in-memory synthetic question-to-export vertical.

Execute in order. No parallel merge is assumed.

## Ordered Rules

Validate closed records; reject duplicates, missing dependencies, and cycles;
compute order-independent graph identity; resolve one explicit entry point;
invoke only typed exact capabilities; retain unavailable, blocked, deferred,
and invalid states; require readiness, validation, and exact-byte confirmation;
then seal receipts.

## Edge Cases And Failure Modes

Zero adapters, unknown stage, missing provider, duplicate provider, cycle,
malformed input/output, thrown adapter, stale prerequisite, missing
confirmation, semantic-quality failure, authority smuggling, and input-order
permutation.

## Verification And Completion

Focused tests pass twice; fresh Alch compilation is byte-identical; the existing
Define suite passes; zero adapters preserve Definition Pack behavior; semantic,
non-collapse, orthogonality, and authority distinctions have separate fixtures.

Observed result:

- `node scripts/verify-ontology-stage-port.mjs`: PASS, four compiled entries,
  115 generated files, byte-identical fresh recompilation;
- `node --test test/ontology-stage-port.test.mjs`: 8/8 PASS twice; and
- `npm test`: 52/52 PASS, including the existing Definition Pack, language
  quality, conversation, durable runtime, and Alch compilation suite.

Open questions and blockers are owned by [the work pack](../WORK-PACK.md#blockers).
