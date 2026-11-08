# Verified inbound requests

`createVerifiedIngress` consumes an injected actual `Request`; it starts no
listener. Manual authenticated submit verifies a credential through the R01
adapter. The optional selected HubSpot-v3 profile verifies exact UTF8 body bytes,
method/configured public URL, timestamp and HMAC signature before parsing events.
Account and subscribed event types must match the selected resource. Secret
rotation/revocation is checked before invoking the original service actor.

The HubSpot contract follows the current primary
[request validation specification](https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/request-validation):
SHA256 HMAC, Base64, method+decoded URI+raw body+timestamp, at most a five-minute
window and constant-time comparison. Only the listed URI escapes are decoded.
Old signature versions reject. This is selected protocol testing, not a real app
registration or qualified live provider.

The host supplies `commitEvent` and `assertCommitted` bound to the original
generated Entry/inbox or command owner. Stable provider/account/event/Entry
identity becomes its replay key. The adapter creates no second message journal,
acks only after original commit, and never treats HTTP acknowledgement as a
separate business completion. A crash/partial batch can be retried through that
original owner. Caller event JSON and signature metadata cannot mint an actor or
commit receipt. Exact raw evidence remains under source retention policy; only
its digest crosses this adapter's metadata seam.

The verified HubSpot event also exposes `objectId` as the canonical string
returned by the existing provider identity codec. The signed raw payload stays
unchanged in `payload`; this is a selected provider field, not general JSON
coercion. No credential, actor or permission is derived from this field.

The reusable `prepareTechnicalEventCommitPort` consumer joins an actual compiled
technical source handle, its declared native event-port factory and one
`business-root` runtime projection Mapping to an exact original generated Entry.
Its frame exposes `owner.observation.event`, `messageIdentity`, `rawSha256` and
`eventSha256`. The last digest covers the canonical normalized event, including
its source/account/event identity, so changing the surrounding batch does not
change one event's business command. A Mapping can select `event.objectId` and
`eventSha256` to construct a domain command without a handwritten projection
callback. The original verified receiver, Auth owner, command store and fresh
commit inspection retain their existing responsibilities. This does not add a
listener or qualify a live provider.

The existing local outbox/inbox stores exact occurrence and consumer-command
identities. Sequential claims select pending rows in insertion order, but two
independent current claims may commit in the opposite order. The selected local
handoff therefore promises deduplication and original commit-before-ACK custody,
not global or per-key processing order. Order-sensitive business rules must use
their authored version/state checks. Invalid source projections, denied commands
and unconfirmed commits do not produce an ACK. No automatic poison-message
discard, dead-letter queue or broker redelivery policy is added by this port;
those require a separately selected delivery owner.

## Open Questions

Installed generated-event integration remains part of the complete local suite.
Production registration, provider accounts, external brokers, listeners/hosting,
TDE, EVF and publication are deferred. Exact provider payloads with unsupported
identity representations reject; no permissive number coercion is used.
