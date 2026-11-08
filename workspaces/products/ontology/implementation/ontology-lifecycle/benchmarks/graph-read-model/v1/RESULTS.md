# Benchmark result: retain the Rust index

Run date: 2026-09-04.

Environment: WSL2 Linux 6.18.33.2, AMD Ryzen 7 5700U, x86-64, Rust 1.94.0.
The result is local, synthetic, single-process evidence only.

## Result

The deterministic 100,000-node / 600,000-triple workload produced the same
normalized result digest in all three query engines:

`874c7185da77bc33c9d66b0559ed1ddcbe6ea28f6af9eb96742e79f703406599`

The purpose-built Rust SPO/POS index outperformed WaveDB's in-memory SPO/POS
graph layer on every query family and rebuilt 8.37 times faster.

| Operation | Rust indexed p50 | WaveDB p50 | WaveDB / Rust |
|---|---:|---:|---:|
| Node by ID | 5.87 us | 13.74 us | 2.34x slower |
| Outgoing relation | 5.56 us | 43.82 us | 7.88x slower |
| Incoming relation | 6.69 us | 23.27 us | 3.48x slower |
| Two-hop traversal | 9.47 us | 49.99 us | 5.28x slower |
| Predicate/object filter | 1.86 ms | 24.79 ms | 13.33x slower |
| Context subgraph | 0.31 ms | 3.47 ms | 11.14x slower |
| Rebuild | 2.01 s | 16.79 s | 8.37x slower |

The Rust index itself is worthwhile compared with the scan control. At this
scale its p50 improvement ranged from 3.35x for a filter returning thousands
of nodes to 2,041x for two-hop traversal. Its trade-off was a 16.9x slower
build than copying the scan vector and about 2x the estimated stored string
payload. That estimate is not RSS.

## WaveDB blockers found by execution

- The WaveDB C graph layer built at commit
  `9c87530e948e414e077fae4f86262a9439905875`; its graph, parser, and schema
  tests passed.
- No root/core license file was present at that commit. Binding-specific
  license files do not resolve reuse terms for the core.
- The in-memory lifecycle attempted WAL/filesystem persistence during
  initialization and graceful destruction. The isolated benchmark skipped
  the defective destroy call and records lifecycle `fail`.
- A persistent smoke rebuild using synchronous per-triple inserts took 39.94
  seconds for only 6,000 triples. This does not compare equivalent durability
  semantics with the Rust in-memory control, but it proves that naive
  event-by-event replay through that API is unsuitable.
- There is no Rust binding in the evaluated repository; production use would
  add FFI or sidecar ownership and failure modes.

## Recommendation

Implement the first large-graph read model as a disposable Rust projection
with SPO and POS indexes. Keep canonical events as the sole authority and
rebuild the index from an exact event cursor.

Reject WaveDB for the current product implementation. Reopen research only if
the core license is clarified and a later version demonstrates clean lifecycle
behavior plus a material advantage over the Rust index under batch rebuild,
persistence, concurrency, and crash-recovery tests.
