# `action.dispatch`

Run one currently permitted local tool action

Declared contract: [API catalog](../../../../proposals/0008-lab-api-contracts/api-contracts.json), SHA-256 `4193281b7cc0bae15e9b54861ee1186ee85db930e2bc5a0093b87a898eb996c1`.
Current runtime qualification: **pending**. This page describes the exact public contract; it is not evidence that the operation works on the developing composite cut.

## Contract

- Branch: Action.
- Declared effect: `local-action`.
- Catalog implementation label: `candidate-contract-only`.
- Trusted channel required: `true`; caller requirement: `assigned-agent-or-operator`.
- Message claims grant authority: `false`.
- Required obligation references: `O-AUTHORITY`, `O-TRANSPORT`, `O-EXACT`.
- Repository admission possible: `false`.
- Runtime activations recorded in catalog: `0`.

## Schemas

- Request: [docs/proposals/0007-lab-integrated-schema-package/schemas/action-request.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/action-request.schema.json) (`183583cc66dd6b81cd7144671bfb4de4f395ea408e710913d80de63954321580`); resource `urn:cyberalchemy-lab:protocol:action-request:v1-candidate`.
- Result: [docs/proposals/0007-lab-integrated-schema-package/schemas/action-receipt.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/action-receipt.schema.json) (`3480b69c5e8903682ba4920e904aff3453d1bbe6a6602ab0250ef7823d22938c`); resource `urn:cyberalchemy-lab:protocol:action-receipt:v1-candidate`.
- Error: [docs/proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json) (`9bb3615757a95c5cdf6ed04da00c874f824b7fe668ddae930e31d70ee1f96f0b`); resource `urn:cyberalchemy-lab:protocol:error-result:v1-candidate`.

## Preconditions

- Re-evaluate authority and bounds immediately before dispatch.
- Verify adapter retry/recovery scope; forbid network/external/activation effects and writes to admission state outside its publisher.

## Postconditions

- Observe actual outputs and completion/failure/uncertainty.
- Indeterminate effects require reconciliation before another dispatch.

## Currentness, deadlines and retry

- Source-cut selectors: `/source_cut`.
- Deadline: Use the strictest caller/policy/message deadline and budget. No effect begins after expiry; after possible effect, expose uncertainty and inspect/reconcile.
- Idempotency required: `true`; namespace: `authenticated-principal`, `authority-scope`, `selected-scope`, `operation`.
- Inner idempotency selector: `/idempotency_key`.
- Retry: Exact same fingerprint returns or points to the recorded result after current read authorization; a different fingerprint conflicts; pending/uncertain keys never redispatch.
- Completion: A result envelope means the handler returned a domain result. Inspect its posture/result and evidence; it does not establish Work satisfaction or admission except the exact observed admitted transaction.

## Errors and external effects

- Allowed error codes: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`.
- External effect references: none declared.

[All operations](README.md).
