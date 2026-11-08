# Fresh Reader stage 0007: observed copy, explicit custody boundary

The 0006 terminal could falsely say `PASS_STAGE_ONLY` when a same-UID actor changed a staged Reader file after the final inventory check. It could also persist PASS after the selected Source period expired during receipt fsync/readback. Both were reproduced in independent synthetic probes. Candidate 0007 preserves the 0006 selected 986-file closure and Source/Reader identities, but uses a new controller identity and a fresh `/tmp/cal-reader-stage-20261020-0001-0007` attempt. It is effect-disabled pending independent review.

The controller's positive statement is **observed copy completion**, not retained-tree custody. A single process cannot make 986 mutable pathnames an atomic immutable snapshot against concurrent same-UID mutation using chmod or ordinary readback. Held directory and file descriptors prevent a selected read from silently following a swapped symlink or replacing its inode during that read; they do not prevent a same-UID peer from changing the tree after the descriptor closes. An exclusive mount/UID boundary would be needed for a continuing custody assertion. The local fixture route therefore does not issue one.

The durable attempt protocol is:

1. Read-only preflight selects exact input pins and checks the Source period and absent attempt; it never opens the private archive body.
2. Durable 0700 attempt and no-replace `consumed.json` precede the first copy. Failure after attempt creation consumes it. The original Source archive is never written or removed.
3. Selected held/no-follow/no-replace copies verify source and destination identity and digest, then fsync data and directory entries. Private files and receipts retain 0600 modes.
4. The controller verifies exact stage inventory and each file by held no-follow descriptor, source archive identity, empty Reader output/evidence, Source predecessor, and current period.
5. It persists a neutral `OBSERVED_STAGE_ONLY` receipt with `reader_input_released=false`; there is no durable PASS. The controller then repeats stage verification and Source/period checks. Its returned OS-zero outcome means these ordered checks completed before expiry. This historical outcome does not imply later currentness or immutable retained paths.
6. Any failure, including expiry during receipt persistence or post-receipt mutation, produces `UNKNOWN` when possible. `UNKNOWN` takes precedence over the neutral receipt; if its write fails, the occupied attempt and nonzero process exit still prevent standalone success. No retry or automatic cleanup occurs.

The later Reader route must freshly check the stage attachment and period immediately before use and establish whatever custody its own claim requires. It must not treat `stage-terminal.json` alone as authorization. A later expired period blocks Reader even if stage copying had completed while current. Synthetic tests are deliberately limited to disposable public bytes; the selected private archive has not been copied or cold-opened by this candidate.
