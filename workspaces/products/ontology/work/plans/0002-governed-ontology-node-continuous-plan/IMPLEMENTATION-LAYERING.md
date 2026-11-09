# Implementation layering

Source: `CAL-PLAN-0002` / `continuous-plan.json`

The layers are dependency and authority boundaries, not code folders. A later layer is not evaluable until its predecessors have current passing receipts.

## L0 — Authority and semantic closure

Decision question: What exact governed-node contract is selected and stable enough to become authored intent?

- `W0` Select the governed-node architecture: Bind one immutable architecture decision before any successor design or implementation bytes change.
- `W1` Close definitions and schema semantics: Define the smallest stable node, relation, challenge-contract, and context-selector contract without implementation leakage.
- `W2` Align product capability and business ontology: Make the selected governed-node behavior an explicit product capability and capability-local business ontology before DomainSpec authoring.

## L1 — Deterministic authored and compiled design

Decision question: Can DomainSpec compile the selected semantics into one byte-stable graph and system ontology?

- `W3` Author DomainSpec and event-sourcing source: Represent the selected product and ontology semantics as authored DomainSpec source before compilation.
- `W4` Compile the graph and system ontology deterministically: Produce byte-stable compiled graph, event contract, and system ontology from the exact authored source epoch.

## L2 — Runtime binding and conformance

Decision question: Does the Rust runtime implement exactly the compiled contract without vacuous or projection-source behavior?

- `W5` Implement the governed-node runtime: Implement only the compiled contract in Rust: append validation, deterministic reduction, exact joins, and rebuildable projections.
- `W6` Bind implementation and prove conformance: Bind every compiled obligation to exact Rust symbols and non-vacuous evidence, while exposing all residue.

## L3 — Migration rehearsal and aggregate validation

Decision question: Can legacy material be projected into the accepted candidate and can the full evidence graph pass as one immutable epoch?

- `W7` Rehearse bounded legacy migration: Test an allowlisted legacy slice against the accepted candidate in isolation without mutating legacy sources or cutting over.
- `W8` Validate the complete candidate epoch: Run one collect-all aggregate validation over frozen W0-W7 bytes and issue a candidate verdict with an explicit authority ceiling.

## Cross-layer invariants

- Canonical append-only events are the replay source; snapshots and projections are disposable read models.
- Each node or relation state is calculated from the latest valid event in its own subject stream.
- Semantic and governance streams remain distinct and join only through exact event identity, digest, and commit position.
- Product Capability and capability-local business ontology precede DomainSpec source; compiled graphs precede implementation binding.
- Every receipt binds one immutable source epoch. Drift reopens the affected gate.
- Migration rehearsal follows accepted conformance and never implies cutover.

## Layer promotion rule

Promotion to the next layer requires every gate in the current layer to PASS. A block yields explicit residue and makes dependent checks `not_evaluable`; it cannot be bypassed by a later focused PASS.
