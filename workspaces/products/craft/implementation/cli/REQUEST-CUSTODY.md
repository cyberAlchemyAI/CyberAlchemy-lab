# Candidate request custody binding

`compileRequestCustody` validates the closed
`domainspec.request-custody/v1-candidate` contract. It binds fingerprint identity,
scalar defaults, bounded retention/capacity/bytes/reservation time, the typed
boolean decision-policy interface, and a one-attempt/write-once lifecycle.
Expiry requires both local outcome and actual transport settlement.

The experimental runtime exports `RequestCustody` and
`createMemoryRequestCustody`. Atomic reservation returns execute with an opaque
store-local token, copied JSON replay, or a typed decision. beginAttempt rejects
forged/reused tokens and precedes transport. recordOutcome writes once;
markTransportSettled is independent and idempotent. Inspection returns metadata
only. The caller supplies a monotonic clock and matching deadline/abort control;
the Alch binding schedules the reservation deadline signal. Cancelled policy
work remains queue-bounded until it settles and cannot commit after cancellation.

This memory-only port is separate from operation-state `runtime/in-memory.ts`
and transactional state/outbox `runtime/durable.ts`. Neither existing runtime
supplies remote-attempt settlement semantics. It does not change frozen meta-types
or grant governance admission. Results and usage are bounded JSON whose concrete
shape belongs to the service's generated mapping contract.

Evidence: `test/generation/request-custody.test.ts` and the paired Alch
inference service custody artifact in its Craft context.

## Open Questions

Restart recovery and multi-host persistence remain separate backend choices.
The joint plan owns remaining service reuse and final tenant security work:
[service binding plan](/home/vlad_/projects/cyberAlchemy-v2/craft/projects/domainspec-v2/development/inference-service-binding-plan/PLAN.md).

## Explicit durable backend successor

The typed custody contract also admits `bounded-sqlite`. Its native binding is
`src/runtime/sqlite-request-custody.ts`: encrypted local SQLite with revision-
checked reservation, write-once outcomes and one persisted attempt. The generated
policy remains the decision owner. Retention requires both outcome and transport
settlement; interrupted requests remain unresolved and never automatically retry.
The operator supplies a private database path, a separate 32-byte key, fixed
limits and a wall-clock millisecond source. Memory behavior remains available.

Open Questions and exact candidate evidence are owned by the
durable inference custody plan (source binding requires reconciliation).

## Trusted operator reconciliation successor

`runtime/custody-reconciliation.ts` defines review/reconcile ports. The SQLite
adapter enables them only with an operator identity, current authorization and a
trusted terminal-evidence resolver. Exact record versions prevent stale closure;
confirmed closure preserves write-once outcomes and fences late execution-token
updates. Encrypted operator/evidence metadata follows normal custody retention.
Reconciliation never retries inference. Current inference authorization still
controls replay. No public operator HTTP permission is implied.

Open Questions and current candidate tests are owned by the
reconciliation plan (source binding requires reconciliation).
