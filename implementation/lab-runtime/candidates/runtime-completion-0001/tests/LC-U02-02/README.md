# LC-U02-02: held roots and stage/member custody

This candidate implements Linux custody mechanics for an explicitly selected,
finite store profile. It does not ship an actual host provider, grant, privileged
entrypoint, control store adapter, canonical pointer writer or deployment.
The accepted LC-U02-01 library is linked unchanged from a separate unit-owned
Cargo test crate. Only `broker/src/roots.rs` and `members.rs` are new broker code.

## Selection and held custody

`Root::open` checks each exact selected administrator ancestor, named and held
inode, actual Linux mount ID, UID/GID/mode and absence of extended access/default
ACLs. All components use `openat2` beneath/no-symlink/no-magic-link resolution;
mount changes are allowed only at explicitly selected ancestor transitions.
Children cannot cross mounts. Missing kernel support refuses; no fallback.
Selection retains complete C01 ancestor, ACL and writable-alias policy bindings.
Its independently selected execution scope binds activation, store, instance, slot
epoch and principal to the physical root. Every action checks that exact scope
before IO. Namespace custody epoch remains distinct from authority slot epoch;
matching root_id alone cannot carry an old signed activation into a new root.
Those bindings are independently verified host inputs, not evidence inferred by
this library. Previous writable FDs, aliases, mount/user namespace control and
administrator parent exclusivity remain actual deployment requirements.

Fixture roots use bounded independent-open-description flock exclusion. Actual
roots cannot obtain that fixture lock. Later fixed code must construct a
crate-private `ParentHold` only after obtaining the established global order
(source slot, publication, replay, native, journal), and bind its exact root,
namespace epoch and full selected policies. `under_parent` borrows that capability
for the entire stage lifetime and acquires no new per-root lock. No public JSON
can construct it. The module must be statically compiled into that fixed trusted
program; loading candidate code into an authority provider is unsupported.

The supported profile uses a single selected filesystem and parent for stage and
immutable generation names; those names are single components. Member paths are
relative, at most 1024 UTF-8 bytes/32 components, with components at most 255 bytes;
backslash, NUL, empty, dot and dot-dot components refuse. The profile bounds a
stage to 1 GiB, 1024 members, 4096 intermediate directories and 32768-byte chunks.
Actual namespace/profile admission must select compatible limits and names.
These filesystem limits do not narrow C01 metadata identities (Unicode scalar
strings and nonnegative signed-i64 sizes remain intact).

## Exact dispatch, durable receipts and restart

`Action::from_verified` requires the original canonical full frame alongside the
accepted Frame and VerifiedDispatch. It verifies the original full-frame digest
and extracts the already verified permit's full stage binding from those same
bytes. Every write/seal/publication compares it to the original durable creation
receipt binding selected for this stage. Immutable operation fingerprint,
operation ID, sequence, root and fixture/actual domain are also compared.
No differently signed stage or renewed member identity can substitute for them.
Authority/currentness verification must happen in the later fixed dispatcher
under the same current selected control/custody context; an Action is an internal
immediate dispatch value, not an independently renewable network authorization.

New stage/member/directory names use exclusive creation. Chunks must be exact,
contiguous and bounded, preserving full member hash/length/preimage identity.
Each chunk is written, the file is synced, and its containing directory is synced
before a pending transition becomes available. Creating intermediate directories
syncs both new directories and their parents. Partial errors preserve owned bytes;
callers must retain the failed attempt and treat possible writes as uncertain.
The library never truncates a tail to make retry succeed.

Disk writes yield only a `Transition` and proposed metadata, never success.
The fixed control adapter must durably store the exact proposed transition/state
under the historical `(operation_id, sequence, full-frame digest)` and return the
independently selected original receipt bytes with complete C01 binding.
`DurableReceipt::from_fixed_control` and `TrustedState::from_fixed_control` are
crate-private integration boundaries; they are not proof that a host store exists.
Actual callers must verify custody, currentness, persistence and exact historical
selection before construction. The public fixture adapter exclusively creates
and fsyncs a real owned receipt, but cannot create an Actual receipt.

Pending proposed state uses null receipt fields for the new range and retains the
prior sequence. After selecting the exact durable receipt, acknowledgment fills
that range/last-receipt binding, advances sequence by one, and for creation fixes
the immutable stage binding to the original creation receipt. The control loader
must reproduce precisely this derivation on restart; it must not select a latest
member receipt or hash a new wrapper to replace missing original evidence.
The pending state digest avoids a receipt/self-hash cycle. Acknowledgment rechecks
all named attachment, inventory and byte ranges after the control append.

Restart accepts only independently selected trusted state, rechecks every held
attachment, exact inventory and contiguous acknowledged range digest, and refuses
missing entries, aliases, corrupt ranges or any unexplained tail. Receipt bindings
are retained per range, including exact original sequence/full-frame identity.
The fixed dispatcher must stop producer effects while receipt/ack outcome is
uncertain and use the accepted read-only historical receipt/recovery routes.
No replay, truncation, garbage collection or guessed newest state is implemented.

Seal verifies every complete member hash and exact closed manifest, then syncs
files and directories. The exact full manifest binding is fixed by seal.
Publication requires that same manifest/target, `renameat2(RENAME_NOREPLACE)` and
parent sync. Existing empty or populated destinations survive. Publication is
again pending until durable control acknowledgment; it is not canonical visibility.
Failures after rename remain uncertain and preserve the observed generation.

## Evidence and limitations

Tests use only owned inert roots and an explicit fixture issuer. They cover real
filesystem operations, symlink/FIFO/hardlink and ancestor/stage substitution,
mount/mode selection, bounded lock contention, chunk gap/overlap/renewal, missing
receipts, wrong historical receipts, complete hashes, no-replace collisions,
original signed-frame stage substitution, and actual child kills before/after
durable fixture acknowledgment. Test-only syscall boundaries exercise failures
after write, file sync, parent sync and rename. No production fault switch exists.
These tests do not prove physical device power-loss durability or host exclusion
against a malicious administrator/same-UID process; actual host invariants remain
G01 and later namespace/dispatcher/qualification units.

`build.py` uses a private exact offline archive/vendor/config/toolchain closure,
no ambient Cargo home or network. Exact broker/source/test-crate inventories
refuse extra build scripts, nested source or nonregular files before Cargo; the
owned package explicitly disables automatic build-script discovery. Python runs with the accepted regular-file cache
prefix, `-B -S`, and a minimal selected environment. Build-input substitution tests
also run with `-O`. Normal test profile strips debug metadata to keep the selected
16 MiB per-file bound; this does not disable assertions. All development failures,
source pre/post images and terminal outcomes remain in the unit evidence directory.
Successful fixtures clean only their exclusive test roots; failed roots are kept.

This unit introduces no original task acceptance. T02 signed current-family and
runtime obligations remain; original 36 tasks/73 DAG edges, 46 inherited tasks,
63 inherited SWUs and 13 acceptance conditions are unchanged.
