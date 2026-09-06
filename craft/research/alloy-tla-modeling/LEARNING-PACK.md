# Final Learning Pack

Profile: domainspec-v2-formal-modeling

Status: executable-surface-ready-with-residue

Promotion scope: local-research-only

## One Sentence

Alloy should prove useful first as a bounded graph counterexample engine, TLA+/PlusCal should prove useful first as a temporal saga model checker, and TypeScript should stay the extraction/witness layer that feeds both while DCB guards freshness of accepted evidence.

## Source-First Spine

| Layer | Source meaning | Closure artifact |
| --- | --- | --- |
| Alloy | Models structures with constraints and finds examples or counterexamples in scope. | `CLAIM-LEDGER.md` C1-C4 |
| TLA+/PlusCal | Models state-based behaviors above code, with TLC finite-model checking and PlusCal translation. | `CLAIM-LEDGER.md` C5-C8 |
| DomainSpec local witness | Existing TypeScript result is a bounded witness and DCB freshness rejection, not proof. | `CLAIM-LEDGER.md` C9-C10 |
| Operator bridge | TLA+ for temporal behavior, Alloy for graph completeness. | `CLAIM-LEDGER.md` C11-C12 |

## Notation Reading

Read `NOTATION-BRIDGE.md` before the examples. The key distinction is:

- Alloy `check` searches for bounded counterexamples to assertions.
- TLA+ `Init` and `Next` define possible behaviors; TLC checks finite models of those behaviors.

## Operator Model

```text
DomainSpec taxonomy and relationships
  -> TypeScript SagaSpec extractor
  -> bounded witness result
  -> choose hard class
     graph completeness -> Alloy check
     temporal behavior -> TLA+/PlusCal TLC model
  -> evidence result
  -> AcceptSagaProofFreshnessClaim only if freshness matters
```

## Tool-Run Evidence

| Surface | Result | Reading |
| --- | --- | --- |
| Toolchain | Portable Java 17.0.19, TLA+ tools v1.7.4, and Alloy 6.2.0 run from ignored `.formal-tools/`. | Ready for local research runs, not committed binaries. |
| Alloy | `showCompleteSaga` SAT; `findMissingCompensation` UNSAT; `checkCompensationCompleteness` has no counterexample in scope 8. | Bounded graph-completeness evidence for the current complete sketch. |
| TLA+ | SANY parses; TLC finds a `FreshnessSafety` violation after `Accepted` followed by waiver change. | Useful temporal residue; freshness semantics need repair or reframing. |
| Fixture contract | JSON Schema and example fixture validate as JSON. | Ready for review before generator code. |

## What To Borrow Carefully

- Alloy's bounded counterexample style for graph completeness.
- TLA+'s state-machine model for saga execution.
- PlusCal as an approachable authoring layer for the first temporal model.
- TLC as a finite-model checking gate.
- DCB read sets for non-rerunnable model evidence, waivers, receipts, or acceptance races.

## What To Keep Analogy-Only

- "Alloy/TLA proves DomainSpec correctness" as a broad slogan.
- "No counterexample" as "globally true."
- "Model checked" as "implementation verified."

## What To Block

- Calling the TypeScript bounded witness a proof.
- Calling DCB the behavioral proof engine.
- Mutating `TAXONOMY.md` or `RELATIONSHIPS.md` from this research tower.
- Registering or running a subagent dispatch without the strategy confirm gate.

## Closed Residue Summary

| Residue | Closure |
| --- | --- |
| Which tool first? | TypeScript stays first; Alloy/TLA are promotion lanes chosen by hard class. |
| Which formal lane for graph completeness? | Alloy. |
| Which formal lane for temporal behavior? | TLA+/PlusCal. |
| What does DCB do after formal modeling? | Freshness/acceptance, not behavior proof. |

## Remaining Honest Cutoff

The tower is closed for feasibility orientation, route selection, and local tool execution. It is not closed for:

- TLA+ freshness repair;
- fixture generator code;
- DomainSpec validator integration;
- proof claims stronger than bounded witness or finite-model check.

## Sources

See `SOURCE-RECORD.md`.
