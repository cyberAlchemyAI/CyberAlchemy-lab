# `files.materialize`

Generate selected managed byte exports or pinned rendered files

Declared contract: [API catalog](../../../../proposals/0008-lab-api-contracts/api-contracts.json), SHA-256 `4193281b7cc0bae15e9b54861ee1186ee85db930e2bc5a0093b87a898eb996c1`.
Current runtime qualification: **pending**. This page describes the exact public contract; it is not evidence that the operation works on the developing composite cut.

## Contract

- Branch: Base.
- Declared effect: `managed-file-write`.
- Catalog implementation label: `candidate-contract-only`.
- Trusted channel required: `true`; caller requirement: `authorized-export-actor`.
- Message claims grant authority: `false`.
- Required obligation references: `O-AUTHORITY`, `O-TRANSPORT`, `O-EXACT`.
- Repository admission possible: `false`.
- Runtime activations recorded in catalog: `0`.

## Schemas

- Request: [docs/proposals/0007-lab-integrated-schema-package/schemas/file-materialization-request.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/file-materialization-request.schema.json) (`885a0263b255e79c5d25a87b64b501f52e47522074d513eda1337453b19ad06a`); resource `urn:cyberalchemy-lab:protocol:file-materialization-request:v1-candidate`.
- Result: [docs/proposals/0007-lab-integrated-schema-package/schemas/file-materialization-receipt.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/file-materialization-receipt.schema.json) (`ab432a703a87ab00e3fcd1c61a76cde5143f15e1a95a588ecaaf1d8c7868ca2b`); resource `urn:cyberalchemy-lab:protocol:file-materialization-receipt:v1-candidate`.
- Error: [docs/proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json) (`9bb3615757a95c5cdf6ed04da00c874f824b7fe668ddae930e31d70ee1f96f0b`); resource `urn:cyberalchemy-lab:protocol:error-result:v1-candidate`.

## Preconditions

- Verify exact byte closure or renderer, output scope, paths/symlinks and privacy.
- Preserve unmanaged files and exclude session memory; pin complete managed output selection.

## Postconditions

- Stage/publish a managed generation with observed output hashes or report failure/uncertainty.
- Generated files grant no admission and are not the canonical replay source.

## Currentness, deadlines and retry

- Source-cut selectors: `/source_cut`.
- Deadline: Use the strictest caller/policy/message deadline and budget. No effect begins after expiry; after possible effect, expose uncertainty and inspect/reconcile.
- Idempotency required: `true`; namespace: `authenticated-principal`, `authority-scope`, `selected-scope`, `operation`.
- Inner idempotency selector: `None`.
- Retry: Exact same fingerprint returns or points to the recorded result after current read authorization; a different fingerprint conflicts; pending/uncertain keys never redispatch.
- Completion: A result envelope means the handler returned a domain result. Inspect its posture/result and evidence; it does not establish Work satisfaction or admission except the exact observed admitted transaction.

## Errors and external effects

- Allowed error codes: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`, `path-collision`, `private-material-excluded`.
- External effect references: none declared.

[All operations](README.md).
