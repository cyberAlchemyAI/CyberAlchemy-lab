# `checkpoint.resolve`

Verify and record actual owner outcomes for exact reviewed members

Declared contract: [API catalog](../../../../proposals/0008-lab-api-contracts/api-contracts.json), SHA-256 `4193281b7cc0bae15e9b54861ee1186ee85db930e2bc5a0093b87a898eb996c1`.
Current runtime qualification: **pending**. This page describes the exact public contract; it is not evidence that the operation works on the developing composite cut.

## Contract

- Branch: Governance.
- Declared effect: `candidate-write`.
- Catalog implementation label: `candidate-contract-only`.
- Trusted channel required: `true`; caller requirement: `accountable-owner`.
- Message claims grant authority: `false`.
- Required obligation references: `O-AUTHORITY`, `O-TRANSPORT`, `O-EXACT`.
- Repository admission possible: `false`.
- Runtime activations recorded in catalog: `0`.

## Schemas

- Request: [docs/proposals/0007-lab-integrated-schema-package/schemas/checkpoint-resolution.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/checkpoint-resolution.schema.json) (`b068fc4c13748880e831aa71f0230f708c702c3cff345840fc2b8b8ac995a23e`); resource `urn:cyberalchemy-lab:protocol:checkpoint-resolution:v1-candidate`.
- Result: [docs/proposals/0007-lab-integrated-schema-package/schemas/validation-report.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/validation-report.schema.json) (`8575f3cfe155a4e58c9f5698cb020e418138c8a62db20fb8a545116aafc3599e`); resource `urn:cyberalchemy-lab:protocol:validation-report:v1-candidate`.
- Error: [docs/proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json) (`9bb3615757a95c5cdf6ed04da00c874f824b7fe668ddae930e31d70ee1f96f0b`); resource `urn:cyberalchemy-lab:protocol:error-result:v1-candidate`.

## Preconditions

- Verify the actual authorization channel and provenance for each required member owner.
- Match exact package, core order, scope, target bytes and current cut; do not infer authorization from caller text.

## Postconditions

- Return a validation report for the recorded resolution.
- All-required-authorized is true only when every required member approves its exact effect.

## Currentness, deadlines and retry

- Source-cut selectors: none declared.
- Deadline: Use the strictest caller/policy/message deadline and budget. No effect begins after expiry; after possible effect, expose uncertainty and inspect/reconcile.
- Idempotency required: `true`; namespace: `authenticated-principal`, `authority-scope`, `selected-scope`, `operation`.
- Inner idempotency selector: `None`.
- Retry: Exact same fingerprint returns or points to the recorded result after current read authorization; a different fingerprint conflicts; pending/uncertain keys never redispatch.
- Completion: A result envelope means the handler returned a domain result. Inspect its posture/result and evidence; it does not establish Work satisfaction or admission except the exact observed admitted transaction.

## Errors and external effects

- Allowed error codes: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`.
- External effect references: none declared.

[All operations](README.md).
