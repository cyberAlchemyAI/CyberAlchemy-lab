# `installation.execute`

Install/upgrade/rollback a selected local package under exact authority

Declared contract: [API catalog](../../../../proposals/0008-lab-api-contracts/api-contracts.json), SHA-256 `4193281b7cc0bae15e9b54861ee1186ee85db930e2bc5a0093b87a898eb996c1`.
Current runtime qualification: **pending**. This page describes the exact public contract; it is not evidence that the operation works on the developing composite cut.

## Contract

- Branch: Base.
- Declared effect: `local-install`.
- Catalog implementation label: `candidate-contract-only`.
- Trusted channel required: `true`; caller requirement: `authorized-local-operator`.
- Message claims grant authority: `false`.
- Required obligation references: `O-AUTHORITY`, `O-TRANSPORT`, `O-EXACT`.
- Repository admission possible: `false`.
- Runtime activations recorded in catalog: `0`.

## Schemas

- Request: [docs/proposals/0007-lab-integrated-schema-package/schemas/install-request.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/install-request.schema.json) (`70c086499c2511411034f8d2bec059af8a592c38825dbcb1cfc7daf783a884c5`); resource `urn:cyberalchemy-lab:protocol:install-request:v1-candidate`.
- Result: [docs/proposals/0007-lab-integrated-schema-package/schemas/installation-receipt.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/installation-receipt.schema.json) (`bbef8408f56e396433972bd360fee692e2aaf55d6d609cc713f25fefefaec80d`); resource `urn:cyberalchemy-lab:protocol:installation-receipt:v1-candidate`.
- Error: [docs/proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json) (`9bb3615757a95c5cdf6ed04da00c874f824b7fe668ddae930e31d70ee1f96f0b`); resource `urn:cyberalchemy-lab:protocol:error-result:v1-candidate`.

## Preconditions

- Verify exact release approval, profile, environment, authority, preimage and recovery contract.
- Keep credentials in private custody; activation/external effects are zero.

## Postconditions

- Return observed installed/rolled-back/failed/indeterminate postimage evidence.
- Installation does not infer a running service or operational acceptance.

## Currentness, deadlines and retry

- Source-cut selectors: none declared.
- Deadline: Use the strictest caller/policy/message deadline and budget. No effect begins after expiry; after possible effect, expose uncertainty and inspect/reconcile.
- Idempotency required: `true`; namespace: `authenticated-principal`, `authority-scope`, `selected-scope`, `operation`.
- Inner idempotency selector: `None`.
- Retry: Exact same fingerprint returns or points to the recorded result after current read authorization; a different fingerprint conflicts; pending/uncertain keys never redispatch.
- Completion: A result envelope means the handler returned a domain result. Inspect its posture/result and evidence; it does not establish Work satisfaction or admission except the exact observed admitted transaction.

## Errors and external effects

- Allowed error codes: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`, `path-collision`, `private-material-excluded`.
- External effect references: none declared.

[All operations](README.md).
