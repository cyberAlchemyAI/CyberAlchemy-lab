# Graph read-model benchmark result

Status: **PASS** for deterministic correctness and two-attempt local stability.

The final attempt set is bound to implementation digest:

`d7831f02ed61dbaadcd63bf20e3e3e59141ae9eb165d20a036df99ba2002f5c5`

All six attempts produced stable fixture, normalized query-result, and index
digests within each profile. Target projection, resulting index, and calculated
delta digests were also stable. These are local, synthetic, single-process results.

## Profiles

| Profile | Nodes | Relations | Subjects | Input payload | Index payload estimate | Candidate build |
|---|---:|---:|---:|---:|---:|---:|
| Smoke | 1,000 | 4,000 | 5,000 | 6.35 MiB | 7.05 MiB | 0.090 s |
| Medium | 10,000 | 40,000 | 50,000 | 63.57 MiB | 70.56 MiB | 1.014 s |
| Large | 50,000 | 200,000 | 250,000 | 318.26 MiB | 353.03 MiB | 5.655 s |

The representative large deterministic cold recovery took 5.900 seconds. The
two large build attempts differed by 1.005×; the largest p50 spread across its
query families was 1.18×, within the declared stability limits.

Payload values count serialized/string material. They are not allocator usage
or resident-set memory.

## Large-profile query result

| Query family | Candidate p50 | Candidate / scan | Interpretation |
|---|---:|---:|---|
| Exact subject | 12.47 us | 0.0030× | about 335× faster |
| Outgoing relation | 35.97 us | 0.0059× | about 170× faster |
| Incoming relation | 39.51 us | 0.0065× | about 155× faster |
| Two-hop traversal | 49.33 us | 0.0039× | about 253× faster |
| Context membership | 0.66 ms | 0.0500× | about 20.0× faster |
| Challenge contract | 11.99 us | 0.0627× | about 15.9× faster |
| Typed property identities | 2.76 ms | 0.3083× | about 3.24× faster |
| Type membership identities | 4.86 ms | 1.0691× | about 1.07× slower |

## Finding

The graph index is effective for exact, edge, path, context, and challenge
queries. It scales to the declared 250,000-subject generated profile with
stable deterministic results.

The previous broad-query defect is repaired without removing the compatibility
APIs. New type/property query methods return deterministic `SubjectKey` pages,
reject zero or oversized limits, and use an exclusive continuation cursor.
Each call returns no more than 4,096 identities; callers resolve complete
semantic snapshots only when needed.

The bounded property API remains faster than the scan control, while the
representative type page is approximately at parity and slightly slower. Both
return the same normalized identities. Their latency is reported directly; the
recovery change does not claim a query-speed improvement.

## Calculated-delta result

| Profile | Total changes | Prior subjects staged | Full clone | Delta apply | Full target rebuild | Apply / rebuild |
|---|---:|---:|---:|---:|---:|---:|
| Smoke | 147 | 127 | no | 0.056 s | 0.082 s | 0.68× |
| Medium | 738 | 638 | no | 0.629 s | 0.973 s | 0.65× |
| Large | 3,690 | 3,190 | no | 3.242 s | 5.632 s | 0.58× |

Every incremental result was exactly equal to a separately constructed full
target read model. Removals include every relation incident to each removed
node. Governance-only replacements preserved the semantic cursor. Invalid base
metadata, stale subject versions, incomplete cursor ranges, missing endpoints,
and target projection digest mismatch fail before the original model changes.

Correctness is established for this workload. The representative attempts in
all three profiles applied the delta faster than a full target rebuild. The bounded
rollback journal stores only changed prior subjects and contracts. Post-delta
endpoint validation and projection-digest validation run before mutation;
governance-only changes bypass semantic reindexing.

This is local synthetic timing, not a production latency guarantee.

## Concurrent snapshot publication

| Profile | Reader threads | Worker observations | Old generation | New generation | Invalid/torn | Publication time |
|---|---:|---:|---:|---:|---:|---:|
| Smoke | 4 | 4,000 | 4,001 | 1 | 0 | 0.068 s |
| Medium | 8 | 8,000 | 8,001 | 1 | 0 | 0.782 s |
| Large | 8 | 8,000 | 8,001 | 1 | 0 | 4.135 s |

The counts include one retained old boundary snapshot and one final new boundary
snapshot in addition to the worker observations. Each old `Arc` snapshot stayed
readable while the serialized writer copy-on-wrote changed map spines and
buckets, validated the successor, and published generation and graph together. Across both
large attempts, all 16,004 observations were valid and none mixed a cursor,
generation, or index digest.

Readers do not block the writer and can retain an old generation after the new
one is published. The writer is serialized. The representative large generation
shared 247,060 of 250,000 subjects, 246,810 of 250,000 challenge contracts, and
790,240 of 801,016 index buckets. Its 4.135-second publication was about 67%
lower than the preceding full-clone epoch's 12.631 seconds. These are local
observations, not a latency guarantee.

## Restart recovery

| Profile | Subjects | Cold recovery | Objective | Exact model/index | Checkpoint used |
|---|---:|---:|---:|---|---|
| Smoke | 5,000 | 0.082 s | 1.000 s | yes | no |
| Medium | 50,000 | 1.028 s | 5.000 s | yes | no |
| Large | 250,000 | 5.900 s | 30.000 s | yes | no |

Every cold recovery bound the expected runtime identity, semantic cursor,
source-event count, source-event-set digest, and rebuilt index digest. Two
attempts per profile met the local objective; the large cold-recovery spread was
1.10×. Unit controls reject a changed runtime identity, changed source envelope,
corrupt governance reference, and mismatched expected rebuilt digest. No checkpoint format is
eligible or read in this regime.

This table proves only recovery from the verified calculated-cut input used by
the generated benchmark. Separate fresh-process experiments prove the 47-event
W7 fixture and synthetic canonical-format event files through 250,000 subjects.
Those regimes do not prove crash consistency, durability, representative
capacity, or a recovery service level.

## Recommendation

Retain the Rust read-model direction and the bounded identity-page contract.
The exact benchmark requirement is satisfied for this prototype: type/property
performance improved while normalized results remained unchanged.

Large calculated-delta correctness, bounded transaction staging, retained
immutable snapshot publication, structurally shared generation staging, and
calculated-cut cold recovery are now evaluable and pass. The next product regime
is a disposable source-bound checkpoint plus canonical tail-replay prototype,
using the measured 250,000-subject event-file recovery as its baseline.
Multi-writer behavior, sustained ingestion, crash consistency, and durability
remain later regimes.

This PASS is prototype evidence only. It grants no product approval, ontology
admission, runtime activation, publication, or cutover.
