# Interfaces, data, and adjacent products map

Reviewed source commit c7fd75f9491253c56e4d4f408ceac179de343e48 in /tmp/cal-open-ontologies.ANeAQC/repo. This mapper inspected code and existing tests; it installed nothing, launched no service, executed no model, and modified no clone files. Paths and one-based line numbers below are source evidence.

## Architectural shape

The root Rust crate is the main engine and interface adapter collection. It exports domain modules from src/lib.rs and owns a large MCP facade in src/server.rs. Optional features change both compiled capabilities and the advertised MCP surface. This is not a workspace of independent microservices: most features call the same GraphStore and StateDb through one crate. Alongside it are separately built Python Lite and Tauri/React Studio products, plus a browser demonstration and document extraction scripts.

Main dependency direction: transport/input records -> server orchestration -> ingest/mapping/extraction/alignment/graph domain modules -> graph store, state store, external providers. Studio -> Tauri -> engine MCP/REST. Python Lite -> pyoxigraph, not the Rust engine. Demo scripts -> model HTTP API and engine MCP HTTP API. Browser try -> released binary subprocess and optional separate certificate checker.

Evidence: src/server.rs:21,48-64,119-170; src/inputs.rs:7; src/lib.rs:62-79,121-154; studio/src/lib/mcp-client.ts:1-21,42-57; python/pyproject.toml:19-49; demo/ontology_from_docs.py:49-51; web/try/api/index.py:122-152,188-196.

## Data intake and mapping

1. src/ingest.rs:19-38 detects CSV, JSON, NDJSON, XML, YAML, XLSX, and Parquet; parse_file_with_format at 455 selects the parser. Parsed output is a vector of string-to-string maps. JSON object/array values are flattened or serialized as strings; this is useful tabular intake, not arbitrary document semantic interpretation.
2. src/mapping.rs:5-23 defines field/predicate/datatype/class/lookup mapping. from_headers at 34 generates naive mappings: first column is identifier, columns become string properties. row_to_triples at 69 creates subject/type triples and typed literals or lookup IRIs; invalid known datatype lexemes are deliberately emitted as plain strings for validation to catch, rather than misleadingly tagged as a valid datatype.
3. src/server.rs:1060-1147 traces onto_ingest: parse data, parse supplied mapping or generate header mapping, render N-Triples, optionally add PROV-O source data, load graph. Source provenance is optional (provenance defaults false at 1105), not a mandatory row-level source digest or admission record. The generated source IRI is filename-derived and source timestamp is current wall clock; do not mistake this for CyberAlchemy's exact immutable evidence identity.
4. onto_map at src/server.rs:1344-1395 queries available classes/properties and returns them, but actually constructs the mapping with MappingConfig::from_headers and the first available class. It is not an implemented semantic column alignment algorithm despite the broader tool description.
5. src/induce.rs:1-31 and 356-365 contains deterministic schema hypothesis generation from tabular observations: identifiers, datatypes, repeated numbered columns, cardinality and small enumerations. Crucial design choices: label outputs as hypotheses, explain each induced statement, use SHACL cardinality instead of OWL functional-property identity inference, and retain observed ranges as evidence instead of constraining future values. onto_induce is at src/server.rs:1151.
6. src/sqlsource.rs:40-61,107-119 wraps PostgreSQL and DuckDB row queries and introspection. Cargo feature flags postgres/duckdb/sql govern availability. src/sql_sync.rs:47-97,168 stores watermarks and uses ordered synchronization; MCP wrappers live at src/server.rs:2934-3051. This is incremental ingestion bookkeeping, not globally atomic CDC across a database and ontology history.
7. src/ossie.rs:1-38 imports conceptual ontology documents into OWL and SHACL. It explicitly names constructs OWL cannot express, generates SHACL where possible, and preserves unsupported derivation/rule strings as declared annotations and issues. This is a valuable model-translation loss ledger.

## Extraction and candidate interpretation

src/extract_scaffold.rs:1-15,42 creates a schema-guided extraction prompt from ontology metadata. It does not call an LLM; the orchestrator supplies generated JSON, validated by validate_extraction at 240. The two MCP tools are src/server.rs:1705-1715. This separation is reusable for Lab intake: produce a bounded request, accept candidate output, independently validate it.

The demo is a different path: demo/ontology_from_docs.py:49-51 calls a configured model endpoint (default localhost:8081/v1) and engine MCP HTTP endpoint (default 127.0.0.1:8137). Its stages derive per-document vocabulary, merge/reconcile, populate and verify. Reconciliation logic is at 621. demo/README.md explains that make demo requires both external services; the separate contradiction_scan.py is not wired into make demo. The committed precomputed artifacts support replay, not a live extraction demonstration.

Adjacent alignment modules are independent signals rather than blanket semantic equivalence: src/align.rs; src/align_fuzzy.rs:25-58,204 (Mamdani fuzzy signal adjudication); src/flora_pipeline.rs:150,173,224 (class candidate enumeration and structural signals); src/crosswalk.rs:100,108,143,259,418 (mapping certification, gaps, SSSOM output); src/communities.rs:28-78 (structural community skeletons). Direct reuse must preserve candidate/score versus admitted semantic mapping distinctions.

## Retrieval, context selection, and embeddings

src/segment_retrieve.rs:1-87 retrieves a bounded neighborhood through named schema predicates and optional instance triples. This is useful seed/hop selection; it is not alone a proof that all needed entailments remain. It also handles RDF term serialization and blank-node identity caveats explicitly.

src/module_extract.rs:874-1095 supplies locality-based axiom modules; src/projection_check.rs and src/projection_entailment.rs evaluate selected-view claims. Parent reasoning mapper covers their proof limits. Important reuse lesson: distinguish simple neighborhood coverage from preserving the conclusions needed by a consumer.

Embedding stack: src/embed.rs:1-47,149,205 loads local ONNX/tokenizer models (tract), and src/embed_remote.rs:1-6,41-94 calls an OpenAI-compatible embeddings endpoint. Local models are external assets, not shipped facts; remote embeddings add network/provider requirements. src/embed_fingerprint.rs:89,145 fingerprints provider configuration to bind cached vectors; src/vecstore.rs:21 maintains vectors; src/hnsw_index.rs:50-100 and183 define cosine/Poincare HNSW variants; src/turbo_index.rs:39 adds feature-gated incremental quantized cosine indexing; src/structembed.rs:11,87 trains structural vectors.

src/eval_rag.rs:31-86,214-244 exposes evaluation reports and lexical similarity/faithfulness-style measures. These are measurements, not semantic entailment proofs. Retaining this distinction is essential for Lab confidence claims.

## Causal layer and plugins

src/civex.rs:1-42 explicitly documents a structural proxy behind four action verdicts EXECUTE/REJECT/EXPERIMENT/ABSTAIN, not full causality or authority. Its default identification mode is structural. Actual code at 426-504 optionally calls the Python DoWhy wrapper when causal-pywhy is compiled and requested, with explicit labeled fallback on unavailable/unidentifiable results. CAUTION: src/civex_pywhy.rs:18-24 still says not integrated; that header is stale relative to executable callsites. Even the optional DAG is formed from ontology structural neighbors plus a synthetic utility sink (src/civex.rs:507-514), so importing this as a causal safety proof would be unjustified.

src/plugins.rs:1-24 defines WASM plugins as JSON-to-JSON transforms with no host imports or direct graph access. Callers may inject explicit SPARQL bindings. ABI requires memory, version, allocation, description, and call exports. Limits at 31-38 include fuel and return-size cap; instantiation at 164-175 rejects host-import requirements. Discovery is local from environment override or user/local plugin folders at 65-81. Feature flag plugins is required. Good reuse pattern: explicit capability-bearing input and bounded computation; no implicit authority from loading a plugin.

## MCP and transport integration

src/server.rs:48-64 constructs services over shared graph/state. Unsupported-build tools are removed before operator filtering (138-170); src/toolfilter.rs:249-256 defines common six-tool spine and profiles at 258 onward. A task profile narrows discovery; a separate mode/allow/deny axis narrows it further. Default profile remains full. This is useful selective context/tool exposure for agents, but tool omission must not be presented as an owner-authorization system.

Rust main supports stdio MCP, streamable HTTP, Unix socket, daemon and local batch/CLI paths (src/main.rs:233,274,327,364). The root mapper handles exact auth/effect details. Credentials and HTTP configuration include bearer token support; optional configured empty token disables that authentication (main.rs:115-120). Batch proxy fallback to local execution is explicit in src/connect.rs:1-20: auth/network mismatch can cause announced local fallback, and local store need not equal daemon store. Integration should pin the target and refuse unintended mode switching for consequential actions.

Observability: src/main.rs:1907-1955 configures tracing level, text/JSON output and stdout/stderr/file routing; server initialization emits cache/tool-filter/provider diagnostics (server.rs:127-231). Query/validation/certificate JSON artifacts form a major inspectable signal surface. I did not identify this as a complete metrics/tracing operations platform; do not infer Prometheus or distributed tracing from the presence of tracing macros.

## Python Lite is a separate implementation

python/pyproject.toml:5-10 names open-ontologies-lite 0.5.0, Python >=3.10. Core dependency is pyoxigraph >=0.5.12,<0.6 at 47-49; server/SHACL/HNSW extras at 51-56 add mcp/pyshacl/hnswlib. It has no Pyo3 binding to the main crate. Its Horn reasoner is pure Python; Lean checker is an optional external binary that must be independently built (comments 28-39).

python/src/open_ontologies_lite/engine.py:81-94,135,182,231 exposes load, row intake, SPARQL, diff, Horn reports. dataframe.py duck-types dataframe export methods; server.py:12,23,34 wraps library operations with FastMCP. Optional alignment accepts caller-provided vectors, not an internal embedding model.

Consequences: Lite is a much smaller experiment surface for RDF export/query validation, but parity with all Rust tools, safety gates or formal behavior is not guaranteed. No installing it into Lab dependency environments during this review.

## Studio, browser try, and demonstrations

Studio package.json selects React 19, TypeScript, Vite 7, Tauri 2, Zustand, Cytoscape, 3D force graph and Vitest. src-tauri is a separate Rust desktop package with a bundled engine sidecar and agent Node sidecar. scripts/prepare-engine.mjs prepares binaries during build. studio/src/lib/mcp-client.ts:1-21 routes MCP through Tauri, while 42-57 routes shared-store REST to localhost.

studio/src/lib/source-factory.ts:5-20 explicitly selects live engine or a committed replay bundle. The same interface is consumed by presentation panels. Replay source (replay-source.ts:15-18,35-63) answers only scripted questions, makes a UI-only resolve no-op, and clearly emits an unscripted marker for other questions.

Source-traced limits: live-source.ts:75-90 throws for corpus bodies because no matching engine/Tauri endpoint exists. Its resolve at177 and ask at194 also throw rather than inventing live functionality. SHACL findings at 116-139 turn engine failures and zero-target/undetermined results into errors rather than displaying a clean empty list. This explicit unknown/error UI behavior is reusable; headline graph/chat screenshots are not proof of end-to-end live feature coverage.

Operational caution: Studio engine startup includes finding and killing port holders, studio/src-tauri/src/engine.rs:67-118. Do not launch this shell on a shared machine as part of a read-only review. This is an observed implementation behavior, not a hypothetical security warning.

web/try/api/index.py is a serverless-style stdlib Python wrapper around a released engine binary, with disposable request dirs at219,273 and optional oo-cert checker at130-152. The checker being absent is explicitly reported; do_induce, do_check, do_plan, run_batch give the public browser surface. engine installation includes atomic replacement/fork-window coordination. This demo does not require building Studio.

Community registry: community/README.md:1-31 distinguishes built-in curated catalog from fetched community ontology data. src/marketplace.rs:399-429 resolves a configurable registry. Packs are data fetched and parsed, not code execution, unlike WASM plugins. Moving registries and external ontology URLs need explicit version/content pinning if used as Lab evidence.

## Testing coverage and small safe verification

Observed test families (not claimed rerun): Rust integration files for ingest/induce/mapping/SQL sync/embeddings/plugins/tool profiles; Python tests under python/tests for graph API, dataframe intake, KGCL, SHACL, Horn checker word discipline, and optional dependencies; Vitest tests under studio/src/lib/__tests__ and state/__tests__; demo/tests and browser install-race tests.

python/tests/conftest.py:1-31,42-79 promotes missing-fixture skips into failures under OO_REQUIRE_FIXTURES=1, with explicit cost-based opt-in exemptions. This prevents a green job from silently skipping its claimed differential tools.

Small safe command selected for root:

    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest web/try/test_engine_install.py

No dependency installs. Three unittest methods at64,86,98; the first runs 24 threads internally, which are not 24 test cases. Uses fake shell executables and temporary copies of local sleep/true, no ontology binary/model/server. Linux-specific third case can skip if system utility sizes coincide. Root reports all three PASS in 0.200 seconds. Passing it verifies demo binary-install mechanics only.

## Broader repository surfaces

The named MCP tool attributes in src/server.rs total 124, all distinct. This is a static declaration count, not a measured tools/list response. src/toolfilter.rs:453-475 lists eight feature-dependent tools: two plugins, four embeddings, and two enabled by either PostgreSQL or DuckDB. Cargo defaults to no optional features, so a source-derived full/default build surface is 116 before further operator filtering. Build and filter state must accompany any advertised tool count.

The 22 case-studies directories are domain evidence bundles, crosswalk datasets and evaluation harnesses: health/clinical triage, ironmaking/plastics, DCAT, heritage, insurance/investment funds, nature governance, skills/occupations/mobility, robotics safety/security, gatekeepers, assurance benchmarks, wastewater and aviation. Their READMEs and local scripts explain assumptions and measurements. They are worked application/data examples, not independent guarantees about core functionality. Some require downloads, domain datasets, model calls or external tools.

Data provenance and license differ from the engine's MIT license. For example case-studies/skills-england-esco-crosswalk/README.md:8-9 identifies source OGLv3 and CC-BY4 licenses and licenses the crosswalk CC-BY4. Copying ontology data requires checking its own source/attribution contract; root MIT is not a blanket data license.

docs contains operational/configuration guides, semantic and proof boundaries, design decision records, plans and visual assets. docs/decisions provides useful decision-rationale evidence but executable code wins when commentary is stale. examples includes small Rust/data examples, document-privacy tokenization/provenance/chunking and a WASM plugin reference. scripts packages development/benchmark/release automation; tools includes differential oracles and figure helpers. data stores example ontology material. .mcp and .claude-plugin declare distribution integrations; root SKILL.md and skills/ hold workflow instructions for engine users, not additional engine implementations. ECOSYSTEM.md:3-10 explicitly separates data packs, markdown skills, independent companion MCP servers and in-process WASM plugins.

## Best reuse candidates for CyberAlchemy

1. Candidate schema induction with per-statement observed evidence, retained as proposed meaning for owner review.
2. Explicit translation loss/unsupported-construct records when turning Lab specifications into OWL/SHACL, rather than claiming every Lab rule became a logical axiom.
3. Purpose-bound retrieval checks: a small context needs the conclusions required by its task, not a high percentage of arbitrary triples.
4. Schema-guided extraction scaffold and independent validator, with the model outside the trusted implementation.
5. Data-versus-code extension separation; optional pure bounded plugins with explicit injected inputs.
6. Live/replay UI adapter seam and undetermined validation states distinct from empty findings.
7. Dependency-light Python RDF export sidecar for a first isolated experiment; do not replace canonical event histories.

No direct drop-in replacement: Ontology Lifecycle has stable governed subjects, event histories, exact semantic/governance joins, owner decisions and admission boundaries. RDF storage, statistical mapping candidates, a generated prompt, a SHACL pass, or a causal proxy does not create those Lab identities or authority effects. The first integration should consume an exact frozen Lab view and return an inert report.
