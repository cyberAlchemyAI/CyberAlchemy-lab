---
node_type: research
role: scout
area: TWO-OFFERS
agent: "Wisnesky, Ryan — scout"
subject: DomainSpec v1 → v2 import triage · two-offers surface
dispatch_id: 2026-06-29-domainspec-v1-import-triage
date: 2026-06-29
discipline: claim <= proof; one verdict per capability; found owner = build-from-owned, never a kill
---

# Scout Memo — TWO-OFFERS Area

> Role: maximize importable surface for v2. READ-ONLY on v1.
> Contradiction resolved per SEED.md: HANDOFF.md calls the deterministic engine the "free
> wedge"; ASSIMILATION-TABLE S3 + memory call it the "proprietary moat." I state the
> resolution in each row and unambiguously in §2 below.

---

## 1. Candidate Rows

### C1 — TEST-PIPELINE derivation rules (the rule table itself)

| field | value |
|---|---|
| **capability** | 14 rule families mapping each DFDS doc section to test obligation types |
| **what it does** | `TEST-PIPELINE.md` (whole file): defines one-to-one mapping: every states.md transition-row = 1 test, every operations.md rule = 2+ tests, every interfaces.md endpoint×status = 1 contract test, etc. 14 rule families × exact cardinality per row. Applies to backend AND UI/E2E (rules 15–20 via `UI-SPEC.md`). |
| **files / lines** | `implementation/domainspec/TEST-PIPELINE.md` (full file, ~450 lines); `domainspec-generate-tests/SKILL.md` step 0 instructs "ENGINE-FIRST" using these exact rule families |
| **candidate verdict** | **IMPORT** |
| **why** | These are the *only* rule definitions anywhere in v1. The engine executes them; v2 must re-own them to govern test derivation. They are content, not code — import as canonical derivation contract, possibly reformulated into a typed obligation-schema. No owner in v2 yet. |
| **leverage** | **H** — no rule table = no deterministic engine in v2. |

---

### C2 — deterministic test-derivation engine (the executor)

| field | value |
|---|---|
| **capability** | No-LLM, no-network pipeline: `parse (docs → G) → derive (δ: pure) → obligation_key (sha1) → emit_spec / emit_tests` |
| **what it does** | `tools/test-derivation-engine/README.md:3-5`: "Compiles a feature's canonical Markdown feature docs into byte-stable test obligations with no LLM and no network in the derivation path, so determinism holds by construction (paper claim C2)." Executes rule families from C1. L0 gate passes on `financial-settlement`: 100% round-trip, byte-identical, tsc 0, 33/33 tests (`CRAFT.md:27`). Parses all 7 doc sections; issues stable `obligation_key = sha1(source_anchor | rule_type | canonical_params)` (`README.md:19`). |
| **files / lines** | `tools/test-derivation-engine/README.md:1–35`; `CRAFT.md:14–27`; `src/grammar/`, `src/ir/`, `src/rules/`, `src/keys/`, `src/emit/`, `src/roundtrip/` |
| **candidate verdict** | **IMPORT** |
| **why** | The engine is the highest-leverage artifact in the two-offers area. It is the load-bearing proof of claim C2. L0 PASSES on one feature; two active blockers to generalize (honesty-foundation gate BLK-TDE-GATE-HONESTY-001, bridging BLK-TDE-AUTH-CONVENTION-001 — `CRAFT.md:18`). Status: `implement` stage, not finished, but the core pipeline is real code with passing tests. Importable as the v2 engine seed with those blockers surfaced as v2 work items. |
| **leverage** | **H** — this is the structural differentiator; no import = v2 must rebuild from scratch. |
| **free / moat note** | See §2. |

---

### C3 — obligation_key (stable identity scheme)

| field | value |
|---|---|
| **capability** | Byte-stable sha1 identifier per obligation: `sha1(source_anchor | rule_type | canonical_params)` |
| **what it does** | `README.md:19`: obligation_key implemented and tested. Enables drift detection (round-trip = engine set ⊇ committed obligations ⇒ PASS), oracle id-bridging, and downstream freshness wiring (HANDOFF gap G2). |
| **files / lines** | `tools/test-derivation-engine/src/keys/` (implementation); `README.md:19`; `CRAFT.md:18` (committed id-map) |
| **candidate verdict** | **IMPORT** |
| **why** | The identity scheme is what makes the engine's output drift-checkable and what the `check` CLI uses for round-trip validation. If v2 imports the engine (C2), the key scheme comes with it — but it should be explicitly carried, not incidentally bundled, because it is the seam for correctness coupling (HANDOFF G2: does a generated test carry a read-set so it can be invalidated when its source spec changes?). |
| **leverage** | **H** (coupled to C2; but the design decision is separable). |

---

### C4 — LLM-backed domainspec-generate-tests skill (pre-engine path)

| field | value |
|---|---|
| **capability** | Agent-driven test spec derivation: reads `TEST-PIPELINE.md` rules and writes `TEST-SPEC.md` by hand |
| **what it does** | `domainspec-generate-tests/SKILL.md`: the legacy path before the engine existed. Skill still wires the two modes — ENGINE-FIRST (step 0: run `cli.js derive`), then LLM-authors *only* the non-engine surface (UI/E2E, scaffolding, story→test map). `SKILL.md:step 2`: "Author ONLY LLM-owned sections OUTSIDE the fence." |
| **files / lines** | `.claude/skills/domainspec-generate-tests/SKILL.md:27–45` |
| **candidate verdict** | **REFORMULATE** |
| **why** | The split is already v1's own verdict: engine owns backend-domain; LLM owns UI/E2E + scaffold. The skill as written is the correct boundary declaration. v2 should reformulate this as a clean two-surface protocol — not import the skill verbatim (it carries v1 path knowledge like `cli.js derive` invocation) but re-author the boundary spec. |
| **leverage** | **M** — the boundary matters; the skill file is the scaffolding, not the asset. |
| **free / moat note** | The LLM-authored surface (UI/E2E + stories) is unambiguously the *free path*. It is also the weaker guarantor; the engine is what backs C2. |

---

### C5 — fail-closed `check` gate (round-trip falsification)

| field | value |
|---|---|
| **capability** | Deterministic round-trip validator: engine set ⊇ committed obligations ⇒ PASS; otherwise FAIL with diff |
| **what it does** | `README.md:21–22` (`src/roundtrip/`): "L0 falsification gate: engine set ⊇ committed ⇒ PASS." `domainspec-generate-tests/SKILL.md:step 5`: `cli.js check {feature}` — FRESH = engine region matches docs AND no LLM row redefined an engine ID; on DRIFT, re-run step 0. This is the gate that makes the engine's output trustworthy and not silently stale. |
| **files / lines** | `tools/test-derivation-engine/README.md:21`; `src/roundtrip/`; `domainspec-generate-tests/SKILL.md:41–43` |
| **candidate verdict** | **IMPORT** |
| **why** | The check gate is the enforcement mechanism that closes the spec→test loop. Without it, imports of the engine (C2) and obligation_key (C3) can drift silently. ASSIMILATION-TABLE A1 explicitly names wiring the engine `check` / `validate-*` into a PostToolUse hook as the highest-ROI move in the whole external sweep. v2 inherits that finding: the gate is importable and should be the *first* wired capability. |
| **leverage** | **H** — wiring this as a PostToolUse hook is the single highest-ROI integration point (confirmed by ASSIMILATION-TABLE A1). |

---

### C6 — full end-to-end pipeline orchestration (domainspec-pipeline skill)

| field | value |
|---|---|
| **capability** | 11-step orchestrator: plan → spec → stories → tests → implement → tag-code → ui-pipeline → observability → instrument → infra-deploy → registry → verify → emit-signals → observer |
| **what it does** | `domainspec-pipeline/SKILL.md`: sequences all specialist skills; never bypasses delegates; propagates flags; emits signals to JSONL. Steps 4 (generate-tests) and 11 (dual-phase observer with "deterministic detector") are the two-offers touch-points. |
| **files / lines** | `.claude/skills/domainspec-pipeline/SKILL.md:29–256` |
| **candidate verdict** | **DROP** |
| **why** | The pipeline is an app-building orchestrator, not a governance/enforcement layer. v2's mission is "govern + enforce Ontology A on evidence" (SEED.md line 17), not to run build pipelines. Importing the pipeline would be an adapter-line violation — it presumes a running project with `docs/features/`, `drizzle/`, `infra/`, UI stacks. The test-derivation capability (C1–C5) is what v2 needs from the pipeline's step 4; the surrounding orchestration is out-of-layer. |
| **leverage** | — (DROP) |

---

### C7 — "ENGINE-FIRST" split contract (boundary declaration)

| field | value |
|---|---|
| **capability** | Architectural principle: engine owns backend-domain obligations; LLM authors only UI/E2E + scaffold; merge boundary fail-closed |
| **what it does** | `domainspec-generate-tests/SKILL.md:26–44`: the split is codified as a process rule. Engine region is fenced, byte-stable, drift-checkable. LLM region references engine obligation IDs read-only; never redefines a backend obligation. This is the free/moat boundary as v1 frames it. |
| **files / lines** | `.claude/skills/domainspec-generate-tests/SKILL.md:26-44` |
| **candidate verdict** | **IMPORT** |
| **why** | This is the conceptual contract that makes the two-offers coexist without collision. v2 must carry this boundary explicitly or risk LLM-authored obligations silently overwriting engine-derived ones. The boundary is protocol-level, not code-level — importable as a governance axiom for the v2 test surface. |
| **leverage** | **M** — architectural discipline, not a capability; but without it the other imports are incoherent. |

---

### C8 — UI/E2E obligation derivation (LLM-authored surface, rules 15–20)

| field | value |
|---|---|
| **capability** | Rules 15–20 in TEST-PIPELINE.md: Page Navigation, User Journey, Form Validation, State Reflection, Responsive Layout, Accessibility tests derived from UI-SPEC.md + UI-ARCHITECTURE.md |
| **what it does** | `TEST-PIPELINE.md:299–446`: six additional rule families that apply when a feature has a UI contract. These are LLM-authored — no engine counterpart exists. Template-based; traceable to UI-SPEC.md route/state/story declarations. |
| **files / lines** | `implementation/domainspec/TEST-PIPELINE.md:299–446` |
| **candidate verdict** | **REFORMULATE** |
| **why** | These rules exist in v1 but have no engine execution path; they are advice to an LLM agent. v2 can reformulate them as an obligation-schema addendum (the "LLM surface" of the two-lane split). They should not be imported verbatim because they assume Playwright + `docs/features/{feature}/UI-SPEC.md` existence — app-runtime artifacts. Reformulate as the "free path" obligation taxonomy under the ENGINE-FIRST boundary (C7). |
| **leverage** | **S** — secondary surface; the backend engine is the load-bearing half. |

---

## 2. Free path vs moat — resolution of the SEED contradiction

The SEED correctly flags that `test-engine/HANDOFF.md` (2026-06-12) calls the deterministic engine
the **"free wedge / publishable into public arcanum"** while ASSIMILATION-TABLE S3 (2026-06-29) +
the memory entry call it the **"proprietary moat"**.

**The contradiction is temporal, not logical.** HANDOFF.md was authored 2026-06-12, before the
engine had a passing L0 gate and before the moat framing was locked. By 2026-06-29, ASSIMILATION-TABLE
S3 is explicit: "Importing [an LLM-mediated test generator] is a *downgrade*: DomainSpec's engine is
no-LLM/no-network deterministic (the proprietary moat); take only the obligation-taxonomy as a
δ-coverage audit checklist." Memory entry `engine-algorithm-is-proprietary.md` confirms: "deterministic
engine: cite+demonstrate results, never publish the algorithm (the moat)."

**Resolution:**

| offer | label | what v1 frames it as |
|---|---|---|
| LLM-authored derivation (domainspec-generate-tests pre-engine path; rules 15–20 UI/E2E) | **FREE PATH** | Unambiguous: the skill file names it the "LLM-authored surface"; HANDOFF calls the engine "free" but that was before the moat decision |
| Deterministic no-LLM engine (C2–C3–C5 cluster) | **MOAT** | ASSIMILATION-TABLE S3 + memory; the *algorithm* is proprietary; the *claim* C2 + demonstrated results are publishable |

**Remaining ambiguity (for the skeptic):** HANDOFF O4 says "A deterministic engine is wedge, not moat." The later
ASSIMILATION-TABLE S3 verdict overrides this on evidence (the moat decision was made after HANDOFF).
However, the nuance is: the *demonstrated results* (L0 passing, obligation counts, byte-stability) are
publishable; the *algorithm* (the δ rule functions in `src/rules/`, the `obligation_key` derivation)
is the moat. v2 should import the engine for internal governance enforcement, not expose the δ rule
algorithm publicly. The boundary the import must respect: `src/rules/` contents stay private; the
obligation schema and the `check` gate behavior are describe-and-demonstrate-able.

---

## 3. Summary table

| # | Capability | Verdict | Leverage | Key reason |
|---|---|---|---|---|
| C1 | TEST-PIPELINE rule families (14+6) | **IMPORT** | H | Only rule definitions; no v2 owner yet |
| C2 | Deterministic test-derivation engine | **IMPORT** | H | Load-bearing C2 proof; real passing L0; moat algorithm private |
| C3 | obligation_key stable identity | **IMPORT** | H | Drift detection seam; couples C2 to correctness |
| C4 | LLM-backed generate-tests skill | **REFORMULATE** | M | Boundary declaration worth keeping; v1-specific path wiring is noise |
| C5 | fail-closed `check` gate | **IMPORT** | H | Highest-ROI wiring point (ASSIMILATION-TABLE A1); closes the loop |
| C6 | full pipeline orchestrator | **DROP** | — | Out-of-layer; adapter-line violation for v2's governance mission |
| C7 | ENGINE-FIRST split contract | **IMPORT** | M | Governance axiom; prevents LLM→engine collision |
| C8 | UI/E2E derivation rules (15–20) | **REFORMULATE** | S | Free-path taxonomy; reformulate sans Playwright/UI-SPEC assumptions |

**Candidate count: 8** (5 IMPORT, 2 REFORMULATE, 1 DROP).

**Top-3 by leverage:**
1. **C2 — deterministic engine** (H): the moat asset; import the implementation, keep `src/rules/` private.
2. **C5 — fail-closed `check` gate** (H): the one wiring gap ASSIMILATION-TABLE A1 called highest-ROI across the entire external sweep; closes the spec→test loop.
3. **C1 — TEST-PIPELINE rule families** (H): the derivation contract; without it the engine has no governed rule base.

**Single highest-leverage import: C5 (`check` gate wired as PostToolUse hook)** — every other import (engine, rules, keys) is already partially built; the gate wiring is the missing enforcement step that makes the entire two-offers surface automatically fail-closed on spec-doc writes rather than manually remembered.
