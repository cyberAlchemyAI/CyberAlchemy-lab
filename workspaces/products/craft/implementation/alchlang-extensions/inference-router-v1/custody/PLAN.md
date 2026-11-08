# ISB-07 request custody construction

Completed owner-directed local candidate. Basis: [ISB-02 dependency meanings](../service-contracts-v1/README.md),
[signatures](../service-contracts-v1/dependencies.d.ts), [support audit](../SUPPORT-MATRIX.md)
and [service plan](../SERVICE-PLAN.md). Authority effect: none.

## D65 construction chain

1. Reuse the Define-backed reservation, attempt, local outcome and independent
   transport settlement meanings, plus the existing business/product scaffolds.
2. Author identity defaults, fingerprint exclusions, retention bounds, compiled
   decision module and memory lifecycle in [request-custody.alch](../request-custody.alch).
3. Lower to a closed candidate DomainSpec custody contract. Compile the existing
   [idempotency policy](../idempotency-policy.alch) as a pure local module.
4. Generate the dispatcher binding and bundle inventory. Bind the DomainSpec
   memory implementation; enforce beginAttempt before generated HTTP sendOnce.
5. Prove port conformance, generated bundle integrity and the existing service
   regressions, then record paired Craft evidence.

## Reuse decision

DomainSpec `impl/cli/src/runtime/in-memory.ts` evaluates operation state; it does
not retain request-key reservations. `impl/cli/src/runtime/durable.ts` commits
state and outbox messages atomically; its commit acknowledgement does not prove
settlement of an already-running remote HTTP attempt. The concern-specific
RequestCustody interface therefore has a bounded memory implementation separate
from those runtimes. Their behavior and durable outbox contracts are unchanged.

## Open Questions

Owned by [README](README.md#open-questions). No blocking local construction question.
