# `capability.adoption.prepare`

Prepare exact capability realization and owner-local adoption declarations

Declared contract: [API catalog](../../../../proposals/0008-lab-api-contracts/api-contracts.json), SHA-256 `4193281b7cc0bae15e9b54861ee1186ee85db930e2bc5a0093b87a898eb996c1`.
Current runtime qualification: **pending**. This page describes the exact public contract; it is not evidence that the operation works on the developing composite cut.

## Contract

- Branch: Governance.
- Declared effect: `candidate-write`.
- Catalog implementation label: `candidate-contract-only`.
- Trusted channel required: `true`; caller requirement: `assigned-agent-or-operator`.
- Message claims grant authority: `false`.
- Required obligation references: `O-AUTHORITY`, `O-TRANSPORT`, `O-EXACT`.
- Repository admission possible: `false`.
- Runtime activations recorded in catalog: `0`.

## Schemas

- Request: [docs/proposals/0007-lab-integrated-schema-package/schemas/capability-adoption-request.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/capability-adoption-request.schema.json) (`5aac4c83d77348710cc98e291104c46cd083f4607f4f7053b33eab099e426b74`); resource `urn:cyberalchemy-lab:protocol:capability-adoption-request:v1-candidate`.
- Result: [docs/proposals/0007-lab-integrated-schema-package/schemas/change-proposal.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/change-proposal.schema.json) (`a759fda7f4b0dc26209d03023b79441a42aea7c8523611fa690e755844f4b75e`); resource `urn:cyberalchemy-lab:protocol:change-proposal:v1-candidate`.
- Error: [docs/proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json) (`9bb3615757a95c5cdf6ed04da00c874f824b7fe668ddae930e31d70ee1f96f0b`); resource `urn:cyberalchemy-lab:protocol:error-result:v1-candidate`.

## Preconditions

- Verify capability, realization binding, nonempty implementations, conformance and scoped owner authority.
- Bind actual observation contract and operational scope; no activation in this operation.

## Postconditions

- Return candidate exact adoption/binding effects.
- Actual operational usefulness must be observed under separately valid action scope.

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
