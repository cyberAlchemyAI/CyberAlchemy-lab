# Context and agent sessions

Open only a current bounded resource; dispose it and reconstruct a fresh one.

Draft prepared on 2026-10-14. Integration and final T21 qualification remain pending.

## Select the session implementation

Admitted v1 has a local source/HEAD-bound Session. Candidate Context consumers additionally bind native event/projection and generator inputs. The composite API selects distinct original/custody/Source8/legacy Session hosts and a Machine transport. A v1 local session is not an all34 Action grant.

Use the [local Session](../../../../../../../runtime-narrative-preparation-0001/evidence/implementation/lab-runtime/v1/lab_runtime/session.py), [ContextSession](../../../../../../../runtime-narrative-preparation-0001/evidence/implementation/lab-context/candidates/v1/context.py) and [captured API session source](../../../../../../../runtime-narrative-preparation-0001/evidence/product/lab/release-candidates/v1/interface/api-integration-v16/source8_context_sessions.py) as version-specific responsibilities. The integrated current learning journey is unqualified; this page explains its prerequisites rather than advertising a successful end-to-end example.

## Obtain a usable context

A Context View binds selected sources, exact cuts/cursors, exclusions, intended use, validity and current policy. The native reader checks original event/executable/request/projection pins before and after a separate native process. Semantic and governance event cursors stay distinct from Project transaction history.

Assignment identifies the task. Permission still needs the real current Principal, allowed operation, scope, policy, nonce, budget and expiry. An opaque context locator, message Actor or copied view supplies no grant. Link [the canonical Context View](../../../../../../../../../../../../lab/reference/records/def-cal-definition-context-view.md) and [authority](../../../../../../../../../../../../lab/guide/authority.md) when those meanings need explanation.

## Keep the lifetime boundaries

A live Session holds a real resource and short memory. Its caller can use only the strictest current call/policy/Session/Context/source/reader bounds. Scope revocation, changed HEAD/source, expired context or exhausted budget stops use. Refreshing a view does not renew the grant or source period.

An API Machine peer binds to the actual still-live parent Session. An application Operator borrows an exact [SessionAttachment](../../../../../../../runtime-narrative-preparation-0001/evidence/product/lab/release-candidates/v1/interface/api-integration-v16/session_attachment.py); closing that borrower must not dispose the parent's credential/custody. A host restart cannot turn a public receipt into the original in-memory resource or signer.

````mermaid
flowchart LR
  S[Durable state and assignment] --> C[Fresh checked Context]
  P[Current policy and grant] --> L[Live Session resource]
  C --> L
  L --> U[Allowed bounded use]
  U --> X[Expiry / revocation / close]
  X --> E[Erase short memory and release signer]
  E --> N[New Session with fresh context]
  S --> N
````

Durable Project State can support a new checked context. Current permission and context are both needed for the live resource. Close, expiry or revocation disposes short memory; a later session reconstructs knowledge rather than restoring that resource.

Explanatory component/sequence map, not a declaration of new ontology relation kinds or qualified runtime execution.

## Local v1 grammar and expected disposition

The admitted parser has session SUBJECT --ttl SECONDS, with interactive context, note TEXT, memory and close commands. EOF also closes it. --context-only exports a candidate packet and immediately closes the resource: that packet is historical preparation output, not an active credential. The v1 parser's default TTL is 900 seconds.

Use this route only with the independently selected source/store and current local authorization. The fresh inspection witness did not open a Session. A separate Session walkthrough, expiry/disposal observation and fresh reconstruction remain required for this handbook's successful session recipe.

## Understand the current failure

The [actual learning measurement](../../../../../../../runtime-narrative-preparation-0001/evidence/docs/plans/0011-lab-runtime-completion/runs/0001-execution/T35/measurement-review-0002.json) expired during lesson selection. It retained valid outer source/reader/call budgets, but the stricter Session/Context boundary had already ended. That is not permission to enlarge the period or replay the old resource.

The new margin adapter can refuse a tail before claim when empirical bounds are unknown or cannot fit. [Pure margin checks](../../../../../../../runtime-narrative-preparation-0001/evidence/docs/plans/0011-lab-runtime-completion/runs/0001-execution/T03/observed-margin-adapter-0003/independent-review-0001.json) do not establish a real safe tail. Start a separately authorized fresh episode only after its selected implementation and current inputs qualify.

## Selected public evidence

- [product/lab/release-candidates/v1/interface/api-integration-v16/session_attachment.py](../../../../../../../runtime-narrative-preparation-0001/evidence/product/lab/release-candidates/v1/interface/api-integration-v16/session_attachment.py). SHA-256 fede0559d0207356bde4c1d1f8c0f7a9b662caedbbb4f18581049337477cab16; 7351 bytes. Public technical snapshot; no authority transfer.

- [product/lab/release-candidates/v1/interface/api-integration-v16/machine_transport.py](../../../../../../../runtime-narrative-preparation-0001/evidence/product/lab/release-candidates/v1/interface/api-integration-v16/machine_transport.py). SHA-256 6f526a737545e4a5e3e6f721d24f68e1192a4176d347498c10dc3c2b090408f7; 11431 bytes. Public technical snapshot; no authority transfer.

- [product/lab/release-candidates/v1/interface/api-integration-v16/source8_context_sessions.py](../../../../../../../runtime-narrative-preparation-0001/evidence/product/lab/release-candidates/v1/interface/api-integration-v16/source8_context_sessions.py). SHA-256 bc9aa26df08b68db2ce5b8de6836627d9e595d3bb62726eef7e5057c35a79359; 38437 bytes. Public technical snapshot; no authority transfer.

- [implementation/lab-context/candidates/v1/context.py](../../../../../../../runtime-narrative-preparation-0001/evidence/implementation/lab-context/candidates/v1/context.py). SHA-256 03f81c418f33894911ad045d3316d14cfc1232906da9b79cdd9ea3074aabccad; 20746 bytes. Public technical snapshot; no authority transfer.

- [docs/plans/0011-lab-runtime-completion/runs/0001-execution/T03/observed-margin-adapter-0003/independent-review-0001.json](../../../../../../../runtime-narrative-preparation-0001/evidence/docs/plans/0011-lab-runtime-completion/runs/0001-execution/T03/observed-margin-adapter-0003/independent-review-0001.json). SHA-256 f9d230b241e5705c2f1cf44c1dbb8161c18199677de6276e09cf90fabcbb73e5; 8243 bytes. Public technical snapshot; no authority transfer.

- [docs/plans/0011-lab-runtime-completion/runs/0001-execution/T35/measurement-review-0002.json](../../../../../../../runtime-narrative-preparation-0001/evidence/docs/plans/0011-lab-runtime-completion/runs/0001-execution/T35/measurement-review-0002.json). SHA-256 000ec20049be7b8e19baec27637b278ad496bafc883ddecea6b3abd15dc8a89c; 29862 bytes. Public technical snapshot; no authority transfer.

- [implementation/lab-runtime/v1/lab_runtime/session.py](../../../../../../../runtime-narrative-preparation-0001/evidence/implementation/lab-runtime/v1/lab_runtime/session.py). SHA-256 9e96494cfe227ce341b8c6281e9cf6676710eae4cf0170ce1891850486573599; 12666 bytes. Public technical snapshot; no authority transfer.
