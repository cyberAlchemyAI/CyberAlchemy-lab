# `session.close`

Terminate a selected session and dispose of its short memory

Declared contract: [API catalog](../../../../proposals/0008-lab-api-contracts/api-contracts.json), SHA-256 `4193281b7cc0bae15e9b54861ee1186ee85db930e2bc5a0093b87a898eb996c1`.
Current runtime qualification: **pending**. This page describes the exact public contract; it is not evidence that the operation works on the developing composite cut.

## Contract

- Branch: Base.
- Declared effect: `ephemeral-session`.
- Catalog implementation label: `candidate-contract-only`.
- Trusted channel required: `true`; caller requirement: `assigned-agent-or-operator`.
- Message claims grant authority: `false`.
- Required obligation references: `O-AUTHORITY`, `O-TRANSPORT`, `O-EXACT`.
- Repository admission possible: `false`.
- Runtime activations recorded in catalog: `0`.

## Schemas

- Request: [docs/proposals/0007-lab-integrated-schema-package/schemas/agent-session-close.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/agent-session-close.schema.json) (`ec16fc05b35292fc2e2e59097eb3e924c36978a0cdd6e55f4e7c22ccccb2972f`); resource `urn:cyberalchemy-lab:protocol:agent-session-close:v1-candidate`.
- Result: [docs/proposals/0007-lab-integrated-schema-package/schemas/agent-session-close-receipt.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/agent-session-close-receipt.schema.json) (`c312cbe7c31a27d1151536b982a4b074143ff31a1319221440d424afb6d4db1c`); resource `urn:cyberalchemy-lab:protocol:agent-session-close-receipt:v1-candidate`.
- Error: [docs/proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json](../../../../proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json) (`9bb3615757a95c5cdf6ed04da00c874f824b7fe668ddae930e31d70ee1f96f0b`); resource `urn:cyberalchemy-lab:protocol:error-result:v1-candidate`.

## Preconditions

- Verify current session binding and actual caller ownership or delegated termination authority.
- Identify unresolved actions; closing a session does not resolve their effects.

## Postconditions

- Closed requires observed termination and memory disposal.
- Retain only eligible audit references and unresolved residue.

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
