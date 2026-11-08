# Selected native effect dispatch

`index.mjs` exports `createEffectDispatcher` and `effects-dispatch/v1`. It imports
the existing public Core `DurableWriteIntentStore`; its prepare/dispatch retirement
and uncertainty state stay in that original journal. Adjunct SQLite rows describe
logical business intent, immutable selected-provider attempts and append-only
native observations. It does not create a business app, worker or retry loop.

**Reuse:** original C11 journal, intent identity and no-effect versus unknown
semantics (`craft.external-effect-recovery`); generated Auth/transaction and
event owners remain unchanged. **Extend:** finite local/model/document/index/
provider slots, native observation admission, source-owned release consumption,
enforced provider/account/operation rate/concurrency/circuit bounds, explicit
attempt/backoff/deadline budget and original-provider inspection. DemoPay's
checked observation is never relabelled as a different provider result.

Create with `{path,slots,releasePort,assertCurrent,now?,policy?}`. `assertCurrent`
must synchronously return `true` only for current tenant/resource/action,
approval/source revisions and execution fence. Slots are selected trusted native
code `{id,kind,provider,account,operation,resourceId,action,execute,inspect?,
validateObservation,sink?,recipient?,requiresRelease?}`. No unrestricted plugin
executor or default fetch exists. All caller sends require source release by
default; disable it only for an explicitly selected local capability with no
derived disclosure. Slot execution and SDK transports must have retries disabled:
this owner admits one invocation per attempt.

`prepare({intentId,slotId,tenant,principal,resourceId,action,approvalRevision,
sourceRevision,fence,payload,deadlineAt,cause,retryOf?})` returns `{attemptId,...}`.
`dispatch({attemptId,ticket,signal?})` sends owned exact bytes after durable
retirement and release consumption. `getAttempt(id)` replays status.
`inspect`/`reconcile({attemptId,signal?})` consult only the original provider;
`validateObservation(result,attempt)` must admit provider-specific evidence for
`confirmed` or `no-effect`. Malformed/timeout/cancel/unverified outcomes are
`unknown`. An explicit retry after validated no-effect creates a new immutable
attempt; no retry follows unknown. Alternate providers additionally require
explicit configured policy. No automatic fallback exists. Terminal no-effect observations (`retryable: false`) do not admit another attempt. Malformed repeatability or delay metadata is not permission to retry.

`retryStatus({attemptId,deadlineAt?,binding?})` and `scheduleRetry` return a
read-only schedule derived from existing durable attempt/observation timestamps;
no second retry journal or automatic send loop is created. The result is due,
waiting with `notBefore`, or blocked with a reason, plus original intent/attempt,
root deadline and attempt/send counts. The provider Retry-After minimum and
original selected backoff are preserved across restart; a required wait past the
original root dispatch deadline blocks instead of shortening it. A retry may use
a shorter deadline, never extend that logical action's original deadline. A
fresh original fence can be supplied in `binding`; all other scope/revision
fields must match, and the original current-authority callback validates it.
`prepare(...retryOf)` enforces these requirements even if a planner lies about
readiness. Root send/inspection budget snapshots cannot be relaxed by reopening
with a larger policy. Existing rows without the new policy snapshot remain
replayable/inspectable, but automatic retry is explicitly blocked as
legacy-policy-unverified; old backoff/provider requirements cannot be inferred.

Inspection records and completion rows are append-only in the same SQLite
owner. Inspection budget is independent of send and credential refresh budgets;
concurrent/restarted owners cannot duplicate a still-live inspection lease.
`inspect({attemptId,signal?,deadlineAt?})` performs current authorization before
wire and even before returning a cached result. Its recovery lifecycle may
outlive the original send deadline, but uses its own bounded inspection timeout
and durable budget. A caller-supplied inspection deadline can shorten that bound.
An expired inspection lease permits another safe original-provider inspection,
not a repeated mutation. Historical inspections before these new adjunct tables
are not retrospectively counted or qualified.


Policy defaults: three send attempts, eight separately metered inspections per intent, two concurrent inspections, two concurrent unresolved dispatches, sixty
dispatches per sixty seconds, circuit after three unknowns for thirty seconds,
thirty-second native and inspection deadlines, no alternate-provider retry. Unknowns retain
conservative concurrency exposure. Original inspect reconciles them. Budgets
apply to provider/account/operation across slots. No lock spans native awaits.
Fresh current authority is checked at dispatch and observation commit. A stale
completion remains unknown. Prepared attempts reopened after process exit cannot
mint a second original journal permit; inspect or explicit review is required.

Setup uses existing local Node/SQLite; credentials stay in selected adapter
owners. Database backup/migration must preserve the journal and immutable adjunct
rows together; there is no destructive auto-upgrade. `retireProvider` prevents
new attempts, retains original inspect code and requires explicit review when
unresolved attempts remain. Preserve old credentials/inspection until resolved.
Metadata retention has no automatic deletion API.

## Open Questions

Real provider protocol/account qualification is unrun; selected adapters must
prove their own definitive inspection semantics. These tests cover local trusted
fixtures and actual SQLite restart only. Final artifacts and combined regression
evidence belong to the enclosing objective's single consolidated proof.

Source-selected longer backoff uses `scheduleRetry({attemptId, binding, notBefore,
deadlineAt})` on this same owner. The append-only `fx_retry_plans` rows cannot
shorten the provider/owner minimum or extend the original deadline. A shortened
plan deadline applies to later attempts of that intent too. `retryStatus` and
`prepare(retryOf)` enforce the retained plan across restart; scheduling never
sends a request. The generated workflow's quiescent wait merely coordinates this
owner and reacquires a fresh fence when due.
