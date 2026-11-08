# LC-U03-01 fixed control ledger

This is inert fixed Rust source and owned fixture verification. It does not
provision host custody, authorize actual workloads, change original acceptance,
or install services. The dependency is accepted LC-U01-02. The separate broker
unit is not imported or changed. No protected body/key is read.

`control_store/src/lib.rs` can be a standalone library or statically included
by later broker main via a fixed module path. Internal `super` references work
in either arrangement. The frozen Cargo dependencies are libc 0.2.189, serde
1.0.229, serde_json 1.0.151 and sha2 0.10.9, all selected from the accepted U01
local offline lock/archive basis. No runtime plugin or Python control writer
is involved. Python scripts only build/test owned fixtures.

## Authority and continuity interface

The host loader supplies an already selected held root identity and a fresh
`TrustedSelection`. `Posture::Actual` rejects fixture headers, including a
fixture checkpoint relabeled by the caller. Only a distinct fixture constructor
exists here. Actual bootstrap is a future gated host provisioner operation; a
missing root, header, witness or continuity chain never invokes initialization.

The authority-domain root and its records/lock inode layout are header-bound.
Host custody must independently establish full mount/ancestor/ACL/alias policy
and select the single authority-domain root across all logical stores. Local
inode/uid checks do not prove that external invariant. The host confirmer must
be outside generation snapshots and application rollback/backups and must
serialize compare-and-advance of exact predecessor/head, domain, root/header,
and selected writer instance/epoch. It must fence competing instances and
revoked writers before admitting effects; an in-memory checkpoint alone is not
a fresh host fence. The fixture witness models this CAS outside the copied
ledger and proves conditional mechanics only.

Each record is created with O_EXCL and held-directory-relative no-follow opens.
File fsync and containing directory fsync precede `PendingCheckpoint`. Newly
named root/records/locks/header/lock files are synced with their parents during
fixture bootstrap. Pending checkpoints cannot yield a borrowed operation or an
acknowledgment. `acknowledge` accepts only a separately selected exact host
confirmation and rechecks complete disk continuity. It does not itself create
host authority. Confirmation is trusted fixed-loader input, never broker JSON.

Crash before confirmation leaves a durable unacknowledged tail: reopen with
the older independent witness quarantines writes but retains any known consumed
event. Crash after confirmation but before reply recovers the same consumed
event under that independently retained confirmation. A witness ahead of the
local chain cannot reconstruct missing identities: inspection reports unknown,
never available. Complete unconfirmed tails require explicit host reconciliation
and fresh independent confirmation; no auto-repair, truncation, reset or GC.

## State, evidence and capacity

Store/slot epochs advance exactly by one. Store replacement cannot bypass an
unresolved operation. Prior slot disposition and containment, plus the complete
C02 SlotReceipt (namespace, family intent, lock identity and time), are retained
as full C01 ByteBindings. The fixed selected authority verifier must validate
those referenced records and exact live state before appending; this ledger
does not dereference evidence or treat a hash/opaque issuer name as authority.
All proof/result/recovery references retain kind/root/path/hash/length.

These C01 references preserve the accepted foundation domain: root and path
lengths count Unicode scalar characters (1..4096), without normalization or an
ASCII restriction; size is 0..i64::MAX. Canonical bytes use exact UTF-8 and signed
i64 JSON. Path traversal, empty components, backslash and NUL remain refused.
Escaped JSON characters remain exact data where the foundation schema admits
them. Local control identifiers retain their separate explicit 128-byte ASCII
identifier rule. The codec/selected record byte limits remain finite; admitting
a binding's schema does not override the selected complete-record capacity.
`codec_vectors.py` independently verifies 33 vectors against the accepted U01
codec/schema, and Rust consumes those exact frozen bytes, including combining
versus precomposed identity, non-BMP characters, escapes, 4096-scalar boundaries
and signed-i64 edges/refusals.

Reservations atomically append operation identity and consumption keyed by the
ledger authority domain plus issuer and host-event identity. Store ID is absent
from the replay key. Result loss, restart, new store IDs and newer epochs never
unconsume the event. Duplicate reservations require inspection, not reexecution.

The bounded baseline serializes one live family and one unresolved operation
per authority domain, across logical stores. `Held::nested` borrows the held
source-slot→publication→replay→native→journal capability. `borrow_operation`
requires the same acknowledged unresolved operation/fingerprint and current
store/slot state; nested effects do not acquire a new family or replay key.
Each real nested effect still needs its own outer verifier authorization.

`Inspection.writable` means control continuity allows bounded appends, never
permission to execute a producer. Unresolved and quarantined counts are exposed.
Quarantined outcomes remain unresolved and fence reserve/store/slot release.
Ordinary append refuses reconciliation variants. A fixed recovery verifier must
supply exact domain/root/writer/head/action and evidence to `reconcile`; only
quarantined outcomes become proven committed/aborted, or a quarantined slot with
no unresolved operation becomes closed. Events/history remain retained.

Finite selected limits bind record count, single record bytes and total bytes.
Normal admissions preserve at least six record-sized terminal slots. The longest
legal terminal path requires five: closing, quarantined outcome, quarantined
slot, outcome reconciliation, terminal slot reconciliation. A sixth slot is
conservative reserve. One unresolved domain operation/live slot makes that
bound enforceable; no automatic expansion or unlimited retries exists. Missing
recovery authority retains quarantine. Exhaustion still permits inspection.
The implementation scans the bounded retained chain under its lock before
writes; it makes no high-throughput/large-history qualification claim.

## Verification and limits

Rust tests cover exact event retention across restart/lost reply/new store,
independent witness mismatch, copied/stale records, writer/branch fencing,
fixture/actual refusal, quarantine recovery, exhausted normal capacity with
complete worst-path terminal recovery, canonical/unknown/duplicate records,
FIFO/symlink/attachment refusal, and borrowed nested capability.

Actual subprocess tests kill a child after durable reservation on both sides
of independent confirmation, reap it, recover locks, and verify consumption.
A separate child contends on the shared domain locks with a bounded timeout.
Test-only compiled syscall-boundary fault injection checks after record create,
write, file fsync and directory fsync; no production fault switch exists. Those
injected failures and process kills are not physical power-loss/media durability
proof. Broken/missing host continuity and actual host antirollback remain G01.

The selected build uses a unit-owned Cargo home/vendor/archives/target/tmp with
`--offline --locked`, baseline actual compiler/linker, minimal environment, and
pre/post checks over effective vendor/config/source/toolchain bytes. The full
local compiler/standard library closure is manifest-selected; larger files are
stream-verified. Host ABI and physical durability remain explicit limits.
Build input negative tests execute normally and under Python -O. Build artifacts
and exact logs are retained for review; temporary fixtures are owned and removed.
