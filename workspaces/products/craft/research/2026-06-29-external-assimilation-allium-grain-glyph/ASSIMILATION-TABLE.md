---
node_type: research
role: synthesizer
subject: external assimilation — allium, grain, glyph
agent: "Milner, Robin — synthesizer / adjudicator"
repo: domainspec-core
inputs:
  - allium-scout.md (Hoare)      vs  allium-skeptic.md (Dijkstra)
  - grain-scout.md (Young)        vs  grain-skeptic.md (Lamport)
  - glyph-scout.md (Hejlsberg)    vs  glyph-skeptic.md (Wadler)
discipline: claim <= proof; one verdict per candidate; found owner = build-from-owned, never a kill
date: 2026-06-29
---

# Assimilation Decision Table — allium · grain · glyph

> Adjudicator: **Milner, Robin.** Not an advocate, not a skeptic. Each scout maximized
> assimilable surface; each skeptic swept DomainSpec's corpus for the existing owner.
> Below I put them head-to-head per candidate and render exactly one verdict, with
> `claim <= proof` on every row. Owner paths cited by the skeptics were sanity-checked
> against the live tree (`TAXONOMY.md`, `DRIFT-CONVERGENCE.md`, `AXIOMS.md`,
> `TEST-PIPELINE.md`, `OBSERVABILITY.md`, the test-derivation-engine, the named skills,
> the `.md` PreToolUse hook, and `telemetry/agents/subagents-dispatch.yaml` all exist).

---

## 1. Verdict at a glance

Across the three repos there are **25 distinct candidates**. The verdict is lopsided and
that lopsidedness is the finding: **2 ASSIMILATE-NOW**, **13 BUILD-FROM-OWNED**, **10
SKIP**. DomainSpec already owns the spine of all three external systems — its 25-concept
`TAXONOMY.md`, its deterministic test-derivation engine, its drift/convergence model, its
subagents-strategy + dispatch ledger, and its ontology-view forbidden-edge guard each
absorb whole clusters of scout candidates. The **single highest-leverage real move** is
narrow and unglamorous: wire the *already-owned* engine `check` / `validate-*` into a
fail-closed **PostToolUse hook on spec-doc writes** (allium #9) — every part exists, only
the wiring is missing, and it is the one thing that makes spec-semantic validation
automatic instead of remembered. The **biggest overclaim avoided** is glyph's **"92% token
reduction"**: that is glyph measuring glyph on one example, not a DomainSpec property —
import the (already-owned) scoping mechanism, never the number. Runner-up overclaim
refused: allium's "structure surfaces contradictions for free" — the detection is either a
closed CLI we don't have or LLM-mediated, so it cannot be claimed as a free property of
notation.

---

## 2. Master table

Legend — Verdict: **A** = ASSIMILATE-NOW, **B** = BUILD-FROM-OWNED, **S** = SKIP. Leverage/Cost: H/M/S(mall)/L(arge).

| # | Candidate | Repo | Verdict | DomainSpec target surface | Existing owner (if build-from-owned) | Lev | Cost | One-line reason |
|---|-----------|------|:---:|---------------------------|--------------------------------------|:---:|:---:|-----------------|
| A1 | Harness-enforced **post-write spec-semantic validator** hook | allium | **A** | `.claude/settings.json` PostToolUse on `docs/features/**` | — (parts owned; *wiring* is the gap) | H | S | The only conceded genuine gap: hook exists but injects frontmatter, not spec-semantic `check`/`validate-*`; close-coverage wiring over owned parts. |
| A2 | Terse single-file **concrete syntax (PEG/EBNF)** that desugars into the taxonomy | glyph | **A** | new front-end → existing engine parser; `TAXONOMY.md` is the target concept set | — (concept model owned; *surface syntax* absent) | M | M | DomainSpec owns the concept model + a machine-parseable doc schema but has no compact PEG surface; a desugaring skin is a real ergonomic gap, not a new capability. |
| B1 | Bidirectional spec↔code reconciliation (`/weed`) | allium | **B** | sharpen `domainspec-audit-alignment` with code→spec direction + divergence taxonomy | `domainspec-audit-alignment` + `DRIFT-CONVERGENCE.md` | H | M | Audit-alignment owns one-way classify+remediate; the code→spec write-back direction is a real sharpening, not a missing capability — build into the owned skill. |
| B2 | Formal **transition graph** + completeness/reachability obligations | allium | **B** | enrich `states.md` schema + δ-rule witnessing check in the engine | `TAXONOMY.md` (State Machine) + `TEST-PIPELINE.md` | H | M | TEST-PIPELINE already derives transition-row tests, state×event rejection tests, terminal no-outbound, invariant PBT — the same completeness surface; add inline edge-list + witnessing as a checklist over the owned derivation. |
| B3 | `open question` as a first-class convergence gate | allium | **B** | optional `open_questions` slot surfaced by engine; convergence note | `domainspec-spec-feature` discovery gate + `readiness-gate`/`decision-gate`/`verify-feature` | M | S | DomainSpec's gate is governance-grade (precondition halt + profiles + evidence); allium's is a loop exit-note. An in-flight `open_questions` field is a cheap sharpening of the owned gate. |
| B4 | Surface/contract boundary primitives | allium | **B** | formalize boundary contracts in the Interface/Mapping artifacts | `TAXONOMY.md` (Interface, Mapping, Event) | H | L | Interface request/response "Maps To" columns + Mapping direction already encode field-level boundary contracts; surface scoping is an extension of the owned concept, planned not urgent. |
| B5 | Post-write CLI hook *pattern* (allium-check.mjs multi-IDE) | allium | **B** | reference UX for the A1 hook wiring | A1's owner (engine `check` / `validate-*`) | M | S | Same surface as A1; the .mjs is a copy-adaptable UX reference (per-machine "show once" notice), not a separate capability — folds into A1. |
| B6 | Code-first **distillation discipline** (3 abstraction tests) | allium | **B** | enrich `domainspec-brownfield-translation` prose | `domainspec-brownfield-translation` (has `observed/stated/hypothesized` confidence taxonomy allium lacks) | M | S | Brownfield skill already does code→as-is spec with a richer confidence taxonomy; the "could it be different? / would we rebuild this?" heuristics are sharper prose to borrow, zero new capability. |
| B7 | Spec-**maturity routing** gate | allium | **B** | pre-check step atop generate-tests / audit-alignment | `readiness-gate` + discovery gate + `verify-feature` | M | S | The "don't run process-level checks on a coarse spec" routing is owned by the readiness/discovery gate family; add a maturity pre-check as a cheap guard. |
| B8 | Schema-validate-**before-invoke** (catalog→explain→validate→invoke) | grain | **B** | dispatch/contract validation discipline | Arcanum `dispatch-spec` (+`dispatch.schema.json`) + `TEST-PIPELINE.md` contract/event tests | H | M | "Validate shape before you act" is owned at dispatch-time and via derived contract tests; a *live runtime* command validator is below the adapter line (see S-grain rows). |
| B9 | Agent-introspection tooling (catalog/diagnostics) | grain | **B** | static spec/registry introspection | GitNexus skills + semantic-index + `domainspec-sync-registry` | M | M | DomainSpec owns rich code+spec-graph introspection; only the *live-running-service* angle is thinner, and that is out-of-layer (see S6). |
| B10 | "Narrow output space → drift structurally impossible" (the thesis) | grain | **B** | cite as external corroboration only | `DRIFT-CONVERGENCE.md` + `AXIOMS.md` (A1/A3) + `TEST-PIPELINE.md` | H | S | This is DomainSpec's literal raison d'être, owned more broadly (semantic/governance/coordination drift, not just storage shape). Nothing to import; grain is citable corroboration. |
| B11 | Machine-readable **CQRS event-model grammar** (`:valid-step`) | grain | **B** | well-formedness schema over spec artifacts | `TAXONOMY.md` flow concepts + `TEST-PIPELINE.md` (events/queries/operations derivation) | M | S | The legal-flow-topology predicate maps onto owned Workflow/Interface/Event concepts; a well-formedness schema is a build-from-owned tightening, not a new grammar. |
| B12 | In-band typed **failure vocabulary** (anomalies) | grain | **B** | typed sigil/spell return-status vocabulary | `domainspec-emit-signals` typed envelope (`SIGNAL-SCHEMA.md`) | M | S | DomainSpec already has a typed signal envelope for observations; a `:incorrect/:forbidden/:conflict/:fault` return taxonomy is a sharpening of the owned signal layer. |
| B13 | Deny-by-default as **compiler convention + audit report** | glyph | **B** | convention report alongside derived artifacts | `ontology-view` forbidden-edge guard + `TEST-PIPELINE.md` "for every state×event NOT in table → rejection test" | M | S | DomainSpec's deny-by-default is *stronger* (unconstructible-by-type + exhaustive derived rejection tests vs a runtime guard string); a `ConventionReport`-style audit record is the only borrowable sliver. |
| S1 | Allium **language / `.allium` substrate** wholesale | allium | **S** | — | (would duplicate `TAXONOMY.md`) | — | — | Wholesale rewrite: a second spec notation duplicating the 25-concept spine — the exact duplicate-terminology hazard allium's own `/distill` flags. |
| S2 | "Structure surfaces **contradictions for free**" claim | allium | **S** | — | (closest: `ontology-view` + `validate-relationships.ts`) | — | — | Overshoot: detection is a closed CLI (`allium analyse`) we lack source for, or LLM-mediated — cannot be claimed as a free property of notation (claim > proof). |
| S3 | `/propagate` **LLM-mediated test generator** | grain/allium | **S** | — | `tools/test-derivation-engine/` (deterministic-by-construction) | — | — | Importing it is a *downgrade*: DomainSpec's engine is no-LLM/no-network deterministic (the proprietary moat); take only the obligation-taxonomy as a δ-coverage audit checklist. |
| S4 | Event store / CQRS runtime, schema-validate-before-**append** | grain | **S** | — | (idea owned ×2: `emit-signals` ledger + `OBSERVABILITY.md` event-replay) | — | — | Below the adapter line (Axiom A2): a Clojure/Postgres/LMDB CQRS runtime DomainSpec does not ship; the append-only-evidence *idea* is already owned, the store is not portable. |
| S5 | Deny-by-default **runtime request auth** (`:authorized?`) | grain | **S** | — | (no owner — and correctly so) | — | — | Genuine absence but out-of-layer: request-level auth ≠ DomainSpec's governance/promotion gates; importing would overshoot scope. Spec-able invariant only. |
| S6 | **Live-runtime** state introspection for agents | grain | **S** | — | (no owner — presumes a running service) | — | — | Real but below the adapter line: presumes a running app DomainSpec does not ship; flag, do not import. |
| S7 | Multi-tenant isolation (RLS, advisory locks, tenant cache keys) | grain | **S** | — | — | — | — | Pure application-runtime infra below the adapter line; importing would claim a multi-tenant runtime DomainSpec does not have. |
| S8 | Two-tier projection cache / read-model runtime (LRU+LMDB) | grain | **S** | — | (concept named in pattern-library) | — | — | Performance-runtime engineering with no spec-layer surface; concept is recognized, the caching engine is not a gap. |
| S9 | Distributed coordination (control plane, event-sourced leases) + periodic-task CAS dedup | grain | **S** | — | — | — | — | Deployment-runtime coordination far below intent→spec layer; not portable, not a gap at this layer. |
| S10 | Datastar reactive UI / clj-dspy bridge / runnable Express+Postgres generators | grain/glyph | **S** | — | UI lane: `UI-ARCHITECTURE.md` + `domainspec-ui-*` | — | — | Stack choices (SSE/Clojure-Python/Express), not mechanisms DomainSpec lacks; glyph's generators would bind the determinism-first engine to an un-checked emit target (OVERSHOOT-2). |

> Note on glyph candidates folded above: glyph #1 (homoiconic task blocks), #3 (compiler-derived
> context profiles), #4 (tier prompts + per-role model routing), #6 (signal-based routing
> inference), #7 (bidirectional decompiler), #8 (utility compression tier) are all **B**, owned by
> `domainspec-subagents-strategy` + `register-dispatch` + the dispatch ledger + `domainspec-context-builder`
> (obligation-gated, stronger than glyph's block-membership scoping) + `distill`. They are sharpenings of
> the owned dispatch/context spine, not net-new — collapsed into B8–B13's reasoning rather than re-listed,
> because the dispute that matters is glyph's *concrete-syntax* gap (A2), which both Wadler and Hejlsberg agree on.

---

## 3. DO THIS NOW

Ranked by ROI. The first two are the **only** true ASSIMILATE-NOW gaps; the rest are
build-from-owned sharpenings ordered by leverage/cost.

**True net-new gaps (ASSIMILATE-NOW):**

1. **Wire the spec-semantic validator hook (A1).** Add a fail-closed **PostToolUse** hook
   on `docs/features/**` writes in `implementation/domainspec/.claude/settings.json` that
   runs the already-owned engine `check` / `validate-relationships.ts` / `validate-doc-links.ts`,
   reusing the multi-IDE UX pattern from allium's `allium-check.mjs` (per-machine "show once"
   notice). Every part is owned; this is coverage wiring, not an external dependency. — *Highest ROI: small cost, closes the one real gap.*

2. **Seed a terse concrete syntax that desugars to `TAXONOMY.md` (A2).** Prototype a
   single-file PEG/EBNF front-end whose every production maps to an existing meta-concept
   and emits the engine's existing doc schema — explicitly a *syntax skin over the owned
   engine*, never a parallel concept set. Borrow glyph's `grammar/glyph.peg` as a design
   reference only. — *Medium cost; defer past A1 but it is the one genuine ergonomic gap both glyph memos concede.*

**Build-from-owned sharpenings (no import, enrich the named owner):**

3. **Add the code→spec direction to `domainspec-audit-alignment` (B1)** with allium's
   divergence taxonomy (spec-bug / code-bug / aspirational / intentional-gap), closing the
   Saturn loop's implementation boundary against `DRIFT-CONVERGENCE.md`.

4. **Add inline edge-list + witnessing check to `states.md` / the engine (B2)** so a declared
   transition with no witnessing operation fails the derivation — a checklist over the
   already-owned `TEST-PIPELINE.md` completeness derivation.

5. **Add an `open_questions` in-flight slot + maturity pre-check (B3 + B7)** to
   `domainspec-spec-feature` / `generate-tests`, making the standing "escalate ambiguity"
   rule structurally enforced by the owned gate family rather than advisory.

---

## 4. Disputed rows (scout vs skeptic) — my adjudication

These are the rows where the advocate and the auditor materially disagreed. I pick the
verdict the evidence sustains; I do not split the difference.

- **`/weed` bidirectional reconciliation (allium #1).** *Scout (Hoare):* net-new — "no
  'update code to match spec' direction at all," Saturn loop incomplete without it.
  *Skeptic (Dijkstra):* ALREADY-OWNED by `audit-alignment` + `DRIFT-CONVERGENCE.md`.
  **My call: BUILD-FROM-OWNED.** Audit-alignment genuinely owns the divergence-classify-and-remediate
  spine; the scout is right that the *code→spec write-back direction* is absent, but that is a
  sharpening of an owned skill, not a new capability — and the precedent rule forbids treating
  a found owner as net-new.

- **Transition graph completeness (allium #2).** *Scout:* H-leverage gap — "lifecycle specs are
  unverified claims," no machine-checkable graph. *Skeptic:* owned by `TAXONOMY.md` State Machine
  + `TEST-PIPELINE.md`. **My call: BUILD-FROM-OWNED.** The skeptic is decisive here: TEST-PIPELINE
  already derives transition-row tests, state×event rejection tests, terminal no-outbound tests and
  invariant PBT — that *is* the completeness/reachability surface. The inline edge-list + per-rule
  witnessing is a worthwhile tightening, not a missing engine.

- **Post-write spec validator hook (allium #5/#9).** *Scout:* M-leverage gap, "engine drift
  check exists but is not auto-wired." *Skeptic:* **GENUINE-GAP (narrow)** — "no single
  harness-enforced hook re-runs spec-semantic validation on every spec-doc write," but it is a
  *wiring gap, not a capability gap*. **My call: ASSIMILATE-NOW (A1).** This is the rare row where
  scout and skeptic *converge* on a real gap; I verified the live `.md` PreToolUse hook injects a
  frontmatter cheatsheet, not spec semantics. Conceded — with the skeptic's discipline that the
  import is owned-parts wiring, never an allium/closed-CLI dependency.

- **"Structure surfaces contradictions for free" (allium headline).** *Scout:* implied as a
  property of the constrained grammar. *Skeptic:* **OVERSHOOT-RISK** — allium has no compiler/runtime;
  detection is the closed `allium analyse` CLI or LLM-mediated. **My call: SKIP (overshoot).** The
  skeptic is right and this is the claim≤proof line: a constrained Markdown/grammar does not yield
  formal contradiction detection for free. DomainSpec's real adjacent owner is `ontology-view` +
  `validate-relationships.ts` (structural, non-LLM) — frame any work there, never as "adopt notation
  that surfaces contradictions."

- **Grain's "narrow the output space" thesis (grain #6 / the whole repo's thesis).** *Scout (Young):*
  the highest-ROI cluster, grain's central importable thesis. *Skeptic (Lamport):* ALREADY-OWNED —
  DomainSpec's literal raison d'être, owned *more broadly*. **My call: BUILD-FROM-OWNED (cite-only).**
  The skeptic wins outright: importing grain's framing as new would claim DomainSpec lacked its own
  thesis. Grain is external corroboration of `DRIFT-CONVERGENCE.md` + `AXIOMS.md`, nothing to assimilate.

- **Glyph token-compression / context profiles (glyph #3, #8).** *Scout (Hejlsberg):* H-leverage —
  compiler-derived per-task context minimization DomainSpec maintains by hand. *Skeptic (Wadler):*
  ALREADY-OWNED by `domainspec-context-builder` (obligation-gated, *stronger* than glyph's
  block-membership scoping) — and the "92% token reduction" is glyph-on-glyph. **My call:
  BUILD-FROM-OWNED, number REFUSED.** The mechanism is owned and DomainSpec's is provably-relevant
  where glyph's is heuristic; the headline metric does not transfer without DomainSpec running its own
  measurement.

- **Glyph typed-intent DSL → codegen (glyph #1, and the runnable-generator angle).** *Scout:* H-leverage,
  homoiconic spec↔work-item + direct emit. *Skeptic:* ALREADY-OWNED by `TAXONOMY.md` + the deterministic
  engine; glyph's Express/Postgres generators are an OVERSHOOT (un-determinism-checked emit against a
  stack the engine doesn't target). **My call: DSL is BUILD-FROM-OWNED; runnable generators are SKIP;
  the one carve-out is the concrete-syntax seed (A2).** The concept set is owned; only the terse surface
  syntax is a genuine gap, and it must desugar into the taxonomy rather than ship glyph's grammar+generators.

---

## 5. What the dispatch deliberately did NOT recommend

No wholesale imports: not the **allium `.allium` language** as a second spec notation (duplicates
`TAXONOMY.md`), not grain's **Clojure/Postgres/LMDB CQRS runtime / multi-tenancy / distributed
coordination / Datastar UI** (all below the adapter line, Axiom A2), not glyph's **Express/Postgres/Zod
generators** (bind the determinism-first engine to an un-checked emit target), and not any **LLM-mediated
test generator** (a downgrade from the deterministic engine moat) — and emphatically not glyph's **"92%
token reduction" / "writes a whole backend"** metrics, which are external measurements, not DomainSpec results.

---

## Dispatch close

- **dispatch_id:** `2026-06-29-external-assimilation-allium-grain-glyph` · **type:** research · **exit_reason:** `resolved`
- **agents_spawned:** 8 total — 3 explorer (scouts: Hoare/Young/Hejlsberg) · 3 skeptic (Dijkstra/Lamport/Wadler) · 1 writer (synthesizer: Milner) · 1 helper (a stray sub-sweep, cap-killed). Plus 2 check-tension gate agents (infrastructure, not counted). `loops_used: 1`.
- **anti-bias gate:** check-tension PASS×2 (checker + reviewer, independent) before launch.
- **operational note:** the first working batch hit a usage-cap ("session limit"); only `allium-scout.md` landed. The remaining 5 pair-agents were re-launched after the cap reset and all completed; verdict unaffected.
- **final_approver:** parent — verified `ASSIMILATION-TABLE.md` and every memo on disk (P8), confirmed owner paths resolve, no kills (precedent rule), claim≤proof held.
