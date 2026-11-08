# Operator reconciliation of uncertain custody outcomes

Product construction: existing one-attempt and write-once custody model → typed
reconciliation port → encrypted SQLite implementation → exact race, isolation,
closure and regression tests. No ontology selectors or admission are dependencies.
This local D65 candidate does not authorize production reconciliation effects.

The operator binding fixes an operator ID, current authorization function and
trusted evidence resolver. Request input contains only scope, request ID, exact
review version and evidence reference. Review requires authorization and returns
sanitized custody metadata plus an opaque version; execution tokens, request
keys and stored result bodies are excluded. Reconcile rechecks authorization
before and after evidence resolution. All external port waits are bounded by
cancellation and a maximum 30-second deadline.

Evidence must bind the exact request, fingerprint, scope, streaming mode and
provider attempt. It must attest a terminal result and transport settlement.
Unknown, missing, wrong-target or contradictory evidence cannot close a request.
Completed JSON, completed stream or confirmed failure reuse existing outcome
semantics. An existing outcome cannot be overwritten; only identical evidence can
finish its missing settlement. The atomic commit checks the reviewed record
version again, records the evidence reference/operator/time, and fences all late
writer updates. No second provider attempt or automatic inference retry is added.

Reconciliation metadata is encrypted in the same record and follows existing
custody retention. Completed JSON still requires current authorization before
replay. Failed/streaming requests retain their existing duplicate behavior.
Normal retention starts after confirmed closure; deduplication is not permanent.

Runnable construction: implement the port, exact tests and paired Craft evidence.
No construction blocker. Operational support is operator-owned: configure a
provider-specific evidence resolver and authorization binding, export evidence
before retention expires, choose key/backup policy, and deploy separately. No
existing records, running services or issuer configuration are changed.

## Open Questions

Provider-specific evidence verification, a separately authenticated management
HTTP API, permanent audit export, backup rollback protection and production
activation remain separate. This candidate supplies the trusted adapter port and
fixture-backed executable tests; a bare caller assertion is never a resolver.
Unverifiable remote outcomes remain unresolved and occupy capacity.
