# catalog.get

Read current/historical artifact contracts and declared relation signatures

Draft reference for the selected API17 capture. Final current operation qualification is pending. [Reference scope and recovery](../README.md).

## Effects and permission

- Declared effect: `read-only`.
- Dispatcher branch: `base`.
- Caller requirement: `bounded-reader`.
- Trusted channel required: `true`.
- Public message claims grant authority: `false`.
- Repository admission possible in this contract: `false`.

Required obligations: `O-AUTHORITY`, `O-TRANSPORT`, `O-EXACT`.

Declared external effects: none.

## Request, result and error schemas

- Request: [original schema](../../../../../../../../proposals/0007-lab-integrated-schema-package/schemas/catalog-request.schema.json); resource `urn:cyberalchemy-lab:protocol:catalog-request:v1-candidate`.
  Selected runtime resource: [versioned schema](../../../../../../../../../product/lab/release-candidates/v1/interface/source8-protocol-v2/schemas/037.schema.json); `urn:cyberalchemy-lab:source8-protocol:protocol:catalog-request:v1-candidate:revision-2`.
- Result: [original schema](../../../../../../../../proposals/0007-lab-integrated-schema-package/schemas/catalog-result.schema.json); resource `urn:cyberalchemy-lab:protocol:catalog-result:v1-candidate`.
  Selected runtime resource: [versioned schema](../../../../../../../../../product/lab/release-candidates/v1/interface/source8-protocol-v2/schemas/038.schema.json); `urn:cyberalchemy-lab:source8-protocol:protocol:catalog-result:v1-candidate:revision-2`.
- Error: [original schema](../../../../../../../../proposals/0007-lab-integrated-schema-package/schemas/error-result.schema.json); resource `urn:cyberalchemy-lab:protocol:error-result:v1-candidate`.
  Selected runtime resource: [versioned schema](../../../../../../../../../product/lab/release-candidates/v1/interface/source8-protocol-v2/schemas/055.schema.json); `urn:cyberalchemy-lab:source8-protocol:protocol:error-result:v1-candidate:revision-2`.

Allowed domain errors: `invalid-contract`, `unauthorized`, `unsupported-version`, `budget-exceeded`, `deadline-exceeded`, `integrity-failed`, `adapter-failed`, `not-found`, `stale-cut`, `unresolved-reference`, `ambiguous-reference`, `closure-missing`, `invalid-cursor`.

Transport refusals are checked separately from domain errors. A response envelope alone does not prove the domain outcome.

## Before calling

- Bind cursor to principal, scope, request selectors and exact cut.
- An empty carrier selection requests all eligible catalog entries within the page budget.

Source-cut selectors: `/source_cut`.

Use the strictest caller/policy/message deadline and budget. No effect begins after expiry; after possible effect, expose uncertainty and inspect/reconcile.

## Idempotency and recovery

Idempotency key required: `false`.

Exact same fingerprint returns or points to the recorded result after current read authorization; a different fingerprint conflicts; pending/uncertain keys never redispatch.

Namespace: `authenticated-principal`, `authority-scope`, `selected-scope`, `operation`.

After a possible effect, preserve the exact original request and inspect its operation journal under current authorization. Pending or uncertain keys must not automatically redispatch.

## Assessing the result

- Return pinned schema/descriptor bindings and current/historical posture.
- Return only eligible relation signatures when requested.

A result envelope means the handler returned a domain result. Inspect its posture/result and evidence; it does not establish Work satisfaction or admission except the exact observed admitted transaction.

## Implementation and evidence

[Selected candidate implementation entry point](../../../../../../../../../product/lab/release-candidates/v1/interface/api-integration-v17/handlers.py). This is a source locator, not proof that the complete operation passed.

The catalog retains its original `candidate-contract-only` authoring label. API17 implementation and execution evidence have separate standing. Final same-candidate all34 operation and security coverage remains pending.
