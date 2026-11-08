# `operation.inspect`

Read the scoped invocation/idempotency record after uncertainty

Declared contract: [API catalog](../../../../proposals/0008-lab-api-contracts/api-contracts.json), SHA-256 `4193281b7cc0bae15e9b54861ee1186ee85db930e2bc5a0093b87a898eb996c1`.
Current runtime qualification: **pending**. This page describes the exact public contract; it is not evidence that the operation works on the developing composite cut.

## Contract

- Branch: Base.
- Declared effect: `read-only`.
- Catalog implementation label: `candidate-contract-only`.
- Trusted channel required: `true`; caller requirement: `operation-owner-or-authorized-auditor`.
- Message claims grant authority: `false`.
- Required obligation references: `O-AUTHORITY`, `O-TRANSPORT`, `O-EXACT`.
- Repository admission possible: `false`.
- Runtime activations recorded in catalog: `0`.

## Schemas

- Request: [docs/proposals/0007-lab-integrated-schema-package/schemas/operation-inspect-request.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/operation-inspect-request.schema.json) (`465f28af37bce0d220d7960461a99a354d82be853782d7961c7726bf5cffd712`); resource `urn:cyberalchemy-lab:protocol:operation-inspect-request:v1-candidate`.
- Result: [docs/proposals/0007-lab-integrated-schema-package/schemas/operation-inspect-result.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/operation-inspect-result.schema.json) (`8b762f08ac3b944a3b6b27fdf9f5210a0d1cc48d7c819b1e7cb877233b601a06`); resource `urn:cyberalchemy-lab:protocol:operation-inspect-result:v1-candidate`.
- Error: [docs/proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json) (`9bb3615757a95c5cdf6ed04da00c874f824b7fe668ddae930e31d70ee1f96f0b`); resource `urn:cyberalchemy-lab:protocol:error-result:v1-candidate`.

## Preconditions

- Resolve by exact call binding or principal-scoped operation/key.
- Authorize operation owner or selected auditor; no cross-principal enumeration.

## Postconditions

- Return known pending/completed/failed/indeterminate result and effect evidence.
- Lookup never redispatches the operation; unknown records return scoped not-found.

## Currentness, deadlines and retry

- Source-cut selectors: none declared.
- Deadline: Use the strictest caller/policy/message deadline and budget. No effect begins after expiry; after possible effect, expose uncertainty and inspect/reconcile.
- Idempotency required: `false`; namespace: `authenticated-principal`, `authority-scope`, `selected-scope`, `operation`.
- Inner idempotency selector: `None`.
- Retry: Exact same fingerprint returns or points to the recorded result after current read authorization; a different fingerprint conflicts; pending/uncertain keys never redispatch.
- Completion: A result envelope means the handler returned a domain result. Inspect its posture/result and evidence; it does not establish Work satisfaction or admission except the exact observed admitted transaction.

## Errors and external effects

- Allowed error codes: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`.
- External effect references: none declared.

[All operations](README.md).
