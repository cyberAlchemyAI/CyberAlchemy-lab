# CAL-GRAPH-READ-MODEL-BENCHMARK-001 protocol

## Research objective

Determine whether CyberAlchemy should continue with a purpose-built indexed
projection, evaluate WaveDB further, or reject WaveDB as a read-model candidate
for large event-calculated ontology graphs.

## Hypotheses

- H1: SPO/POS indexing preserves the normalized results of the scan control.
- H2: indexed traversal latency grows more slowly than scan latency.
- H3: an external database is justified only if it clears correctness and adds
  measurable value beyond the purpose-built index after integration, rebuild,
  storage, licensing, and operational costs are counted.

## Fixed inputs

- generator seed: recorded per run;
- graph shape: two attribute triples plus N typed relation triples per node;
- query families: the six families listed in `README.md`;
- query trace: identical for every backend;
- Rust build profile: `--release` for timed runs;
- WaveDB source: exact commit recorded in the run.

## Measurements

- deterministic fixture digest;
- normalized result digest and equality;
- build/rebuild time;
- incremental insert latency;
- p50, p95, p99, and maximum query latency by family;
- estimated stored string bytes for the Rust controls;
- external source/build/license posture.

Estimated bytes are not resident memory and must not be presented as RSS.

## Scale ladder

| Profile | Nodes | Triples with 4 relations/node | Purpose |
|---|---:|---:|---|
| smoke | 1,000 | 6,000 | correctness and harness check |
| medium | 10,000 | 60,000 | fast comparative signal |
| large | 100,000 | 600,000 | first large-graph local run |
| stress | 1,000,000 | 6,000,000 | explicit later capacity run |

## Admission rules for results

1. Validate passing and failing synthetic receipts.
2. Run unit tests.
3. Generate the deterministic fixture and trace.
4. Require equal normalized results before considering latency.
5. Preserve each live run as a separate append-only JSONL record.
6. Record missing tools, licensing ambiguity, or backend failure as
   `not_evaluable` or `fail`; do not omit the lane.

## Decision rule

- Prefer the indexed Rust projection when it gives adequate performance with
  less operational and licensing risk.
- Continue WaveDB research only after core licensing is clarified, its pinned
  source builds reproducibly, and its result digest matches both controls.
- Consider WaveDB adoption only in a separate reviewed product decision after
  it demonstrates a material benefit on rebuild time, traversal latency, or
  persistent footprint that compensates for FFI/process integration cost.
