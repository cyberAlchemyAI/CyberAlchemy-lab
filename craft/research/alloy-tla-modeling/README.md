# Alloy And TLA Modeling Research Tower

Status: executable-surface-ready-with-residue

Promotion scope: local-research-only

## Source Boundary

- Primary sources:
  - Alloy Tools official site, about page, documentation page, FAQ, and command docs.
  - Leslie Lamport's TLA+ pages, the TLA+ tools repository, and the TLA+ Toolbox paper.
- Local sources:
  - `arcanum/definitions/TAXONOMY.md`
  - `arcanum/definitions/RELATIONSHIPS.md`
  - `projects/domainspec-v2/research/dcb-saga-correctness/`
- Date checked: 2026-06-16
- Non-goals:
  - Do not claim a formal proof from this tower.
  - Do not mutate DomainSpec taxonomy, relationships, templates, validators, or generated registries.
  - Do not register or run a subagent dispatch without the `/domainspec-subagents-strategy` human confirm gate.

## One-Sentence Result

Use Alloy for bounded DomainSpec relationship and graph-completeness counterexamples, use TLA+/PlusCal for saga execution and temporal obligations, and keep TypeScript as the repo-local extraction plus bounded-witness layer. The local tool surface now runs, but the TLA+ freshness model has repair residue.

## Reading Order

1. `README.md`
2. `TOWER.md`
3. `SOURCE-RECORD.md`
4. `NOTATION-BRIDGE.md`
5. `CLAIM-LEDGER.md`
6. `GLOSSARY.md`
7. `DEFINITIONS.md`
8. `DISTILL.md`
9. `BRIDGE-DECISIONS.md`
10. `LEARNING-PACK.md`
11. `subagents/PROPOSED-DISPATCH.md`
12. `examples/README.md`

## Artifact Index

| Artifact | Role | Status |
| --- | --- | --- |
| `README.md` | Tower entry point and closure summary | pass |
| `TOWER.md` | Research frame, lanes, and target problem | pass |
| `SOURCE-RECORD.md` | Source boundary with dates and labels | pass |
| `CLAIM-LEDGER.md` | Source-backed and local-inference claim table | pass |
| `NOTATION-BRIDGE.md` | Minimal formal notation bridge | pass |
| `GLOSSARY.md` | Local operator glossary | pass |
| `DEFINITIONS.md` | Definition cards for tower terms | pass |
| `DISTILL.md` | Smallest usable operator model | pass |
| `RELATED-FRAMEWORK-CROSSWALK.md` | Bounded related-framework crosswalk | pass |
| `BRIDGE-DECISIONS.md` | Borrow/block/promotion decisions | pass |
| `LEARNING-PACK.md` | Final learning pack for reuse | executable-surface-ready-with-residue |
| `levels/L0-corpus.md` | Corpus inventory | pass |
| `levels/L1-residue-map.md` | Residue map | pass |
| `levels/L2-closure-plan.md` | Closure and next-run plan | pass |
| `gates/closure-gates.md` | Research-tower validation gates | pass |
| `residue/open-residue.md` | Open residue ledger | pass |
| `SUBAGENT-CLOSEOUT.md` | Subagent closeout ledger | not-used |
| `subagents/PROPOSED-DISPATCH.md` | `/domainspec-subagents-strategy` proposed dispatch sheet | proposed |
| `invoke-plan/WORK-PACK.md` | Executable invoke plan for installing Alloy/TLA tooling and validation surface | completed-with-residue |
| `invoke-plan/IMPLEMENTATION-LAYERING.md` | L0-L3 rollout boundary for the formal-tooling surface | pass |
| `invoke-plan/EXECUTION-PACK.md` | Wave choreography for the install and validation plan | pass |
| `tooling/README.md` | Local wrapper and cache policy | pass |
| `fixtures/README.md` | Formal fixture contract notes | pass |
| `examples/OrderFulfillmentSaga.alloy` | Alloy sketch for graph completeness | bounded-pass-with-syntax-repair |
| `examples/OrderFulfillmentSaga.tla` | TLA+ sketch for temporal saga behavior | counterexample-captured |

## Closure Gates

- Source claims labeled: pass
- Notation explained: pass
- Glossary and definitions complete: pass
- Related work bounded: pass
- Subagent closeout: not-used
- Promotion boundary explicit: pass
- Final learning pack complete: partial
- Formal tool validation: partial-with-evidence
  - Alloy bounded graph check: pass in scope 8.
  - TLA+ safety check: freshness counterexample captured.

## Next Execution Plan

Use [invoke-plan/WORK-PACK.md](invoke-plan/WORK-PACK.md) for execution evidence.
Next work should repair or reframe the TLA+ freshness semantics, then decide
whether to add generator code from the formal fixture contract.
