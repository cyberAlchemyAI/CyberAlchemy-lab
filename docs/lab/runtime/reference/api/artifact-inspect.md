# `artifact.inspect`

Inspect selected sections and independent status facets of one exact revision

Declared contract: [API catalog](../../../../proposals/0008-lab-api-contracts/api-contracts.json), SHA-256 `4193281b7cc0bae15e9b54861ee1186ee85db930e2bc5a0093b87a898eb996c1`.
Current runtime qualification: **pending**. This page describes the exact public contract; it is not evidence that the operation works on the developing composite cut.

## Contract

- Branch: Base.
- Declared effect: `read-only`.
- Catalog implementation label: `candidate-contract-only`.
- Trusted channel required: `true`; caller requirement: `bounded-reader`.
- Message claims grant authority: `false`.
- Required obligation references: `O-AUTHORITY`, `O-TRANSPORT`, `O-EXACT`.
- Repository admission possible: `false`.
- Runtime activations recorded in catalog: `0`.

## Schemas

- Request: [docs/proposals/0007-lab-integrated-schema-package/schemas/artifact-inspect-request.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/artifact-inspect-request.schema.json) (`ac67b07a579b0b99ae8ba9300cfe2de9e685ea304ce288a85523e9e810b9340d`); resource `urn:cyberalchemy-lab:protocol:artifact-inspect-request:v1-candidate`.
- Result: [docs/proposals/0007-lab-integrated-schema-package/schemas/artifact-inspect-result.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/artifact-inspect-result.schema.json) (`c2dc3f6db261289763bf988d4348112fd931abf8aebb4f4e848e47329b876f57`); resource `urn:cyberalchemy-lab:protocol:artifact-inspect-result:v1-candidate`.
- Error: [docs/proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json) (`9bb3615757a95c5cdf6ed04da00c874f824b7fe668ddae930e31d70ee1f96f0b`); resource `urn:cyberalchemy-lab:protocol:error-result:v1-candidate`.

## Preconditions

- Resolve exact artifact identity, revision, carrier and bytes.
- Authorize each selected section; excluded sections carry no body or bindings.

## Postconditions

- Included sections are a subset of the request, with disclosed authorized omissions.
- Body/header/contract identities agree; effective admission is evidence-derived.

## Currentness, deadlines and retry

- Source-cut selectors: `/source_cut`.
- Deadline: Use the strictest caller/policy/message deadline and budget. No effect begins after expiry; after possible effect, expose uncertainty and inspect/reconcile.
- Idempotency required: `false`; namespace: `authenticated-principal`, `authority-scope`, `selected-scope`, `operation`.
- Inner idempotency selector: `None`.
- Retry: Exact same fingerprint returns or points to the recorded result after current read authorization; a different fingerprint conflicts; pending/uncertain keys never redispatch.
- Completion: A result envelope means the handler returned a domain result. Inspect its posture/result and evidence; it does not establish Work satisfaction or admission except the exact observed admitted transaction.

## Errors and external effects

- Allowed error codes: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `invalid-connection`, `noncollapse-failed`.
- External effect references: none declared.

[All operations](README.md).
