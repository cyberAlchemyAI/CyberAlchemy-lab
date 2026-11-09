# Design: reuse upstream code behind an isolated worker

Source: fabio-rovai/open-ontologies, exact commit c7fd75f9491253c56e4d4f408ceac179de343e48. Reviewed source in /tmp/cal-open-ontologies.ANeAQC/repo. Design evidence only: no copying into the Lab, installation, service start, engine build, or code mutation was performed by this mapper.

## Recommended code-reuse boundary

Copy the upstream standalone Rust engine as one pinned third-party source unit and call its existing local batch interface from a thin Lab adapter. This copies and uses the implementation, rather than recreating its rule engines, parsers, validators, semantic difference logic or certificates inside the Lab.

Keep Lab identities, events, subject versions, relationship admissions and decisions outside the upstream graph. The Lab adapter exports an exact selected view into a disposable RDF working copy and receives an inert report. Upstream graph writes during analysis affect only that disposable copy.

This is more practical than copying individual Rust modules into ontology-lifecycle. Most modules are designed for the common GraphStore/StateDb and Cargo feature environment; transplanting them changes the dependency/verification boundary while saving little implementation work.

## Source-copy units and closures

| Unit | Exact paths to retain | Why this is a coherent unit |
| --- | --- | --- |
| Main standalone engine | Cargo.toml, Cargo.lock, .cargo/config.toml, src/**, LICENSE; retain README.md, CHANGELOG.md and SECURITY.md as upstream packaging/review context | All root module declarations and CLI/server/domain dependencies stay aligned; lockfile and exact patched store dependency remain visible. Build under this source unit as the Cargo root rather than importing it piecemeal into a Lab crate. |
| Upstream checker unit | lean/** with its toolchain and lake metadata, plus LICENSE; parent proof mapper selects exact checker targets | Certificate checks need their actual source and pinned toolchain. Copying only a theorem file does not copy its executable/parser proof closure. Treat binaries separately in the build manifest. |
| Small shared Rust test helpers | tests/common/mod.rs | Fixture strictness and fork/exec test gate are standalone stdlib helpers; preserve original source attribution. These are test helpers, not production synchronization code. |
| Targeted interface regressions | tests/ingest_format_test.rs; tests/batch_reason_budget_test.rs; tests/cli_reasoner_config_test.rs; tests/mapping_test.rs; tests/mapping_boolean_lexical_test.rs; tests/mapping_iri_component_test.rs; tests/mapping_percent_iri_test.rs; relevant snapshot/version tests selected by runtime mapper | Copy the complete test files and any referenced helper/fixture paths. Run unchanged against the vendored standalone crate where possible. Several tests use Cargo's CARGO_BIN_EXE_open-ontologies and CARGO_MANIFEST_DIR, so placing them in a different package breaks their closure. |
| Small synthetic Horn fixtures | tests/fixtures/horn/** | Supplies good and deliberately forged certificate inputs, user versus builtin rule tables, premise/index/binding mutations and self-support cycles. Keep pairings and full directory structure, not only the good case. These are examples of certificate mechanics, not domain admissions. |
| Small synthetic shape fixtures | Specific tests/fixtures/shaclcore/*.nt required by chosen upstream tests | Select exact files through fixture-reference closure. Include valid, invalid, unsupported and unknown-datatype cases. Do not silently copy baseline.json or an entire standards suite and claim its historical results are fresh. |
| Optional Python Lite unit | python/pyproject.toml, python/README.md, python/src/open_ontologies_lite/**, root LICENSE; targeted python/tests and conftest.py | A coherent separately implemented RDF library package. Must include horn/tables/builtin_rules.tsv as package data because rule loading uses resources; copying only engine.py loses package-level imports and functionality. |

File selection should be machine-generated from an allowlist plus literal referenced-file closure, then reviewed. Explicitly exclude .git, target, node_modules, local config, downloaded models and generated caches. Preserve the original license notices within copied code. Do not rewrite imports or run automated formatting on the upstream copy merely to match Lab style.

If the third-party engine is ever made a dependency inside a larger Cargo workspace, its own patch.crates-io can be ignored because patches belong to the Cargo root. That would lose the intended Oxigraph fork unless the workspace also carries it. The isolated standalone build avoids that issue and preserves the upstream Cargo.toml as reviewed.

## Why selective module extraction is the second choice

The smallest relatively independent source candidates are:

- src/induce.rs and src/mapping.rs as a pair. Induction imports MappingConfig and FieldMapping; MappingConfig calls induce::Dt for lexical validation (mapping.rs:97). Production logic needs serde and the pair; tests inside induce.rs additionally call GraphStore at795. A port copying only one file is incomplete.
- src/ossie.rs needs serde and serde_json for production and carries translation-loss reporting in the same file. Its tests additionally reference GraphStore at1269; whole-module reuse plus its tests therefore expands to the engine environment.
- src/ingest.rs requires anyhow, csv, serde_json, quick-xml, serde_yaml, calamine, arrow and parquet through its parser branches. Copying the “simple ingestion helper” has a much larger dependency surface than its first function suggests.
- src/extract_scaffold.rs requires GraphStore and language::parse_literal. It is not just a standalone prompt template.
- src/segment_retrieve.rs requires GraphStore and RDF serialization behavior. Slicing this alone would omit the separate preservation checks that determine whether a retrieved context still supports required conclusions.
- src/sql_sync.rs depends on StateDb. Copying it does not bring SQL source identity, atomicity across systems, or Lab admission.

If a later layer needs these in-process, make extraction an explicit tracked fork with its own dependency closure and parity tests. For the first analyzer, using the intact upstream worker maximizes real reused code and minimizes rewritten semantics.

## Actual local worker interface

Use a subprocess argument array, never a shell script containing interpolated paths or queries:

    [binary_path, "--no-connect", "--data-dir", unique_job_dir,
     "--json", "batch", "-", "--bail"]

The global --no-connect flag is declared at src/main.rs:212-214. live_daemon at1563-1567 returns no daemon under that flag. This matters: otherwise proxy-able commands may target a running daemon and a different shared store.

Send a JSON array on stdin. The argument-array form preserves positional arguments:

    [
      {"command": "load", "args": ["/job/selected-view.ttl"]},
      {"command": "stats"},
      {"command": "vocab-check", "args": ["/job/data.ttl"]},
      {"command": "shacl", "args": ["/job/shapes.ttl"]}
    ]

The exact requested operations should be an allowlist generated by the adapter, never arbitrary agent-provided batch commands. The sample is an interface shape, not an executed experiment. Every chosen command/profile must be exercised against the pinned version before that adapter is accepted.

Important parser behavior at src/batch.rs:1607-1647:

- A string args value is one positional argument.
- An array is a sequence of literal positional/flag arguments.
- An object is flattened into flags; args={"path":"x.ttl"} becomes --path x.ttl and can break positional commands. Use arrays or a bare string for paths.

Batch shares one graph inside its process, executes commands in order, and emits NDJSON envelopes with seq, command and result (src/batch.rs:80-136). Use one batch for load followed by checks because separate one-shot in-memory invocations would not share the graph.

Parse every envelope and the process exit status. Per-command result.exit_code and stop_the_line are propagated to the final status. Do not interpret a zero shell exit as independent evidence of every semantic obligation; the adapter must require expected rows, expected command names, output shape, source fingerprints, and the selected verdict policy. --bail concerns errors and stop-the-line results; do not assume that every domain-level nonzero result interrupts subsequent lines.

Only permit commands that work on copied inputs and a disposable state directory. Do not start serve, serve-http, daemon, serve-unix, Studio, marketplace fetch, SQL connectors or remote embedding calls in the initial worker. This is a bounded analyzer, not an alternate owner of the Lab.

## Build and dependency boundary

Cargo defaults to no optional features. Keep that exact initial feature set rather than --all-features. Core RDF, reason, shape and planning paths still have substantial dependencies, including Oxigraph/RocksDB, SQLite, Tokio, Axum, rmcp, arrow and parquet; “single binary” does not mean a small source build.

The engine pins Oxigraph to revision 37db8e1522585ed2f9aa994be6c5c716859af5c8 in Cargo.toml's patch.crates-io. This fork carries snapshot and lexical-form changes; replacing it with the normal 0.5 crate is a behavior change. Capture the fork's full dependency identity and license alongside the root source.

Optional features are explicit expansion choices:

- embeddings: tract ONNX, tokenizers, instant-distance, bincode and external model/tokenizer assets; remote embedding settings may introduce a network provider.
- postgres/duckdb/sql: relational connections and additional native builds. sql means both connectors.
- plugins: wasmi WASM host, local plugin discovery and plugin input context.
- causal-pywhy: Python subprocess plus separately installed DoWhy/networkx/pandas/numpy; default structural assumptions differ from an actual backdoor identification result.
- turbovec: implies embeddings and changes the cosine index backend.

src/toolfilter.rs:453-475 filters eight MCP tools by feature availability. This matters if an MCP-facing layer is added later; it is not needed to invent a new tool server for the first batch worker.

The repo does not pin a Rust compiler through a root rust-toolchain file; CI selects stable. Record the actually selected rustc and cargo versions and target triple in Lab build provenance instead of presenting “stable” as a reproducible compiler identity. Root edition is 2024. .cargo/config.toml carries MSVC static-runtime flags and should remain attached to the source unit for Windows builds.

The initial review ran Cargo metadata offline/no-deps but did not compile the core. A proposed source-copy list is not evidence that this exact engine builds in the Lab environment.

## Python Lite: an alternate lower-weight layer, not engine parity

Copying the Python unit is reasonable if the first experiment needs RDF parsing, SPARQL, vocabulary checking, typed row intake, KGCL or the pure-Python Horn certificate emitter without compiling the Rust engine.

Core dependency is pyoxigraph >=0.5.12,<0.6 (python/pyproject.toml:47-49). It is a wheel wrapper over the RDF store, not the same Rust engine crate. Optional server, shacl and align extras add MCP, pyshacl and hnswlib separately. Do not install those extras by default. The standalone Lean checker is intentionally an external binary, never an implied Python dependency.

The package imports more than the engine class at top level. Preserve __init__.py, dataframe.py, engine.py, kgcl.py, vocab_check.py, the horn package including its table, and optional modules if preserving upstream packaging unchanged. Keep the package whole rather than surgically re-exporting one class and then accidentally triggering missing imports.

Python's Horn reasoner uses the same design/rule table as Rust and its header explicitly says it is not an independent semantic oracle (horn/reason.py:1-31). Agreement catches transcription errors more than shared rule misunderstandings. It reports no verified verdict without the external checker; horn/certify.py:1-29 delegates verdict words to the checker.

If Rust is the chosen analyzer engine, adding Lite immediately creates a second implementation/profile matrix. Prefer a single engine for the initial result contract, with Lite later as an optional lightweight mode or differential leg. Report which implementation, version, rule table, optional extras and checker produced each result. Never silently fall back from Rust to Lite and preserve the same conformance claim.

## Test code that can be reused directly

1. Keep tests/common/mod.rs: fixture requirements fail under OO_REQUIRE_FIXTURES=1 instead of silently returning success; exec_gate coordinates file-writing/fork tests. This helper alone is not an application writer lock.
2. Preserve python/tests/conftest.py with selected Python tests. It catches run-time and collection-time skips, promoting missing required fixtures to failure. Any opt-in slow skip remains explicit.
3. Useful dependency-light Python cases: test_engine.py, test_dataframe.py, test_kgcl.py, test_kgcl_literal_datatype.py, test_query_triple_terms.py, test_vocab_check.py, test_library_needs_no_server_stack.py. These test the package that was copied; they do not verify Lab RDF export is meaning-preserving.
4. For certificates retain test_horn_certificate_bytes.py, test_horn_rule_table.py, test_horn_checker_relative.py, test_horn_unchecked_never_reports_checked.py and test_the_verdict_words_are_never_written_in_python.py. Audit literal paths: test_horn_rule_table.py:104 reaches repository tests/fixtures/horn/builtin_rules.tsv. Preserve that path or record a deliberate harness patch.
5. Keep negative fixtures together with good ones. Certificates with forged conclusions, invalid premise indices, mismatched bindings and self-support must fail for their stated reasons.
6. Do not copy tests/induce_one_sheet_test.rs alone and call it self-contained. It reads benchmark/data/pizza-menu.csv and benchmark/epc/epc-sample.csv through CARGO_MANIFEST_DIR. Those datasets require a selected fixture/license closure. Same warning applies to tests with external prover/model/network preflights.

web/try/test_engine_install.py is a reusable demonstration of executable atomic-replacement tests but should not become the Lab's binary identity mechanism unchanged. The corresponding installer at web/try/api/index.py:50-55 treats file size plus executable bit as installed; different same-size bytes can look identical. The Lab worker should select a fixed binary and verify its full digest, not depend on that install cache. Root ran its three tests successfully, which verifies race mechanics only.

New Lab-specific acceptance tests still need to cover exact event-cut export, identity/reference preservation, unsupported-field loss reporting, result binding, rejected stale inputs, separate-agent job directories and refusal to apply upstream findings as owner decisions. Those are adapter obligations; upstream copied tests cannot establish them.

## Provenance and source-copy manifest

Suggested fields for a reviewed source-copy record:

- Record schema/version; acquisition time; upstream repository URL; commit ID and tree ID; local clean-check status at acquisition.
- One entry per copied file: upstream path, destination path, Git blob ID, byte length, SHA-256, copy mode unchanged/patched, and original source URL pinned to commit.
- License identity, exact license file bytes/digest, retained notices, separately licensed file/data exceptions and required attribution text.
- Included roots and explicit excluded roots; fixture-reference closure; test fixture role good/negative/unsupported; no broad dataset copying by implication.
- Patch ID and patch digest for every departure from upstream bytes, affected paths, reason, reviewer/evidence, and tests required by that patch.
- Cargo.lock/pyproject/package-table digests, resolved dependency versions and source revisions (including patched Oxigraph), feature set, compiler/runtime versions and build command argv.
- Selected tests, actual result files/digests, discovered/passed/failed/skipped counts, skip reasons, required-tool policy and evidence boundary.
- Output binary SHA-256, target platform, build profile/options, checker binary identities and toolchain identities.

A separate per-analysis manifest binds:

- Job/agent identity; exact Lab source event cut; complete selected-view digest including review information; input artifact/version/digests; export-mapping version and configuration digest.
- Original Lab input digests, RDF and SHACL input digests, source-record/term mapping, known unsupported constructs and omitted fields.
- Exact worker binary/checker digests, command argv, structured stdin digest, working-directory identity, selected feature/profile, limits/timeouts.
- Raw stdout/stderr digests, process exit status, parsed report digest, each reported rule/verdict, unavailable tools and unsupported/incomplete reasoning.
- Output posture analysis-only; authority effect none; admission effect none; no source-event append; no shared-state writes or activation.

An upstream content digest or checked RDF derivation is evidence about those exact bytes and formal assumptions. It is not a certificate that a translated Lab rule, ontology admission, causal claim, or real-world assertion is true.

## Dataset and asset copying exclusions

The engine's root LICENSE is MIT, but the repository contains separate licenses. No broad benchmark/**, data/**, demo/corpus/**, case-studies/**, generated media, downloaded ontologies or model files should enter the default code-copy set.

Observed concrete exceptions:

- tests/w3c-shacl/LICENSE.md names the W3C Software and Document License. Reusing that suite needs its own source/license envelope.
- benchmark/ontoaxiom/LICENSE is Apache-2.0.
- demo/corpus/dcat-us/jsonschema/LICENSE.md is a separate source license.
- case-studies/skills-england-esco-crosswalk/README.md:8-9 identifies OGLv3/CC-BY4 source data and CC-BY4 crosswalk licensing.
- case-studies/robot-safety-security-crosswalk/LICENSE distinguishes CC-BY4 vocabulary/mappings/docs, separately described code, and third-party standards rights.
- case-studies/modip-plastics-kg/LICENSE distinguishes CC-BY4 source records/derived vocabulary and MIT code.

Select needed synthetic fixtures file by file, retain applicable root/license notices, and document provenance. Do not copy domain benchmark assets merely because an upstream test references them; either admit that exact fixture closure separately or choose a different upstream regression for the first layer.
