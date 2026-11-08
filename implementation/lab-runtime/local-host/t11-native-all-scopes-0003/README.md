# T11 exact-230 native runner successor

This runner selects the unchanged, independently cold-reviewed
`t11-native-all-scopes-0002/runtime` and its SHA-pinned manifest. It retains
the nine bounded batches, signed exact-body delivery, cumulative original-byte
verification, per-scope final fresh-process readback, and task-owned scratch
cleanup. The four cold tests pass normally and with `-O`.

The preceding `0002` native attempt applied the four legacy batches to a
disposable store, then stopped at its duplicate negative. That negative changed
the proposal ID, so the exact-batch guard correctly refused it before reaching
the requested reused-Decision check. Its zero-byte `RESULT.json` and
`RUN.stderr` are retained as failed diagnostic evidence; they are not a
230-member terminal receipt. This successor keeps the exact proposal ID,
updates only the expected HEAD to the committed successor, and requires the
native reused-Decision refusal while confirming the applied projection did
not change. It does not relax the batch guard or original-byte limit.

The native rerun exited zero. [RESULT.json](RESULT.json) has SHA-256
`cd954c1573c5f1af0f72272715394632e37e75ef2ff237d2d6cbeca2bf53e0d8`:
nine native batches applied all 230 exact fixture bodies across the six
original scopes. Final fresh-process cold readbacks cover 220+1+1+1+1+6
members. The four intermediate legacy heads had 64, 128, 131, then zero
unresolved selected internal references; only the final head is complete.
Wrong-scope, missing-consumer, expired-grant, stale-head, wrong-member,
changed-original-digest, missing-member, and duplicate-after-apply negatives
refused. `RUN.stderr` is empty and task-owned scratch is empty after exit.
Even this fixture pass is not original T11 admission: the source snapshot is
historical, signatures are local fixtures, and original producer
execution/current grants remain distinct. The receipt reports original
operational completion as 0/230.
