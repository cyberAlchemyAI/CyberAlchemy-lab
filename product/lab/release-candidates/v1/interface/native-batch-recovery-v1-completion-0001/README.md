# Native batch interruption and owned recovery

The original native crate remains byte-identical in `production/`; the separate
observer crate adds only three checkpoint calls and one waiting helper. Stripping
that exact delta restores the original `lib.rs` bytes. The tests use the complete
public `append` command, both original batch APIs, original event validation,
and a separately built original native executable for cold replay. No stripped
persistence-only replacement supplies the semantic evidence.

Direct `NativeCandidateStore.append` calls reach `persist_batch` without an outer
publisher. Real kills after sentinel creation, after the first hardlink and before
cleanup leave recognized zero/partial/full event residue in both stream families.
The original reader correctly refuses `APPEND_IN_PROGRESS`. Its direct API has
no cold crash reconciliation entrypoint. This establishes a recovery/availability
gap; it does not prove that the original reader exposes partial semantic cuts.

API ontology projection has a different boundary: it copies a previously sealed
mapped archive and invokes the native reader, then publishes an immutable
generation and `HEAD`. It does not call the direct append API. Governance
`OwnedPublisher` commits its JSON transaction `HEAD`; repository publication
commits an immutable bundle directory. Neither separate publisher protocol can
be borrowed as proof of direct native batch recovery.

`recoverable_store.py` is an explicit candidate successor wrapper. It requires an
independently identified mode0700 root, exact native executable digest, request
digest, prior `HEAD` digest and independent `PendingPins`. The original native
serializer supplies event bytes; the wrapper preserves those exact substrings,
including struct order and number/string encoding. It refuses requests whose
event digests change when the native sealer checks them.

The wrapper appends only in an uncommitted owned stage copied from the committed
generation. It validates the exact complete postimage through fresh full native
replay, syncs the event directories, and publishes the generation with no-replace
rename. Atomic `HEAD` replacement is the selected-reader commit point; the helper
syncs its parent before reporting a durable completed result. Readers can use
the previous complete generation while native staging is interrupted.

Cold recovery either completes an exactly recognized publication or reconstructs
the independently selected request in a new stage from the original committed
generation. Interrupted stages, sentinels, temporaries and journal files are
retained. An empty native sentinel does not establish its creator or grant
authority: it is never deleted or reused. Foreign names, nonempty unknown locks,
changed event bytes, altered controls, symlinks and unreadable unselected files
refuse before another append or commit. No unknown residue is swept away.

The measurements cover actual process/group `SIGKILL` on this Linux filesystem,
including cuts before generation publication, before `HEAD` commit and after
`HEAD` commit. They do not simulate host power loss or storage-device failure.
Cooperating writers use a persistent kernel file lock; selected roots and source
code must remain protected by the independent runtime profile.

This wrapper is not yet selected by the shared API17 or admitted native lifecycle
entrypoint. Integration must bind its source, controls, root, native executable
and protected operation authority, then qualify that exact selected call path.
The measured direct-append recovery gap remains applicable to the old adapter
until that integration occurs. Technical fixtures create no admission, action
authority, private credentials, service or external publication.
