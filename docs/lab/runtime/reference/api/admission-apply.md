# `admission.apply`

Apply one exact authorized canonical artifact transaction

Declared contract: [API catalog](../../../../proposals/0008-lab-api-contracts/api-contracts.json), SHA-256 `4193281b7cc0bae15e9b54861ee1186ee85db930e2bc5a0093b87a898eb996c1`.
Current runtime qualification: **pending**. This page describes the exact public contract; it is not evidence that the operation works on the developing composite cut.

## Contract

- Branch: Governance.
- Declared effect: `canonical-commit`.
- Catalog implementation label: `candidate-contract-only`.
- Trusted channel required: `true`; caller requirement: `authorized-application-adapter`.
- Message claims grant authority: `false`.
- Required obligation references: `O-AUTHORITY`, `O-TRANSPORT`, `O-EXACT`.
- Repository admission possible: `true`.
- Runtime activations recorded in catalog: `0`.

## Schemas

- Request: [docs/proposals/0007-lab-integrated-schema-package/schemas/commit-request.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/commit-request.schema.json) (`7a8b2f2b5d94287235acafa51d7d25f2e2bb8ca30065c3fcdb70a7136543775b`); resource `urn:cyberalchemy-lab:protocol:commit-request:v1-candidate`.
- Result: [docs/proposals/0007-lab-integrated-schema-package/schemas/commit-receipt.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/commit-receipt.schema.json) (`f419536a258f51d36a427ba940ccf50916fa8bb6771f013a079676e0c8bb8724`); resource `urn:cyberalchemy-lab:protocol:commit-receipt:v1-candidate`.
- Error: [docs/proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json) (`9bb3615757a95c5cdf6ed04da00c874f824b7fe668ddae930e31d70ee1f96f0b`); resource `urn:cyberalchemy-lab:protocol:error-result:v1-candidate`.

## Preconditions

- Verify proposal/package/resolution, owner authority, complete closure and expected current head.
- Serialize publication and bind local versus repository authority; zero activation and external effects.

## Postconditions

- Commit exact immutable content/events and publish one canonical head or report uncertainty.
- Projection/file outcomes are separately reported and cannot undo a committed transaction.

## Currentness, deadlines and retry

- Source-cut selectors: `/expected_cut`.
- Deadline: Use the strictest caller/policy/message deadline and budget. No effect begins after expiry; after possible effect, expose uncertainty and inspect/reconcile.
- Idempotency required: `true`; namespace: `authenticated-principal`, `authority-scope`, `selected-scope`, `operation`.
- Inner idempotency selector: `/idempotency_key`.
- Retry: Exact same fingerprint returns or points to the recorded result after current read authorization; a different fingerprint conflicts; pending/uncertain keys never redispatch.
- Completion: A result envelope means the handler returned a domain result. Inspect its posture/result and evidence; it does not establish Work satisfaction or admission except the exact observed admitted transaction.

## Errors and external effects

- Allowed error codes: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`.
- External effect references: none declared.

[All operations](README.md).
