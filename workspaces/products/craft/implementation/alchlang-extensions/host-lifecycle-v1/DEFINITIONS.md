# Lifecycle prototype definitions

Host-owned candidate meanings; no canonical vocabulary promotion.

Selection binds tenant/project/function to revision and route epoch. Desired mode
is durable accepting or draining intent. Runtime generation is an opaque random
identity persisted before each launch; it is distinct from storage generation.
A fence hashes selection, route epoch, lifecycle version and runtime generation.

Drain closes invocation admission and finishes existing event delivery. Failure or
timeout leaves admission closed. Drained means no active invocation, pending/leased
outbox rows or dead letters. Resume explicitly opens the gate after healthy-host
verification. Restart preserves revision, storage and desired mode, first draining
a live process; a failed drain leaves the gate closed. Restart never discards data.

Observation is ready, draining, drained, starting, stopped, failed or unknown.
A failed/absent probe is never proof of readiness. Counts unavailable due to missing,
locked, corrupt or unexpected storage are null with a reason, never fabricated zeros.

Lifecycle request identity binds tenant/project/function/request_id plus exact action
and expected fence. Identical resubmission returns the original record. Conflicting
reuse is rejected. Intent precedes effects; uncertain effects remain visible and
prevent conflicting actions until startup reconciliation proves a bounded result.

## Open Questions

See PLAN.md#open-questions. Stop, redrive and automatic runtime recovery are deferred.
