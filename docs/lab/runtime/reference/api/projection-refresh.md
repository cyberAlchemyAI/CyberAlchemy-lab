# `projection.refresh`

Build and select a complete disposable SQLite generation

Declared contract: [API catalog](../../../../proposals/0008-lab-api-contracts/api-contracts.json), SHA-256 `4193281b7cc0bae15e9b54861ee1186ee85db930e2bc5a0093b87a898eb996c1`.
Current runtime qualification: **pending**. This page describes the exact public contract; it is not evidence that the operation works on the developing composite cut.

## Contract

- Branch: Base.
- Declared effect: `projection-write`.
- Catalog implementation label: `candidate-contract-only`.
- Trusted channel required: `true`; caller requirement: `projection-builder`.
- Message claims grant authority: `false`.
- Required obligation references: `O-AUTHORITY`, `O-TRANSPORT`, `O-EXACT`.
- Repository admission possible: `false`.
- Runtime activations recorded in catalog: `0`.

## Schemas

- Request: [docs/proposals/0007-lab-integrated-schema-package/schemas/projection-refresh-request.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/projection-refresh-request.schema.json) (`429b03db532b607ff4f24b5ffdd2b7166720baec89fae288591f287d60572899`); resource `urn:cyberalchemy-lab:protocol:projection-refresh-request:v1-candidate`.
- Result: [docs/proposals/0007-lab-integrated-schema-package/schemas/projection-query-status.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/projection-query-status.schema.json) (`8c49fca9a0d312ce0dd3476440c78383f2aeb1ee8d21604b321b853589a8aff7`); resource `urn:cyberalchemy-lab:protocol:projection-query-status:v1-candidate`.
- Error: [docs/proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json) (`9bb3615757a95c5cdf6ed04da00c874f824b7fe668ddae930e31d70ee1f96f0b`); resource `urn:cyberalchemy-lab:protocol:error-result:v1-candidate`.

## Preconditions

- Resolve projector, exact schema/catalog, source verification and expected generation.
- Verify complete generation, foreign keys, integrity, watermarks and compatibility before switching visibility.

## Postconditions

- Return observed ready/stale/building/invalidated generation metadata.
- Canonical history remains the replay source; projection failure is not canonical rollback.

## Currentness, deadlines and retry

- Source-cut selectors: `/source_cut`.
- Deadline: Use the strictest caller/policy/message deadline and budget. No effect begins after expiry; after possible effect, expose uncertainty and inspect/reconcile.
- Idempotency required: `true`; namespace: `authenticated-principal`, `authority-scope`, `selected-scope`, `operation`.
- Inner idempotency selector: `None`.
- Retry: Exact same fingerprint returns or points to the recorded result after current read authorization; a different fingerprint conflicts; pending/uncertain keys never redispatch.
- Completion: A result envelope means the handler returned a domain result. Inspect its posture/result and evidence; it does not establish Work satisfaction or admission except the exact observed admitted transaction.

## Errors and external effects

- Allowed error codes: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`.
- External effect references: none declared.

[All operations](README.md).
