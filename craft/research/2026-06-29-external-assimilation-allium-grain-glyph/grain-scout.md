# grain-scout.md
# Scout: Young, Greg — Repo: grain (ObneyAI/grain)
# Date: 2026-06-29

---

## Mission Frame

Grain is an opinionated Clojure/Polylith toolkit for AI-native, multi-tenant, event-sourced/CQRS systems. Its thesis: **narrow the output space so LLM drift is structurally impossible** — constraints bottom out at the storage layer. Every command, query, and event flows through the same schema-gated, tenant-scoped append-only ledger. Humans and AI agents share one store, one audit trail, one constraint set.

This report is advocacy. The skeptic audits ownership — not my job here. Every candidate below cites a real mechanism in the grain clone.

---

## Ranked Import Candidates

---

### 1. code-agent-tools: Schema-gated agent introspection + validate-before-invoke

**What it is:** A dev-only nREPL namespace that exposes the live Grain runtime to a coding agent as plain EDN. The agent calls `catalog` to discover all registered commands, queries, read models, processors, and schemas; calls `explain-schema` to see the exact Malli shape; calls `validate` before touching state; and only then calls `invoke-command!`. The toolkit enforces a workflow: **catalog → explain → validate → invoke**.

**Source:** `components/code-agent-tools/src/ai/obney/grain/code_agent_tools/core.clj` (full 300-line implementation), `components/code-agent-tools/src/ai/obney/grain/code_agent_tools/interface.clj` (public API), `docs/code-agent-tools.md` (workflow spec)

**Why it is leverage for DomainSpec:** DomainSpec is "typed intent → reality." The current gap is that an agent generating implementation has no runtime surface to ask "does what I'm about to emit match what the system actually accepts?" grain's code-agent-tools closes that gap structurally: the agent cannot invoke without passing a schema check first. The `:missing-schemas` field in `catalog` actively enumerates schema coverage gaps, turning schema hygiene from a static audit into a live runtime signal. The `sanitize` function ensures vars/fns/classes never leak out as raw runtime objects — a safety discipline DomainSpec's agent-facing tools currently lack explicitly.

**Port note:** This is an IDEA to port. Clojure-specific (nREPL, EDN, Malli, Integrant). The mechanism — introspect-the-registry, validate-before-invoke, sanitize-before-return — is language-agnostic and directly maps to DomainSpec's command/query layer.

**Leverage: H | Adoption cost: M**

---

### 2. event-store-v3: Schema-validation-at-append-boundary (deny-by-default on storage)

**What it is:** Every event appended to the store is validated against a Malli schema keyed by `:event/type` before the storage call runs. If the schema is missing or the event fails validation, the append returns an anomaly — it never reaches the storage layer. Commands and queries are schema-validated before handlers execute. The pattern: **validate-before-effect**, not validate-on-read.

**Source:** `components/event-store-v3/src/ai/obney/grain/event_store_v3/core.clj` lines 28–66 (the `append` function), `components/command-processor-v2/src/ai/obney/grain/command_processor_v2/core.clj` lines 41–56 (`process-command` schema check before `execute-command`). The allium spec in `components/event-store-v3/event-store-v3.allium` formalizes this as the `deny-by-default schema validation` invariant.

**Why it is leverage for DomainSpec:** DomainSpec's correctness gap is that implementation drift is caught late — at review or test time, not at the storage boundary. Grain's model makes schema violation structurally impossible to persist: a mistyped event is an in-band anomaly (`::anom/incorrect`), not a silent bad record. For Saturn's intent↔reality loop, this is the tightest possible feedback — the store itself rejects drift. Directly importable as a design principle for DomainSpec's command execution layer: schema check on command receipt AND on event emit, both before any state change.

**Port note:** IDEA to port. The validate-before-effect principle and the dual-check pattern (command schema + domain event schema at separate gates) are the mechanism to adopt.

**Leverage: H | Adoption cost: S**

---

### 3. todo-processor-v2: Durable watermark checkpointing as Saturn evidence ledger

**What it is:** Every event processed by a todo processor is checkpointed atomically in the event store itself via a `grain/todo-processor-checkpoint` event with a CAS guard. The checkpoint uses O(1) reverse-seek on the store to find the high-watermark — no separate checkpoint table, no external coordination. At-least-once and at-most-once semantics are explicit handler return values (`{:result/checkpoint :after}` or `:before`). On restart, catch-up replays only events after the last watermark.

**Source:** `components/todo-processor-v2/src/ai/obney/grain/todo_processor_v2/core.clj` — `make-checkpoint-event` (lines 43–53), `append-with-checkpoint` (lines 62–99), `already-checkpointed?` (lines 129–141), `get-last-processed-id` (lines 242–257), `catch-up-tenant` (lines 259–274).

**Why it is leverage for DomainSpec / Saturn:** Saturn closes intent↔reality with evidence. Right now, Saturn's evidence mechanism is described but not structurally implemented. Grain's checkpoint pattern gives a concrete model: **the evidence record is itself an event in the same store**, CAS-guarded so it cannot be duplicated. Every processor step that succeeds emits a checkpoint event; every failure is also recorded (`:grain/todo-processor-effect-failure`). The event log *is* the audit trail — no separate evidence store needed. DomainSpec's verify/reflect cycle could adopt this: phase completion = checkpoint event; divergence from spec = anomaly event; Saturn projects the ledger as a read model.

**Port note:** IDEA to port. The mechanism (checkpoint-as-event, CAS dedup, high-watermark O(1) lookup) is language-agnostic. The Clojure UUID-v7 ordering trick (monotonicity allows single-read O(1) max) is particularly worth porting.

**Leverage: H | Adoption cost: M**

---

### 4. schema-util + defschemas: Process-wide mutable schema registry with last-writer-wins

**What it is:** A single global Malli registry atom. Components call `defschemas` (a macro wrapping `register!`) to contribute named schemas. The registry is the Malli default registry — any schema name registered here is resolvable everywhere in the process without explicit import. `register!` is idempotent; last-writer-wins for the same name.

**Source:** `components/schema-util/src/ai/obney/grain/schema_util/interface.cljc` (full 30-line file). The `defschemas` macro is the registration point used by every component.

**Why it is leverage for DomainSpec:** DomainSpec currently lacks a central, runtime-resolvable schema registry. The result: schema checks are localized rather than process-wide, and an agent cannot ask "what schemas exist?" at runtime. Grain's approach — one atom, one macro, one registry — means any registered type is globally addressable. For DomainSpec's agent tooling, this is the prerequisite for candidate #1: without a global registry, `catalog`'s `:missing-schemas` report cannot be computed. Trivially portable to any language with a registry pattern.

**Port note:** IDEA to port (the `defschemas` macro is Clojure-specific; the pattern of a global mutable schema registry backed by a validation library is universal).

**Leverage: H | Adoption cost: S**

---

### 5. event-model: Machine-readable Malli schema for the CQRS event model vocabulary

**What it is:** A Malli schema defining the structural grammar of a Grain event model — six building-block kinds (command, event, view, todo-processor, screen, periodic-task), valid connection grammar (`:valid-step` predicate enforces legal wiring: `command → event`, `event → view`, `view → todo-processor`, etc.), payload-schema obligations on data-carrying kinds, and `given-when-then` acceptance examples directly on command entries.

**Source:** `components/event-model/src/ai/obney/grain/event_model/interface.clj` (full 128-line schema definition). The allium spec in `components/event-model/event-model.allium` describes this as "design-time vocabulary and well-formedness grammar."

**Why it is leverage for DomainSpec:** DomainSpec's spec-feature and init phases produce an informal event model, but there is no machine-readable schema enforcing its structure. Grain's `event-model` schema is directly importable as a schema governing DomainSpec's own spec artifacts: a spec file that fails validation against this schema cannot produce a valid implementation — **the spec grammar becomes a constraint, not a suggestion**. The `:valid-step` predicate is particularly high-value: it encodes the legal flow topology as a pure predicate, rejectable at parse time.

**Port note:** IDEA to port. The Malli schema structure maps directly to JSON Schema, Zod, or any typed schema system DomainSpec targets.

**Leverage: H | Adoption cost: S**

---

### 6. read-model-processor-v2: Two-tier deterministic projection cache with versioned watermarks

**What it is:** Projections (read models) use an L1 in-process LRU atom and an L2 LMDB on-disk store. Both are keyed by `(name, version, tenant-id, scope-hash)`. Watermarks are UUID v7 event IDs — incremental updates read only events after the last watermark. L2 auto-switches between monolithic (< 10K keys), segmented (64 hash-based shards, only changed shards written back), and partitioned (per-partition cache entries with a cross-partition entity index) storage strategies. L1 TTL is configurable per read model.

**Source:** `components/read-model-processor-v2/src/ai/obney/grain/read_model_processor_v2/core.clj` — the full 710-line implementation. Key functions: `p-unpartitioned` (lines 624–703), `p-partitioned` (lines 608–618), `process-events` (lines 65–75), `changed-segments` (lines 102–109).

**Why it is leverage for DomainSpec:** Saturn's "evidence" is a read model over the intent↔reality event log. The challenge is that re-projecting the full history on every check is expensive and makes the feedback loop slow. Grain's watermark+cache pattern solves this: Saturn's read models (phase status, spec drift, test coverage) would each be `defreadmodel` reducers that advance incrementally with zero full-replay cost after the first projection. The version field (`version 1`) also gives an explicit cache-invalidation mechanism: bumping version forces a full replay, which is how Saturn would handle spec changes.

**Port note:** IDEA to port. The mechanism (reducer + watermark + tiered cache + version key) is language-agnostic. LMDB is the Clojure-specific part.

**Leverage: M | Adoption cost: L**

---

### 7. Allium behavioral specs: Machine-checkable component contracts co-located with source

**What it is:** Every grain component ships a `.allium` file beside its source (`components/<name>/<name>.allium`). These are behavioral specifications in Allium language v3 — capturing entities, rules, contracts, invariants, and surfaces. The `allium-specs.md` doc reports 37 components all passing `allium check` and `allium analyse` with no errors. The specs were adversarially audited against source and tests.

**Source:** `docs/allium-specs.md` (index of all 37 specs), any individual `.allium` file — e.g., `components/command-processor-v2/command-processor-v2.allium` (referenced in allium-specs.md), `components/code-agent-tools/code-agent-tools.allium`.

**Why it is leverage for DomainSpec:** DomainSpec's `check-tension` and `verify-feature` skills surface spec-vs-reality divergence. Grain demonstrates what a mature co-located spec discipline looks like at component granularity — every component has a spec, every spec is machine-checked, every spec is adversarially audited. The Allium format itself (entities / rules / contracts / invariants / surfaces) maps well to DomainSpec's existing ontology. Adopting co-located `.allium` (or equivalent) files per DomainSpec phase output would make tension-checking a `find components -name '*.allium' -exec allium check {} \;` one-liner.

**Port note:** IDEA to port — and possibly a literal code candidate if Arcanum publishes Allium. The co-location discipline is the mechanism; the Allium tool is an implementation detail.

**Leverage: M | Adoption cost: M**

---

### 8. anomalies: In-band failure as data (deny anomaly propagation)

**What it is:** A single one-line predicate `(defn anomaly? [x] (when (::anom/category x) x))` over cognitect.anomalies. Every fallible function in grain returns either a result map or an anomaly map with a category (`:fault`, `:conflict`, `:not-found`, `:incorrect`, `:forbidden`). The call site always branches on `anomaly?` before proceeding. No exceptions for domain errors; exceptions are only for unrecoverable programmer errors.

**Source:** `components/anomalies/src/ai/obney/grain/anomalies/interface.cljc` (1 file, 3 lines). Used at every call site in every component.

**Why it is leverage for DomainSpec:** DomainSpec's agent orchestration currently has no uniform failure signal. A sigil/spell that returns an error throws or returns an untyped map — the caller has to infer whether it failed. The anomaly pattern gives DomainSpec's sigils a typed, in-band failure vocabulary: `:incorrect` (bad input), `:forbidden` (auth), `:conflict` (CAS), `:fault` (unexpected). The router can branch on anomaly category without parsing error messages. This is particularly important for Saturn's feedback loop: a phase that returns `{::anom/category ::anom/conflict}` is machine-interpretable — "spec changed, replay needed."

**Port note:** IDEA to port. The cognitect.anomalies vocabulary is language-agnostic (it's just data keys). Already well-established in the Clojure ecosystem; the concept translates trivially.

**Leverage: M | Adoption cost: S**

---

### 9. periodic-task + CAS dedup: Cross-node once-per-tick guarantee via event store CAS

**What it is:** Each node runs a periodic task independently. The handler returns a `{:result/cas {:types ... :predicate-fn ...}}` CAS guard. The event store enforces the predicate atomically before appending: only the first node to win the CAS appends the trigger event; all others get a silent `::anom/conflict`. No external lock service. CAS predicates are pure functions over the current event stream.

**Source:** `components/periodic-task/src/ai/obney/grain/periodic_task/core.clj` (implementation), `docs/core-concepts.md` lines 118–142 (the billing example with CAS predicate). The allium spec at `components/periodic-task/periodic-task.allium` formalizes: "at-most-once-per-fire dedup via CAS."

**Why it is leverage for DomainSpec:** DomainSpec's orchestrate skill fans out subagents. The risk is duplicate phase execution when multiple agents or retries are running. Grain's CAS-dedup pattern gives DomainSpec a structural once-per-phase-tick guarantee backed by the event store — no external coordination, no lock table, no Redis. The predicate checks the event history itself: "has this phase already fired for this spec version?" If yes, the CAS conflicts and the duplicate is silently discarded.

**Port note:** IDEA to port. The CAS-on-event-store pattern is language-agnostic; the UUID v7 ordering (monotonicity allows simple timestamp-based predicates) is a useful implementation detail.

**Leverage: M | Adoption cost: M**

---

### 10. clj-dspy + defsignature: Malli schema → DSPy/Pydantic signature bridge

**What it is:** A `defsignature` macro that takes a Clojure Malli schema (inputs and outputs) and translates it to a DSPy `Signature` class with Pydantic `BaseModel` typed I/O, running in an embedded Python process via `libpython-clj`. Descriptions from Malli metadata (`:desc`) become Pydantic `Field(description=...)` args. The macro attaches `:dspy/signature` metadata to the Clojure var so the signature is discoverable at compile time.

**Source:** `components/clj-dspy/src/ai/obney/grain/clj_dspy/core.clj` — `malli-schema->python-type` (lines 9–51), `generate-signature` (lines 178–210), `defsignature` macro (lines 212–230). Marked deprecated in the allium spec but still present and working.

**Why it is leverage for DomainSpec:** DomainSpec generates code using LLM calls. If those LLM calls are typed DSPy signatures — with Malli-derived input/output schemas — the LLM output is schema-validated before use. The `expand-with-props` function (lines 53–123) is particularly interesting: it fully dereferences and inlines Malli schemas including nested ref chains, producing a complete Pydantic model with no dangling refs. This is the "narrow the LLM's output space" thesis applied to structured generation. Even if the Clojure/Python bridge is not used, the pattern (schema → structured LLM signature → validated output) is directly applicable to DomainSpec's generation pipeline.

**Port note:** IDEA to port. The Clojure/Python bridge is not portable, but the pattern (Malli/typed schema → typed LLM signature → validated output) is. The deprecated status means this is already superseded in grain — take the idea, not the code.

**Leverage: M | Adoption cost: L**

---

## Summary Table

| # | Candidate | Leverage | Cost | Port type |
|---|-----------|----------|------|-----------|
| 1 | code-agent-tools: catalog/validate/invoke workflow | H | M | IDEA |
| 2 | event-store-v3: schema-validate-before-append | H | S | IDEA |
| 3 | todo-processor-v2: checkpoint-as-event + CAS dedup | H | M | IDEA |
| 4 | schema-util: global mutable schema registry | H | S | IDEA |
| 5 | event-model: machine-readable CQRS grammar | H | S | IDEA |
| 6 | read-model-processor-v2: watermark+tiered projection cache | M | L | IDEA |
| 7 | Allium behavioral specs: co-located machine-checkable contracts | M | M | IDEA (+ possibly literal) |
| 8 | anomalies: in-band typed failure vocabulary | M | S | IDEA |
| 9 | periodic-task: CAS-based cross-node once-per-tick | M | M | IDEA |
| 10 | clj-dspy/defsignature: schema → structured LLM signature | M | L | IDEA (deprecated in grain) |

---

## Critical Observation

All 10 candidates are **IDEA to port** — grain is Clojure; DomainSpec is language-agnostic at the sigil/skill layer. No literal code is portable. But the mechanisms are unusually precise: every one is a working, production-tested implementation, not a design pattern on paper. The highest ROI cluster is candidates 2+4+1 as a stack: global schema registry (4) → validate-before-append (2) → catalog/validate/invoke agent tooling (1). That stack, ported to DomainSpec's command execution layer, is the structural LLM drift prevention mechanism grain describes as its thesis.
