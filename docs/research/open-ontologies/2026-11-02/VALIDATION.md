# What was checked

Review date: **2026-11-02**. Source commit: `c7fd75f9491253c56e4d4f408ceac179de343e48`.
Clone: `/tmp/cal-open-ontologies.ANeAQC/repo`.

The [machine-readable verification record](review-verification.json) contains
the final inventory and link-check counts. The
[synthesis review note](mapper-notes/review.md) records follow-up review and
the dependency-source check used to qualify snapshot claims.

## Executed

| Check | Result | What it establishes |
| --- | --- | --- |
| Clone and exact HEAD identification | PASS | The local review uses the named commit. |
| Inventory of every tracked path | 2,924 paths | Paths, sizes, content fingerprints and top-level accounting. |
| Main Rust source classification | 107/107 files, no unclassified modules | Structural coverage; not implementation correctness. |
| `cargo metadata --no-deps --format-version 1 --offline` | PASS | Cargo can read package metadata without resolving/building all dependencies. |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest web/try/test_engine_install.py` | 3 tests PASS, no skips, 0.200 seconds | Browser-demo atomic binary installation and fork/write coordination using fake executables and system utilities. |
| Documentation links, pinned source references and inventory consistency | Checked by the package validation pass | The report navigates to existing files and the inspected source symbols/lines. |

The 24 threads in the first browser test are internal probes, not 24 extra test
cases. These tests do not exercise ontology semantics. Source: [three browser-install tests](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/web/try/test_engine_install.py#L1).

## Inspected without executing

Three mapper passes inspected runtime/storage and concurrency;
reasoning/certificates/formal workspaces and CI; interfaces/data/adjacent apps.
The main pass synthesized the map, checked critical plan/apply and snapshot
paths, compared Lab contracts, and inventoried every tracked file.

The supporting mapper reports are preserved under `mapper-notes/`. They are
working source notes; the synthesis and verification scope here govern claims
about this review. No mapper independently ran engine or formal tests.

## Not executed

- Full Rust build/test/clippy or feature-matrix suite.
- Lean, Isabelle, Rocq, Aeneas, Dafny or Kani builds and proofs.
- W3C suites, differential solvers, large benchmarks or downloaded corpora.
- Python Lite/Vitest suites needing additional dependencies.
- Studio, daemon, server, plugin execution, models or database integration.

The committed W3C SHACL core baseline records 62 pass, 15 fail and 43
undetermined out of 120. The full-result comparison records 54 pass, 23 fail
and 43 undetermined. Those are upstream baseline files, not fresh results from
this review. Source: [recorded SHACL baseline](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/tests/w3c_shacl_baseline.json#L1).

## Scope of confidence

This is a complete structural inventory plus selective source-level analysis.
Recommendations, identified code-path risks and proof-scope descriptions are
not certification of the engine or a guarantee about every version/profile.
The absence of a symbol or field in a reviewed path is scoped to that path.
No integration was applied to Lab runtime code or canonical histories.
