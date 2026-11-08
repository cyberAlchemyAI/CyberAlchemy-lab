# Continuous prototype plan

## Product construction lane

1. **Done — canonical calculation:** consume `EventStore::ontology_at` and
   exact governance events at one semantic cursor.
2. **Done — graph scaffold:** index subjects, types, properties, relation
   direction, context membership, and challenge contracts.
3. **Done — query surface:** expose exact lookup, neighbor lookup, relation
   matches, multi-hop traversal, context membership, and challenge lookup.
4. **Done — testable product prototype:** prove deterministic rebuild,
   incremental/full rebuild equivalence, real W7 queries, and fail-closed cursor
   regression.
5. **Done — large deterministic benchmark:** run source-bound smoke, medium,
   and large profiles through 250,000 governed subjects; preserve two-attempt
   correctness, stability, payload, build/rebuild, and query evidence.
6. **Done — bounded broad-query results:** add deterministic `SubjectKey` pages
   with explicit limit and exclusive continuation cursor; prove equivalence and
   rerun all benchmark profiles. Large type/property p50 improved about 31× and
   35× respectively while normalized results remained unchanged.
7. **Done — calculated-delta boundary:** define and implement an exact calculated-delta
   or event-batch boundary, apply node/relation additions, changes, retirements,
   removals, and governance replacements incrementally, then benchmark
   incremental/full-rebuild equivalence at large scale.
8. **Done — bounded atomic transaction:** replace the full-model clone used for atomic
   delta application with bounded transaction staging or a rollback journal;
   preserve fail-closed atomicity and rerun the same exact-equivalence workload.
9. **Done — versioned concurrent snapshots:** define immutable concurrent snapshot
   publication so readers observe one complete calculated cursor while a new
   delta is staged; prove reader consistency under controlled contention.
10. **Done — structurally shared generations:** replace the full graph clone used to stage a
   new published generation with structurally shared subjects and index buckets;
   preserve retained old snapshots and atomic generation publication.
11. **Done — measurable cold recovery:** define measurable restart recovery requirements,
   including maximum replay time, checkpoint validity, corruption behavior, and
   exact rebuild-equivalence evidence; implement and test a checkpoint-free,
   source-bound recovery constructor through 250,000 generated subjects.
12. **Done — process-level canonical event-file recovery:** start independent
   processes that load the frozen W7 semantic and governance event directories,
   calculate the projection, rebuild the read model, verify the exact source
   envelope and index digest, and fail closed for missing input or a changed
   expected digest.
13. **Done — generated event-file scale:** generate 5,000- and 50,000-subject
   canonical-format event-file fixtures, derive expectations independently,
   measure load/validation separately from calculation/rebuild, repair the
   quadratic governance join exposed by the large profile, and pass two exact
   fresh-process attempts plus a tampered-file control per profile.
14. **Done — resource-bounded event-file parity:** generate 250,000 governed
   subjects as 500,000 canonical-format event files, enforce RAM, filesystem,
   inode, virtual-memory, RSS, and time bounds, repair serial event-file loading,
   and pass two exact fresh-process recoveries plus a non-canonical control.
15. **Done — disposable checkpoint and tail replay:** define
   a source-bound checkpoint format whose deterministic bytes remain a
   non-canonical-source and replaceable cache, prototype verified checkpoint
   plus canonical-event tail replay,
   and compare it with the measured checkpoint-free baseline. At 50,000
   subjects, four exact balanced checkpoint-tail recoveries opened only the
   1,000-event tail per stream. The JSON checkpoint stayed within the declared
   1.25x bound and its median was 1.226x faster than full replay, but it won only
   one of four pairs, so no recovery-speed benefit is claimed.
16. **Done — process-interruption-safe checkpoint maintenance:** implement
   same-directory staged writes, file sync, monotonic atomic replacement,
   parent-directory sync, and a non-blocking single-writer lock. Two independent
   W7 sequences preserve an exact old or new recoverable target across process
   termination at both write boundaries and pass stale, incomparable,
   invalid-existing, symlink, idempotence, and writer-contention controls.
17. **Done — sustained calculated-batch ingestion and backpressure:** implement
   a 16-slot single-ingress queue with explicit accepted and retryable-overload
   receipts, semantic and governance watermarks, projection-lag telemetry,
   fail-closed worker status, exact drain, and immutable reader generations. Two
   independent 500-batch attempts sustained 174 and 180 batches/s, projected
   every accepted batch, ended at zero lag, matched an independent final
   rebuild, and produced no torn generation across 13,117,521 reader snapshots.
18. **Current product frontier — canonical append-to-calculation bridge:** bind
   accepted semantic and governance event appends to deterministic calculated
   batches, preserve their dual-stream ordering and acknowledgement boundary,
   and recover accepted-but-unprojected work after a process restart.
19. **Later product work:** test real power-loss/storage durability and broader
   platform semantics before selecting durable persistence.

## Operational residue lane

- Persistence technology and licensing are undecided.
- One serialized ingress owner, bounded backpressure, overload retry, exact
  drain, and retained immutable reader generations are tested for calculated
  batches. Multi-writer ordering and durable accepted-work recovery remain
  undefined.
- Calculated-cut cold recovery is rebuild-only and meets the declared local
  synthetic objectives. Process recovery now reaches 250,000 subjects and
  500,000 event files, but the fixture is synthetic and not a service-level
  workload.
- The parity fixture used 690,644,470 logical event bytes and 2,085,994,496
  allocated filesystem bytes. Recovery peaked at 3,045,052 KiB RSS; allocator
  behavior and sustained-resource pressure remain unmeasured.
- Large bounded-journal delta behavior is benchmarked: 3,190 prior subjects are
  staged for 3,690 changes and the mutable delta application does not clone the
  full model. Versioned publication now shares 247,060 of 250,000 subjects and
  790,240 of 801,016 index buckets in the representative large attempt; its
  copy-on-write map spines remain a measured optimization residue.
- WaveDB remains rejected as the current dependency candidate by the frozen
  benchmark; it can be reconsidered only as a new reviewed candidate.
- A self-digested disposable checkpoint format, exact prefix boundary, canonical
  tail validation, and invalidation controls now pass locally at 50,000 subjects.
  Same-directory staged atomic replacement and process-interruption controls now
  pass on the frozen W7 fixture. Sudden power loss, storage-controller behavior,
  cross-platform replacement, orphan-stage retention/deletion, and durability
  remain product construction or operational policy—not a persistence selection.
- Product approval, ontology admission, activation, publication, and cutover
  remain separate owner decisions after testable-product evidence exists.

This operational residue does not stop prototype construction or tests. It does
stop durability, production-readiness, and activation claims.
