# LC-U02-01 protocol and authority boundary

This unit is an inert Rust library and fixture suite. It starts no listener or
service, loads no protected key, installs nothing, and writes no stage/member,
control record or generation. `VerifiedDispatch` is a pure checked decision, not
a durability receipt or deployed custody qualification. Original T02/T35 and all
36-task/73-edge/13-AC, 46-row/63-edge inherited obligations remain in force.

## Static extension point

Cargo uses `src/protocol.rs` as its library entry and `authority.rs` as a static
module. Default Cargo binary discovery remains enabled for the later unit-owned
`src/main.rs`. Later held-root/member/state/quota/control-store/generation/journal
modules can be statically declared by that main, importing
`lab_completion_broker::{...,authority::*}` with the already selected dependencies.
No accepted file needs modification to add those modules. Later units use their
own selected build drivers/manifests; this unit's driver refuses extra broker
modules to keep its frozen source closure exact. No privileged Python plugin or
caller-selected code extension exists.

## Wire and source identity

The only transport is Linux AF_UNIX SOCK_SEQPACKET. Each received packet has
exactly one kernel SCM_CREDENTIALS record, positive PID and UID/GID below
UINT32_MAX. SO_PASSCRED is enabled on the receiving socket; no SO_PEERCRED-only
shortcut is used. Every delivered SCM_RIGHTS descriptor is adopted and closed
before refusal, including control truncation. Unknown ancillary types, missing or
duplicate credentials, MSG_TRUNC/MSG_CTRUNC, stream/datagram sockets and oversized
packets refuse. Receive waits are bounded to at most 60 seconds.

Packet maximum is 65,536 bytes, embedded permit 8,192 bytes, raw member chunk
32,768 bytes, exact batch at most 32 chunks, ancillary buffer at most 2,048 bytes.
Smaller batches are required when long selected locators would exceed a bound.
Canonical bytes use compact UTF-8 sorted JSON keys, exact Unicode strings, signed
i64 integers, depth at most 64. Duplicate keys, floating/negative-zero numbers,
invalid Unicode and noncanonical wire bytes refuse.

`binding()` validates the full C01 ByteBinding:
`{kind,root_id,relative_path,sha256,size_bytes}`. Its kind is one of execution,
semantic, evidence, public-package, protected-input. Activation, intent, original
request, semantic target, source cut, effect selection, preimage, stage identity,
receipt/result and disclosure subject references retain all five fields. No
Python/Rust conversion drops a locator or invents one.

`content_digest()` instead returns
`{schema_version:"lab-completion-content-digest/v1",sha256,size_bytes}` for bytes
embedded in the wire or already selected in fixed trusted control: signed permit,
signed authority basis, selected enrollment and captured member identity. It is
not accepted as a ByteBinding. The source/member mapping remains independently
anchored in the full bindings and trusted control snapshot.

The outer closed frame is `{schema_version,request,permit}`, domain
`lab-completion-broker-frame/v1`. The request's closed field set is
`REQUEST_FIELDS`; its authorization_binding is the ContentDigest of the exact
canonical signed permit. Response envelopes sign a closed
`lab-completion-broker-response/v1` payload with full request wire digest,
operation_id, sequence, durable_phase, status, bounded public error and full
result ByteBinding. `verify_receipt` verifies exact bytes/domain/signature/request
selection; a signature alone does not prove that fsync or publication occurred.

## Authority and immutable state

Original core domain `lab-completion-operation-request-core/v1` explicitly binds
the original request, semantic target, source cut, effect selection, pre-existing
EffectAuthorityBasis digest, scope, output slots, quotas and original deadline.
The basis exists before the operation fingerprint. A derived
`lab-completion-broker-permit/v1` binds that fingerprint and the closed
`lab-completion-message-authorization-core/v1` for each permitted exact chunk.
The latter explicitly enumerates request fields excluding its derived permit;
there is no generic caller-field stripping and no hash cycle.

Broker-domain timestamps are integer Unix seconds with inclusive not_before and
exclusive expires_at. The future issuer adapter must bind the original exact
period evidence and issue a broker interval wholly contained within it; it must
not silently widen subsecond/ISO source periods through rounding. This unit does
not reinterpret an existing signed owner payload as a new broker authorization.

Reservation grants carry no member payload. Later fixed control code may durably
reserve epoch/control/stage identity before acknowledging them. Producer bytes
are captured once; the fixed control store selects their full member hash,
length, root, stage, member, preimage and chunk size before admitting the first
chunk. The issuer may issue all bounded batches or renew within the approved
scope without a human prompt for each chunk. Renewal preserves the stored
operation fingerprint, original deadline, captured member identity, cumulative
quotas and next contiguous mutation sequence/offset. A changed full member hash
cannot be authorized merely by re-signing a new permit.

`ControlSnapshot` is supplied afresh under the fixed Rust control lock, never
deserialized from the caller. It independently selects current principal/scope,
activation, store, instance, epoch, intent, roots, operation ID/fingerprint,
stage/member identity, phase, original deadline, cumulative counters and caller
kernel identity. IssuerCurrentness independently selects the enrollment digest,
revocation ByteBinding, current checked_at and revoked status; signed assertions
cannot substitute for that trusted current observation. Missing trusted state
refuses; no actual enrollment/provider is shipped.

`recorded_request` is the fixed loader's exact incoming mutation
(operation_id,sequence) lookup. None means verified absent while holding the
control lock, never 'lookup omitted'. A different full-frame digest conflicts
before any mutation branch, including a renewed permit. An unrecorded mutation
must use durable next_sequence. A duplicate effect frame is never written again
and returns RECEIPT_DISCLOSURE_REQUIRED; it does not itself disclose a receipt.

## Explicit read-query namespace and recovery

Coordinator/reviewer C05 resolution uses the existing closed fields: disclosure
signing domain plus closed read verb plus request_id identify a read query;
operation_id and sequence reference its original target. This is a distinct
read-query namespace, not a claim to replay or occupy a mutation slot. Every
query revalidates its current signed `lab-completion-broker-disclosure-permit/v1`,
which binds the complete message authorization core, current scope, original
target fingerprint, exact full subject binding and output cap. Changed query
material without a corresponding valid current grant refuses. A newly issued
valid disclosure is a new read authorization, not an effect-slot replay.

`inspect`, `inspect_operation` and `read_receipt` return only Decision::Disclosure.
They reserve no durable sequence, write no control record and consume no original
effect/action quota. `read_receipt` sequence must equal the independently loaded
historical receipt.sequence and subject must equal its full receipt binding.
The loader selects that historical record for the requested operation/sequence,
not merely the latest active member/receipt. Before returning its bytes, later
code must verify its stored signed receipt/request digest and bounded selection.
An uncertain receipt is unavailable until current authorized reconciliation;
inspection remains available for verified bounded subjects in UNKNOWN/quota
exhaustion. Broken control can disclose only independently verified surviving
subjects, with explicit limitations; the loader cannot fabricate missing facts.

Current disclosure may use a new activation/intent after the original basis,
source family and effect period have expired. The original stored operation
fingerprint stays unchanged; old source/basis bodies need not be loaded. This is
the defined client recovery path for lost/expired effect acknowledgments: acquire
current disclosure, read the original exact receipt, inspect/reconcile uncertainty,
then continue only from independently verified durable state. Never redispatch
the producer, reset offsets/quotas, or re-sign changed bytes at a mutation slot.

`reconcile_operation` and `close_family` require distinct current
`lab-completion-recovery-authorization/v1` plus independently selected one-use
RecoverySelection. It binds exact observed phase, selected action/subject,
preimages, unchanged original deadline/counters/cursors and full signed permit
digest. Reconcile is legal only in quarantined/UNKNOWN; close is nonterminal.
Terminal has no new mutation even under a freshly signed repair. Future fixed
store code must atomically consume the recovery selection before its one repair,
maintain uncertainty/descendant cleanup, and persist receipts before acknowledgment.
Decision::Recovery cannot be treated as a Fresh producer dispatch.

## Issuer adapters and local build provenance

Original owner adapter: T33/authentic-publisher-successor-inactive-0007/
lab_runtime/owner_ingress.py SHA256
50c0972b00890a38beed942e9a030511ba0e00452aa1c3829e7a9e892374e587.
It signs canonical `{issuer_ref,payload}`, Ed25519 public key as lowercase raw
32-byte hex and signature as lowercase 64-byte hex. Explicit enrollment
owner-hex-v1/broker-intent selects this interpretation.

Original transport adapter: T02/optimized-context-revision-0002/context/control.py
SHA256 088412f6eb37ab05c1ea86c1f0caf51ea257743585c67ec897df8c0a1a15ea49.
Its base64 Ed25519 key/signature signs the exact closed host challenge bytes.
custody-challenge-base64-v1/transport-authentication produces a distinct marker;
it cannot mint broker permits. Later host code must retain one-use/current
challenge custody. All included keys are public fixture bytes; fixture enrollment
cannot satisfy an Actual-domain selection and there is no automatic trust fallback.

Cargo dependencies are exact serde1.0.229, serde_json1.0.151,
ed25519-dalek2.2.0, libc0.2.189, sha2 0.10.9, base64 0.22.1. The 41-package lock
comes from locally verified archives/index records and the accepted predecessor
codec lock; no network or package installation occurs. CARGO_HOME/TARGET/TMP are
owned unit evidence paths. Selected vendor files/checksums/config and 110 local
compiler/standard-library/linker/runtime inputs are reverified before/after build.
Fixture builds qualify only this observed Linux x86_64 environment. These pins
do not establish hostile-host custody, cross-platform reproducibility or live
deployment authority.

The unit's cases include real kernel socket/credential/FD/truncation tests,
closed codec/signature/identity/scope/renewal/recovery negatives, full Python/Rust
request/response and signing vectors (including a maximum raw chunk), and
extracted-build-script/config/tool substitution refusal. Python checks run normally
and under -O with guarded -B -S and the selected regular-file cache prefix.
Final acceptance requires coordinator-selected case execution and independent
review; author runs and the dispatch proposal grant no authority themselves.
