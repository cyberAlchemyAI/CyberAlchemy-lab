# Errors and negative results

Status: candidate error contract.

## Three result levels

- Transport error: no valid application envelope or the trusted channel cannot deliver it. It can have null call ID/digest and must not expose private exceptions. If effects may have started, policy is `inspect-first`.
- Application error: valid correlated call fails a verified precondition, authority, integrity, budget or recovery obligation. Each operation declares its eligible codes.
- Domain result: the operation returns a typed result with its own posture/result. `blocked`, `denied`, `failed`, `pending` and `indeterminate` are valid result states where declared. A result envelope does not mean successful Work completion.

## Application codes

| Code | Condition | Recovery |
|---|---|---|
| `invalid-contract` | Message shape, body/header agreement, selector, fingerprint encoding or operation precondition is invalid. | No blind retry. Correct/verify inputs or use an explicitly safe same-key operation retry under the contract. |
| `stale-cut` | Required current cut/head/preimage differs from the exact expected state. | No blind retry. Correct/verify inputs or use an explicitly safe same-key operation retry under the contract. |
| `unresolved-reference` | A required subject or selected dependency cannot be resolved. | No blind retry. Correct/verify inputs or use an explicitly safe same-key operation retry under the contract. |
| `ambiguous-reference` | More than one permitted subject resolves to the requested reference. | No blind retry. Correct/verify inputs or use an explicitly safe same-key operation retry under the contract. |
| `unauthorized` | Actual caller lacks the exact read/action/owner scope; do not disclose forbidden existence. | No blind retry. Correct/verify inputs or use an explicitly safe same-key operation retry under the contract. |
| `expired-authority` | Selected action authority is outside its valid period. | No blind retry. Correct/verify inputs or use an explicitly safe same-key operation retry under the contract. |
| `revoked-authority` | Verified revocation removes the selected permission. | No blind retry. Correct/verify inputs or use an explicitly safe same-key operation retry under the contract. |
| `gate-required` | An actual required owner/gate outcome is absent. | No blind retry. Correct/verify inputs or use an explicitly safe same-key operation retry under the contract. |
| `conflict` | Selected predecessor, run state or generation conflicts with current state. | No blind retry. Correct/verify inputs or use an explicitly safe same-key operation retry under the contract. |
| `invalid-connection` | Endpoint mapping, declared pair or qualifier contract is invalid/unbound. | No blind retry. Correct/verify inputs or use an explicitly safe same-key operation retry under the contract. |
| `noncollapse-failed` | Required semantic orthogonality/noncollapse obligation failed or is not satisfied. | No blind retry. Correct/verify inputs or use an explicitly safe same-key operation retry under the contract. |
| `closure-missing` | Selected content/schema/evidence/dependency closure is incomplete. | No blind retry. Correct/verify inputs or use an explicitly safe same-key operation retry under the contract. |
| `indeterminate` | Effects or completion cannot be established from verified observations. | Reconcile first; schema forbids blind retry. |
| `recovery-required` | Selected residue/effects require verified reconciliation before proceeding. | Reconcile first; schema forbids blind retry. |
| `unsupported-version` | Exact API/body/profile/schema compatibility is unsupported. | No blind retry. Correct/verify inputs or use an explicitly safe same-key operation retry under the contract. |
| `budget-exceeded` | Known input/output/depth/action budget is exceeded; unknown effects use indeterminate. | No blind retry. Correct/verify inputs or use an explicitly safe same-key operation retry under the contract. |
| `path-collision` | Managed output would collide with unmanaged content or violate safe output scope. | No blind retry. Correct/verify inputs or use an explicitly safe same-key operation retry under the contract. |
| `private-material-excluded` | Required selected output is forbidden by custody/disclosure policy. | No blind retry. Correct/verify inputs or use an explicitly safe same-key operation retry under the contract. |
| `not-found` | No eligible subject or operation record exists in this caller scope; no cross-scope enumeration. | No blind retry. Correct/verify inputs or use an explicitly safe same-key operation retry under the contract. |
| `unsupported-operation` | Declared adapter/operation is unavailable; unknown wire operations use a transport error. | No blind retry. Correct/verify inputs or use an explicitly safe same-key operation retry under the contract. |
| `idempotency-conflict` | The scoped key is already bound to a different stable fingerprint. | No blind retry. Correct/verify inputs or use an explicitly safe same-key operation retry under the contract. |
| `integrity-failed` | Verified bytes, hash chain, manifest or projection integrity does not match. | No blind retry. Correct/verify inputs or use an explicitly safe same-key operation retry under the contract. |
| `invalid-cursor` | Cursor does not match caller/scope/selectors/cut/generation or its validity. | No blind retry. Correct/verify inputs or use an explicitly safe same-key operation retry under the contract. |
| `deadline-exceeded` | Known no-effect operation misses its deadline; uncertain effects require reconciliation. | No blind retry. Correct/verify inputs or use an explicitly safe same-key operation retry under the contract. |
| `adapter-failed` | Known handler failure with bounded observed effects; uncertainty must use indeterminate. | No blind retry. Correct/verify inputs or use an explicitly safe same-key operation retry under the contract. |
## Transport codes

`malformed-json`, `invalid-envelope`, `unauthenticated-channel`, `unsupported-protocol`, `unsupported-operation`, `invalid-call-id`, `input-too-large`, `deadline-exceeded`.

The first seven are pre-dispatch rejections and require `effect_may_have_started: false` and `no-retry`. A deadline/connection uncertainty after possible dispatch requires `effect_may_have_started: true` and `inspect-first`. Never translate that uncertainty into an empty successful receipt.

Application `retry_policy` is an instruction constrained by the operation, current authority, exact input and evidence. `idempotent-retry` does not authorize repeating arbitrary actions. Errors disclose only caller-eligible gaps/evidence. Unrecoverable private details remain in appropriate private custody.
