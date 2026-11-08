# Ontology graph read-model prototype

This isolated Rust candidate calculates a disposable graph query model from the
canonical CyberAlchemy ontology event store. It does not own events, ontology
meaning, acceptance, admission, activation, or any external effect.

The model indexes the latest active node and relation snapshots at one exact
semantic cursor. It supplies:

- exact subject and type lookup;
- typed-property lookup;
- bounded type and typed-property identity pages with continuation cursors;
- outgoing and incoming SPO/POS-style relation lookup;
- ordered multi-hop traversal;
- context membership from `belongs_to` relations and explicit context
  properties;
- the exact governance challenge contract joined to every projected subject.
- an atomic calculated-delta boundary for node/relation additions, updates,
  removals, incident-edge cleanup, and governance-only replacement, using a
  bounded rollback journal instead of a full read-model clone.
- versioned immutable `Arc` snapshots: existing readers retain one complete
  generation while a serialized writer stages and atomically publishes the next.
- copy-on-write graph storage that shares unchanged subject payloads, challenge
  contracts, and index buckets between immutable generations.
- checkpoint-free cold recovery bound to the expected runtime identity, cursor,
  source-event envelope, and rebuilt index digest;
- a self-digested, disposable checkpoint cache with an exact canonical-event
  tail boundary and final independent source/index expectation;
- monotonic checkpoint maintenance through a synced same-directory stage,
  atomic rename, parent-directory sync, and non-blocking per-target writer lock.
- bounded single-ingress calculated-batch projection with explicit overload,
  retry, semantic/governance watermarks, lag telemetry, exact drain, observable
  worker failure, and immutable reader snapshots.

The event store remains the canonical replay source. The read model declares
`canonical_replay_source: false` and `authority_effect: none`; deleting it loses
no canonical information.

## Run it

From this directory:

```bash
cargo run --locked --bin cal-ontology-graph-read-model -- summary
cargo run --locked --bin cal-ontology-graph-read-model -- outgoing CA2-PRODUCT-ONTOLOGY includes_capability
cargo run --locked --bin cal-ontology-graph-read-model -- traverse CA2-PROJECT-ONTOLOGY-PRODUCT develops,includes_capability
cargo run --locked --bin cal-ontology-graph-read-model -- context CA2-PROJECT-ONTOLOGY-PRODUCT
cargo run --locked --bin cal-ontology-graph-read-model -- challenge CA2-PRODUCT-ONTOLOGY
cargo run --locked --bin cal-ontology-graph-read-model -- recover-files \
  ../../../migration/cal-w7-ontology-product-epoch-001/fixtures/output/semantic-events \
  ../../../migration/cal-w7-ontology-product-epoch-001/fixtures/output/governance-events \
  recovery-expectation-w7.json

checkpoint_dir="$(mktemp -d /tmp/cal-graph-checkpoint.XXXXXX)"
checkpoint_path="$checkpoint_dir/checkpoint.json"
cargo run --locked --bin cal-ontology-graph-read-model -- checkpoint-create \
  ../../../migration/cal-w7-ontology-product-epoch-001/fixtures/output/semantic-events \
  ../../../migration/cal-w7-ontology-product-epoch-001/fixtures/output/governance-events \
  23 23 "$checkpoint_path"
cargo run --locked --bin cal-ontology-graph-read-model -- recover-checkpoint-tail \
  "$checkpoint_path" \
  ../../../migration/cal-w7-ontology-product-epoch-001/fixtures/output/semantic-events \
  ../../../migration/cal-w7-ontology-product-epoch-001/fixtures/output/governance-events \
  recovery-expectation-w7.json 47

cargo run --locked --bin cal-ontology-graph-read-model -- checkpoint-write-atomic \
  ../../../migration/cal-w7-ontology-product-epoch-001/fixtures/output/semantic-events \
  ../../../migration/cal-w7-ontology-product-epoch-001/fixtures/output/governance-events \
  35 35 "$checkpoint_path"
```

Run the complete repeatable validation:

```bash
python3 validate.py
```

Run the source-bound generated graph benchmark:

```bash
python3 benchmark/run.py run smoke
python3 benchmark/run.py run medium
python3 benchmark/run.py run large
python3 benchmark/validate.py
```

Run the exact W7 fresh-process recovery experiment:

```bash
python3 process-recovery/run.py --rerun
python3 process-recovery/validate.py
```

Run the generated canonical-format event-file profiles:

```bash
python3 event-file-benchmark/run.py run medium --rerun
python3 event-file-benchmark/run.py run large --rerun
python3 event-file-benchmark/validate.py
```

Run the resource-bounded 250,000-subject parity profile only on a host that
meets its preflight requirements:

```bash
python3 event-file-parity/run.py run parity --rerun
python3 event-file-parity/validate.py
```

Run the disposable checkpoint versus full replay experiment:

```bash
python3 checkpoint-recovery/run.py run large --rerun
python3 checkpoint-recovery/validate.py
```

Run the atomic replacement process-interruption experiment:

```bash
python3 checkpoint-crash-consistency/run.py run w7-process-interruption --rerun
python3 checkpoint-crash-consistency/validate.py
```

Run the sustained calculated-batch ingestion experiment:

```bash
python3 sustained-ingestion/run.py run sustained --rerun
python3 sustained-ingestion/validate.py
```

The parity run temporarily creates 500,000 files and checks for at least 7 GB
available memory, 5 GB filesystem capacity, and 600,000 free inodes before it
starts.

The current benchmark covers up to 50,000 nodes, 200,000 relations, and
250,000 governed subjects. Its large mixed delta covers 3,690 changed records
and proves exact equivalence with a full target rebuild. See
[`benchmark/RESULTS.md`](benchmark/RESULTS.md).

The validator writes `receipts/prototype-validation.json`. A PASS means only
that this prototype's declared tests and dependency checks passed. It is not a
product approval, ontology admission, activation, publication, or cutover.

## Current boundary

This version is process-local and non-authoritative. The large benchmark shows that
the edge/path indexes and bounded type/property identity pages work through
250,000 governed subjects and that calculated batches preserve exact rebuilt
state. The bounded rollback journal stages 3,190 prior records for the 3,690
change large batch. Under eight-reader controlled contention, 8,002 boundary
and worker observations contained zero torn generations. The representative
large publication shared 247,060 of 250,000 prior subjects, 246,810 challenge
contracts, and 790,240 of 801,016 index buckets; it took 4.14 seconds versus
12.63 seconds for the preceding full-clone publication epoch. Persistence,
multi-writer semantics, canonical append acknowledgement, durable pending-work
recovery, query planning, allocator accounting, and any third-party database
integration remain later product work.
The earlier benchmark supports the native Rust index
direction and does not admit WaveDB as a dependency.

Cold recovery from a verified calculated cut rebuilt the representative
250,000-subject profile in 5.036 seconds against a 30-second local objective.
Two fresh processes recovered the 47-event frozen W7 fixture directly from its
canonical semantic and governance event directories in 21.83 ms and 10.66 ms.
Generated canonical-format recovery also passed through 50,000 subjects and
100,000 event files in 3.18 seconds and 3.12 seconds. The resource-bounded
parity profile recovered 250,000 subjects from 500,000 files in 63.38 seconds
and 64.67 seconds, peaking at 3,045,052 KiB RSS and reproducing the exact source
and index digests. See
[`event-file-benchmark/RESULTS.md`](event-file-benchmark/RESULTS.md) and
[`event-file-parity/RESULTS.md`](event-file-parity/RESULTS.md). The disposable
checkpoint experiment then recovered the same 50,000-subject final graph from
a 49,000-subject checkpoint plus 1,000 canonical tail events per stream. Four
balanced attempts preserved exact outputs and passed the checkpoint and tail
corruption controls. The 4.631-second checkpoint median was 1.226x faster than
the 5.676-second full-replay median, but it won only one pair. It therefore
establishes no recovery-speed benefit under the declared rule; it stays within
the declared 1.25x prototype bound.
See
[`checkpoint-recovery/RESULTS.md`](checkpoint-recovery/RESULTS.md). This admits
no durable checkpoint or persistence technology. Atomic maintenance now also
passes two deterministic W7 process-interruption sequences; see
[`checkpoint-crash-consistency/RESULTS.md`](checkpoint-crash-consistency/RESULTS.md).
Sudden power loss and storage durability are explicitly not established.

The sustained-ingestion prototype also passed two 500-batch release-process
attempts through a 16-slot queue at 174 and 180 batches/s. Every accepted batch
was projected, explicit overload was retryable, final semantic and governance
lag was zero, the independently rebuilt final digest matched, and more than 13
million concurrent reader snapshots contained no torn generation. See
[`sustained-ingestion/RESULTS.md`](sustained-ingestion/RESULTS.md). This is a
calculated-batch projection result; canonical append, durable pending-work
recovery, and multi-writer ordering remain unproved.
