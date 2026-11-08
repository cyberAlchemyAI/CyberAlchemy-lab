# Atomic checkpoint process-interruption protocol

The checkpoint writer takes a non-blocking advisory lock for one target. It
validates any current checkpoint, rejects non-monotonic replacement, writes the
new deterministic cache bytes to a uniquely named file in the target directory,
syncs that file, atomically renames it over the target, and syncs the parent
directory. The persistent zero-byte lock file carries no checkpoint state; its
operating-system lock is released when a process terminates.

The harness sets `CAL_CHECKPOINT_ATOMIC_FAULT` at either `after-stage-sync` or
`after-rename-before-directory-sync` and sets
`CAL_CHECKPOINT_ATOMIC_TERMINATE=exit-75`. The CLI exits immediately with status
75 after the selected boundary. The harness then verifies target bytes and
performs a real checkpoint-plus-canonical-tail recovery to the frozen W7 final
expectation.

An interrupted pre-rename stage is intentionally left as an orphan diagnostic
artifact; it is never read as a checkpoint and does not block a later write.
Automatic orphan deletion is outside this experiment because deletion policy is
operational lifecycle work. Temporary experiment directories are removed by the
harness after their evidence is captured.

The after-rename control verifies process-visible state on the current local
filesystem. It cannot establish what survives an unflushed hardware cache or
sudden power loss, so the report must keep that claim explicitly false.
