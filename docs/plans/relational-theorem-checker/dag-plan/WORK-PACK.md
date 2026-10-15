# Work pack

> Generated from [PLAN-SOURCE.json](../PLAN-SOURCE.json).
> Standalone candidate. 33/35 tasks accepted with hash-bound evidence; see task receipts for review scope. No formal Invoke admission is claimed.

## Task board

| Task | Layer / wave | Accepted prerequisites | Working units | Validation |
|---|---|---|---|---|
| [P01 — Define the relational semantics and theorem targets](work-pack/tasks/P01.md) | L0 / W00 | none | SWU-P01-1 | V-P01 |
| [P03 — Formalize typed graphs and independent validity predicates](work-pack/tasks/P03.md) | L0 / W01 | P01 | SWU-P03-1 | V-P03 |
| [P04 — Define the reference checker in Lean](work-pack/tasks/P04.md) | L0 / W02 | P03 | SWU-P04-1 | V-P04 |
| [P05 — Prove and review general reference-checker soundness](work-pack/tasks/P05.md) | L0 / W03 | P04 | SWU-P05-1 | V-P05 |
| [B00 — Refresh the execution baseline after formalization](work-pack/tasks/B00.md) | L0 / W04 | P05 | SWU-B00-1 | V-B00 |
| [P02 — Align schemas and implement decoding from the formal model](work-pack/tasks/P02.md) | L0 / W05 | B00 | SWU-P02-1 | V-P02 |
| [P06 — Produce a bound demonstration and hostile controls](work-pack/tasks/P06.md) | L0 / W06 | P02, P04, P05 | SWU-P06-1 | V-P06 |
| [G0 — Review the working proof gate](work-pack/tasks/G0.md) | L0 / W07 | P06 | SWU-G0-1 | V-G0 |
| [C01 — Resolve the effective registry snapshot](work-pack/tasks/C01.md) | L1 / W08 | G0 | SWU-C01-1 | V-C01 |
| [C02 — Reconcile carrier and registry coverage](work-pack/tasks/C02.md) | L1 / W09 | C01 | SWU-C02-1 | V-C02 |
| [C03 — Generalize registry-driven checking](work-pack/tasks/C03.md) | L1 / W10 | C01, C02 | SWU-C03-1, SWU-C03-2 | V-C03 |
| [C04 — Resolve qualified references](work-pack/tasks/C04.md) | L1 / W11 | C01, C03 | SWU-C04-1 | V-C04 |
| [C05 — Measure semantic coverage and exercise the baseline](work-pack/tasks/C05.md) | L1 / W12 | C03, C04 | SWU-C05-1 | V-C05 |
| [C06 — Make replay deterministic and invalidate stale evidence](work-pack/tasks/C06.md) | L1 / W13 | C05 | SWU-C06-1 | V-C06 |
| [G1 — Review the faithful baseline gate](work-pack/tasks/G1.md) | L1 / W14 | C05, C06 | SWU-G1-1 | V-G1 |
| [E01 — Classify relation-change proposals](work-pack/tasks/E01.md) | L2 / W15 | G1 | SWU-E01-1 | V-E01 |
| [E02 — Derive the required obligation set](work-pack/tasks/E02.md) | L2 / W16 | E01 | SWU-E02-1 | V-E02 |
| [E03 — Check compatibility and prove preservation](work-pack/tasks/E03.md) | L2 / W17 | E02 | SWU-E03-1, SWU-E03-2 | V-E03 |
| [E04 — Check inhabited models and conservative expansions](work-pack/tasks/E04.md) | L2 / W17 | E02 | SWU-E04-1 | V-E04 |
| [E05 — Compose the compatibility and invalidation report](work-pack/tasks/E05.md) | L2 / W18 | E03, E04 | SWU-E05-1 | V-E05 |
| [G2 — Review supported non-rule extension readiness](work-pack/tasks/G2.md) | L2 / W19 | E05 | SWU-G2-1 | V-G2 |
| [I01 — Specify the restricted inference and root profile](work-pack/tasks/I01.md) | L3 / W20 | G2, E02 | SWU-I01-1 | V-I01 |
| [I02 — Check derivation certificates and prove soundness](work-pack/tasks/I02.md) | L3 / W21 | I01 | SWU-I02-1, SWU-I02-2 | V-I02 |
| [I03 — Check the least fixed point and completeness](work-pack/tasks/I03.md) | L3 / W22 | I02 | SWU-I03-1, SWU-I03-2 | V-I03 |
| [I04 — Prove protected lineage through indirect chains](work-pack/tasks/I04.md) | L3 / W23 | I02, I03 | SWU-I04-1 | V-I04 |
| [I05 — Check independence and non-entailment witnesses](work-pack/tasks/I05.md) | L3 / W21 | I01, E04 | SWU-I05-1 | V-I05 |
| [I06 — Discharge rule-change extension obligations](work-pack/tasks/I06.md) | L3 / W24 | I04, I05, E02, E05 | SWU-I06-1 | V-I06 |
| [G3 — Review inference discipline](work-pack/tasks/G3.md) | L3 / W25 | I03, I06 | SWU-G3-1 | V-G3 |
| [R01 — Define CLI and outcome contracts](work-pack/tasks/R01.md) | L4 / W26 | G3 | SWU-R01-1 | V-R01 |
| [R02 — Verify proof submissions and fresh replay](work-pack/tasks/R02.md) | L4 / W26 | G3, P05 | SWU-R02-1 | V-R02 |
| [R03 — Verify evidence bundles and aggregate obligations](work-pack/tasks/R03.md) | L4 / W27 | R01, R02, C06, E02, I06 | SWU-R03-1, SWU-R03-2 | V-R03 |
| [R04 — Integrate CLI and CI diagnostics](work-pack/tasks/R04.md) | L4 / W28 | R01, R03 | SWU-R04-1 | V-R04 |
| [R05 — Recheck the application baseline in a candidate adapter](work-pack/tasks/R05.md) | L4 / W28 | R03, C06 | SWU-R05-1 | V-R05 |
| [R06 — Run a representative shadow pilot](work-pack/tasks/R06.md) | L4 / W29 | R04, R05 | SWU-R06-1 | V-R06 |
| [G4 — Review supported use and audit plan alignment](work-pack/tasks/G4.md) | L4 / W30 | R06 | SWU-G4-1 | V-G4 |

Accepted tasks and working units: **P01, P03, P04, P05, B00, P02, P06, G0, C01, C02, C03, C04, C05, C06, G1, E01, E02, E03, E04, E05, G2, I01, I02, I03, I04, I05, I06, G3, R01, R02, R03, R04, R05**. Remaining tasks are **not-started**. F0 ownership and author self-review are recorded in task evidence.

## Working-unit policy

Units run in their listed order. The first unit depends on the final accepted unit of every prerequisite task. Split tasks require both units before task validation. Acceptance is evaluated against task criteria, not output filenames.

## Shared context

- [Context and trust boundaries](work-pack/shared/context.md)
- [Cross-task gaps](work-pack/shared/cross-task-gaps.md)
- [Cross-task decisions](work-pack/shared/cross-task-decisions.md)
- [Traceability](work-pack/shared/traceability.md)
- [Working-unit manifest](swu-manifest.json)
