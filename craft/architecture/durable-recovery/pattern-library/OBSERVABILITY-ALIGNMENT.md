# Observability Alignment

Required logical signals:

- dispatch created, transition committed, and terminal disposition recorded;
- claim acquired, released, superseded, and rejected by fencing;
- lease granted, renewed, expired, and lost during execution;
- attempt started and finished with succeeded, failed, or unknown outcome;
- retry scheduled and made eligible;
- binding preflight rejected before mutation;
- replay hit versus first semantic application;
- outbox publication lag and duplicate delivery;
- restart reconciliation decision.

Every signal binds `intent_id`, `dispatch_id`, plan occurrence, dispatch version, and—where applicable—Claim,
Lease, fencing token, Attempt, and Invocation Identity. Business payloads and secrets are excluded by default.

Telemetry observes committed state; it does not grant a Claim, renew a Lease, select retry, decide a terminal
disposition, or prove an Operation's business effect without the Operation-owned result evidence.
