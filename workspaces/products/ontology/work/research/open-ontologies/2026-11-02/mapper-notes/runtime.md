# Open Ontologies runtime mapper report

Repository: /tmp/cal-open-ontologies.ANeAQC/repo
Commit: c7fd75f9491253c56e4d4f408ceac179de343e48
Method: static source tracing only; no external repository code executed and no tests run.

## Main architectural shape

- A single Rust library crate exposes most domain modules publicly through src/lib.rs:1-174. A thin "hexagonal" separation is not enforced: domain services often directly use GraphStore, StateDb, filesystem writes, and subprocesses.
- src/main.rs supplies CLI commands, stdio MCP, streamable HTTP MCP, REST, Unix/named-pipe fact grounding, and a daemon proxy. The CLI and MCP call the same library services; src/batch.rs is an additional command dispatcher over them.
- src/server.rs:23-45 holds an MCP tool router, prompt router, SQLite state, Arc<GraphStore>, session ID, registry, configured repository directories, tool-surface filter, and optional embeddings.
- HTTP mode creates ONE shared graph (src/main.rs:2393), clones it for the service factory (2451), and gives sessions fresh server objects. The constructor explicitly documents shared in-memory triples (src/server.rs:53-55). Session identity is not a graph branch or a pinned version.
- src/state.rs:421-449 is SQLite metadata in Arc<Mutex<Connection>>, with WAL, foreign keys, synchronous NORMAL, schema migrations, plans, snapshots, lineage, locks, watchers, caches and other service state. Graph triples live separately in Oxigraph, not in SQLite.
- src/graph.rs:181-231 wraps Oxigraph Store directly, without an outer global mutex. It supports in-memory and RocksDB-backed storage. A persistent directory allows one read-write process handle (219-224). The daemon is the entry point for sharing that handle across CLI callers.

## Read stability and simultaneous agents

The reusable pattern is excellent but narrower than "agents each have a branch."

1. A certified dataset extraction calls GraphStore::triples_in_scope (src/graph.rs:1089-1150), which obtains one MVCC snapshot through read_one_state (1240-1249). triples_outside uses the same mechanism (1271-1293).
2. read_one_state calls Store::snapshot from a pinned Oxigraph fork. It does not open a read transaction. The distinction matters: in-memory Oxigraph read transactions block writers, whereas this snapshot pins a state without holding the writer lock.
3. The reasoning paths extract an owned list ONCE and then build local interned facts from it (src/reason.rs:1638-1648 for built-in forward chaining; 3355-3372 for supplied Horn rules). This allows writers to progress while the run reads the stable input.
4. tests/read_does_not_block_writers_test.rs:38-94 deliberately holds one long selection over 200,000 seed triples and checks that the writer progressed DURING that individual read; merely measuring gaps between multiple calls would be a false positive.
5. Saved ontology versions are N-Quads strings plus labels in SQLite, not long-lived exported handles (src/ontology.rs:242-273). Restoring one changes the common graph (276-295).
6. Temporal scopes select named graphs by valid time and recorded time, NOT branches or per-agent checkout identities. ScopeRequest and ScopeManifest in src/temporal.rs:351-412 name that decision; src/graph.rs:31-125 makes ReadScope a value.
7. HTTP sessions share the graph. A per-session registry has one "active" ontology slot (src/registry.rs:1-19,63-71), but switching/reloading that slot replaces the shared store. Do not interpret the session-specific active metadata as isolated per-session graph storage.

Conclusion for CyberAlchemy: the stable-read / progressing-writer mechanism matches our rationale and is useful as an implementation alternative or test oracle. It does not provide autonomous agent branches, automatic merges, or a public API allowing a client to retain an arbitrary old StoreSnapshot across many MCP requests.

Dependency caveat: Cargo.toml patches Oxigraph to a git revision, 37db8e1522585ed2f9aa994be6c5c716859af5c8. The comments explain snapshot and RDF lexical-form changes. Stock oxigraph 0.5 is not an interchangeable drop-in for this implementation.

## Ontology change planning

src/plan.rs is the Terraform-like ONTOLOGY REPLACEMENT planner; do not conflate it with action-sequence planning in plan_classical.rs / plan_pddl.rs / plan_validate.rs.

- plan_inner (430-546) loads the proposed complete Turtle into an isolated store, compares class/property/individual sets, reports triple insertion/deletion counts, and counts references to removed terms as a structural blast radius.
- "Locked IRIs" are read into plan diagnostics (468-511). They are not independently enforced by apply.
- PlanChecks supports logical-defect checking and deductive conservativity (src/plan.rs:46-56,187-237); the MCP path enables both by default and supports explicit opt-outs (src/server.rs:2548-2602). These checks add information/risk to a report; they do not create authority.
- The logic check uses three-valued consistency and reports null rather than true for a budget exhaustion or unsupported construct (src/plan.rs:357-425).
- Plans persist proposed Turtle, owner, and shape summaries in SQLite (src/plan.rs:670-698). Only 100 plans are retained; this is not a durable unbounded event ledger.
- The default "latest plan" is scoped to the MCP session owner; CLI plans have a constant CLI owner. That prevents session A accidentally selecting session B's latest plan (701-745). An explicit plan ID deliberately crosses owners, without an authorization check (705-711; tests/plan_ownership_test.rs:104-123).

## Apply, stale plans, and atomicity limits

This is the largest practical mismatch for the Lab.

- apply_plan gates only on Monitor::is_blocked unless mode is force (src/plan.rs:571-581). The comments explicitly state that risk_score and logic do not gate application (549-560).
- There is NO persisted base graph revision/digest in the plan record or load query (670-719). At apply time it calculates a difference between the CURRENT live graph and the old proposed full Turtle (594,618-644).
- Consequence: if another caller changed the graph after review, this operation can remove that caller's additions to reach the old target. There is no stale-reviewed-base rejection in this path. This is a source-based conclusion, not a newly executed exploit.
- Nonblank changes execute deletions then insertions in separate 500-triple SPARQL updates (647-659). An entire multi-batch apply is not one atomic transaction.
- If either side contains blank nodes, apply calls clear, then load_turtle as separate operations (596-598). Rollback similarly clears before loading the saved snapshot (src/ontology.rs:289-290). Those composed operations can expose empty/partial intermediate states despite atomic document loads.
- mark_applied is an advisory SQL update after graph writes; its error is discarded (src/plan.rs:762-770). Graph mutation and metadata record are not one cross-store commit.
- Migration adds guessed equivalentClass/equivalentProperty bridges after target mutation, using rename candidates from drift similarity. Bridges carry scores and unbridged removals are reported (src/plan.rs:773-845); some bridge-write errors are ignored (810-812). A similarity score must not become a Lab semantic equivalence automatically.

What IS atomic: parsing an individual document finishes before mutation, then all quads are inserted in one Oxigraph transaction (src/graph.rs:243-276). The generic replace_file/replace_nquads path clears and inserts in the SAME transaction (413-429). This stronger operation is available but not used by every planner/rollback path.

## Temporal version semantics

src/temporal.rs describes two clocks: when an assertion is valid, and when it was recorded/believed. It uses named graphs with validFrom/validTo and recordedAt/recordedUntil. Half-open intervals preserve correction boundaries (35-51). supersedes/retracts are asserted links rather than guesses (53-85). Invalid/unreadable bounds are reported, not silently treated as timeless (87-114).

The reusable rule is "never reason over the union of incompatible versions by accident": reason/SHACL paths require explicit temporal scope or an explicit all_versions choice on a versioned store (temporal.rs:116-132 and 610-674). This also guards a true proof over the wrong selected dataset, which a theorem checker alone cannot detect.

For the Lab's cursor model this is a complementary clock, not a substitute. Mapping requires explicit meaning for semantic commit cursor, governance knowledge cursor and domain-valid time.

## Drift, monitoring, audit

- DriftDetector compares canonicalised versions and reports vocabulary additions/removals, rename confidence and signals, and a drift velocity (src/drift.rs:16-101).
- If blank-node canonicalisation exceeds its budget, it reports exact:false and omitted counts rather than pretending the comparison was exact (89-98).
- Monitor stores watchers, runs checks, and supports notify, block-next-apply, auto-rollback, and log actions (src/monitor.rs:9-34,78-151). Auto-rollback uses latest saved version, not event-log compensation.
- Monitor state is mutable SQLite flags (154-170); a force apply overrides it. Webhooks are spawned asynchronously and failures can be ignored; they are observations, not a durable transactional authority channel.
- LineageLog is an append-style SQLite session operation log (src/lineage.rs:24-57). Inserts and webhook errors are discarded. It is not the Lab's hash-chained canonical semantic+governance event store.
- IDs for sessions and plans use time/counter-derived u64s (lineage.rs:87-96), suitable identifiers in this context but not cryptographic principal identities.

## Security/effect surfaces

- MCP tool filtering removes routes, so excluded tools cannot be invoked, not merely hidden (src/toolfilter.rs:1-32). Task profile and allow/deny mode compose by narrowing; default full exposes the whole build surface.
- Streamable HTTP auth is one optional shared bearer token (src/main.rs:2631-2669); /health is intentionally outside the auth layer and only returns status+version (2671-2689). CORS is permissive (2690). No per-agent principal/role/operation authorization was found in these transport/router paths.
- Plan ownership is usability protection, not ACL isolation: explicit plan ID crosses owners.
- configured ontology repo file discovery has a path guard (src/repo.rs:93-135), but other tools accept arbitrary local input/output paths, subprocess commands and remote source endpoints according to their own contracts. Reusing an MCP "read_only" profile should be preceded by effect-by-effect review; an apparently analytical tool may write a certificate, cache or output.
- Monitor auto-rollback, apply/migrate, load/clear, reasoning materialisation, remote push, and plugin calls are effectful. Attach the Lab's effect policy outside those operations.

## Action dynamics and concurrency are a separate subsystem

src/dynamics.rs defines parameterized action schemas, preconditions and KGCL-like add/remove effects. Parameter type_iri is currently documentation/caller-supplied preconditions rather than automatic type checking (35-44). Nondeterministic outcomes exist despite stale module-level deferred notices (70-85).

src/dynamics_bcplus.rs:74-181 defines a concurrent "tick" by computing effects then detecting cross-step add/remove conflicts before mutation. It describes atomic commit in prose, but implementation inserts additions in one load then executes individual deletes (171-180), followed by invariant checks/compensation. This should not be imported as a general concurrent transaction engine without new atomicity/current-base testing. It is not the ontology-versioning subsystem.

## Tests to consult (inspected, NOT executed)

- tests/read_does_not_block_writers_test.rs: writer progress during one pinned read.
- tests/store_atomicity_test.rs: one-state reads and whole-document writes.
- tests/transaction_isolation_test.rs and transaction_memory_test.rs: backend-specific read-transaction costs.
- tests/plan_ownership_test.rs: default owner scoping and explicit cross-owner plan targeting.
- tests/plan_delta_test.rs: individual triple updates rather than ignoring instance data.
- tests/plan_persistence_test.rs and plan_mcp_test.rs: plans survive transient service objects and calls.
- tests/plan_logic_test.rs: informational logical defect/risk checks.
- tests/plan_migrate_test.rs: scored rename matching and unbridged removals.
- tests/version_dataset_roundtrip_test.rs and version_provenance_test.rs: snapshots preserve graph identity.

## Reuse recommendations

High value:
1. Borrow the writer-progress-during-one-read regression test, plus pinned immutable input selection.
2. Preserve scope as an explicit value and carry it with reasoning/validation evidence; never combine ontology versions implicitly.
3. Show structural diff, semantic consequence diff, and logical defects separately in a proposed change report.
4. Report null/unknown/skipped/exact:false with causes and counts; do not turn unfinished work into success.
5. Carry per-session plan ownership and explicit IDs, while separately enforcing the Lab's principal and exact-base approval rules.
6. Borrow blank-node canonicalisation budgets and explicit approximation reports only if the Lab exposes RDF bnodes.
7. Borrow phase-aware runtime budgets and operationally visible effective settings (src/runtime.rs).

Do NOT copy as-is:
- No-base-version apply, advisory locked-IRI reports, automatic equivalence bridges, global rollback, cross-store non-atomic audit writes, or mutation-capable MCP profiles without Lab authority checks.
- Do not replace the Lab's canonical event history with this mutable triplestore and SQLite snapshots.
- Do not describe the no-lock read mechanism as no-lock writes, per-agent branches, or distributed multiwriter merges.
