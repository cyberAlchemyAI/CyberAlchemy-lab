# `context.get`

Deliver bounded Context and Ontology Views for one assignment

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

- Request: [docs/proposals/0007-lab-integrated-schema-package/schemas/context-query.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/context-query.schema.json) (`ebc44fa120e65f12f2aa0e67c9442d278394e2186d7342923e20f4388e44b556`); resource `urn:cyberalchemy-lab:protocol:context-query:v1-candidate`.
- Result: [docs/proposals/0007-lab-integrated-schema-package/schemas/context-delivery.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/context-delivery.schema.json) (`03a28d61e1c55e24b882834c47386561570b225d46f82f9169cfdf29283d698e`); resource `urn:cyberalchemy-lab:protocol:context-delivery:v1-candidate`.
- Error: [docs/proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json) (`9bb3615757a95c5cdf6ed04da00c874f824b7fe668ddae930e31d70ee1f96f0b`); resource `urn:cyberalchemy-lab:protocol:error-result:v1-candidate`.

## Preconditions

- Resolve assignment, Work and one-Goal Coordination Context.
- Verify included sources, exclusions, lesson applicability, privacy and budgets.

## Postconditions

- Ready requires actual view bindings and enforced scope.
- Context grants no authority; blocked delivery may have no views.

## Currentness, deadlines and retry

- Source-cut selectors: `/source_cut`.
- Deadline: Use the strictest caller/policy/message deadline and budget. No effect begins after expiry; after possible effect, expose uncertainty and inspect/reconcile.
- Idempotency required: `false`; namespace: `authenticated-principal`, `authority-scope`, `selected-scope`, `operation`.
- Inner idempotency selector: `None`.
- Retry: Exact same fingerprint returns or points to the recorded result after current read authorization; a different fingerprint conflicts; pending/uncertain keys never redispatch.
- Completion: A result envelope means the handler returned a domain result. Inspect its posture/result and evidence; it does not establish Work satisfaction or admission except the exact observed admitted transaction.

## Errors and external effects

- Allowed error codes: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`.
- External effect references: none declared.

[All operations](README.md).
