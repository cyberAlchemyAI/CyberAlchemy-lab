# `session.inspect`

Read session metadata and unresolved action references

Declared contract: [API catalog](../../../../proposals/0008-lab-api-contracts/api-contracts.json), SHA-256 `4193281b7cc0bae15e9b54861ee1186ee85db930e2bc5a0093b87a898eb996c1`.
Current runtime qualification: **pending**. This page describes the exact public contract; it is not evidence that the operation works on the developing composite cut.

## Contract

- Branch: Base.
- Declared effect: `read-only`.
- Catalog implementation label: `candidate-contract-only`.
- Trusted channel required: `true`; caller requirement: `session-owner-or-authorized-auditor`.
- Message claims grant authority: `false`.
- Required obligation references: `O-AUTHORITY`, `O-TRANSPORT`, `O-EXACT`.
- Repository admission possible: `false`.
- Runtime activations recorded in catalog: `0`.

## Schemas

- Request: [docs/proposals/0007-lab-integrated-schema-package/schemas/session-inspect-request.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/session-inspect-request.schema.json) (`2643bba623e2a4fa16ed4c803c30d4f2e46df6fc2a06c29ec0ea6e590f7d1343`); resource `urn:cyberalchemy-lab:protocol:session-inspect-request:v1-candidate`.
- Result: [docs/proposals/0007-lab-integrated-schema-package/schemas/session-inspect-result.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/session-inspect-result.schema.json) (`5c4f90eca18c9a0d3b81342440ece7892e00c024ab5d33b1e6bb0701850cb235`); resource `urn:cyberalchemy-lab:protocol:session-inspect-result:v1-candidate`.
- Error: [docs/proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json) (`9bb3615757a95c5cdf6ed04da00c874f824b7fe668ddae930e31d70ee1f96f0b`); resource `urn:cyberalchemy-lab:protocol:error-result:v1-candidate`.

## Preconditions

- Authorize session ownership or an exact audit scope.
- Never expose short memory, private credentials or a session dump.

## Postconditions

- Return observed metadata/receipt references; absence is scoped not-found.
- Expired and uncertain states remain distinct from verified closed.

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
