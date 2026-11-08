# Lab API operation reference

Documentation draft for the API17 input capture selected on 14 October 2026. The composite declares 34 operations across base, Action and Governance branches. These pages explain exact declared contracts and selected resource remapping; they do not establish final runtime qualification, current operator installation, owner acceptance or release.

The historical catalog authoring labels describe the catalog package. Candidate implementation files are selected separately and linked on each page. A result envelope must be assessed against its domain posture and evidence. Paperclip reader integration does not establish autonomous engineering or research task execution.

| Operation | Declared effect | Branch | Current execution standing |
| --- | --- | --- | --- |
| [`context.get`](operations/context-get.md) | read-only | base | Pending final qualification |
| [`artifact.inspect`](operations/artifact-inspect.md) | read-only | base | Pending final qualification |
| [`artifact.query`](operations/artifact-query.md) | read-only | base | Pending final qualification |
| [`session.open`](operations/session-open.md) | ephemeral-session | base | Pending final qualification |
| [`session.close`](operations/session-close.md) | ephemeral-session | base | Pending final qualification |
| [`change.prepare`](operations/change-prepare.md) | candidate-write | base | Pending final qualification |
| [`change.validate`](operations/change-validate.md) | candidate-write | base | Pending final qualification |
| [`proposal.review`](operations/proposal-review.md) | candidate-write | base | Pending final qualification |
| [`checkpoint.resolve`](operations/checkpoint-resolve.md) | candidate-write | governance | Pending final qualification |
| [`admission.apply`](operations/admission-apply.md) | canonical-commit | governance | Pending final qualification |
| [`action.evaluate`](operations/action-evaluate.md) | read-only | actions | Pending final qualification |
| [`action.dispatch`](operations/action-dispatch.md) | local-action | actions | Pending final qualification |
| [`action.reconcile`](operations/action-reconcile.md) | recovery | actions | Pending final qualification |
| [`workflow.transition`](operations/workflow-transition.md) | workflow-write | base | Pending final qualification |
| [`classification.prepare`](operations/classification-prepare.md) | candidate-write | base | Pending final qualification |
| [`failure.assess`](operations/failure-assess.md) | candidate-write | base | Pending final qualification |
| [`challenge.submit`](operations/challenge-submit.md) | candidate-write | base | Pending final qualification |
| [`challenge.resolve`](operations/challenge-resolve.md) | candidate-write | base | Pending final qualification |
| [`lesson.select`](operations/lesson-select.md) | read-only | base | Pending final qualification |
| [`lesson.apply`](operations/lesson-apply.md) | candidate-write | base | Pending final qualification |
| [`lesson.assess`](operations/lesson-assess.md) | candidate-write | base | Pending final qualification |
| [`ontology.project`](operations/ontology-project.md) | ontology-representation | base | Pending final qualification |
| [`projection.refresh`](operations/projection-refresh.md) | projection-write | base | Pending final qualification |
| [`files.materialize`](operations/files-materialize.md) | managed-file-write | base | Pending final qualification |
| [`package.export`](operations/package-export.md) | managed-file-write | base | Pending final qualification |
| [`package.import`](operations/package-import.md) | candidate-write | base | Pending final qualification |
| [`installation.execute`](operations/installation-execute.md) | local-install | base | Pending final qualification |
| [`lab.status`](operations/lab-status.md) | read-only | base | Pending final qualification |
| [`catalog.get`](operations/catalog-get.md) | read-only | base | Pending final qualification |
| [`session.inspect`](operations/session-inspect.md) | read-only | base | Pending final qualification |
| [`operation.inspect`](operations/operation-inspect.md) | read-only | base | Pending final qualification |
| [`typed.extension.prepare`](operations/typed-extension-prepare.md) | candidate-write | base | Pending final qualification |
| [`capability.adoption.prepare`](operations/capability-adoption-prepare.md) | candidate-write | governance | Pending final qualification |
| [`release.prepare`](operations/release-prepare.md) | candidate-write | base | Pending final qualification |

## Authentication, calls and replies

- [Call envelope](../../../../../../../proposals/0008-lab-api-contracts/schemas/api-call.schema.json).
- [Reply envelope](../../../../../../../proposals/0008-lab-api-contracts/schemas/api-reply.schema.json).
- [Transport refusal](../../../../../../../proposals/0008-lab-api-contracts/schemas/transport-error.schema.json).
- [Trusted caller context](../../../../../../../proposals/0008-lab-api-contracts/schemas/trusted-call-context.schema.json).

The envelope links above retain the original catalog declaration. API17 selects its local v2 call and reply schemas and separately selects its authentication schema. These local registrations also override matching resource IDs after the versioned resource map; referenced resources follow that registry selection.

### Selected local runtime schemas

- [authentication](../../../../../../../../product/lab/release-candidates/v1/interface/api-integration-v17/authentication.schema.json); resource `urn:cyberalchemy-lab:source8-protocol:api:reader-authentication:v2-candidate:revision-3:ontology-0144:binding-0145`.
- [api-call](../../../../../../../../product/lab/release-candidates/v1/interface/api-integration-v17/schemas/api-call.schema.json); resource `urn:cyberalchemy-lab:source8-protocol:api:api-call:v2-candidate:revision-2`.
- [api-reply](../../../../../../../../product/lab/release-candidates/v1/interface/api-integration-v17/schemas/api-reply.schema.json); resource `urn:cyberalchemy-lab:source8-protocol:api:api-reply:v2-candidate:revision-2`.
- [artifact-inspect-result](../../../../../../../../product/lab/release-candidates/v1/interface/api-integration-v17/schemas/artifact-inspect-result.schema.json); resource `urn:cyberalchemy-lab:source8-protocol:protocol:artifact-inspect-result:v2-candidate:revision-2`.
- [catalog-envelope](../../../../../../../../product/lab/release-candidates/v1/interface/api-integration-v17/schemas/catalog-envelope.schema.json); resource `urn:cyberalchemy-lab:source8-protocol:protocol:catalog-representation-envelope:v1-candidate:revision-2`.
- [package-export-plan](../../../../../../../../product/lab/release-candidates/v1/interface/api-integration-v17/schemas/package-export-plan.schema.json); resource `urn:cyberalchemy-lab:source8-protocol:internal:package-export-plan:v1-candidate:revision-2`.
- [package-import-plan](../../../../../../../../product/lab/release-candidates/v1/interface/api-integration-v17/schemas/package-import-plan.schema.json); resource `urn:cyberalchemy-lab:source8-protocol:internal:package-import-plan:v1-candidate:revision-2`.

The maintained composition authenticates independent branches. An opaque public context locator or message Actor is not a grant. Each selected branch repeats its current source, principal, scope, policy, nonce and expiry checks.

## Currentness and recovery

- The outer expected source cut agrees with the primary message cut or referenced review/package cut; verify secondary ontology heads and environment preimages independently.
- Resolve trusted caller context through the actual authenticated local channel; body actor/role claims must match or be rejected.
- Verify live scope, source cut, expiry, revocation, gates and budget immediately before effects; a cached permit is not standing authority.
- Correlate response call_id, operation and request binding with the exact input; no authority follows from a result envelope.
- Enforce the declared inner command-key selector against the envelope; nested proposal/action keys in validation/evaluation calls remain separate material bindings; never retry under a changed payload and the same key.
- Durable idempotency records share crash-consistent effect/recovery evidence. After loss or uncertainty, inspect/reconcile; never recreate a missing key and blindly redispatch.
- Read operations can be retried at the same exact cut within current permission; requesting latest again is a new observation.
- Reject effectful calls expired before execution; if an effect may have started, preserve uncertainty, inspect and reconcile before retry.
- A committed canonical transaction remains committed when a later projection or file generation fails.
- Short session memory and private credentials never enter replies, exports, logs or canonical artifacts; eligible audit evidence is governed separately.
- Unknown/unbound workflows, endpoint mappings and prospective contracts block only affected selected uses; no implicit alias or schema fallback.
- Record enough public outcome metadata for scoped inspection while retaining private provenance and secrets outside the repository.

## Exact inputs and publication standing

The generator checks directly displayed contract/schema/code inputs. This is not a self-contained $ref registry or a full schema-validity proof. The runtime separately selects the remaining domain, dependency and storage schema registrations.

[Additional selected typed-relation schema](../../../../../../../../product/lab/release-candidates/v1/interface/typed-relation-schema-v4/schema.json) is also directly bound.

[Documentation input selection](../input-selection.json) binds the public contract and schema files used here. The source manifest is a captured input inventory; unavailable historical physical inputs remain a separate unresolved proof obligation. The selected API is an unfrozen successor candidate. Fresh execution freeze, full operation/security qualification, installation walkthrough, website integration and Markdown import remain required for T21 completion.
