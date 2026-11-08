# Task Session Report: DCB Saga Correctness Toy Game

Date: 2026-06-16
Task: execute toy game from `HANDOFF.md`
Result: PASS

## Scope

Executed one bounded task: build and run the TypeScript toy harness for
`OrderFulfillmentSaga`.

Write scope:

- `projects/domainspec-v2/research/dcb-saga-correctness/toy-harness/`
- `projects/domainspec-v2/research/dcb-saga-correctness/toy-run-result.md`
- `projects/domainspec-v2/research/dcb-saga-correctness/toy-run-result.json`
- `projects/domainspec-v2/research/dcb-saga-correctness/session-evidence/`

No DomainSpec taxonomy, relationship, template, validator, or generated registry
files were changed.

## Context Pack

Context pack:

```text
projects/domainspec-v2/research/dcb-saga-correctness/session-evidence/20260616-toy-game-context-pack.md
```

Strict coverage: pass.

Controlling sources:

- `HANDOFF.md`
- `TOY-RUN-PLAN.md`
- `TOY-SAGA-SCENARIO.md`
- `PROOF-OBLIGATIONS.md`
- `MODEL-CHOICE.md`
- `SYNTHESIS.md`
- `RESIDUE.md`
- `dcb-saga-correctness-research.dispatch.json`

## Decisions

Resolved decisions:

1. Use TypeScript bounded witness first.
2. Use `AcceptSagaProofFreshnessClaim`, not `AcceptSagaCorrectnessClaim`.
3. Include `HumanWaiverApplied(waiver:ship-after-payment-timeout-v1)` and
   `ExternalEvidenceReceiptRecorded(payment-auth-provider-r42)` as
   non-rerunnable evidence.
4. Use per-dependency hashes for deterministic facts.
5. Preserve `Saga -> orchestrates -> Operation[]` as graph residue instead of
   mutating `RELATIONSHIPS.md`.

Blocker decisions: none.

## Gate Verdict

Pass.

- Scope is bounded to the DCB saga research packet.
- Existing TS tooling is available through
  `implementation/domainspec/backend/node_modules/.bin/tsx`.
- Prior dispatch subagent lifecycle is closed and validator-clean.
- No consequential unresolved choice remained before mutation.

## Execution

Added:

- `toy-harness/saga-spec.ts`
- `toy-harness/order-fulfillment.fixture.ts`
- `toy-harness/run-toy.ts`

Generated:

- `toy-run-result.json`
- `toy-run-result.md`

The toy implements:

```text
SagaSpec
  -> validateGraph(spec)
  -> enumerateRuns(spec)
  -> assertBehavioralObligations(run)
  -> buildReadSet(facts)
  -> AcceptSagaProofFreshnessClaim
```

## Validation

Commands:

```bash
implementation/domainspec/backend/node_modules/.bin/tsx projects/domainspec-v2/research/dcb-saga-correctness/toy-harness/run-toy.ts
implementation/domainspec/backend/node_modules/.bin/tsc --noEmit --target ES2022 --module NodeNext --moduleResolution NodeNext --allowImportingTsExtensions --types node --typeRoots implementation/domainspec/backend/node_modules/@types --skipLibCheck projects/domainspec-v2/research/dcb-saga-correctness/toy-harness/saga-spec.ts projects/domainspec-v2/research/dcb-saga-correctness/toy-harness/order-fulfillment.fixture.ts projects/domainspec-v2/research/dcb-saga-correctness/toy-harness/run-toy.ts
python3 -m json.tool projects/domainspec-v2/research/dcb-saga-correctness/toy-run-result.json >/tmp/dcb-saga-toy-result.json
python3 arcanum/formulae/dispatch-spec/scripts/validate-dispatch.py projects/domainspec-v2/research/dcb-saga-correctness/dcb-saga-correctness-research.dispatch.json
python3 - <<'PY'
import json
p='projects/domainspec-v2/research/dcb-saga-correctness/toy-run-result.json'
obj=json.load(open(p))
checks = {
  'scenario': obj['scenario'] == 'OrderFulfillmentSaga',
  'bounded': obj['witness_kind'] == 'bounded',
  'graph_flag': obj['graph_witness'] == 'flag',
  'behavior_pass': obj['behavioral_witness'] == 'pass',
  'freshness_rejected': obj['freshness_claim'] == 'rejected',
  'command': obj['command'] == 'AcceptSagaProofFreshnessClaim',
  'all_assertions_pass': all(a['status'] == 'pass' for a in obj['behavior']['assertions']),
}
if not all(checks.values()):
    raise SystemExit(1)
PY
```

Results:

- toy run: pass
- TypeScript typecheck: pass
- JSON parse: pass
- dispatch validation: pass
- acceptance checks: pass

## Evidence Summary

`toy-run-result.json` records:

- `scenario = OrderFulfillmentSaga`
- `witness_kind = bounded`
- `graph_witness = flag`
- `behavioral_witness = pass`
- `freshness_claim = rejected`
- `command = AcceptSagaProofFreshnessClaim`
- `stale_fact = HumanWaiverApplied:waiver:ship-after-payment-timeout-v1`
- all behavioral assertions pass

Graph flag is expected and preserves residue:

```text
orchestrates signature for Saga is residue: RELATIONSHIPS.md types orchestrates as Workflow -> Operation[].
```

## Subagent Closeout

This task-session spawned no new subagents.

Inherited dispatch subagent lifecycle:

- spawned: 5
- joined: 5
- closed: 5
- open: 0
- status: pass

Reroute/residue paths:

- `RESIDUE.md`
- `SYNTHESIS.md`
- `MODEL-CHOICE.md`
- `PROOF-OBLIGATIONS.md`
- `TOY-RUN-PLAN.md`

## Follow-Up

Optional next route:

- Promote the toy to TLA+/PlusCal if temporal interleaving becomes the hard
  class.
- Promote to Alloy if graph completeness becomes the hard class.
- Resolve `orchestrates` and compensation semantics through a later governance
  task before claiming canonical proof readiness.
