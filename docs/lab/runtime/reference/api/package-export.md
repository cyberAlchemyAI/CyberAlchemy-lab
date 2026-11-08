# `package.export`

Export selected portable original content and complete dependencies

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

- Request: [docs/proposals/0007-lab-integrated-schema-package/schemas/package-export-request.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/package-export-request.schema.json) (`b2275e33395cafdff7e80077987a24a5d2a0ab14629724800868039b9d36a5a7`); resource `urn:cyberalchemy-lab:protocol:package-export-request:v1-candidate`.
- Result: [docs/proposals/0007-lab-integrated-schema-package/schemas/file-materialization-receipt.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/file-materialization-receipt.schema.json) (`ab432a703a87ab00e3fcd1c61a76cde5143f15e1a95a588ecaaf1d8c7868ca2b`); resource `urn:cyberalchemy-lab:protocol:file-materialization-receipt:v1-candidate`.
- Error: [docs/proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json) (`9bb3615757a95c5cdf6ed04da00c874f824b7fe668ddae930e31d70ee1f96f0b`); resource `urn:cyberalchemy-lab:protocol:error-result:v1-candidate`.

## Preconditions

- Verify selected original bytes and the complete required dependency closure.
- Resolve export destination from the exact export contract; exclude credentials/session memory.

## Postconditions

- Return a managed generation receipt binding exported package bytes and dependencies.
- Exported source admission evidence does not admit the package in another target.

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
