# Disposable checkpoint and canonical-tail results

The current source-bound `large` epoch passes its declared local synthetic
exactness and bounded-performance quality bar. The four paired attempts used
alternating execution order to reduce cache/order bias.

| Strategy | Attempt 1 | Attempt 2 | Attempt 3 | Attempt 4 | Median | Peak RSS |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Full canonical event replay | 11.146 s | 3.918 s | 3.994 s | 7.359 s | 5.676 s | 664,724 KiB |
| Disposable checkpoint plus canonical tail | 4.339 s | 4.164 s | 4.922 s | 8.715 s | 4.631 s | 761,044 KiB |

Both strategies reproduced the same independently generated final
source-event-set digest and graph index digest in four fresh processes. Each
checkpoint attempt loaded exactly 1,000 semantic and 1,000 governance event
files after a cursor 49,000 boundary; the final cursor was 50,000.

This JSON checkpoint does **not** establish a recovery-speed benefit. Its
median was 1.226x faster than full replay, but it won only one of four paired
attempts and therefore did not meet the declared performance-claim rule. Its
checkpoint-to-full median ratio was 0.816, inside the declared 1.25x prototype
bound, so the checkpoint remains eligible only as an exact disposable cache
and file-fanout reducer. A preindexed or binary format must earn any future
speed claim in a new evidence epoch.

The generated checkpoint was 108,446,895 bytes (108,453,888 allocated bytes).
Checkpoint construction took 25.409 seconds and peaked at 926,580 KiB RSS. Its
cost is measured but excluded from recovery because the checkpoint is a prior,
replaceable cache-maintenance product.

The experiment rejected:

- a non-canonical checkpoint as `CHECKPOINT_NON_CANONICAL_JSON`;
- a changed checkpoint body with its old digest as
  `CHECKPOINT_BODY_DIGEST_MISMATCH`;
- a non-canonical first semantic tail event as `NON_CANONICAL_JSON`.

The evidence is in `evidence/`, the timestamped and latest reports are in
`runs/`, and `validation.json` rebinds them to the current implementation,
generator, experiment, and resource-requirement digests.

This result supports only a local synthetic disposable-checkpoint prototype.
The event files remain canonical. Process-interruption-safe atomic replacement
is measured separately. Power-loss durability, retention, representative
workloads, canonical append acknowledgement, durable pending-work recovery,
multi-writer ordering, approval, admission, and activation are not established.
