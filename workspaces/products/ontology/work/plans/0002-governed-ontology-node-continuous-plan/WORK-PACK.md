# Continuous work pack

Work Pack: `CAL-PLAN-0002`  
Designation: `planning-candidate-blocked-at-w0`  
Execution entry: blocked

This Work Pack is descriptive until W0 and the admitted Design prerequisites close. Each SWU has one primary behavior, an explicit owner/write scope, done criteria, and validation bindings.

## W0 — Select the governed-node architecture

Layer: `L0`  
Depends on: `none`  
Current state: `blocked-human-decision`

Bind one immutable architecture decision before any successor design or implementation bytes change.

### SWU-W0-001

Primary behavior: Produce the owner decision for the exact CAL-PROP-0004 digest.

Owner: CyberAlchemy-v2 architecture decision owner

Write scope:

- `docs/decisions/<new-governed-node-decision>/`

Done criteria:

- The decision names the proposal digest.
- The result is selected, amended-selected, or rejected.
- Rejected stops the plan; amended-selected creates a new bound proposal digest.

Validation:

- `VAL-W0-DECISION` — One immutable selected, amended, or rejected decision receipt; only selected or amended-selected continues.

Split analysis: Atomic because it makes one authority-bearing architecture choice and changes no implementation.

Gate `G-W0` — owner: human architecture owner

Pass condition: An exact-digest decision selects the governed-node envelope and semantic/governance stream split.

Failure action: `stop`

## W1 — Close definitions and schema semantics

Layer: `L0`  
Depends on: `W0`  
Current state: `pending-prerequisites`

Define the smallest stable node, relation, challenge-contract, and context-selector contract without implementation leakage.

### SWU-W1-001

Primary behavior: Author canonical definitions for governed node identity, semantic state, governance state, challenge resolution, relation endpoints, context selection, confidence axes, and typed residue.

Owner: definitions owner

Write scope:

- `docs/definition-packs/<governed-node-pack>/`

Done criteria:

- Each term has one canonical meaning and authority owner.
- Semantic confidence, governance confidence, and evidence strength remain distinct.
- ASD-STE100 guidance affects explanatory prose only, not identifier semantics.

Validation:

- `VAL-SCHEMA-NEGATIVE` — Valid fixtures pass; missing identity, invalid endpoints, collapsed confidence axes, and malformed challenge fields fail closed.

Split analysis: Atomic as one mutually dependent semantic vocabulary; splitting would leave schema terms undefined.

### SWU-W1-002

Primary behavior: Author schemas and negative fixtures for nodes, relations, challenge contracts, context selectors, and exact cross-stream references.

Owner: ontology contract owner

Write scope:

- `ontology-lifecycle/domainspec/event-sourcing/schemas/`
- `ontology-lifecycle/fixtures/schema-negatives/`

Done criteria:

- All proposal-required challenge fields are represented.
- Relations require valid typed endpoints.
- Context membership is derived from explicit selectors.
- Every required field has at least one rejecting negative fixture.

Validation:

- `VAL-SCHEMA-NEGATIVE` — Valid fixtures pass; missing identity, invalid endpoints, collapsed confidence axes, and malformed challenge fields fail closed.
- `VAL-VACUITY` — Each mutation causes its named invariant to fail; no test passes without exercising its bound invariant.

Split analysis: Atomic because schemas and their falsifying witnesses define one acceptance surface.

Gate `G-W1` — owner: definitions and ontology contract owners

Pass condition: Definitions and schemas close over every selected proposal field and all negative fixtures fail for the intended reason.

Failure action: `repair-W1`

## W2 — Align product capability and business ontology

Layer: `L0`  
Depends on: `W1`  
Current state: `pending-prerequisites`

Make the selected governed-node behavior an explicit product capability and capability-local business ontology before DomainSpec authoring.

### SWU-W2-001

Primary behavior: Revise the Product Capability to state governed-node event calculation, challenge handling, and context-artifact projection behavior.

Owner: Product Capability owner

Write scope:

- `ontology-lifecycle/product-capability.json`

Done criteria:

- Behavior is user/product language, not Rust structure.
- Every promised behavior maps to a W1 definition.
- Acceptance remains owner-bound.

Validation:

- `VAL-SCHEMA-NEGATIVE` — Valid fixtures pass; missing identity, invalid endpoints, collapsed confidence axes, and malformed challenge fields fail closed.

Split analysis: Atomic as one capability contract.

### SWU-W2-002

Primary behavior: Revise the capability-local business ontology with governed node, relation, challenge, residue, and context-artifact relationships.

Owner: business ontology owner

Write scope:

- `ontology-lifecycle/business-ontology.json`

Done criteria:

- Concept and relation identifiers are unique.
- All relation endpoints resolve.
- Challenge and context relationships are explicit rather than prose-only.

Validation:

- `VAL-SCHEMA-NEGATIVE` — Valid fixtures pass; missing identity, invalid endpoints, collapsed confidence axes, and malformed challenge fields fail closed.

Split analysis: Atomic because the concept set and relationship closure must be reviewed together.

Gate `G-W2` — owner: Product Capability and business ontology owners

Pass condition: Both candidate artifacts bind the same definitions and have no unresolved endpoint or behavior mapping.

Failure action: `repair-W2`

## W3 — Author DomainSpec and event-sourcing source

Layer: `L1`  
Depends on: `W2`  
Current state: `pending-prerequisites`

Represent the selected product and ontology semantics as authored DomainSpec source before compilation.

### SWU-W3-001

Primary behavior: Extend the DomainSpec development source with governed-node types, relationships, invariants, selectors, and projection obligations.

Owner: DomainSpec source owner

Write scope:

- `ontology-lifecycle/domainspec/`

Done criteria:

- Every W2 behavior has an authored source mapping.
- No generated graph is hand-edited.
- The development profile remains visibly candidate until admitted.

Validation:

- `VAL-DOMAINSPEC-TWICE` — Both runs pass and generated graph/system-ontology bytes are identical.
- `VAL-DOMAINSPEC-BACKEND` — Type checking and the complete backend test suite pass, including event-sourcing compiler negatives.

Split analysis: Atomic as one dependency-closed authored source increment.

### SWU-W3-002

Primary behavior: Extend the event-sourcing source with the selected streams, complete-state events, exact joins, projections, and runtime obligations.

Owner: DomainSpec event-sourcing contract owner

Write scope:

- `ontology-lifecycle/domainspec/event-sourcing/source.json`
- `ontology-lifecycle/domainspec/event-sourcing/schemas/`

Done criteria:

- Canonical events remain the replay source.
- Node and relation latest snapshots are per subject.
- Challenge governance joins by event id, digest, and commit position.
- Context views declare consistent-cut selectors.

Validation:

- `VAL-EVENT-CONTRACT-TWICE` — Both checks pass with identical compiled contract and receipt identity.
- `VAL-DOMAINSPEC-BACKEND` — Type checking and the complete backend test suite pass, including event-sourcing compiler negatives.

Split analysis: Atomic because streams, events, joins, and projections form one compile contract.

Gate `G-W3` — owner: DomainSpec source owners

Pass condition: Authored source is dependency-closed, schema-valid, and traceable to W2 without touching generated outputs by hand.

Failure action: `repair-W3`

## W4 — Compile the graph and system ontology deterministically

Layer: `L1`  
Depends on: `W3`  
Current state: `pending-prerequisites-and-profile-admission`

Produce byte-stable compiled graph, event contract, and system ontology from the exact authored source epoch.

### SWU-W4-001

Primary behavior: Compile the DomainSpec graph, event-sourcing contract, and system ontology with source-bound receipts.

Owner: DomainSpec compiler owner

Write scope:

- `ontology-lifecycle/domainspec/.domainspec/generated/`
- `ontology-lifecycle/domainspec/event-sourcing/generated/`
- `ontology-lifecycle/system-ontology/`

Done criteria:

- All outputs are generated from source.
- Receipts bind exact source and compiler digests.
- Two unchanged runs produce identical bytes.

Validation:

- `VAL-DOMAINSPEC-TWICE` — Both runs pass and generated graph/system-ontology bytes are identical.
- `VAL-EVENT-CONTRACT-TWICE` — Both checks pass with identical compiled contract and receipt identity.
- `VAL-DOMAINSPEC-BACKEND` — Type checking and the complete backend test suite pass, including event-sourcing compiler negatives.

Split analysis: Atomic because all compiled artifacts must share one source epoch.

Gate `G-W4` — owner: DomainSpec compiler and profile admission owners

Pass condition: The exact profile/source epoch is admitted and two compiles yield identical outputs and receipts.

Failure action: `block`

## W5 — Implement the governed-node runtime

Layer: `L2`  
Depends on: `W4`  
Current state: `pending-prerequisites`

Implement only the compiled contract in Rust: append validation, deterministic reduction, exact joins, and rebuildable projections.

### SWU-W5-001

Primary behavior: Implement typed semantic and governance event payloads plus append-time invariant checks.

Owner: Rust runtime owner

Write scope:

- `ontology-lifecycle/runtime/src/`
- `ontology-lifecycle/runtime/tests/`
- `ontology-lifecycle/runtime/fixtures/`

Done criteria:

- Payloads map exactly to compiled schemas.
- Expected-version, event identity, ordering, and continuity checks fail closed.
- No implementation-only semantic field exists.

Validation:

- `VAL-RUST-RUNTIME` — Formatting and all runtime tests pass with the locked dependency set.
- `VAL-VACUITY` — Each mutation causes its named invariant to fail; no test passes without exercising its bound invariant.

Split analysis: Atomic as the write-side contract and its falsifying tests.

### SWU-W5-002

Primary behavior: Implement per-subject latest-state reducers and exact semantic-governance join validation.

Owner: Rust runtime owner

Write scope:

- `ontology-lifecycle/runtime/src/`
- `ontology-lifecycle/runtime/tests/`
- `ontology-lifecycle/runtime/fixtures/`

Done criteria:

- Node and relation state comes from each subject stream's latest valid event.
- Governance cannot mutate semantic state.
- Wrong event id, digest, or commit position is rejected.

Validation:

- `VAL-RUST-RUNTIME` — Formatting and all runtime tests pass with the locked dependency set.
- `VAL-VACUITY` — Each mutation causes its named invariant to fail; no test passes without exercising its bound invariant.
- `VAL-REPLAY-EQUALITY` — Latest snapshots, ontology-at-cursor, governed-node view, and context-artifact view are byte-identical across rebuilds.

Split analysis: Atomic because reducer state and cross-stream join consistency are one state-transition behavior.

### SWU-W5-003

Primary behavior: Implement ontology-at-cursor, governed-node, and context-artifact projections from canonical events.

Owner: Rust runtime owner

Write scope:

- `ontology-lifecycle/runtime/src/`
- `ontology-lifecycle/runtime/tests/`
- `ontology-lifecycle/runtime/fixtures/`

Done criteria:

- All views rebuild from empty state.
- A global commit-position cut prevents fractured context views.
- No projection or snapshot is accepted as canonical replay input.

Validation:

- `VAL-RUST-RUNTIME` — Formatting and all runtime tests pass with the locked dependency set.
- `VAL-REPLAY-EQUALITY` — Latest snapshots, ontology-at-cursor, governed-node view, and context-artifact view are byte-identical across rebuilds.
- `VAL-VACUITY` — Each mutation causes its named invariant to fail; no test passes without exercising its bound invariant.

Split analysis: Atomic because the three read models share one consistency-cut and replay-source rule.

Gate `G-W5` — owner: Rust runtime owner

Pass condition: All positive, negative, replay-equality, and projection-source tests pass against the W4 compiled epoch.

Failure action: `repair-W5`

## W6 — Bind implementation and prove conformance

Layer: `L2`  
Depends on: `W5`  
Current state: `pending-prerequisites`

Bind every compiled obligation to exact Rust symbols and non-vacuous evidence, while exposing all residue.

### SWU-W6-001

Primary behavior: Produce an exact ConstructionBinding from definitions and compiled obligations to implementation symbols and tests.

Owner: ConstructionBinding owner

Write scope:

- `ontology-lifecycle/conformance/construction-binding.json`

Done criteria:

- Every compiled obligation has at least one implementation symbol and test.
- Every bound digest is current.
- Unbound symbols and obligations are reported rather than omitted.

Validation:

- `VAL-BINDING-CURRENTNESS` — All exact bindings resolve to current bytes and no implementation symbol is unbound.
- `VAL-RUST-RUNTIME` — Formatting and all runtime tests pass with the locked dependency set.

Split analysis: Atomic because partial binding would overstate implementation conformance.

### SWU-W6-002

Primary behavior: Run an independent conformance and vacuity audit for the exact W4/W5 epoch.

Owner: independent validation owner

Write scope:

- `ontology-lifecycle/conformance/verification.json`
- `ontology-lifecycle/conformance/d65-status.json`

Done criteria:

- Each negative witness demonstrably trips its intended invariant.
- Dependent checks are not_evaluable when a predecessor fails.
- Known residue is explicit and acceptance-critical residue is classified.

Validation:

- `VAL-VACUITY` — Each mutation causes its named invariant to fail; no test passes without exercising its bound invariant.
- `VAL-BINDING-CURRENTNESS` — All exact bindings resolve to current bytes and no implementation symbol is unbound.
- `VAL-RUST-RUNTIME` — Formatting and all runtime tests pass with the locked dependency set.
- `VAL-DOMAINSPEC-BACKEND` — Type checking and the complete backend test suite pass, including event-sourcing compiler negatives.

Split analysis: Atomic as an independent evidence verdict over one immutable candidate epoch.

Gate `G-W6` — owner: independent validation and human acceptance owners

Pass condition: Conformance evidence passes, vacuity mutations fail as expected, binding is current, and the exact candidate is explicitly accepted for migration rehearsal.

Failure action: `block`

## W7 — Rehearse bounded legacy migration

Layer: `L3`  
Depends on: `W6`  
Current state: `conditional-pending-accepted-W6-candidate`

Test an allowlisted legacy slice against the accepted candidate in isolation without mutating legacy sources or cutting over.

### SWU-W7-001

Primary behavior: Create an exact legacy inventory and mapping manifest for one owner-selected ontology slice.

Owner: migration owner

Write scope:

- `ontology-lifecycle/migration/<epoch>/manifest.json`

Done criteria:

- Every input path and digest is allowlisted.
- Every legacy shape is mapped, rejected, or carried as typed residue.
- The manifest grants no cutover authority.

Validation:

- `VAL-MIGRATION-REHEARSAL` — Every input is classified, every output has lineage, no legacy file is mutated, and no cutover occurs.

Split analysis: Atomic as one source-bound migration manifest.

### SWU-W7-002

Primary behavior: Replay the allowlisted legacy slice into an isolated empty event store and compare rebuilt projections.

Owner: migration validation owner

Write scope:

- `ontology-lifecycle/migration/<epoch>/fixtures/`
- `ontology-lifecycle/migration/<epoch>/receipt.json`

Done criteria:

- Legacy sources remain unchanged.
- Every output event has lineage.
- Projection bytes match the manifest expectation.
- No live cutover or publication occurs.

Validation:

- `VAL-MIGRATION-REHEARSAL` — Every input is classified, every output has lineage, no legacy file is mutated, and no cutover occurs.
- `VAL-REPLAY-EQUALITY` — Latest snapshots, ontology-at-cursor, governed-node view, and context-artifact view are byte-identical across rebuilds.

Split analysis: Atomic as one isolated rehearsal and receipt.

Gate `G-W7` — owner: migration validation owner

Pass condition: The allowlisted rehearsal targets the exact accepted W6 candidate, is lineage-complete, deterministic, non-destructive, and has no unclassified input.

Failure action: `block`

## W8 — Validate the complete candidate epoch

Layer: `L3`  
Depends on: `W7`  
Current state: `pending-all-prior-gates`

Run one collect-all aggregate validation over frozen W0-W7 bytes and issue a candidate verdict with an explicit authority ceiling.

### SWU-W8-001

Primary behavior: Execute and join every declared final validation against one immutable source epoch.

Owner: independent aggregate validation owner

Write scope:

- `ontology-lifecycle/conformance/<final-epoch>/`

Done criteria:

- All W0-W7 gates have passing receipts.
- All required validation ids run even when a predecessor blocks, with dependent results marked not_evaluable.
- Two-run outputs are byte-identical.
- Acceptance-critical residue is empty for PASS.
- The verdict states that PASS is candidate evidence, not admission, publication, deployment, or cutover authority.

Validation:

- `VAL-W0-DECISION` — One immutable selected, amended, or rejected decision receipt; only selected or amended-selected continues.
- `VAL-SCHEMA-NEGATIVE` — Valid fixtures pass; missing identity, invalid endpoints, collapsed confidence axes, and malformed challenge fields fail closed.
- `VAL-DOMAINSPEC-TWICE` — Both runs pass and generated graph/system-ontology bytes are identical.
- `VAL-EVENT-CONTRACT-TWICE` — Both checks pass with identical compiled contract and receipt identity.
- `VAL-DOMAINSPEC-BACKEND` — Type checking and the complete backend test suite pass, including event-sourcing compiler negatives.
- `VAL-RUST-RUNTIME` — Formatting and all runtime tests pass with the locked dependency set.
- `VAL-REPLAY-EQUALITY` — Latest snapshots, ontology-at-cursor, governed-node view, and context-artifact view are byte-identical across rebuilds.
- `VAL-VACUITY` — Each mutation causes its named invariant to fail; no test passes without exercising its bound invariant.
- `VAL-BINDING-CURRENTNESS` — All exact bindings resolve to current bytes and no implementation symbol is unbound.
- `VAL-MIGRATION-REHEARSAL` — Every input is classified, every output has lineage, no legacy file is mutated, and no cutover occurs.
- `VAL-AGGREGATE` — All prerequisite gates and validations pass; acceptance-critical residue is empty; the output remains candidate evidence only.

Split analysis: Indivisible terminal join: splitting the aggregate would permit partial PASS claims across different epochs.

Gate `G-W8-FINAL` — owner: independent aggregate validation owner

Pass condition: Every required check passes against the same frozen epoch and acceptance-critical residue is empty.

Failure action: `block-and-report-all`

## Terminal claim ceiling

- This package is a planning candidate, not canonical Invoke Plan v2 output.
- Validation of this package proves plan coherence and source currentness only.
- A future W8 PASS would prove a validated candidate for the frozen epoch, not ontology admission or acceptance.
- No wave authorizes publication, deployment, migration cutover, goal completion, or external effects.
