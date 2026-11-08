# Context Pack: DCB Saga Correctness Toy Game

Status: task-session context pack
Date: 2026-06-16
Task: execute toy game from `HANDOFF.md`
Mode: standard

## Task Contract

Implement a small TypeScript bounded witness under:

```text
projects/domainspec-v2/research/dcb-saga-correctness/toy-harness/
```

Required outputs:

```text
projects/domainspec-v2/research/dcb-saga-correctness/toy-run-result.md
projects/domainspec-v2/research/dcb-saga-correctness/toy-run-result.json
```

## Obligations

| ID | Obligation | Evidence |
| --- | --- | --- |
| O1 | Include `OrderFulfillmentSaga`. | `HANDOFF.md`, `TOY-SAGA-SCENARIO.md` |
| O2 | Use TypeScript as a bounded witness, not a proof. | `MODEL-CHOICE.md`, `SYNTHESIS.md` |
| O3 | Check graph completeness and preserve Saga `orchestrates` residue as a flag. | `PROOF-OBLIGATIONS.md`, `RESIDUE.md`, `TOY-RUN-PLAN.md` |
| O4 | Check at least one bounded behavioral obligation. | `TOY-SAGA-SCENARIO.md`, `TOY-RUN-PLAN.md` |
| O5 | Include one non-rerunnable fact or concurrent race. | `TOY-SAGA-SCENARIO.md` |
| O6 | Use hashes/rerun semantics for deterministic facts. | `PROOF-OBLIGATIONS.md`, `SYNTHESIS.md` |
| O7 | Reject one stale `AcceptSagaProofFreshnessClaim`. | `HANDOFF.md`, `TOY-SAGA-SCENARIO.md` |
| O8 | Do not mutate taxonomy, relationships, templates, validators, or generated registries. | `HANDOFF.md`, `MODEL-CHOICE.md` |

Coverage: pass.

## Selected Sources

- `HANDOFF.md`: task objective, write scope, acceptance criteria, stop conditions.
- `TOY-RUN-PLAN.md`: expected files, harness shape, graph/behavior/freshness checks.
- `TOY-SAGA-SCENARIO.md`: participants, operations, waiver, external receipt, bounded run.
- `PROOF-OBLIGATIONS.md`: graph, temporal, and DCB claim obligations.
- `MODEL-CHOICE.md`: TypeScript-first bounded witness decision.
- `SYNTHESIS.md`: proof/freshness split and DCB guardrail.
- `RESIDUE.md`: orchestrates signature, compensation, participant, DCB evidence, read-marker residue.
- `dcb-saga-correctness-research.dispatch.json`: prior subagent lifecycle closeout.
- `implementation/domainspec/backend/package.json`: local `tsx` availability via backend workspace.

## Decisions

Resolved by controlling artifacts:

- Use TypeScript bounded witness first.
- Name the freshness command `AcceptSagaProofFreshnessClaim`.
- Use a human waiver plus external receipt as the non-rerunnable class.
- Use per-dependency hashes for deterministic facts.
- Treat `Saga -> orchestrates -> Operation[]` as graph residue instead of mutating relationship definitions.

## Gate Verdict

Pass. No blocker-level user decision is required before mutation because the
controlling artifacts already select the implementation path and write scope.

## Validation Surface

Run:

```bash
implementation/domainspec/backend/node_modules/.bin/tsx projects/domainspec-v2/research/dcb-saga-correctness/toy-harness/run-toy.ts
python3 -m json.tool projects/domainspec-v2/research/dcb-saga-correctness/toy-run-result.json >/tmp/dcb-saga-toy-result.json
python3 arcanum/formulae/dispatch-spec/scripts/validate-dispatch.py projects/domainspec-v2/research/dcb-saga-correctness/dcb-saga-correctness-research.dispatch.json
```
