# Testing Alignment

| Property family | Minimum deterministic evidence |
| --- | --- |
| Intent and plan immutability | repeated planning plus persisted reread equality |
| Dependency contract separation | exact role-specific contract inventory; universal-Port and provider-import hostiles fail |
| Persistence binding | Repository, adapter, resource, profile, mapping, and evidence refs close without mandatory Interface masquerade |
| Transaction binding | exact Unit of Work participants plus commit, rollback, conflict, partial-commit, and restoration observations |
| Failure outcome binding | retryable/non-retryable/unknown classification retains raw evidence and cannot choose Retry |
| Durable runtime binding | exact durable-only composition closes; synchronous profile remains exempt |
| Version and fencing | competing claim/commit interleavings with stale-token rejection |
| Lease liveness | controlled clock expiry before and during invocation |
| Attempt and replay identity | crash/retry/takeover cases proving new attempt and stable invocation identity |
| Atomic dispatch outbox | injected failure before and after commit, proving both-or-neither visibility |
| Operation replay safety | duplicate invocation against a durable result ledger, proving one semantic application |
| Retry | persisted budget and `not_before`, explicit continuation, no replan/substitution |
| Terminal result | completed/exhausted/escalated closure and no-successor hostile case |
| Restart | reopen the store and resume from the first incomplete occurrence |
| Evidence honesty | missing observer input yields `unsupported`, never PASS |

The first reference implementation may use a deterministic in-memory or file-backed test adapter. That proves
the concern-specific contract and state-machine boundary only; a production store adapter needs its own
profile binding, concurrency, transaction, and crash evidence.
