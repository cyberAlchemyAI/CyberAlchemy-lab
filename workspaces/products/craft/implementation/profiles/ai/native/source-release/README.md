# Source release original owner

`index.mjs` exports `createSourceReleaseService({path,now?})` and ABI
`source-release-port/v1`. The host keeps `authority` and supplies `port` only to
its checked generated application/effect owners. This is an in-process technical
port; the existing generated Auth owner must supply the actual tenant/principal.
It is not an HTTP identity authenticator. Do not expose authority or recover and
inspection methods directly as user endpoints.

Required behavior → reuse → delta:

- **Reuse:** existing generated Auth/business transaction owners remain the
  owners of authenticated submission and business changes.
- **New:** original source-release owner stores full immutable context manifests
  and single-use release tickets in owned SQLite. Submission grants no egress.
- **Configure:** trusted inline classification/access records and authored egress
  policy; absent policy, classification or current read access denies release.
- **Extend:** R05 registers `readCurrent` on this owner; documents retain current
  ACL/version authority rather than copying permissions into app tables.

Authority methods: `putInlineSource({id,tenant,revision,aclRevision,
classifications,readers,bytes})`, `setPolicy({id,revision,tenants,actions,sinks,
recipients,classifications})`, `defineContext({id,tenant,principal,inputs})`,
`registerAdapter(id,{readCurrent})`, `revokeInlineSource(id)`. Context inputs are
the complete producer-owned input set, including uncited material; consumers
cannot supply a replacement manifest. `readCurrent({id,tenant,principal})`
returns the same source shape; it must be synchronous and authoritative.

Port methods: `captureContext({contextId,tenant,principal})`,
`recoverManifest(id)`, `describeManifest(handle)`, `issueRelease({manifest,
policyId,attemptId,fence,resourceId,action,sink,recipient,payload,expiresAt})`,
`consumeRelease(ticket,{attemptId,fence,resourceId,action,sink,recipient,tenant,
principal,payload})`, `inspectConsumption(ticket)`. Handles are instance-local
opaque objects. Manifest IDs survive restart; tickets deliberately do not revive.
Consumption atomically checks current full context, source/ACL/policy revisions,
exact bytes and full destination/attempt binding. A consumed ticket stays spent
after crash. New tickets require the effect owner to admit a new dispatch.

SQLite uses WAL, FULL synchronization, immediate mutations and immutable
manifest/ticket/consumption rows. No network transaction is held. Local trusted
operators own setup and DB backups. Schema is v1 only; upgrades must preserve
these records and reject incompatible migrations. Revocation/deletion removes
inline readable bytes while preserving digest provenance. Retention of immutable
release metadata is operator-owned; this module provides no automatic deletion.

## Open Questions

Hosted source adapters, provider credentials and live account qualification remain
outside this local implementation. Provider/model evidence and final selected
package identities are finalized by the enclosing selected-objective proof.

Recipient release requires current source read access by default, independently
of the invoking operator. Exact processingDestinations {sink,recipient} can be
authored for selected model/checkpoint destinations; they do not grant a customer
access. requireRecipientRead:false is an explicit destination-policy posture for
non-human processing profiles, not an implicit Entry permission. Missing recipient
access or any uncited source revocation denies issue and consumption.
