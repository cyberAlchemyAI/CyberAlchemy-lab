# session.open

Open one ephemeral machine Agent session for an exact assignment

Draft reference for the selected API17 capture. Final current operation qualification is pending. [Reference scope and recovery](../README.md).

## Effects and permission

- Declared effect: `ephemeral-session`.
- Dispatcher branch: `base`.
- Caller requirement: `assigned-agent-or-operator`.
- Trusted channel required: `true`.
- Public message claims grant authority: `false`.
- Repository admission possible in this contract: `false`.

Required obligations: `O-AUTHORITY`, `O-TRANSPORT`, `O-EXACT`.

Declared external effects: none.

## Request, result and error schemas

- Request: [original schema](../../../../../../../../proposals/0007-lab-integrated-schema-package/schemas/agent-session-open.schema.json); resource `urn:cyberalchemy-lab:protocol:agent-session-open:v1-candidate`.
  Selected runtime resource: [versioned schema](../../../../../../../../../product/lab/release-candidates/v1/interface/source8-protocol-v2/schemas/019.schema.json); `urn:cyberalchemy-lab:source8-protocol:protocol:agent-session-open:v1-candidate:revision-2`.
- Result: [original schema](../../../../../../../../proposals/0007-lab-integrated-schema-package/schemas/agent-session-result.schema.json); resource `urn:cyberalchemy-lab:protocol:agent-session-result:v1-candidate`.
  Selected runtime resource: [versioned schema](../../../../../../../../../product/lab/release-candidates/v1/interface/source8-protocol-v2/schemas/020.schema.json); `urn:cyberalchemy-lab:source8-protocol:protocol:agent-session-result:v1-candidate:revision-2`.
- Error: [original schema](../../../../../../../../proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json); resource `urn:cyberalchemy-lab:protocol:error-result:v1-candidate`.
  Selected runtime resource: [versioned schema](../../../../../../../../../product/lab/release-candidates/v1/interface/source8-protocol-v2/schemas/055.schema.json); `urn:cyberalchemy-lab:source8-protocol:protocol:error-result:v1-candidate:revision-2`.

Allowed domain errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `conflict`, `idempotency-conflict`, `expired-authority`, `revoked-authority`, `gate-required`, `indeterminate`, `recovery-required`.

Transport refusals are checked separately from domain errors. A response envelope alone does not prove the domain outcome.

## Before calling

- Verify profile/implementation/capabilities, authority envelope, assignment and delivered context.
- Verify context and authority expiration and effective budgets.

Source-cut selectors: `/source_cut`.

Use the strictest caller/policy/message deadline and budget. No effect begins after expiry; after possible effect, expose uncertainty and inspect/reconcile.

## Idempotency and recovery

Idempotency key required: `true`.

Exact same fingerprint returns or points to the recorded result after current read authorization; a different fingerprint conflicts; pending/uncertain keys never redispatch.

Namespace: `authenticated-principal`, `authority-scope`, `selected-scope`, `operation`.

After a possible effect, preserve the exact original request and inspect its operation journal under current authorization. Pending or uncertain keys must not automatically redispatch.

## Assessing the result

- Active creation returns a new session/instance and observed timestamps.
- Blocked creation returns no created identity; short memory is never durable.

A result envelope means the handler returned a domain result. Inspect its posture/result and evidence; it does not establish Work satisfaction or admission except the exact observed admitted transaction.

## Implementation and evidence

[Selected candidate implementation entry point](../../../../../../../../../product/lab/release-candidates/v1/interface/api-integration-v17/service.py). This is a source locator, not proof that the complete operation passed.

The catalog retains its original `candidate-contract-only` authoring label. API17 implementation and execution evidence have separate standing. Final same-candidate all34 operation and security coverage remains pending.
