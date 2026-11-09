# Governed ontology node continuous implementation plan

Plan ID: `CAL-PLAN-0002`  
Status: `planning-candidate-blocked-at-w0`  
Execution authority: `none`

## Outcome

Evolve the existing thin event-sourced ontology witness into a stable governed-node model whose canonical events calculate semantic and governance projections, then validate the complete candidate in one aggregate terminal wave.

This is a non-executing successor plan. It preserves the current thin deterministic witness and starts at the unresolved governed-node architecture decision. A future terminal PASS proves only a validated candidate for one frozen epoch.

## Continuous path

```text
W0 architecture selection
 -> W1 definitions and schemas
 -> W2 Product Capability and business ontology
 -> W3 authored DomainSpec and event-source contract
 -> W4 deterministic graph and system ontology
 -> W5 Rust reducer and projections
 -> W6 exact binding and non-vacuous conformance
 -> W7 isolated migration rehearsal
 -> W8 aggregate immutable-epoch validation
```

Each wave has a local gate. W8 joins all evidence; it does not postpone basic validation or grant acceptance.

## Preserved evidence

- The current event-sourcing contract compiles deterministically.
- The current Rust witness has 12 focused passing tests.
- Semantic and governance streams already have an exact-reference join candidate.

## Open blockers

- `BLK-ARCH-SELECTION` blocks `W0`: CAL-PROP-0004 is a draft successor candidate with decision_posture not-selected. Resolution: A human owner selects, amends, or rejects the exact proposal digest.
- `BLK-DESIGN-ADMISSION` blocks `W1`: Invoke Plan v2 requires exact admitted Design source and admission receipts, which do not exist for this successor architecture. Resolution: After W0 selection, author and admit the governed Design package before design-dependent execution.
- `BLK-PROFILE-ADMISSION` blocks `W4`: The current DomainSpec development profile is not admitted. Resolution: Obtain owner-bound admission for the exact profile/source epoch; do not refresh status fields to simulate it.

## Waves

| Wave | Layer | Outcome | Gate owner | Current state |
|---|---|---|---|---|
| `W0` | `L0` | Bind one immutable architecture decision before any successor design or implementation bytes change. | human architecture owner | `blocked-human-decision` |
| `W1` | `L0` | Define the smallest stable node, relation, challenge-contract, and context-selector contract without implementation leakage. | definitions and ontology contract owners | `pending-prerequisites` |
| `W2` | `L0` | Make the selected governed-node behavior an explicit product capability and capability-local business ontology before DomainSpec authoring. | Product Capability and business ontology owners | `pending-prerequisites` |
| `W3` | `L1` | Represent the selected product and ontology semantics as authored DomainSpec source before compilation. | DomainSpec source owners | `pending-prerequisites` |
| `W4` | `L1` | Produce byte-stable compiled graph, event contract, and system ontology from the exact authored source epoch. | DomainSpec compiler and profile admission owners | `pending-prerequisites-and-profile-admission` |
| `W5` | `L2` | Implement only the compiled contract in Rust: append validation, deterministic reduction, exact joins, and rebuildable projections. | Rust runtime owner | `pending-prerequisites` |
| `W6` | `L2` | Bind every compiled obligation to exact Rust symbols and non-vacuous evidence, while exposing all residue. | independent validation and human acceptance owners | `pending-prerequisites` |
| `W7` | `L3` | Test an allowlisted legacy slice against the accepted candidate in isolation without mutating legacy sources or cutting over. | migration validation owner | `conditional-pending-accepted-W6-candidate` |
| `W8` | `L3` | Run one collect-all aggregate validation over frozen W0-W7 bytes and issue a candidate verdict with an explicit authority ceiling. | independent aggregate validation owner | `pending-all-prior-gates` |

## Final validation

All required checks PASS on one frozen epoch, all predecessor gates PASS, no selected source digest drifts, and acceptance-critical residue is empty.

Required checks:

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

## Execution boundary

Next route: `decision-gate`. Task Session allowed: `false`. W0 architecture selection and admitted Design receipts are absent.

Claim ceiling:

- This package is a planning candidate, not canonical Invoke Plan v2 output.
- Validation of this package proves plan coherence and source currentness only.
- A future W8 PASS would prove a validated candidate for the frozen epoch, not ontology admission or acceptance.
- No wave authorizes publication, deployment, migration cutover, goal completion, or external effects.
