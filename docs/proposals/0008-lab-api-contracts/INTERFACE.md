# Local call and trust boundary

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
