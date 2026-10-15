# Authority, state and recovery policies

Status: proposed implementation requirements. Schemas enforce selected shapes; application code must verify these rules and produce evidence.

## Effects and owners

| Effect | Boundary |
|---|---|
| read-only | Authorized bounded reads and deterministic views; no canonical state mutation |
| candidate-write | Stage exact candidate material/reports/reviews; no admission |
| ephemeral-session | Open/close bounded machine Agent identity and short memory |
| local-action | Exact evaluated local tool effects within declared scopes |
| workflow-write | Authorized coordination state/observations; output admission remains separate |
| canonical-commit | Exact all-or-nothing selected artifact transaction under local or repository authority |
| recovery | Verify and reconcile only selected uncertain effects/residue |
| ontology-representation | Authorized representation in its independently headed ontology store |
| projection-write | Disposable complete SQLite generation and active-generation selection |
| managed-file-write | Scoped portable export or managed exact/rendered file generation |
| local-install | Exact selected local package install/upgrade/rollback with observed postimage |

`authority_effect: none` on a request/receipt means that message does not itself grant authority. It does not mean every operation is free of local effects. Actual effects are declared per operation. External effects and service/runtime activations are zero in this selected API scope.

## Source cuts and concurrency

The outer cut must agree with the primary message cut or exact referenced review/package cut. Secondary ontology heads, workflow run revisions, session bindings, projection generations and environment preimages remain separate expected-state checks. A local session close uses its exact session binding and termination authority; stale Project State must not prevent required memory disposal.

Exact historical reads disclose their cut. `artifact.query` supports canonical, projection or preferred-projection basis. Current reads require verified current sources; exact-historical reads require the selected cut; stale projection use requires explicit `allow-stale` and disclosure of requested/applied cuts. Bound cursors include effective principal, scope, selectors, order, actual cut and generation; a cursor cannot be reused across them.

Canonical writers serialize or compare-and-swap the exact expected head under the chosen publisher contract. There is no inferred cross-store atomic transaction. Canonical commit, ontology representation, SQLite activation and file publication retain separate heads/receipts. A derived failure never deletes a committed transaction.

## Hashing and original bytes

Wire request binding is SHA-256 over exact received UTF-8 JSON bytes, excluding transport framing. Artifact/package bindings hash original content bytes. Idempotency uses a separate fingerprint over stable control inputs with [RFC 8785 JCS](https://www.rfc-editor.org/rfc/rfc8785); that scheme provides deterministic canonical JSON for compatible control values. It never canonicalizes or changes original artifact bytes.

Fingerprint inputs are API version, operation, authenticated principal, authority scope, selected scopes, exact source-profile binding, outer expected cut and full domain message. The outer correlation ID, context handle, response ceiling, deadline and idempotency key are excluded. Inner message budgets/deadlines remain part of that exact message. Unsupported numeric values, duplicate keys or invalid Unicode fail explicitly rather than being silently coerced. A future implementation must bind and verify its JCS codec; the authoring example encoder covers only ASCII-key/small-integer examples and is not a general JCS implementation.

## Idempotency

Effectful operations require a key in the stable namespace of principal, authority scope, selected scope and operation. The source profile is part of the fingerprint, not a new namespace; changing profiles cannot make an old key silently execute again.

1. Atomically claim the key/fingerprint before effects and retain exact input/effect evidence under the chosen custody policy.
2. Same key and fingerprint: return the recorded result or inspection reference after current read authorization. Do not redispatch completed, pending or uncertain operations.
3. Same key and different fingerprint: `idempotency-conflict`; no effects.
4. Pending/uncertain record: inspect, observe and reconcile under exact recovery authority. Do not infer failure from timeout or process exit.
5. Lost/expired record: its absence is not proof of no effects. Retain a verified tombstone or reconcile expected state before any re-execution. Private idempotency records are operational metadata, not Agent long-term memory.
6. A declared nested command-key selector must equal its envelope key for change.prepare, action.dispatch, admission.apply, workflow.transition and ontology.project. Keys inside an existing proposal passed to change.validate, or a proposed action passed to action.evaluate, remain material fields and are not rebound to the wrapper key. Changed payloads require new preparation/authorization where applicable, rather than blind retry with a new key.

Read-only retries use the same exact cut and current permission. A new latest read can produce a different observation and is identified as such.

## Budgets and timeouts

The effective budget is the strictest host policy, trusted context, outer call and inner message bound. Enforce input/response bytes, action count, graph depth, result limit and expiration. No effect begins after the deadline. If an effect might have started, return/retain uncertainty and permit scoped inspection/reconciliation; timeout does not authorize replay.

Before effects, ensure the minimum receipt fits negotiated response limits or that exact outcome can be retrieved under the scoped operation record. Oversized reads are paged or rejected with explicit budget evidence. Do not truncate an artifact and present it as byte-exact content.

## Sessions and privacy

Machine Agent identity is ephemeral and not reused as a durable actor instance. Session memory expires with the session and never appears in canonical artifacts, API replies, exports or logs. Durable continuity comes from Project State through source-bound Context and Ontology Views. Eligible operational observations, reflections and lessons use their own contracts, evidence and admission rules.

## Final checkpoint

The Agent prepares and validates exact candidates. Actual owner outcomes are recorded through `checkpoint.resolve` under verified channel provenance. `admission.apply` independently verifies exact authority and expected current heads. All required owner members and scopes remain distinct even when one final interaction reviews them together. Unknown future artifacts or effects cannot be pre-admitted.
