# Candidate authenticated local reader API

This R03 step implements `lab.status` and `catalog.get` over independently pinned private candidate archives. All 34 original API operations remain in the Product scope. The remaining 32 handlers, SQLite parity, complete Agent/session workflows and human owner pilot are unfinished.

## Authentication and trust

The host starts from an independently supplied digest of an externally provisioned reader policy. The policy file must belong to the host's Linux user, have mode 0600, remain outside the repository in an explicitly owned temporary root, and retain its expected bytes. This OS check protects host policy integrity; it does not claim to authenticate the client's Linux UID.

The policy selects one already pinned saved source, one exact read scope, a Principal reference, an Ed25519 public key, expiration, request/response/call limits and the two read operations. A one-use challenge binds a random nonce, host instance, connection, policy digest and expiration. The client signs the exact compact challenge encoding. The host verifies that signature and creates the trusted context. Message-supplied identities or context objects grant no authority.

The context carries public authentication/policy/profile evidence, zero action permission and no private credentials. It is scoped to the actual connection and discarded at close. The fixture provisioner creates an independent temporary reader key; it does not impersonate a canonical owner, admit a Principal/Role or grant repository actions. Authentication artifacts retained by tests contain public policies, nonces and signatures. Private keys stay in the owned temporary root and are removed.

Policy change/revocation or expiry invalidates subsequent reads. A body actor, role, opaque context reference or scope that disagrees with the verified context fails before handler access. No network listener or service activation is created.

## Framing and exact bytes

Stdio uses one complete UTF-8 JSON value per LF-delimited line. LF is excluded from wire digests. Before dispatch, the host bounds frame bytes, nesting, collections and supported Unicode/numbers, and rejects duplicate keys, malformed input, unsupported versions/operations and unknown fields.

The outer request binding hashes the exact received call bytes. The inner request binding hashes the exact top-level `message` value span received within that call, including its own whitespace and UTF-8 encoding. This is distinct from both the outer wire digest and any artifact content encoding. The trusted-context binding hashes its host-produced compact encoding. No general JCS compatibility is claimed.

Every returned domain result and application error validates against the existing 34-operation API reply schema and its selected operation branch. Transport errors use the original transport-error schema. A valid result envelope establishes only the observed handler result. It establishes no Work satisfaction, canonical admission or human pilot outcome.

## Scope and source cuts

The selected source archive is independently bound by original bytes, configuration, source profile, baseline and signed HEAD. The existing signed runtime verifies the complete original transaction chain, signatures and deterministic projections in a newly owned read copy. The copy is removed after the connection.

`lab.status` with null inner/outer cuts captures the selected saved current cut. A supplied cut must match an exact verified prefix of that original signed chain, including commit identity, profile and stream cursors/digests. Historical projections reconstruct both target changes and deterministic consequences and verify the recorded projection digest. An historical read does not change the selected saved HEAD or authorize a current operation.

Read currentness is checked against the captured repository material closure. Changed or missing source bytes produce `stale-cut`; they never replace historical content. The handler reports its actual supported operations and remaining gaps. This package reads saved candidate branches, and does not select or modify an existing/live operational store.

## Catalog and cursors

The catalog returns exact eligible current and historical carrier versions with schema/descriptor byte bindings, schema selector, semantic kind, admission reference and independent current/historical read posture. It returns the exact selected closed relation signatures only when requested. File presence and authored candidate labels do not override effective eligibility.

An opaque random page cursor indexes connection-local state bound to Principal, authority/read scope, trusted context, exact cut, carrier filters, relation selection and page size. Unknown, substituted, cross-context, changed-filter or changed-cut cursors fail. Cursor state is erased at close. CLI offsets from the inspection package are not these API cursors.

## Deadlines and budgets

The strictest outer, message and policy deadline applies. An expired deadline prevents handler access; a deadline that expires during a read returns an error. The strictest requested/inner/host response ceiling applies, and an oversized response returns a complete bounded error without a partial body. Request bytes, call count, catalog page size and cursor count also have host ceilings.

## Existing approvals

Candidate construction and these newly owned fixtures use the recorded development authorization. Actual fixture authentication proves the cryptographic channel and bounded implementation behavior; it is not an R08 owner response. Exact new protocol/handler/implementation/evidence members remain part of final S02/R08 review. Existing source/runtime/admission bytes remain immutable.
