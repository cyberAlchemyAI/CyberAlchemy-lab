---
node_type: research
role: skeptic
agent: "Russell, Bertrand — audit skeptic"
subject: DomainSpec v1 → v2 import triage
dispatch_id: 2026-06-29-domainspec-v1-import-triage
date: 2026-06-29
discipline: claim <= proof; one verdict per capability; found owner = build-from-owned, never a kill
sources:
  - projects/domainspec-v2/research/2026-06-29-v1-import-triage/SEED.md
  - projects/domainspec-v2/research/2026-06-29-correctness-ownership-sweep/findings.md
  - .arcanum/inventory/entries/kodamai-smithe-correctness-layer-synthesis.md
  - projects/domainspec-v2/research/2026-06-29-external-assimilation-allium-grain-glyph/ASSIMILATION-TABLE.md
  - projects/domainspec-v2/research/test-engine/HANDOFF.md
  - implementation/domainspec/TEST-PIPELINE.md
  - implementation/domainspec/AXIOMS.md
  - implementation/domainspec/DRIFT-CONVERGENCE.md
  - projects/domainspec-v2/research/dcb-correctness/SYNTHESIS.md
  - .arcanum/inventory/entries/ontology-operationalization-in-the-machine-synthesis.md
---

# Audit Memo — Skeptic (Russell, Bertrand)
## DomainSpec v1 → v2 Import Triage

> Role: sweep for existing owners; refuse overclaims; apply claim ≤ proof on every row.
> A found owner is REFORMULATE, never DROP. Genuinely absent surface = IMPORT.
> Verdict options: IMPORT (bring in), REFORMULATE (build-from-owned), DROP (out-of-layer/downgrade).

---

## Candidate sweep

### C1 — TAXONOMY.md + 25-concept spine (language Ontology A)

**Owner:** `implementation/domainspec/TAXONOMY.md` — 25 meta-types, ~29 typed edges, Edge Law.
**Witnessed:** Yes — edge-signature validation runs in the saga toy harness; `validate-relationships.ts` enforces label membership; `generate-registry.ts` materializes the type set.
**Verdict: REFORMULATE.** The concept model is wholly owned. v2's work is *endpoint-pair admissibility* (make forbidden edges unconstructible by type, not just labeled forbidden) — a finishing move over the owned spine, not a re-import. Overclaim to avoid: "TAXONOMY.md is already a formal type-checker" — it is a label registry; the endpoint-pair predicate is net-new code.

### C2 — AXIOMS.md + DRIFT-CONVERGENCE.md (governance doctrine)

**Owner:** `AXIOMS.md` A1–A3+ and `DRIFT-CONVERGENCE.md` — semantic/contract/runtime/governance/coordination drift taxonomy, convergence evidence requirement.
**Witnessed:** Defined-governed; no runtime sensor, but the conceptual definitions are durable.
**Verdict: REFORMULATE.** Bring the doctrine forward; wire the *sensor* (the observer loop). The **coverage gap** is `DRIFT-CONVERGENCE.md` acknowledging runtime drift as a concept while the actual sensor (`run-async-observer.ts`) is "built, under-performing" (per `ontology-operationalization-in-the-machine-synthesis` §Decision spine). That is a wiring gap, not a conceptual gap — REFORMULATE, not IMPORT.

### C3 — TEST-PIPELINE.md rule tables (doc-section → test-type mapping)

**Owner:** `implementation/domainspec/TEST-PIPELINE.md` — deterministic rule tables: each transition-table row = 1 test case, fixed templates per doc section (states, operations, interfaces, events, queries, workflows, mappings).
**Witnessed:** Rule tables are defined; the *executor* is absent (confirmed: `HANDOFF.md` "the agent reading TEST-PIPELINE.md and writing tests by hand"; grep zero hits for LLM/model calls in `.ts` tooling).
**Verdict: REFORMULATE.** The rule tables are owned and load-bearing — v2 inherits them unchanged. The gap is the *executor* that mechanically applies the rules (HANDOFF.md A7 = "designed-not-wired"; correctness-sweep confirms). That executor is net-new code on top of owned rules. Do NOT import TEST-PIPELINE.md as if it were the engine — it is the spec the engine runs; label clearly.

### C4 — Deterministic spec→test engine (the executor)

**Owner:** Zero. HANDOFF.md O4 places the *engine method* as "free wedge → public-arcanum eligible." The correctness-ownership sweep confirms: "spec→test engine (A7) = designed-not-wired, no code."
**Verdict: IMPORT.** Genuinely net-new code; no v1 owner. The rule tables (C3) are the input spec; the executor is the gap. The SEED's framing is correct.
**Claim fence:** HANDOFF.md calls the engine the "free wedge" (publishable); ASSIMILATION-TABLE S3 calls the *deterministic engine* the "proprietary moat." These are reconcilable: the **rule-table method** is the free/publishable layer (it is already in TEST-PIPELINE.md, which is owned and readable); the **moat** is the attestation, governance-data, and vertical (the Lean formal-proof lever, per HANDOFF.md O4: "only a Lean formal-proof lever would be moat"). The deterministic executor itself sits in the free wedge — correctly labeled so. Overclaim: calling the executor "provably correct" before a soundness theorem exists.

### C5 — DCB freshness guard (AcceptSpecCodeCorrectnessClaim design)

**Owner:** `dcb-correctness/SYNTHESIS.md` + `HANDOFF.md` — design-only; no toy execution, no wired code.
**What is owned:** The *distinction* between validator-pass and claim-freshness is defined-governed (correctness-sweep B5). The actual DCB edge (concurrent-acceptance discrimination, PROOF-OBLIGATIONS.md:59) collapses today to a content-hash in the toy harness (correctness-sweep A3: "dcb→hash flip verdict-invariant").
**Verdict: REFORMULATE** for the validator-vs-freshness *distinction* (owned, carry forward); **IMPORT** for the actual DCB concurrency/TOCTOU discrimination edge (net-new for everyone — correctness-sweep confirms neither we nor Kodamai own this). These must be labeled separately in v2; conflating them is the collapse risk.

### C6 — Honest-labeling discipline (five-label proof vocabulary + P8 scope fence)

**Owner:** `alloy-tla/CLAIM-LEDGER.md C3/C8` + `DISTILL.md` + `DEPENDENCY-MAP H-3` + `DEC-CONV-01` (correctness-sweep B1/B2). Executed per-row; definition cards with misuse warnings (B4).
**Verdict: REFORMULATE.** This IS the Kodamai competitive wedge per correctness-sweep findings §One-line answer. Bring forward unchanged; it is the highest-confidence owned surface. Overclaim to flag: any label upgrade from "constrained" to "correct" without a behavioral/concurrency verifier — the sweep self-caught this and it must stay self-caught in v2.

### C7 — Full domainspec-* skills suite (40+ skills)

**Owner:** `.claude/skills/` — every skill is wired, executed, used in production (audited by ASSIMILATION-TABLE §2 which sanity-checked named skills as live).
**Verdict: REFORMULATE.** Skills are owned and functioning; v2 does not re-import them — it governs/enforces over them. The governance surface is exactly what v2 adds. Importing them wholesale as if v2 rebuilds the skill suite is a category error. The net-new v2 layer is: (a) PostToolUse hook wiring for spec-semantic validation on writes (ASSIMILATION-TABLE A1 — wiring gap, parts owned); (b) endpoint-pair type enforcement (C1 above); (c) the sensor/observer loop (C2). Skills themselves = REFORMULATE (sharpen into v2 governance context, do not re-import).

### C8 — Behavioral saga witnesses (σ-edge graph, compensation ordering, bounded witness)

**Owner (partial):** `dcb-saga-correctness/toy-harness/saga-spec.ts` — σ-edge graph/compensation check (L203) and edge-signature validation (L165) are executed-wired and sound (correctness-sweep A1/A5 = GO). The behavioral saga witness (A2) is partial: one genuine negative-witness leg; two assertions tautological (empty-trace lying run passed; red-team 2026-06-17 M2/M3).
**Verdict: REFORMULATE** for the clean legs (A1/A5, negative-witness seed of A2); the two tautological assertions are a demotion, not a kill — replace with trace-derived outcomes. Overclaim to quarantine: do not carry forward A2's tautological assertions as "behavioral witnesses" — label them "literal-driven stubs pending replacement."

### C9 — Observability / telemetry layer (OBSERVABILITY.md, subagents-dispatch.yaml, otel)

**Owner:** `implementation/domainspec/OBSERVABILITY.md` + `telemetry/agents/subagents-dispatch.yaml` + the `domainspec-instrument-otel` and `domainspec-otel-verify` skills.
**Verdict: REFORMULATE.** Owned infrastructure; v2 inherits it. The sensor loop gap (C2) is the upgrade surface, not a re-import. No overclaim risk here.

### C10 — Write-authority proviso (no modeling surface writes promotion-status)

**Owner:** `ontology-operationalization-in-the-machine-synthesis` §Decision spine — architectural invariant ("the absence of the edge, not a relaxable policy").
**Verdict: REFORMULATE.** Load-bearing architectural constraint; carry forward as a hard constraint in v2, not merely a design preference. This is the single rule that keeps the map from collapsing into a decision — its absence is a kill, not a tradeoff.

---

## The free-wedge vs moat contradiction — resolution

HANDOFF.md (test-engine) calls the deterministic engine the "free wedge" (O4). ASSIMILATION-TABLE S3 defends the deterministic engine as the "proprietary moat." Both are partially right; the confusion is about which *layer* is free and which is moat:

| Layer | Free or Moat? | Evidence |
|---|---|---|
| TEST-PIPELINE.md rule tables (the method) | **Free** — already readable/public in the repo; publishable to arcanum | HANDOFF.md O4; rules are not executable without an engine |
| Deterministic executor (the engine code) | **Free wedge** — no LLM, no external model; the commodity/publishable layer | HANDOFF.md O4 explicit; S3 in ASSIMILATION-TABLE names it the moat but that is an overclaim |
| Attestation + governance-data + vertical integration | **Moat** — the Saturn/DomainSpec vertical around the engine, not the engine itself | ASSIMILATION-TABLE S3 context; memory entry `engine-algorithm-proprietary` |
| Lean formal-proof lever | **Moat** — explicitly gated (`g05`) per HANDOFF.md O4 | correctness-sweep B3; `domainspec-lean-formalization/` |

**Ruling:** The S3 ASSIMILATION-TABLE label "proprietary moat" refers to the *system* (engine + attestation + vertical), not the executor alone. HANDOFF.md O4's "free wedge" label for the deterministic executor is the more precise claim and survives scrutiny. The executor is publishable; the attestation/formal-proof layer is moat. No contradiction remains once the referent is scoped. v2 should carry this distinction explicitly — collapsing them (labeling the whole system "moat" or the whole system "free") is the overclaim risk.

---

## Overclaims flagged (claim ≤ proof enforcement)

1. **"Provably correct"** — nowhere in the v1 corpus does an agent have a behavioral/concurrency verifier. The correct term is "constrained" (decidable σ-edge/graph checks + content-hash freshness). The gap between "provably constrained" and "provably correct" is exactly the Kodamai gap we self-caught — carrying "provably correct" into v2 marketing without a behavioral verifier reproduces Kodamai's inflation. Verdict: QUARANTINE the phrase; replace with the five-label vocabulary (C6).

2. **DCB freshness = DCB concurrency discrimination** — the toy harness collapses DCB to content-hash; calling it "DCB freshness" implies the full concurrent-acceptance guard. Verdict: label separately (content-hash freshness = owned; DCB concurrency edge = net-new). See C5.

3. **"The engine is the moat"** — overclaim in the direction of over-restricting. The executor is free-wedge material; the moat is the attestation+vertical+formal-proof layer. Collapsing these delays publishing the free wedge without protecting the actual moat. See contradiction resolution above.

4. **Behavioral saga witness (A2) as a whole** — two of three assertions are tautological (empty-trace run passes). Carrying A2 forward without the demotion label inflates the witnessed surface. Verdict: REFORMULATE with explicit partial-witness label.

---

## Summary verdict table

| # | Candidate | Verdict | Owner (if reformulate) | Net-new surface |
|---|---|---|---|---|
| C1 | TAXONOMY.md 25-concept spine | REFORMULATE | `TAXONOMY.md` | endpoint-pair admissibility predicate |
| C2 | AXIOMS + DRIFT-CONVERGENCE doctrine | REFORMULATE | `AXIOMS.md` / `DRIFT-CONVERGENCE.md` | observer sensor wiring |
| C3 | TEST-PIPELINE.md rule tables | REFORMULATE | `TEST-PIPELINE.md` | — (rules carry forward unchanged) |
| C4 | Deterministic spec→test executor | IMPORT | — | the executor is net-new code (free wedge) |
| C5a | DCB validator-vs-freshness distinction | REFORMULATE | `dcb-correctness/SYNTHESIS.md` | — |
| C5b | DCB concurrency/TOCTOU discrimination | IMPORT | — | net-new for everyone |
| C6 | Honest-labeling discipline (5-label + P8) | REFORMULATE | CLAIM-LEDGER/DEPENDENCY-MAP | — |
| C7 | domainspec-* skills suite | REFORMULATE | `.claude/skills/` | PostToolUse hook wiring (A1) |
| C8 | Saga behavioral witnesses (clean legs) | REFORMULATE | `saga-spec.ts` A1/A5/A2-partial | trace-derived assertion replacement |
| C9 | Observability/telemetry infrastructure | REFORMULATE | `OBSERVABILITY.md` | sensor loop upgrade |
| C10 | Write-authority proviso | REFORMULATE | `ontology-operationalization-synthesis` | — (hard constraint, carry as-is) |

**No DROPs.** Every candidate has either a live owner (REFORMULATE) or is a genuine gap (IMPORT). The precedent rule holds throughout: a found owner is build-from-owned, never a kill.

---

## Close

No scout memo exists yet in this folder — this memo is written directly from the SEED + the three owned sweeps it cites. The correctness-ownership sweep and the Kodamai synthesis together do the heavy lifting; this audit adds the structured per-candidate ruling and the free/moat boundary resolution. The synthesizer (Spivak) should use this memo as the skeptic's input and render findings.md.

`exit_reason: resolved` (audit-skeptic scope complete; awaiting synthesizer)
