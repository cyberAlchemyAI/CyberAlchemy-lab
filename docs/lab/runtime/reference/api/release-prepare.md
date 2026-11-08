# `release.prepare`

Prepare an exact candidate release for its final review

Declared contract: [API catalog](../../../../proposals/0008-lab-api-contracts/api-contracts.json), SHA-256 `4193281b7cc0bae15e9b54861ee1186ee85db930e2bc5a0093b87a898eb996c1`.
Current runtime qualification: **pending**. This page describes the exact public contract; it is not evidence that the operation works on the developing composite cut.

## Contract

- Branch: Base.
- Declared effect: `candidate-write`.
- Catalog implementation label: `candidate-contract-only`.
- Trusted channel required: `true`; caller requirement: `assigned-agent-or-operator`.
- Message claims grant authority: `false`.
- Required obligation references: `O-AUTHORITY`, `O-TRANSPORT`, `O-EXACT`.
- Repository admission possible: `false`.
- Runtime activations recorded in catalog: `0`.

## Schemas

- Request: [docs/proposals/0007-lab-integrated-schema-package/schemas/release-manifest.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/release-manifest.schema.json) (`708c1972019ea71750536492f828cf1bb695e4431f3b8fbb1bf3bb9e4be70afc`); resource `urn:cyberalchemy-lab:protocol:release-manifest:v1-candidate`.
- Result: [docs/proposals/0007-lab-integrated-schema-package/schemas/proposal-review.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/proposal-review.schema.json) (`53d288cc2a46e2ed68500ddec7646e835955151436d5b0c1ae962cf1445591fe`); resource `urn:cyberalchemy-lab:protocol:proposal-review:v1-candidate`.
- Error: [docs/proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json) (`9bb3615757a95c5cdf6ed04da00c874f824b7fe668ddae930e31d70ee1f96f0b`); resource `urn:cyberalchemy-lab:protocol:error-result:v1-candidate`.

## Preconditions

- Require candidate posture and actual package, acceptance, pilot, privacy, environment and installation bindings.
- A candidate missing any required evidence remains blocked; do not fabricate release approval.

## Postconditions

- Return a candidate proposal review; release Decision remains independently required.
- No publication, installation, external effect or activation occurs.

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
