# `workflow.transition`

Apply one permitted coordination transition with observed satisfaction

Declared contract: [API catalog](../../../../proposals/0008-lab-api-contracts/api-contracts.json), SHA-256 `4193281b7cc0bae15e9b54861ee1186ee85db930e2bc5a0093b87a898eb996c1`.
Current runtime qualification: **pending**. This page describes the exact public contract; it is not evidence that the operation works on the developing composite cut.

## Contract

- Branch: Base.
- Declared effect: `workflow-write`.
- Catalog implementation label: `candidate-contract-only`.
- Trusted channel required: `true`; caller requirement: `assigned-agent-or-operator`.
- Message claims grant authority: `false`.
- Required obligation references: `O-AUTHORITY`, `O-TRANSPORT`, `O-EXACT`.
- Repository admission possible: `false`.
- Runtime activations recorded in catalog: `0`.

## Schemas

- Request: [docs/proposals/0007-lab-integrated-schema-package/schemas/workflow-transition.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/workflow-transition.schema.json) (`bd109387bcf42f3c70f3879c01be1f9ef73c4725d63894121387ef1e5dc2056c`); resource `urn:cyberalchemy-lab:protocol:workflow-transition:v1-candidate`.
- Result: [docs/proposals/0007-lab-integrated-schema-package/schemas/workflow-transition-receipt.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/workflow-transition-receipt.schema.json) (`a7bd337011af5bc9efe4d914ea66062ffcdcc814a6bea708314db413bb1ac7ff`); resource `urn:cyberalchemy-lab:protocol:workflow-transition-receipt:v1-candidate`.
- Error: [docs/proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json) (`9bb3615757a95c5cdf6ed04da00c874f824b7fe668ddae930e31d70ee1f96f0b`); resource `urn:cyberalchemy-lab:protocol:error-result:v1-candidate`.

## Preconditions

- Resolve actual lifecycle mappings, decision profile, actor routes and all transition checks.
- Match current run revision/state and satisfaction evidence; block unbound template workflows.

## Postconditions

- Record observed transition and candidate outputs under the selected coordination authority.
- No automatic output admission; indeterminate transition requires recovery.

## Currentness, deadlines and retry

- Source-cut selectors: `/source_cut`.
- Deadline: Use the strictest caller/policy/message deadline and budget. No effect begins after expiry; after possible effect, expose uncertainty and inspect/reconcile.
- Idempotency required: `true`; namespace: `authenticated-principal`, `authority-scope`, `selected-scope`, `operation`.
- Inner idempotency selector: `/idempotency_key`.
- Retry: Exact same fingerprint returns or points to the recorded result after current read authorization; a different fingerprint conflicts; pending/uncertain keys never redispatch.
- Completion: A result envelope means the handler returned a domain result. Inspect its posture/result and evidence; it does not establish Work satisfaction or admission except the exact observed admitted transaction.

## Errors and external effects

- Allowed error codes: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`, `invalid-connection`, `noncollapse-failed`.
- External effect references: none declared.

[All operations](README.md).
