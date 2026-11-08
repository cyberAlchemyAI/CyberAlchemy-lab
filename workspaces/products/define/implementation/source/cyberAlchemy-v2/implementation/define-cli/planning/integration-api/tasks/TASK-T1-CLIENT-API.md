# TASK T1 — Stable Define Client API

Layer: L1. Status: testable candidate complete. Authority effect: none.

## Objective

Expose start, resume, list stages, next question, submit response, inspect
readiness, confirm artifact, and export artifact through one transport-neutral
facade, then migrate CLI/chat adapters without changing semantics.

## Inputs And Outputs

Inputs are accepted L0 protocols and current session/durable runtimes. Outputs
are a closed Client API package, narrow public exports, consumer parity
fixtures, and migration evidence.

## Smallest Working Unit

One `createDefineClient` instance serves both a CLI fixture and chat fixture over
the same confirmed revision while raw adapters remain inaccessible to them.

## Ordered Rules

Map each client operation to one typed runtime command/read; preserve expected
revision and idempotency; record user postures without semantic inference;
separate inspect from confirm; require exact candidate bytes for confirmation;
return closed results with stable reason codes and no authority effect.

## Edge Cases And Failure Modes

Revision conflict, repeated command, denied actor context, deferred response,
cross-interface resume, incompatible schema, storage failure, and confirmation
against changed candidate bytes.

## Verification And Completion

All client operations have contract tests; current durable, conversation, CLI,
audit-minimization, and replay tests pass; no consumer invokes Module Port or an
adapter directly.

Observed candidate evidence on 2026-09-08:

- `createDefineClient` exposes exactly the eight named operations with closed,
  digest-bound, authority-none results;
- CLI and chat wrappers resumed and mutated one confirmed durable revision;
- answer, correction, refusal, and deferral postures remained explicit and
  replayable;
- exact candidate bytes were required at confirmation and again at export;
- revision conflict, idempotent retry, denied actor, incompatible schema,
  storage failure, and confirmation drift stayed distinct;
- the focused Client API suite passed twice at 8/8; and
- the complete Define test surface passed 60/60, while both Alch verifiers
  reported byte-identical regeneration.

The interactive Definition Pack CLI remains behaviorally unchanged. Selecting
whether it becomes an explicit built-in stage remains the design-owned open
question; this L1 candidate does not silently make that decision.

Open questions and blockers are owned by [the work pack](../WORK-PACK.md#blockers).
