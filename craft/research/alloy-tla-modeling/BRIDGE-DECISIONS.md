# Bridge Decisions

Status: pass

## Decision Table

| Candidate | Decision | Use when | Do not use when | Required evidence |
| --- | --- | --- | --- | --- |
| TypeScript bounded witness | borrow-carefully | Need fast repo-local extraction, graph sanity, bounded traces, and DCB read-set construction. | Need a formal proof claim. | `tsx` or `tsc` run plus result JSON/MD. |
| Alloy static graph model | promotion-candidate | Need bounded counterexamples for participants, operation ownership, compensation links, typed edges, and relationship coverage. | The hard question is long-running temporal execution. | Alloy command, scope, analyzer result, counterexample or no-counterexample statement. |
| Alloy 6 temporal model | future-work | A graph-heavy model needs a small amount of mutable state or temporal checking. | It would duplicate a cleaner TLA+ execution model. | Explicit justification plus tool dependency setup. |
| TLA+/PlusCal with TLC | promotion-candidate | Need finite-model checks over saga state, traces, compensation, retries, and freshness acceptance. | The question is only missing relationships or static graph completeness. | TLA+ module, config/model, TLC result, state-space/scope notes. |
| TLAPS | future-work | A stable TLA+ theorem deserves deductive proof beyond finite-model checking. | The model is still changing or the theorem is not small. | TLAPS proof artifact and proof-check result. |
| DCB freshness acceptance | borrow-carefully | A model verdict, waiver, external receipt, or correctness claim depends on facts that may change after a read marker. | Facts are deterministic and cheap to rerun or content-hash. | Read set, stale/current facts, accepted/rejected command result. |
| "Alloy or TLA as proof engine for all DomainSpec" | block | n/a | Always too broad for this tower. | No promotion path. |

## Immediate Recommendation

Create two follow-up `task-session` slices:

1. Alloy graph check:
   - take the existing `OrderFulfillmentSaga` fixture;
   - encode participants, forward operations, compensations, and typed edges;
   - run an assertion that every completed forward operation has compensation or terminal policy;
   - preserve the `orchestrates` Saga-vs-Workflow residue.
2. TLA+ temporal check:
   - encode the bounded trace as `Init` and `Next`;
   - check success safety and failure safety;
   - add freshness rejection as a separate action;
   - record model scope and TLC result.

## Promotion Guardrail

Promotion into DomainSpec validators or templates requires a separate approved task. This tower can recommend the lanes; it must not mutate canonical taxonomy or relationship definitions.
