---
node_type: research
role: skeptic
area: layering-alignment
agent: "Schön, Donald — SKEPTIC / reflective-practitioner"
subject: DomainSpec v1 → v2 import triage — layering alignment
date: 2026-06-29
discipline: claim <= proof; default-deny anything that overshoots the adapter line or duplicates owned forbidden-edge/taxonomy layering
sources:
  - projects/domainspec-v2/research/2026-06-29-v1-import-triage/SEED.md
  - implementation/domainspec/TAXONOMY.md
  - implementation/domainspec/RELATIONSHIPS.md
  - implementation/domainspec/AXIOMS.md
  - .arcanum/inventory/entries/ontology-operationalization-in-the-machine-synthesis.md
  - projects/domainspec-v2/research/2026-06-29-external-assimilation-allium-grain-glyph/ASSIMILATION-TABLE.md
  - projects/domainspec-v2/research/2026-06-29-correctness-ownership-sweep/findings.md
  - projects/domainspec-v2/research/test-engine/HANDOFF.md
---

# Layering-Skeptic Memo — v1 → v2 Import Triage

**Role:** Schön, Donald — SKEPTIC for LAYERING ALIGNMENT.
**Method:** owner-sweep first; default-deny on two grounds — (a) adapter-line overshoot (Axiom A2:
domain decisions stay domain/application, never infrastructure or app-runtime), and (b) duplication of
already-owned forbidden-edge/taxonomy layering without additive delta. Every REFORMULATE cites the
existing owner.

---

## Adapter-line definition (the fence)

Axiom A2 (`AXIOMS.md`): *domain policy, invariants, and state transitions belong in domain and
application layers, never infrastructure adapters.* v2's goal (`SEED.md`) is "govern + enforce
Ontology A on evidence." Anything that presupposes a **running application** (live runtime, live
agent state, running service introspection, CQRS append store, request-level auth enforcement, tenant
RLS) is **below the adapter line** — it is an app-runtime concern, not a language/governance concern.
The synthesis (`ontology-operationalization-in-the-machine-synthesis.md` §decision-spine) further
distinguishes schema-drift (eliminable via type-enforcement) from instance-drift (not eliminable via
schema alone — needs behavioral contracts). Any candidate that conflates the two overshoots.

---

## Candidate verdicts

### C1 — TAXONOMY.md: 25 meta-concepts + 29 typed edges

**Owner-sweep:** TAXONOMY.md is the existing owner (cited throughout ASSIMILATION-TABLE; confirmed
live). **Verdict: REFORMULATE.** v2's task is to take this schema and make it machine-enforced (the
endpoint-type gap named in the synthesis: `validate-relationships.ts` today checks label membership
only, not endpoint-pair admissibility — the "well-typed = can't-drift" upgrade is the real net-new).
Import the schema; net-new only the endpoint-pair type enforcement. Do NOT re-derive the 25 concepts
— TAXONOMY.md is canonical.

### C2 — RELATIONSHIPS.md: Edge Law (29 typed edges, forbidden-edge guard)

**Owner-sweep:** `RELATIONSHIPS.md` + `validate-relationships.ts` (tools/) own the label-membership
check. The synthesis explicitly names the residue: endpoint-pair admissibility typing is absent, making
the guard label-only today. **Verdict: REFORMULATE.** Sharpen into v2 as endpoint-typed Edge Law
validator. The ASSIMILATION-TABLE (B13) also found this: `ontology-view` forbidden-edge guard is the
owned surface; a `ConventionReport`-style audit is the sliver to borrow. Nothing new to import —
only the endpoint-pair gap is genuinely net-new, and it is a finishing task on owned wiring.

### C3 — UI meta-concepts (11: Page, Layout, Component, View Model, Hook, Form, Action, Guard, Binding, Adapter, State Indicator)

**Owner-sweep:** TAXONOMY.md §UI Structural/Behavioral/Connective/Presentational owns all 11. Their
layer assignment is stated: Pages → routes; Hooks/Bindings → hooks layer; Guards/Actions → component
layer. Cross-layer edges (fetches, mutates, reflects, derives, contracts, mirrors) are owned in
RELATIONSHIPS.md. **Layering concern:** Guard and Action are client-side, presupposing a running UI
runtime. They belong to the *language schema for describing a domain*, not to v2's governance
enforcer. **Verdict: REFORMULATE.** Import UI concepts as language-schema nodes; v2 enforces their
typed edges against spec artifacts. Do NOT attempt to enforce `Guard` or `Action` correctness at
runtime — that is below the adapter line (app-runtime). Schema-level: owned; behavioral-correctness:
instance-drift (not eliminable by schema alone, per synthesis).

### C4 — Observer tools (run-async-observer.ts, run-fast-observer.ts, governance-attenuation-audit.ts)

**Owner-sweep:** The synthesis (`leverage-point-finish-the-built-observer`) confirms these exist in
code but are under-performing — the feedback loop is not closed. ASSIMILATION-TABLE §DO-THIS-NOW
(A1) names wiring the PostToolUse hook as the highest-ROI move; the synthesis calls finishing the
observer the highest structural leverage point. **Layering check:** The observer is a governance
read-only tool (reads spec artifacts, reports drift) — it does NOT write promotion-status (write-
authority proviso). This is layer-clean: it sits at the governance observation layer, not runtime.
**Verdict: REFORMULATE (IMPORT for the owned build, net-new only for the missing PostToolUse wiring
A1 and the endpoint-pair gap in the Edge Law validator).** No overshoot — build-from-owned. The only
import is wiring, as A1 already established.

### C5 — spec→test engine (test-engine/HANDOFF.md, tools/test-derivation-engine/)

**Owner-sweep:** `test-engine/HANDOFF.md` states "designed-not-wired / not executed." `correctness-
ownership-sweep/findings.md` (A7) assigns verdict `designed-not-wired / net-new code`. The engine
does not yet exist as a wired executor; the mapping rules (`TEST-PIPELINE.md`) exist but the executor
is missing. **Layering check:** A deterministic spec→test engine is layer-clean — it consumes spec
artifacts and emits test artifacts; it does NOT touch app-runtime. The HANDOFF explicitly marks it as
the "free wedge" (publishable, commodity, not moat). The ASSIMILATION-TABLE (S3) protects the moat:
the deterministic engine is NOT the LLM-mediated generator — that would be a downgrade. **Verdict:
IMPORT (ASSIMILATE-NOW as net-new code, with strict discipline: deterministic-by-construction only,
no LLM path in this surface).** Layer: spec-artifact → test-artifact, entirely above the adapter line.

### C6 — Validator tooling (validate-relationships.ts, validate-orphans.ts, validate-doc-links.ts, validate-work-pack-coverage.ts, validate-signals.ts)

**Owner-sweep:** All validators exist in `tools/` (confirmed live in ASSIMILATION-TABLE §adjudicator
note). The PostToolUse hook wiring is the A1 gap already resolved as ASSIMILATE-NOW. **Layering
check:** These are static-analysis tools operating on spec artifacts — layer-clean. `validate-
relationships.ts` currently does label-membership only; the endpoint-pair upgrade is the net-new
(C2). **Verdict: REFORMULATE.** All validators are build-from-owned. The only net-new is endpoint-
pair typing in `validate-relationships.ts` (subsumed under C2). No new import needed.

### C7 — Axiom A2 / AXIOMS.md governance axioms (A1–A6)

**Owner-sweep:** `AXIOMS.md` owns all 6 axioms. **Layering check:** These are governance-layer
epistemic foundations — precisely what v2 must enforce, not bypass. A2 is the adapter-line axiom
this memo enforces. **Verdict: REFORMULATE.** Bring into v2 as the invariant surface against which
all other candidates are measured. Nothing net-new — the axioms are the authority.

### C8 — App-runtime concerns (live-runtime introspection, CQRS runtime, request-level auth, multi-tenant RLS, live agent state)

**Owner-sweep:** ASSIMILATION-TABLE (S4–S10) already swept and SKIPped every runtime-level
candidate. Correctness-ownership-sweep does not surface any runtime-governance ownership. **Layering
verdict: DROP.** These are below the adapter line (Axiom A2). Importing any runtime concern into v2's
language-governance layer would be a layering violation — it would force v2 to presuppose a running
application it does not and should not ship. Confirmed DROP; no owner needed (absence is correct).

### C9 — Schema-drift elimination vs instance-drift (two-ontologies distinction)

**Owner-sweep:** The synthesis (`schema-drift-eliminable-instance-drift-not`) owns this distinction
explicitly. Ontology A (DomainSpec language) and Ontology B (cav2 authority) must ALIGN, not merge.
Schema drift is eliminable via endpoint-type enforcement (C2). Instance drift requires behavioral
contracts — a separate, harder surface (correctness-ownership-sweep B6/B7: net-new). **Layering
check:** v2 can and must enforce schema-level non-drift (typed nodes + typed edges = can't-construct-
forbidden). Instance drift is below what spec governance can eliminate. **Verdict: REFORMULATE.**
Sharpen v2's scope claim accordingly: v2 governs schema-level Ontology A; instance-drift claims are
demoted to net-new behavioral-contract work (B6/B7 in correctness sweep). Do not overclaim that v2
eliminates all drift — that is claim > proof.

### C10 — The "deterministic engine = free wedge" vs "deterministic engine = proprietary moat" contradiction (SEED.md §contradiction)

**Owner-sweep:** ASSIMILATION-TABLE (S3) + memory (engine-algorithm-proprietary) + correctness-sweep
both resolve this. The **deterministic engine METHOD** (rule-table executor, what the spec→test engine
does) is the free wedge — it is the commodity surface, publishable to arcanum. The **moat** is:
attestation corpus + governance-data + vertical integration + provability lever (Lean formal proof).
The test-derivation-engine (`tools/test-derivation-engine/`) is the free wedge. The Lean kernel
(`domainspec-lean-formalization/`) is the moat amplifier. **Layering verdict:** Both sides are layer-
clean; the contradiction is a naming/scope confusion, not a layering violation. **Verdict: REFORMULATE
the HANDOFF.md claim.** The HANDOFF says "free wedge" without specifying that the Lean formal-proof
lever must remain moat-only. Add that boundary to any v2 framing. No DROP, no net-new — a prose
sharpening.

---

## Default-deny ledger (what this review blocked)

| # | Candidate | Block reason | Axiom / Rule |
|---|-----------|-------------|--------------|
| D1 | Live-runtime agent state introspection | Below adapter line — presupposes running service | Axiom A2; confirmed S6 in ASSIMILATION-TABLE |
| D2 | CQRS runtime / append store as v2 asset | Below adapter line — app-runtime persistence | Axiom A2; confirmed S4 in ASSIMILATION-TABLE |
| D3 | Request-level auth enforcement (`:authorized?`) | Below adapter line — app-runtime auth | Axiom A2; confirmed S5 in ASSIMILATION-TABLE |
| D4 | Multi-tenant isolation (RLS, locks, tenant keys) | Below adapter line — infra concern | Axiom A2; confirmed S7 in ASSIMILATION-TABLE |
| D5 | LLM-mediated test generator | Downgrade from deterministic engine moat; claim > proof | S3 in ASSIMILATION-TABLE; engine-algorithm-proprietary memory |
| D6 | "v2 eliminates all drift" claim | Instance drift not eliminable by schema alone | Synthesis `schema-drift-eliminable-instance-drift-not` |
| D7 | Ontology A and B merge / v2 as type-checker for cav2 | Two-ontologies rule: ALIGN, never merge | Synthesis `two-ontologies-language-vs-authority-no-merge` |

---

## Summary verdict table

| Candidate | Verdict | Owner (cite) |
|-----------|:-------:|--------------|
| C1 TAXONOMY 25 meta-concepts | REFORMULATE | `TAXONOMY.md` (canonical) |
| C2 Edge Law / forbidden-edge guard | REFORMULATE | `RELATIONSHIPS.md` + `validate-relationships.ts`; net-new: endpoint-pair typing |
| C3 UI meta-concepts (11) | REFORMULATE | `TAXONOMY.md` §UI; no runtime enforcement |
| C4 Observer tools | REFORMULATE | `tools/run-async-observer.ts`; A1 wiring net-new |
| C5 spec→test engine | IMPORT | `test-engine/HANDOFF.md` (designed-not-wired); deterministic-only |
| C6 Validator tooling | REFORMULATE | `tools/validate-*.ts`; endpoint-pair gap → C2 |
| C7 AXIOMS.md (A1–A6) | REFORMULATE | `AXIOMS.md` (the authority) |
| C8 App-runtime concerns | DROP | Axiom A2; ASSIMILATION-TABLE S4–S10 |
| C9 Schema-drift vs instance-drift | REFORMULATE | Synthesis §schema-drift-eliminable-instance-drift-not |
| C10 Free-wedge/moat boundary | REFORMULATE (prose) | HANDOFF.md + S3 + engine-algorithm-proprietary memory |

---

## Net net

One genuine IMPORT: the spec→test engine executor (C5) — no current code, layer-clean, deterministic-
only. Eight REFORMULATE rows — the spine is owned; the net-new work is two wiring gaps (A1 PostToolUse
hook, C2 endpoint-pair Edge Law upgrade) plus one prose sharpening (C10 free-wedge boundary). Seven
DEFAULT-DENY blocks — all runtime/below-adapter-line or claim>proof. The lopsidedness is the finding:
v2 is finishing and wiring, not rebuilding. The write-authority proviso (no modeling surface writes
promotion-status) is the single architectural invariant every wiring decision must preserve.
