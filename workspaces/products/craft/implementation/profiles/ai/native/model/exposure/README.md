# Shared model exposure owner

`index.mjs` exports `createExposureLedger({path,releasePort,now?,observer?})` and
`model-exposure-ledger/v1`. The host retains `authority`; checked model/agent
owners receive `port`. This is the authoritative local allocation ledger, not an
account-wide provider spending control. Apps sharing a cap must use this same
owner. No provider request or independent effect journal exists here.

Required behavior → existing capability → delta:

- **Reuse:** SQLite transactions and replay design (`craft.transactions`), the
  original R02/C11 intent and effect owner (`craft.external-effect-recovery`),
  and original source-release port. Existing generated business runtime stays.
- **New:** atomic request/attempt/token/maximum-cost reservations and shared
  billing-account/tenant/application allocation with explicit unknown exposure.
- **Configure:** trusted price-policy revision and defensible maximum possible
  charge for each paid request; no money cap is claimed without that bound.
- **Extend:** optional explicit agent run envelopes aggregate uniquely charged
  children; opaque managed accounting rejects until an enforceable bound exists.

Authority: `configureAllocation({id,billingAccount,tenant,application,maxAttempts,
maxTokens,maxCostMicros?})`; `application:'*'` applies the same shared cap across
apps in that billing account and tenant. All matching allocations must admit the
reservation atomically. Identity cannot change underneath an allocation.
`settle({reservationId,reason,actualTokens,actualCostMicros?})` is explicit host
reconciliation; it records an immutable review event and prevents later dispatch.
Missing settled cost retains the prior conservative monetary bound.

Port: `reserve({requestId,attemptId,billingAccount,tenant,application,modelId,
destination,resourceId,fence,promptSha256,inputSha256,payloadSha256,maxTokens,
maxCostMicros?,pricePolicyRevision?,runId?,childId?})` returns an opaque handle
with durable `.id`. Identical replay costs once; changed identity for the same
attempt rejects. Explicit retries need new attempt IDs and new reservations.
`recoverReservation(id)` restores a handle after restart. `inspect(handle)` and
`allocationSummary(id)` distinguish observed units, reserved maximum exposure
and unknown amounts. Monetary values are exact nonnegative decimal micro-units.

One model call uses this order:

1. Prepare an R02 effect attempt and reserve its maximum exposure.
2. Issue the source-owned single-use ticket for those exact bytes and destination.
3. `markRelease(reservation,{ticket})` checks the original ticket and stores its
   unique identity, complete binding digest and manifest ID.
4. `dispatch({reservation,dispatcher,attemptId,ticket,signal?})` durably checkpoints
   the attempt, then delegates to the original R02 effect owner, which retires
   custody, consumes the ticket and invokes the selected provider once.
5. The trusted model adapter calls `observeUsage(reservation,{attemptId,fence,
   inputTokens,outputTokens,costMicros?,receiptId})` only for validated actual usage.
   Duplicate exact observations replay; mismatched attempt/fence/receipt rejects.

`recordEstimate` records estimates without refund. `markUnknown` retains reserved
exposure on timeout, cancellation, missing usage and interrupted dispatch. Every
crash boundary remains conservatively charged; no transaction spans provider I/O.
Observed tokens without observed money reduce only token exposure. Counters use
exact integer arithmetic. A reported overrun remains visible as actual exposure
and prevents further admission when over cap; technical price/max-token selection
must establish the requested bound before promising a hard cap.

`createRun({runId,billingAccount,tenant,application,maxChildAttempts,maxTokens,
maxCostMicros?,accounting:'explicit'})` creates a resumable envelope. Child
reservations reference runId/childId and debit the same allocation once. Envelope
summaries aggregate child references with `summaryDebit:0`. Duplicate children
cannot spend again; unknown children retain their maximum. `runSummary(runId)`
survives restart. Opaque harness accounting is explicitly unsupported.

SQLite uses WAL/FULL durability and append-only reservation/run/event records.
Backups and schema upgrades must preserve reservation identities, all events,
source ticket provenance and the original effect database. There is no automatic
retention/deletion or destructive migration. Credential and provider retirement
stay owned by the original adapter/effect owner. Reconcile unresolved exposure
before retiring that owner's inspection/usage credentials.

## Open Questions

Actual provider/model qualification, authenticated distributed ownership and
unrelated provider-account spending are outside these local fixtures. Schema
upgrade implementation and retention duration require selected operator policy.
Final built artifact identities and the enclosing objective's single consolidated
proof remain owned by the root implementation.
