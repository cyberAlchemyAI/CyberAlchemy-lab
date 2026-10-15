#!/usr/bin/env python3
"""Render candidate API descriptions from exact operation metadata."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent

def write(name,text):(HERE/name).write_text(text.strip()+'\n')
contract=json.loads((HERE/'api-contracts.json').read_text())
ops=contract['operations']

write('PROPOSAL.md','''# Lab local API contracts

Status: **candidate design; no API handlers or server implemented by this package**. This follows [schema review 0001](../0007-lab-integrated-schema-package/reviews/0001/REVIEW.md).

## Produced

- 34 closed operation contracts with exact request/result/error schema bindings.
- Five JSON schemas: correlated call, reply, transport error, adapter-resolved trusted context and the machine-readable contract catalog.
- Four representative messages per operation: invocation, separate domain request, result reply and error reply; two transport errors and one illustrative trusted context.
- Explicit caller/authority requirements, effects, source-cut preconditions, deadlines, idempotency, paging, recovery and completion limits.

The reviewed schema package now has 80 candidate protocol schemas, 79 shape messages and eight additional bootstrap/inspection messages beyond its original version. Existing 143 domain versions, four storage schemas and SQL read model remain unchanged.

## Design choice

Use one **local callable API**: `handle(call, adapter_resolved_trusted_context)`. A future authenticated local stdio adapter can carry UTF-8 JSON calls and replies using these same contracts. CLI or Agent tool adapters delegate to the same application services. The primary implementation path remains local; these contracts introduce no network listener.

The public call contains a scoped context handle. The adapter derives authenticated identity and verifies the associated context. Role/capability names in a message are claims to check; they cannot grant themselves authority.

## Review navigation

1. [Complete operation list and descriptions](API-CONTRACTS.md).
2. [Exact call, reply and trust boundary](INTERFACE.md).
3. [Authority, effects, freshness, hashing, retry and recovery rules](POLICIES.md).
4. [Errors and negative results](ERRORS.md).
5. [Workflow examples](WORKFLOWS.md).
6. [Authoring review and evidence](REVIEW.md).

Machine-readable sources are [api-contracts.json](api-contracts.json), [individual operation records](operations/lab.status.json), [schemas](schemas/api-call.schema.json) and the [example index](examples/index.json). The [authoring receipt](receipts/api-authoring.json) binds exact package files and source schemas.

## Authority and completion

Reading, candidate preparation, ephemeral sessions, bounded local actions, canonical admission, ontology representation, projections, managed files and local installation have different effects. Only `admission.apply` applies the selected artifact admission transaction. A result reply can contain a blocked, denied, failed or indeterminate domain result; returning a reply is not operational success.

One final owner checkpoint can authorize the exact reviewed independent Decision members when the actual package and required evidence exist. Preparation cannot fabricate their owner outcomes. Future unknown effects remain outside that authorization. The selected contracts permit zero runtime activations and no external effects.

## Next implementation dependency

Resolve the selected semantic endpoint and workflow bindings, implement the application services and trusted adapters, then obtain the exact required implementation and operational evidence before admission. This package records contract authoring only.
''')

rows=['# API operations\n\nStatus: candidate local application contracts. Every operation receives the correlated [API call](schemas/api-call.schema.json) and an adapter-resolved [trusted context](schemas/trusted-call-context.schema.json); it returns an [API reply](schemas/api-reply.schema.json) or an eligible [transport error](schemas/transport-error.schema.json).\n\n| Operation | Description | Effect | Idempotency key |\n|---|---|---|---|']
for o in ops:rows.append(f'| [{o["operation"]}](operations/{o["operation"]}.json) | {o["description"]} | {o["effect_kind"]} | '+('Required' if o['idempotency_required'] else 'Must be null')+' |')
for o in ops:
    name=o['operation'];req=o['request_schema']['ref'];res=o['result_schema']['ref']
    rows.append(f'\n## {name}\n\n{o["description"]}.\n\n- Request: [exact schema](../../../{req}).\n- Result: [exact schema](../../../{res}).\n- Caller route: `{o["authority"]["caller_requirement"]}` plus actual authority evaluation.\n- Effects: `{o["effect_kind"]}`.\n- Cut selectors: '+(', '.join('`'+x+'`' for x in o['source_cut_selectors']) or 'Outer cut and exact referenced state/package/session bindings')+'.\n\n### Preconditions\n\n'+ '\n'.join('- '+x for x in o['preconditions'])+'\n\n### Observed result\n\n'+'\n'.join('- '+x for x in o['postconditions'])+f'\n\n[Invocation](examples/{name}/request.json) · [Domain request](examples/{name}/message.json) · [Result](examples/{name}/response.json) · [Error](examples/{name}/error-response.json). These are shape illustrations with placeholder authority and handler references.\n\nAllowed application errors: '+', '.join('`'+x+'`' for x in o['allowed_error_codes'])+'.')
write('API-CONTRACTS.md','\n'.join(rows))

write('INTERFACE.md','''# Local call and trust boundary

Status: proposed contract. Transport selection and input schemas do not establish an implemented service.

## Call

[api-call.schema.json](schemas/api-call.schema.json) closes dispatch to 34 operation branches. Every call has:

| Field | Meaning |
|---|---|
| schema_version | Exact candidate wire contract version |
| call_id | Correlation identifier, unique within the authenticated connection; not artifact identity |
| operation | Declared operation name selecting exact message/result/error schemas |
| caller_context_ref | Opaque reference to context resolved through the actual local adapter |
| expected_source_cut | Selected exact read cut or anticipated primary write cut; nullable only for bootstrap/session-close/inspection operations |
| deadline | Outer deadline; effective deadline is the strictest outer, inner and policy bound |
| max_response_bytes | Requested response byte ceiling, capped by host policy |
| idempotency_key | Required for effects/candidate writes/session changes; null for read-only operations |
| message | Exact operation-specific protocol payload; actual domain artifact bodies retain their contracts |

The public message cannot supply a trusted identity object. The adapter resolves and verifies [trusted-call-context](schemas/trusted-call-context.schema.json): host and connection, principal, role/evidence/policy bindings, authority and read scopes, source profile, expiration, limits and optional ephemeral Agent/session/assignment references. Context contains no private credentials and cannot be trusted merely because it validates against a schema.

Body actor, principal, session, assignment and scope claims must match the verified context and selected delegation. Disagreement fails before effects. Actual permission is evaluated from source-bound authority, live revocation/expiry and required gates.

## Reply

[api-reply.schema.json](schemas/api-reply.schema.json) has a result and error branch for each operation. It returns call ID, operation, exact wire-request binding, trusted-context binding, handler binding, observation time, kind and typed message.

A `kind: result` reply means the handler returned a domain result. A denied action, blocked review, pending ontology projection or failed generation can be such a result. The caller must inspect the domain posture/result and evidence. `kind: error` carries an operation-eligible application error.

The outer `request_binding` binds exact received API call bytes. Inner protocol `request_binding`, proposal, Decision core and artifact-content bindings keep their own subjects and encoding boundaries. They must not be replaced with the outer wire digest. The examples store a separate `message.json` to illustrate that distinction. Original artifact content hashes always bind original bytes.

## Framing and malformed input

The primary interface is a local function. A selected stdio adapter uses one complete UTF-8 JSON call per line and one reply/error per line. The framing LF is excluded from wire hashes. It rejects invalid JSON, duplicate object keys, unknown fields/protocol/operation, invalid identifiers, oversized input and unsupported numeric/Unicode control values before dispatch. Wire and parser limits are enforced before allocating unbounded data.

No notification or batch mode is declared. Unexpected connection loss after possible effects creates uncertainty; it cannot establish that nothing happened. [Transport errors](schemas/transport-error.schema.json) allow null identifiers/digests when a full request could not be parsed or received. They disclose no internal exception, private source or credential.

## Bootstrap

`lab.status` captures the scoped current cut when the request and outer cut are null. `catalog.get` then uses that exact cut to discover eligible contracts/signatures. `artifact.query` selects exact revisions, and `artifact.inspect` reads selected sections. This avoids requiring an artifact assignment merely to discover which source cut or contract exists. Agent context/session calls retain their actual assignment requirements.

## Compatibility

The revised candidate `tool-service-*` schemas retain a closed service dispatcher and informational caller requirement. API callers use the correlated envelopes here; the client-declared requirement is never permission. API v1-candidate has no promise of compatibility with frozen v1/v2 executable message contracts. Their adapters and source profiles need exact implementation bindings before use.
''')

write('POLICIES.md','''# Authority, state and recovery policies

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
''')

codes=json.loads((HERE.parent/'0007-lab-integrated-schema-package/schemas/error-result.schema.json').read_text())['properties']['code']['enum']
conditions={
'invalid-contract':'Message shape, body/header agreement, selector, fingerprint encoding or operation precondition is invalid.',
'stale-cut':'Required current cut/head/preimage differs from the exact expected state.',
'unresolved-reference':'A required subject or selected dependency cannot be resolved.',
'ambiguous-reference':'More than one permitted subject resolves to the requested reference.',
'unauthorized':'Actual caller lacks the exact read/action/owner scope; do not disclose forbidden existence.',
'expired-authority':'Selected action authority is outside its valid period.',
'revoked-authority':'Verified revocation removes the selected permission.',
'gate-required':'An actual required owner/gate outcome is absent.',
'conflict':'Selected predecessor, run state or generation conflicts with current state.',
'invalid-connection':'Endpoint mapping, declared pair or qualifier contract is invalid/unbound.',
'noncollapse-failed':'Required semantic orthogonality/noncollapse obligation failed or is not satisfied.',
'closure-missing':'Selected content/schema/evidence/dependency closure is incomplete.',
'indeterminate':'Effects or completion cannot be established from verified observations.',
'recovery-required':'Selected residue/effects require verified reconciliation before proceeding.',
'unsupported-version':'Exact API/body/profile/schema compatibility is unsupported.',
'budget-exceeded':'Known input/output/depth/action budget is exceeded; unknown effects use indeterminate.',
'path-collision':'Managed output would collide with unmanaged content or violate safe output scope.',
'private-material-excluded':'Required selected output is forbidden by custody/disclosure policy.',
'not-found':'No eligible subject or operation record exists in this caller scope; no cross-scope enumeration.',
'unsupported-operation':'Declared adapter/operation is unavailable; unknown wire operations use a transport error.',
'idempotency-conflict':'The scoped key is already bound to a different stable fingerprint.',
'integrity-failed':'Verified bytes, hash chain, manifest or projection integrity does not match.',
'invalid-cursor':'Cursor does not match caller/scope/selectors/cut/generation or its validity.',
'deadline-exceeded':'Known no-effect operation misses its deadline; uncertain effects require reconciliation.',
'adapter-failed':'Known handler failure with bounded observed effects; uncertainty must use indeterminate.',
}
rows=['''# Errors and negative results

Status: candidate error contract.

## Three result levels

- Transport error: no valid application envelope or the trusted channel cannot deliver it. It can have null call ID/digest and must not expose private exceptions. If effects may have started, policy is `inspect-first`.
- Application error: valid correlated call fails a verified precondition, authority, integrity, budget or recovery obligation. Each operation declares its eligible codes.
- Domain result: the operation returns a typed result with its own posture/result. `blocked`, `denied`, `failed`, `pending` and `indeterminate` are valid result states where declared. A result envelope does not mean successful Work completion.

## Application codes

| Code | Condition | Recovery |
|---|---|---|''']
for code in codes:
    policy='Reconcile first; schema forbids blind retry.' if code in ['indeterminate','recovery-required'] else 'No blind retry. Correct/verify inputs or use an explicitly safe same-key operation retry under the contract.'
    rows.append(f'| `{code}` | {conditions[code]} | {policy} |')
rows.append('''## Transport codes

`malformed-json`, `invalid-envelope`, `unauthenticated-channel`, `unsupported-protocol`, `unsupported-operation`, `invalid-call-id`, `input-too-large`, `deadline-exceeded`.

The first seven are pre-dispatch rejections and require `effect_may_have_started: false` and `no-retry`. A deadline/connection uncertainty after possible dispatch requires `effect_may_have_started: true` and `inspect-first`. Never translate that uncertainty into an empty successful receipt.

Application `retry_policy` is an instruction constrained by the operation, current authority, exact input and evidence. `idempotent-retry` does not authorize repeating arbitrary actions. Errors disclose only caller-eligible gaps/evidence. Unrecoverable private details remain in appropriate private custody.
''')
write('ERRORS.md','\n'.join(rows))

write('WORKFLOWS.md','''# API workflow descriptions

Status: proposed sequences; example messages are shape illustrations with placeholder authority, identities and handlers. No sequence below was executed by creating this package.

## Discover all definitions and understand their status

1. `lab.status` captures the permitted source profile and current cut.
2. `catalog.get` discovers the exact current Definition carrier and historical versions.
3. `artifact.query` selects definitions at that cut, with a canonical or verified projection basis, limit/depth/byte bounds and a bound cursor.
4. `artifact.inspect` requests chosen sections: body, exact contract, effective admission evidence, lifecycle, relations, provenance and gaps. Metadata-only inspection carries no body.
5. The reader distinguishes effective admission, immutable body label, implementation observation and outcome. A contract being current does not admit every instance using it.

Example invocation: [artifact.query](examples/artifact.query/request.json). Example selected inspection: [artifact.inspect](examples/artifact.inspect/request.json). These use illustrative references; substitute actual authorized bindings only during implementation operation.

## Ephemeral Agent engineering work

`context.get` → `session.open` → `artifact.inspect` / `artifact.query` → `action.evaluate` → `action.dispatch` → `change.prepare` → `change.validate` → `proposal.review` → actual owner outcomes → `checkpoint.resolve` → `admission.apply` → `projection.refresh` / `ontology.project` / selected `files.materialize` → `session.close`.

Independent engineering satisfaction and Work Outcome Assessment must be evidenced before claims of completed Work. The selected workflow mappings, actor routes and method/implementation contracts must exist. Unbound workflow templates cannot be run just because their JSON is valid. Context and short memory confer no extra action authority.

## Failures, challenges and operational lessons

- Observed failure → `classification.prepare` → `failure.assess` → exact candidate review/admission where required.
- Eligible contestation → `challenge.submit` → response under Challenge Contract → actual resolution Decision → `challenge.resolve` → selected exact consequences.
- Evidence-based lesson candidate through `change.prepare` → assessed review/admission → `lesson.select` for a later assignment → `lesson.apply` → `lesson.assess` using actual outcomes and counterevidence.

Classification, cause, lesson applicability and observed improvement remain distinct. The generic candidate pipeline supports the already bound artifact contracts; it does not introduce a universal body type.

## Typed extension and selected migration

`typed.extension.prepare` binds unique semantics, orthogonal axis, exact endpoint/qualifier contracts, noncollapse evidence and affected carrier successors. Missing endpoint mappings block the affected use. Extension admission occurs through the same exact final review and canonical transaction; it cannot be inferred from schema validity.

`package.import` prepares source/target mappings and complete selected-item dispositions. `ontology.project` represents committed eligible source subjects under its independent ontology cut/authority. Imported source evidence and ontology representation do not grant target repository authority.

## Capability and release

`capability.adoption.prepare` prepares exact realization/adoption declarations with conformance, operational scope and observation contracts. Actual pilot work needs its own currently valid action authority. `release.prepare` reviews a candidate with exact package bytes, acceptance, privacy, pilot and environment evidence. A reviewed owner release Decision is required before selected `installation.execute`; installation has zero activation/external effects.

## Timeout and recovery

1. An uncertain `action.dispatch`, `admission.apply`, `ontology.project`, file generation or installation result preserves its input/key/effect evidence.
2. Use `operation.inspect` with the exact call binding or scoped operation/key. Do not send a changed body with the same key.
3. If completed, return the recorded result after current read authorization. If pending, wait/inspect within budgets. If uncertain, invoke `action.reconcile` only under the selected exact recovery contract.
4. Verify actual state and allowed residue. Rebuild disposable projections or managed outputs where their contracts permit it. Preserve committed history.
5. A missing operation record after a crash is not proof that no effect occurred. Reconcile expected state before any authorized retry.

See the [uncertain transport timeout](examples/transport-uncertain-timeout.json) and [operation lookup](examples/operation.inspect/request.json).
''')

write('REVIEW.md','''# API authoring review

Status: candidate local interface derived after schema review. No independent audit, implementation or owner admission is claimed.

## Scope

All 34 selected service operations have descriptions, exact message/result/error schemas, actual-caller routes, effect classification, cut/preimage conditions, idempotency, budget/deadline, completion and recovery obligations. Four envelope/context schemas and one contract-catalog schema close the selected local interface. Existing domain and storage contracts retain their exact bindings.

## Reproduce

Regenerate the revised schema package and its evidence first, then this dependent API package:

```bash
python3 docs/proposals/0007-lab-integrated-schema-package/build_package.py
python3 docs/proposals/0007-lab-integrated-schema-package/build_examples.py
python3 docs/proposals/0007-lab-integrated-schema-package/build_docs.py
python3 docs/proposals/0007-lab-integrated-schema-package/reviews/0001/build_fixtures.py
python3 docs/proposals/0007-lab-integrated-schema-package/check_package.py
python3 docs/proposals/0008-lab-api-contracts/build_contracts.py
python3 docs/proposals/0008-lab-api-contracts/build_docs.py
python3 docs/proposals/0008-lab-api-contracts/check_contracts.py
```

API authoring binds the revised schema manifest, review and authoring receipt. Rewriting that receipt changes a dependency binding even if schema bodies are unchanged; regenerate the dependent API authoring afterward. No hash cycle is introduced: schemas/manifest precede schema receipt, which precedes API contract and API receipt.

The [authoring receipt](receipts/api-authoring.json) checks exact source bindings, schema meta-validation and offline refs, operation coverage, request/result/error examples, selected invalid envelope/retry shapes, correlation/digest consistency and frozen runtime hashes. It does not verify a real authority channel, signature, JCS codec, idempotency journal, publisher, crash recovery, privacy enforcement, performance or operational outcomes.

## Execution requirements

Implement and verify the selected application services, local adapter and codec. Resolve the [remaining schema/model bindings](../0007-lab-integrated-schema-package/FIT-REPORT.md). Prepare actual authorized scopes, materialized targets and required observed evidence. Present the complete bounded package for its final owner checkpoint. This contract package authorizes none of those future effects by itself.
''')
write('examples/README.md','''# Illustrative API messages

For each of 34 operations, request.json is the wire call, message.json is its separately serialized domain payload, response.json is a typed result reply and error-response.json is an application error reply. Wire and inner-message digests are computed from their respective example bytes and must not be substituted for each other.

Identity, scope, authorization, source-cut and handler bindings are placeholders. The trusted-context example is a shape example, not authenticated context. Returning a shape-valid result does not prove that a handler ran; candidate/blocked/denied dispositions are preferred where the source schema permits them.

The example fingerprint encoder handles only ASCII object keys and small exact integers. It is not a general RFC 8785 implementation or codec conformance evidence. Original artifact bytes are never normalized for these fingerprints.

[index.json](index.json) links all examples and exact illustrative wire/message hashes. See [workflow descriptions](../WORKFLOWS.md) for coherent proposed sequences.
''')
print(json.dumps({'operation_descriptions':len(ops),'documentation_files':8}))
