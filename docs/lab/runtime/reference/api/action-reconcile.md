# `action.reconcile`

Reconcile selected uncertain effects or verified recovery residue

Declared contract: [API catalog](../../../../proposals/0008-lab-api-contracts/api-contracts.json), SHA-256 `4193281b7cc0bae15e9b54861ee1186ee85db930e2bc5a0093b87a898eb996c1`.
Current runtime qualification: **pending**. This page describes the exact public contract; it is not evidence that the operation works on the developing composite cut.

## Contract

- Branch: Action.
- Declared effect: `recovery`.
- Catalog implementation label: `candidate-contract-only`.
- Trusted channel required: `true`; caller requirement: `authorized-recovery-actor`.
- Message claims grant authority: `false`.
- Required obligation references: `O-AUTHORITY`, `O-TRANSPORT`, `O-EXACT`.
- Repository admission possible: `false`.
- Runtime activations recorded in catalog: `0`.

## Schemas

- Request: [docs/proposals/0007-lab-integrated-schema-package/schemas/recovery-request.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/recovery-request.schema.json) (`b9d607a58bd4ce44b07c8e2402883ae9f9be1d8cf9204a09a1c7a67708abf7cc`); resource `urn:cyberalchemy-lab:protocol:recovery-request:v1-candidate`.
- Result: [docs/proposals/0007-lab-integrated-schema-package/schemas/recovery-receipt.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/recovery-receipt.schema.json) (`1869c29174af04669a22352574ae5dcd757286eb9c6c35aaa91999de27a05ac3`); resource `urn:cyberalchemy-lab:protocol:recovery-receipt:v1-candidate`.
- Error: [docs/proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json) (`9bb3615757a95c5cdf6ed04da00c874f824b7fe668ddae930e31d70ee1f96f0b`); resource `urn:cyberalchemy-lab:protocol:error-result:v1-candidate`.

## Preconditions

- Authorize only the selected recovery contract and allowed residue.
- Observe the actual state; do not replay a non-idempotent action to discover its outcome.

## Postconditions

- Return observed recovery bindings or preserved uncertainty.
- Never delete committed history or infer a failed action had no effect.

## Currentness, deadlines and retry

- Source-cut selectors: `/expected_cut`.
- Deadline: Use the strictest caller/policy/message deadline and budget. No effect begins after expiry; after possible effect, expose uncertainty and inspect/reconcile.
- Idempotency required: `true`; namespace: `authenticated-principal`, `authority-scope`, `selected-scope`, `operation`.
- Inner idempotency selector: `None`.
- Retry: Exact same fingerprint returns or points to the recorded result after current read authorization; a different fingerprint conflicts; pending/uncertain keys never redispatch.
- Completion: A result envelope means the handler returned a domain result. Inspect its posture/result and evidence; it does not establish Work satisfaction or admission except the exact observed admitted transaction.

## Errors and external effects

- Allowed error codes: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`.
- External effect references: none declared.

[All operations](README.md).
