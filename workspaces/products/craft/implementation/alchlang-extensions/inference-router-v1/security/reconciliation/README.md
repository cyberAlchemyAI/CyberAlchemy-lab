# Operator custody reconciliation

An authorized operator can review an unresolved request and close it using a
configured, trusted evidence resolver. Closure persists the confirmed outcome,
settles the local custody record and blocks late worker writes. It never sends
another provider request. Unknown or unverifiable outcomes remain unresolved.

The native API is available on `dispatcher.custody` when the durable binding
includes `reconciliation: {operatorId, authorize, resolveEvidence}`. These are
operator-owned adapter functions, not fields accepted from an inference client.
An unconfigured store rejects review and reconciliation.

```js
const control = {
  signal: abortController.signal,
  deadline: Date.now() + 10_000,
};
const selected = {requestId, scope: trustedCustodyScope};
const review = await dispatcher.custody.review(selected, control);
const closed = await dispatcher.custody.reconcile({
  ...selected,
  version: review.version,
  evidenceRef: verifiedEvidenceReference,
}, control);
```

`authorize` receives the configured operator ID, exact scope/request ID and
`custody.review` or `custody.reconcile`. It must return exactly true. Reconciliation
checks it again after evidence resolution. The resolver receives an evidence
reference and the exact request fingerprint/provider-attempt target. It must
verify terminal evidence and return `{evidenceRef, target, transportSettled: true,
outcome}` using the existing typed outcome contract. A caller cannot submit an
outcome directly. Resolver errors, changed targets, stale versions, missing
settlement, cancellation and deadlines leave the record unchanged.

Review omits execution tokens, idempotency keys and result bodies. Reconciliation
metadata records operator, evidence reference, time and outcome, encrypted with
the custody record. It follows the same retention window; export it through an
operator-owned audit integration if longer retention is required. Completed JSON
still needs fresh inference authorization before replay. Streams do not replay;
confirmed failures retain their existing duplicate behavior until normal expiry.

The typed port (source binding requires reconciliation),
[tests](reconciliation.test.mjs), [plan](PLAN.md) and RESULT.json (result record excluded)
define and bind this local candidate. Tests use actual SQLite and generated Alch
policy with fixture authorization/evidence adapters. No provider-specific verifier,
public management HTTP endpoint or production reconciliation is activated here.

## Open Questions

Owned by [PLAN.md](PLAN.md#open-questions): provider-specific evidence verification,
authenticated management HTTP binding, long-term audit export, backups and
production activation. The next construction step is the provider evidence adapter;
unverifiable records continue to occupy capacity.
