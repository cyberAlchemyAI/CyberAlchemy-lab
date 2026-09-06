# Benchmark protocol

## Question

Does the actual graph read-model candidate calculate deterministic indexes and
answer ontology-shaped queries correctly as a generated graph grows, and what
local build, query, and estimated payload costs are observed?

## Workload

Each profile deterministically generates active node snapshots, directed
relation snapshots, typed properties, contexts, and one exact challenge
contract per subject. These are noncanonical calculated-cut fixtures.

Each profile also derives one mixed calculated delta from that fixture. The
batch adds, updates, and removes nodes and relations, removes every relation
incident to a removed node, and replaces governance contracts without falsely
advancing the semantic cursor. The incrementally updated model must be exactly
equal to a read model rebuilt from the calculated target cut.

The restart-recovery regime discards the prior read model and performs a cold
rebuild from the verified calculated cut. Recovery must match the declared
runtime identity, cursor, source-event count, source-event-set digest, and
expected rebuilt index digest. Each profile has an explicit maximum local cold
recovery time. No checkpoint input is accepted.

The concurrency regime retains an immutable generation-zero `Arc` snapshot,
starts one serialized writer, and runs the configured reader threads while the
writer stages generation one. Every observation must match the complete old or
new cursor/index-digest tuple. The old snapshot must remain readable after the
writer completes, and the final published model must equal the full target
rebuild. The publication receipt must also prove that unchanged subjects,
challenge contracts, and index buckets are pointer-shared while changed values
are not falsely counted as shared.

The query trace covers:

1. exact subject lookup;
2. bounded, cursor-paged subject identity lookup by type;
3. bounded, cursor-paged subject identity lookup by typed property;
4. outgoing relation lookup;
5. incoming relation lookup;
6. two-hop traversal;
7. context membership; and
8. challenge-contract lookup.

Broad type and property results use pages of at most 4,096 `SubjectKey`
identities. The actual candidate is compared with a scan control. Results are normalized
and compared before timings are eligible for interpretation.

## Measurements

- fixture generation time;
- scan-control build time;
- candidate build and identical rebuild time;
- candidate estimated string payload and generated input payload;
- p50, p95, p99, and maximum latency by query family for both backends;
- candidate/scan p50 ratio;
- deterministic fixture, normalized result, and candidate index digests.
- calculated-delta apply time and full target rebuild time;
- transaction strategy, staged prior-subject count, and full-model-clone flag;
- delta operation counts and exact incremental/full-rebuild model equivalence;
- deterministic target projection, target index, and delta digests.
- old/new/invalid concurrent snapshot observations and publication time;
- retained-old-snapshot, nonblocking-reader, generation, and final-model checks.
- prior and shared subject, challenge-contract, and index-bucket counts.
- cold-recovery time, objective, exact model/index equivalence, source envelope,
  checkpoint-use flag, and corruption-control count.

Estimated payload is not allocator accounting or RSS. Timings are local,
single-process, synthetic observations and include owned result construction.

## Stability and adjudication

`run.py run <profile>` performs two attempts. Correctness or digest divergence
blocks. Timing spread above the configured threshold flags the report but does
not invalidate correctness. The runner keeps attempt JSON, raw logs, and a
timestamped report.

## Claim ceiling

The maximum claim is: this exact prototype produced correct deterministic
results for the declared generated workload on this local environment. The
benchmark cannot prove production readiness or authorize any lifecycle effect.
