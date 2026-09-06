# Grain — Precedent / Ownership Skeptic Report

> Skeptic: **Lamport, Leslie** (precedent/ownership SKEPTIC vector — minimize imports to genuine gaps)
> Repo: `domainspec-core` (root `/home/vrondelli/projects/domainspec-core`)
> Subject: **Grain** (ObneyAI) — Clojure/Polylith event-sourced/CQRS building blocks
> Date: 2026-06-29
> Method: read-only skim of grain (`readme.md`, `docs/core-concepts.md`, `docs/code-agent-tools.md`) + sweep of DomainSpec's OWN corpus for existing owners.
> Discipline: **claim ≤ proof**. Skeptical in BOTH directions — I do not invent owners to kill a candidate, and I do not wave through a duplicate. A found owner is **build-from-owned, NEVER a kill**. Where grain is heavy Clojure infra, I separate the **portable idea** from the **non-portable code**.

This is the minimizing vector. A separate scout independently maximizes the assimilable surface; I have not seen their list. My job is to name what DomainSpec already owns and flag candidates that would overshoot claim ≤ proof.

---

## What Grain offers (the surface I am adjudicating)

1. Event-sourced **event store as single source of truth** (immutable facts + audit trail shared by humans/code/agents).
2. **CQRS** — commands (only path to state change) / queries (read projections) split.
3. **Schema-validate-before-invoke** — agent validates a payload against the schema registry before invoking a command/query.
4. **Agent-introspection tooling** — `grain-code-agent-tools`: `catalog`, `diagnostics`, `schemas`/`explain-schema`/`validate`, `events`, `projection` over a **live running app via nREPL**.
5. **Deny-by-default authorization** — every command/query requires an `:authorized?` predicate; missing/false ⇒ rejected.
6. **"Narrow the output space so LLM drift is structurally impossible"** — the central thesis: the codebase the LLM targets bounds the valid-output space; shallow constraints bottom out at storage.
7. **Multi-tenant isolation** — `:tenant-id` on every op; Postgres RLS + per-tenant advisory locks; tenant-scoped cache keys.
8. **Read-model projections + two-tier caching** (LRU + LMDB, watermark-incremental, partitioned).
9. **Distributed coordination** — control-plane, event-sourced tenant leases, coordinator election.
10. **Datastar reactive UI** (SSE-streamed hiccup).

---

## Verdicts

### 1. Event store as "single source of truth" / immutable evidence ledger
**Verdict: OVERSHOOT-RISK (idea partially ALREADY-OWNED; code NOT portable).**

- Portable *idea* — "append-only immutable facts as the audit trail / source of runtime truth" — is **already owned** in two distinct DomainSpec registers:
  - **Append-only signal ledger** — `implementation/domainspec/.claude/skills/domainspec-emit-signals/SKILL.md` writes one-JSON-line-per-observation to `docs/signals/pipeline-signals.jsonl` ("append-only signal log... Never overwrite existing content"), with a typed envelope (`domainspec/templates/SIGNAL-SCHEMA.md`). This *is* an event-sourced evidence ledger for governance.
  - **Domain-event runtime model** — `implementation/domainspec/OBSERVABILITY.md` already treats domain events as first-class: `events.md → event.emit / event.consume / event.consumer.lag` metrics, "Phantom events... data integrity issue," and notably `computed_balance = replay all transactions from event log` (line ~490) — i.e. event-replay-as-source-of-truth is *already* in the observability model.
  - The **ledger primitive** itself is under explicit, deliberate review in the v2 spine: `cyberAlchemy-v2/authority/definitions/reviews/ledger-primitive-review.md` ("scoped state/evidence register; no as semantic authority" — promotion *blocked* pending schema/relation vocab). DomainSpec already knows what a ledger is and has deliberately NOT promoted it.
- **Why OVERSHOOT** if imported as grain frames it: grain's event store is a concrete **Clojure/Postgres/SQLite/LMDB CQRS runtime** (`grain-event-store-postgres-v3`, Fressian serialization, UUID v7 ordering). Porting *that* would claim DomainSpec ships a multi-backend event-sourcing runtime — it does not, and that is not DomainSpec's layer (DomainSpec is **typed-intent → spec → derived obligations**, code is downstream per Axiom A1). Adopt the *idea* (already owned twice over); do **not** import the store.

### 2. CQRS (command/query split)
**Verdict: OVERSHOOT-RISK (architectural pattern, not a DomainSpec primitive).**

- DomainSpec already *describes* commands/queries/events/read-models as documentable surfaces it derives tests from — `implementation/domainspec/TEST-PIPELINE.md` (`operations.md → Rule/Calculation/Postcondition tests`, `queries.md → Query Tests`, `events.md → Event Flow Tests`, `interfaces.md → Contract Tests`) and `implementation/domainspec/architecture/pattern-library/concepts/backend/query.md`. CQRS is one architecture among many that DomainSpec can *spec over*, not something it should *adopt as its own engine*.
- Importing CQRS-as-grain-ships-it would overshoot: it bakes one opinionated architecture into a framework whose whole point (Axiom A2 — "decisions belong to the domain, not adapters") is to be architecture-agnostic above the adapter line. The pattern is portable as a pattern-library entry; the runtime is not.

### 3. Schema-validate-before-invoke (agent safety workflow)
**Verdict: ALREADY-OWNED (idea) — owner named below.**

- The discipline "validate the shape against a registered schema *before* you act" is owned in two places:
  - **Route/dispatch shape**: Arcanum `dispatch-spec` — `arcanum/.claude/skills/dispatch-spec/SKILL.md` + `dispatch.schema.json` (21.6K) validates a dispatch route's shape before it runs.
  - **Spec-derived contract/event validation**: `interfaces.md → Contract Tests` and `events.md → Event Flow Tests` in `implementation/domainspec/TEST-PIPELINE.md`; envelope-schema enforcement in `domainspec-emit-signals` (`SIGNAL-SCHEMA.md`, "Enforce session completeness invariants").
- Honest nuance: grain's `tools/validate` is a **runtime payload check against a live schema registry** (Malli). DomainSpec's owners are **design-time / dispatch-time**, not a live runtime command-validation gate. The *principle* is owned; a runtime "validate this command map before invoke-command!" layer is **not** a DomainSpec concern (it lives below the adapter line, Axiom A2). Build-from-owned on the principle; do not claim a runtime validator.

### 4. Agent-introspection tooling (catalog / diagnostics)
**Verdict: ALREADY-OWNED — owner named below.**

- DomainSpec owns structured agent-introspection richly:
  - **GitNexus** skills — `implementation/domainspec/.claude/skills/gitnexus/{gitnexus-exploring,gitnexus-impact-analysis,gitnexus-debugging,gitnexus-guide}/SKILL.md` — map execution flows for an agent (the project CLAUDE.md mandates GitNexus/`semantic_query` *before* grep).
  - **Semantic index** — `list_domains` / `semantic_query` (semantic-index skill) — locate concepts by meaning.
  - **Live registry/catalog** — `implementation/domainspec/.claude/skills/domainspec-sync-registry/SKILL.md` keeps `docs/registry.md` + `docs/glossary.md` as the catalog of concepts; `domainspec-context-builder` does selector-level retrieval.
- Honest nuance (the one real delta): grain's catalog introspects a **live running app over nREPL** (runtime registries, event store contents, projections, diagnostics health). DomainSpec's introspection is over the **codebase + spec/concept graph** (static/structural). The *agent-introspection capability* is owned; the specific **"introspect the live runtime state of a running service"** angle is thinner in DomainSpec. That sliver is a candidate, but as a *runtime* concern it is below DomainSpec's layer — see GENUINE-GAP note in §11. The general capability is build-from-owned, not a kill.

### 5. Deny-by-default authorization
**Verdict: GENUINE-GAP (as runtime request auth) — but out-of-layer; do NOT conflate with owned governance gates.**

- DomainSpec has **no runtime `:authorized?` request-authorization predicate**. Grep for `multi.tenant|deny.by.default|RLS` finds only incidental research mentions, no owner.
- **Skeptic caution — do not invent an owner:** DomainSpec *does* own a family of **gates** — `cyberAlchemy-v2` promotion gate (`authority/definitions/DEFINITIONS.md` "promotion gate / owner gate / authority gate"), `domainspec-readiness-gate`, `decision-gate`, and Axiom A5 ("blocking controls before merge/close"). These are **governance/promotion/closure gates** — "is this allowed to *count / merge / promote* now?" They are NOT request-level authorization ("is this caller allowed to run this command?"). Conflating the two would be a false ALREADY-OWNED.
- So: genuine gap **as a runtime auth mechanism** — but it is grain *application-runtime* infra, below DomainSpec's adapter line (Axiom A2). Importing it would overshoot DomainSpec's scope. Verdict net: a real absence, correctly out-of-scope; adopt only as a *spec-able invariant* DomainSpec could derive tests for, not as a shipped auth layer.

### 6. "Narrow the output space → drift structurally impossible" (the thesis)
**Verdict: ALREADY-OWNED (this is DomainSpec's home turf) — owner named below.**

- This is the **strongest duplicate**. Grain's thesis — "when natural language is the compiler, the codebase bounds the valid-output space; narrow it until drift is structurally impossible" — is precisely DomainSpec's reason to exist, owned canonically:
  - **`implementation/domainspec/DRIFT-CONVERGENCE.md`** — the canonical definition of drift (semantic/contract/runtime/governance/coordination) and convergence as evidence-backed drift reduction. DomainSpec's drift model is **strictly broader** than grain's (grain narrows codebase shape; DomainSpec also covers semantic, governance, and coordination drift).
  - **`implementation/domainspec/AXIOMS.md`** — A1 (semantic authority precedes implementation), A3 (governance must be computable / machine-verifiable), A4 (observation independent from execution). A3 is the deterministic-narrowing claim grain makes, generalized.
  - **`implementation/domainspec/TEST-PIPELINE.md`** — the actual narrowing mechanism: formal docs → *deterministic* derived test obligations (the deterministic engine). This is DomainSpec narrowing the valid-output space via derived coverage, not via storage-layer shape.
- **Why NOT a kill, why NOT an import:** grain *validates* the thesis from the storage/runtime end; DomainSpec owns it from the **spec/intent** end. There is nothing to import — the claim is already owned more generally. At most, grain is **citable external corroboration** of a thesis DomainSpec already holds. Importing grain's framing as if new would overshoot (claim DomainSpec lacked the thesis).

### 7. Multi-tenant isolation (RLS, advisory locks, tenant-scoped cache keys)
**Verdict: GENUINE-GAP, but OVERSHOOT to import — heavy Clojure/Postgres infra, out-of-layer.**

- No owner in DomainSpec (sweep returns only incidental research-doc mentions). Honest gap.
- But this is pure **application-runtime infrastructure** (Postgres Row-Level Security, advisory locks, LMDB cache-key tenancy). It is below DomainSpec's adapter line (Axiom A2 — infra adapters hold no domain policy) and is non-portable Clojure code. Importing it would claim DomainSpec ships multi-tenant runtime isolation — a large overshoot. Net: real absence, correctly *not* DomainSpec's job. Not a candidate.

### 8. Read-model projections + two-tier caching (LRU + LMDB, partitioned)
**Verdict: OVERSHOOT-RISK — pure runtime infra, not a DomainSpec or Arcanum concern.**

- DomainSpec *names* read-models/projections as documentable surfaces (`architecture/pattern-library/concepts/ui/view-model.md`, `.../backend/query.md`, `drizzle-mirror-projection-repository.ts` in the backend impl) — so the *concept* is recognized. But grain's two-tier caching, Fressian serialization, watermark increments, and partition manifests are deep performance-runtime engineering with zero spec-layer surface. Importing = claiming a caching engine DomainSpec does not have and does not need. No genuine gap at DomainSpec's layer.

### 9. Distributed coordination (control plane, event-sourced leases)
**Verdict: OVERSHOOT-RISK — out-of-scope runtime infra.**

- No owner; correctly so. Coordinator election and tenant leases are deployment-runtime concerns far below DomainSpec's intent→spec layer. Not portable, not a gap at this layer. Reject as an import.

### 10. Datastar reactive UI (SSE hiccup)
**Verdict: OVERSHOOT-RISK / out-of-scope.**

- DomainSpec has its own UI-architecture lane (`implementation/domainspec/docs/UI-ARCHITECTURE.md`, `domainspec-ui-*` skills). Datastar is a specific Clojure+SSE rendering stack. No overlap to build from, no gap to fill — a tech choice, not a mechanism DomainSpec lacks. Reject.

### 11. (Derived) Live-runtime state introspection for agents
**Verdict: GENUINE-GAP (narrow), but at grain's layer not DomainSpec's.**

- The one sliver §4 leaves open: DomainSpec introspects *code + spec graph*, not *a live running service's runtime state* (event-store contents, current projections, health diagnostics). That live-runtime-introspection angle is genuinely thinner in DomainSpec. But it presumes a running app runtime (grain's layer), so it is a gap *below* DomainSpec's adapter line — adopt only if/when DomainSpec ever ships a runtime, which it does not. Flag, do not import now.

---

## Tally

| Verdict | Count | Items |
| --- | --- | --- |
| **ALREADY-OWNED** (build-from-owned, never a kill) | **3** | §3 schema-validate-before-invoke (Arcanum `dispatch-spec` + TEST-PIPELINE contract/event tests); §4 agent-introspection (GitNexus / semantic-index / `domainspec-sync-registry`); §6 narrow-output/drift thesis (`DRIFT-CONVERGENCE.md` + `AXIOMS.md` A1/A3 + `TEST-PIPELINE.md`) |
| **GENUINE-GAP** | **3** | §5 deny-by-default runtime auth; §7 multi-tenant isolation; §11 live-runtime state introspection — *all three out-of-layer (below DomainSpec's adapter line), so absence is correct, not a defect* |
| **OVERSHOOT-RISK** | **5** | §1 event store (idea owned ×2, code not portable); §2 CQRS; §8 two-tier caching/projections runtime; §9 distributed coordination; §10 Datastar UI |

**Bottom line (skeptic vector):** Grain's *ideas* that DomainSpec would actually want are **already owned** — the "narrow the valid-output space until drift is structurally impossible" thesis is DomainSpec's literal raison d'être (`DRIFT-CONVERGENCE.md`, `AXIOMS.md`, `TEST-PIPELINE.md`), the append-only evidence ledger is owned (`domainspec-emit-signals` + the cav2 ledger review), and agent-introspection + validate-before-act are owned (GitNexus/semantic-index, `dispatch-spec`). Grain's *genuine* gaps (runtime auth, multi-tenancy, live-runtime introspection) all sit **below DomainSpec's adapter line** as Clojure runtime infra — real absences that are correctly out-of-scope, not assimilation targets. The single legitimate move is to **cite grain as external corroboration** of DomainSpec's already-owned thesis; importing any grain *mechanism* as described would claim more than proof sustains.
