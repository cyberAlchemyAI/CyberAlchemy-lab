# Authentic owner-response ingress v1 candidate

This separate T33 candidate verifies external evidence. It creates no owner
decision, signature, key, governing role, admitted artifact, or publication.
`owner_ingress.py` contains no signing function. All generated issuer keys exist
only in the technical test process and are destroyed at process termination.
The original publisher, generator closure, and fixture key adapter are untouched.

## Trust inputs and required external mechanism

`TrustContext` and `Selection` are supplied by the trusted coordinator, **never**
deserialized from an ingress request, inferred from its issuer/key fields, or
accepted from a public API caller. `usage` is installed configuration; a payload
claim that it is human/actual/approved has no effect. Python callers capable of
replacing coordinator code/configuration are outside this candidate's trust
boundary. The exposed byte ingress accepts only the three signed evidence
envelopes. There is no endpoint to register caller-selected trust anchors.

Before installing an `actual-owner` context, an independent operator must supply:

1. A host issuer and separately selected Ed25519 verification key, backed by an
   authenticated human conversation mechanism. The host must attest the actual
   human identity, immutable message/conversation IDs and UTF-8 content, and an
   explicit review disposition selected by that human after the exact review
   presentation. It must never reclassify an agent message or general goal as an
   explicit disposition. The host signed presentation binds the reviewed bundle
   ID/path, authority digest, whole review digest, ordered complete member cores,
   and exact material displayed to the owner. The presentation includes all
   reviewed effects and evidence, not merely a title or digest.
2. A distinct governing registry issuer/key and real current authority resolver.
   It must validate the existing governing owner roles, applicable scope, period,
   principal and all authority basis/evidence/claim dependencies independently.
   Its signed proof is evidence of that resolution, not a grant. It must bind the
   exact `RepositoryAuthority.core()` digest, complete owner category mapping,
   original evidence references and byte hashes, and a registry cursor freshly
   selected by the coordinator. Proofs cannot become current merely because
   their expiry lies in the future. Revocation/suspension changes the selected
   proof/cursor and invalidates new-commit verification.
3. Independent immutable selection of the full review and exact three envelope
   digests. This includes the actual host message, and the independently current
   registry cursor, principal and repository scope. Selecting digest values from
   the incoming request defeats the contract and is prohibited.

Neither a candidate `role-assignment` carrier (`authority_effect: none`,
`status: candidate-unadmitted`) nor possession of a repository signing key is an
authority resolver. The actual role-assignment schema was inspected unchanged;
this module does not invent a new governing Role or waive its source criteria.
Host and registry issuer IDs **and** keys must differ. All envelope signatures
cover compact sorted UTF-8 JSON of `{issuer_ref,payload}` without a trailing
newline; keys and signatures use lower-case hex. Envelope digests cover the
whole envelope including signature. UTC dates use seconds and `Z`.

No such actual host signing endpoint/key or governing role resolver has been
selected in this run. Tool discovery found thread summary readers, not signed
human-evidence issuance. Existing local signed runtime host grants serve reader
authentication, not human repository-admission decisions. Actual message,
authority proof, approving outcome and production trust installation are absent.
Provisioning these is a concrete prerequisite; T26 must obtain the real outcome.

## Executable verifier and publisher boundary

`ingest(bytes, review, selection, trust)` rejects duplicate JSON keys, nonfinite
values and inputs over 1 MiB, and verifies all three exact closed signed payloads.
The signed schemas and complete required fields are executable in `verify`.
Member core hashes retain original promotion **pretty-printed material bytes**;
review/authority hashes retain its compact semantic digest. No original review
or generator input is rewritten. A changed core, target, authority, bundle or
signed message breaks its independent selection, signature, or exact binding.
All checks use actual UTC time, without caller clocks, renewal or backdating.

`verify` returns evidence with `authority_effect: none`. It can verify reject or
revise dispositions. `verify_for_publication` additionally requires the exact
positive outcome and independently installed actual-owner context. The original
key-adapter response has a different schema and a null human outcome; it cannot
pass this gate. A technical positive remains technical, even with valid
signatures. Production bootstrap may never install fixture-generated anchors.

`ReplayJournal.reserve` re-verifies inputs and atomically reserves the trusted
host issuer/mechanism/conversation/message identity using an exclusive 0600
file and fsync in a private coordinator-owned directory. Parallel or repeated
new-commit attempts fail closed, including changed envelopes for the same ID.
The coordinator must protect this directory and its parents against replacement
or deletion and retain it across restarts. Reservations precede publication;
crashes before commitment leave a consumed reservation and no authority to retry
with altered targets. Resolving such a precommit interruption requires explicit
reconciliation against independently verified commit state; this module has no
reservation-delete or synthetic replacement approval endpoint.

The original publisher is **not integrated** with this successor. Its original
render/source/code/schema/permission/live-currentness checks remain required.
A successor publisher must call the actual-owner gate plus replay reservation
for new commits and reverify current authority/message/review immediately before
its atomic commit, under the existing publication locks. It must persist the
exact signed evidence, selected trust/key/configuration and immutable commit
pins, and protect them in its full independently frozen generator closure. It
must not bypass the new gate by invoking the old fixture helper.

Repair of an already independently verified committed immutable bundle uses
the original exact bundle/authority/response pins and repair pathway; it is not
a new commit and must not reserve/reapprove the owner message again. An expired
response or consumed reservation cannot block repair solely for requiring a
fresh owner decision. This candidate contains no publisher/repair side effects,
and does not claim publisher integration, shared qualification, actual R08,
real owner authority, or admission. Integration and independent contract review
remain explicit closure dependencies.

## Technical verification

The tests exercise independently signed disposable host and registry fixtures,
wrong issuer/signature/owner/scope/role/cursor, expired/future authority, changed
review/member/message, caller human flags, copied goal requests, old key-adapter
shape, repeated persistent reservation, rejected disposition, and strict JSON.
All contexts remain `technical-fixture`; no approving actual-owner response is
generated. The task-local run manifest pins code, contract and original inputs.
Test success is a focused candidate result, not full implementation acceptance.
