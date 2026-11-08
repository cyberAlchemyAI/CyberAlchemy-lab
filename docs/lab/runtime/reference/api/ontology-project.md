# `ontology.project`

Apply selected ontology representations with an independent cut

Declared contract: [API catalog](../../../../proposals/0008-lab-api-contracts/api-contracts.json), SHA-256 `4193281b7cc0bae15e9b54861ee1186ee85db930e2bc5a0093b87a898eb996c1`.
Current runtime qualification: **pending**. This page describes the exact public contract; it is not evidence that the operation works on the developing composite cut.

## Contract

- Branch: Base.
- Declared effect: `ontology-representation`.
- Catalog implementation label: `candidate-contract-only`.
- Trusted channel required: `true`; caller requirement: `authorized-representation-actor`.
- Message claims grant authority: `false`.
- Required obligation references: `O-AUTHORITY`, `O-TRANSPORT`, `O-EXACT`.
- Repository admission possible: `false`.
- Runtime activations recorded in catalog: `0`.

## Schemas

- Request: [docs/proposals/0007-lab-integrated-schema-package/schemas/ontology-project-request.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/ontology-project-request.schema.json) (`50aa3178b47c2b370d42d1c9287c2d6b0162c90341aefa01dfb8784d906ccf5c`); resource `urn:cyberalchemy-lab:protocol:ontology-project-request:v1-candidate`.
- Result: [docs/proposals/0007-lab-integrated-schema-package/schemas/ontology-projection-receipt.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/ontology-projection-receipt.schema.json) (`c01ee8ceb6a3efff0b4d0ac5744060e565956d6fcb30f4ae6d5015cd6fc48391`); resource `urn:cyberalchemy-lab:protocol:ontology-projection-receipt:v1-candidate`.
- Error: [docs/proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json) (`9bb3615757a95c5cdf6ed04da00c874f824b7fe668ddae930e31d70ee1f96f0b`); resource `urn:cyberalchemy-lab:protocol:error-result:v1-candidate`.

## Preconditions

- Verify represented source revisions, mapping/profile closure and ontology authority.
- Global typed relation projections remain read-only; local edges obey their own declared profile.

## Postconditions

- Return observed represented references, ontology watermark/view or pending/blocked/uncertain state.
- Ontology representation confers no Lab admission authority.

## Currentness, deadlines and retry

- Source-cut selectors: `/lab_source_cut`, `/ontology_expected_cut`.
- Deadline: Use the strictest caller/policy/message deadline and budget. No effect begins after expiry; after possible effect, expose uncertainty and inspect/reconcile.
- Idempotency required: `true`; namespace: `authenticated-principal`, `authority-scope`, `selected-scope`, `operation`.
- Inner idempotency selector: `/idempotency_key`.
- Retry: Exact same fingerprint returns or points to the recorded result after current read authorization; a different fingerprint conflicts; pending/uncertain keys never redispatch.
- Completion: A result envelope means the handler returned a domain result. Inspect its posture/result and evidence; it does not establish Work satisfaction or admission except the exact observed admitted transaction.

## Errors and external effects

- Allowed error codes: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`, `invalid-connection`, `noncollapse-failed`.
- External effect references: none declared.

[All operations](README.md).
