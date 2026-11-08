# Atomic checkpoint process-interruption results

Status: **PASS** for two independent W7 sequences. Both produced the same
normalized state digest:
`cf37fcb0e8c5ac1cdc3b94c2ec53cdf9e9d9db1f280ea9041ace10c775ab1ecd`.

Each sequence established:

- normal cursor 15 creation used a synced same-directory stage, atomic rename,
  and parent-directory sync;
- process exit 75 immediately after cursor 23 staging sync left the cursor 15
  target byte-identical and exactly recoverable to cursor 47;
- a normal cursor 23 replacement was synced and exactly recoverable;
- process exit 75 after cursor 35 rename but before parent-directory sync left
  a valid cursor 35 target that exactly recovered to cursor 47;
- retrying cursor 35 was idempotent and did not stage or rename again;
- cursor regression returned `CHECKPOINT_REPLACEMENT_REGRESSION` without
  changing the target;
- an incomparable cursor pair returned `CHECKPOINT_REPLACEMENT_INCOMPARABLE`
  without changing the target;
- invalid existing bytes returned `CHECKPOINT_EXISTING_INVALID` and were
  preserved;
- a symbolic-link target returned `CHECKPOINT_TARGET_SYMLINK_FORBIDDEN` without
  touching its referent;
- a held writer lock returned `CHECKPOINT_WRITER_BUSY` without changing the
  target.

An interrupted pre-rename stage remains an orphan diagnostic file and is never
read as a checkpoint. The experiment removes its temporary directory only after
capturing evidence; automatic orphan retention/deletion policy remains separate
operational work.

The evidence is in `evidence/`, raw command output is in `raw-logs/`, and the
source-bound report is `runs/latest-w7-process-interruption.json`.

This proves local process-interruption behavior at two explicit write
boundaries. It does not simulate sudden power loss, storage-controller caches,
filesystem corruption, or cross-platform rename behavior. It establishes no
durability, production, approval, admission, activation, publication, or
cutover claim.
