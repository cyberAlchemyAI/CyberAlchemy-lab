# Graph read-model benchmark v1

Status: testable research prototype. It is not an admitted runtime component.

Current evidence-backed recommendation: retain the purpose-built Rust SPO/POS
index and reject WaveDB for the current product implementation. See
`RESULTS.md`.

This package tests one narrow question: can a disposable indexed read model
answer ontology-shaped graph queries correctly and materially faster than a
full scan as graph size grows?

Canonical events remain the only source of truth. A benchmark backend may be
deleted and rebuilt from those events. It cannot accept ontology meaning,
calculate authority, change a lifecycle decision, or become an event store.

## Competitors

1. `rust_scan_control` stores the generated triples in one vector and scans it.
2. `rust_spo_pos_index` stores subject-predicate-object and
   predicate-object-subject indexes in memory.
3. `wavedb_graph` is an external candidate pinned to commit
   `9c87530e948e414e077fae4f86262a9439905875`.

The second competitor is essential. It separates the value of indexing from
the value of adopting a database. WaveDB must beat or otherwise justify itself
against this control, not merely beat a scan.

## Ontology-shaped workload

Every generated node has a type, a context, and a configurable number of typed
relations. The deterministic query trace covers:

- node lookup;
- outgoing typed relation;
- incoming typed relation;
- two-hop traversal;
- predicate/object filtering; and
- context subgraph extraction.

Correctness is checked before timing. Backends with different normalized query
results are excluded from performance comparison.

## Run it

Fast verification:

```bash
./run.sh smoke
```

Larger local run (100,000 nodes and 600,000 triples with the defaults):

```bash
./run.sh large
```

Custom run:

```bash
cargo run --release -- \
  --nodes 250000 \
  --edges-per-node 4 \
  --queries 600 \
  --repetitions 5 \
  --seed 65 \
  --output evidence/custom.jsonl
python3 validate.py evidence/custom.jsonl
```

`--output` is append-only JSONL. Use a new evidence filename when changing the
environment or benchmark parameters.

## WaveDB lane

WaveDB has a concrete C graph API with SPO/POS indexes and traversal queries.
The pinned source and three upstream graph tests built after a temporary CMake
tool was supplied. No license file was found for the repository root/core at
the pinned commit. The binding directories have their own license files, which
do not by themselves establish the reuse terms for the C core.

`prepare-wavedb.sh` verifies the pinned commit and attempts an external build.
It never copies WaveDB into this repository. Until the C core license is
clarified, WaveDB remains `not_evaluable` for adoption. The adapter does
produce the same correctness digest, but its in-memory lifecycle fails and its
large-run performance does not beat the Rust index.

## Claim ceiling

Results describe one local, single-process, synthetic experiment. They do not
prove production suitability, crash recovery, concurrent correctness,
durability, operational maintainability, or governance authority. A future
decision may use these receipts as evidence, but the benchmark does not make
that decision.
